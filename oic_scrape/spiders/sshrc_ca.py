from datetime import datetime
import scrapy
import re
from urllib.parse import urlparse, parse_qs
from oic_scrape.items import AwardItem, AwardParticipant
from currency_converter import ECB_URL, CurrencyConverter, RateNotFoundError


"""
Scrapy Spider for SSHRC (Social Sciences and Humanities Research Council) Canada

Design Notes:
Currency Conversion to USD is estimated based on the exchange rate at the start of the calendar year of the award.
"""


class SshrcCaSpider(scrapy.Spider):
    name = "sshrc-ca"
    allowed_domains = ["www.outil.ost.uqam.ca"]
    start_urls = ["http://www.outil.ost.uqam.ca/CRSH/RechProj.aspx?vLangue=Anglais"]
    FUNDER_ORG_NAME = "Social Sciences and Humanities Research Council"
    FUNDER_ORG_ROR_ID = "https://ror.org/04j5jqy92"

    start_year = "1998"
    end_year = str(datetime.now().year + 1)

    def __init__(
        self,
        start_year: str = "1998",
        end_year: str = str(datetime.now().year + 1),
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # Adjust from exclusive end_year to inclusive end_year
        self.start_year = start_year
        self.end_year = str(int(end_year) - 1)

        self.currency_converter = CurrencyConverter(
            ECB_URL, fallback_on_missing_rate=True
        )

    def parse(self, response):
        # NOTE: There are diacritics in the POST API payload, so we need to be sure they're correctly encoded
        formdata = {
            "vVersion": "Normal",
            "vFinComp": "Comp",
            "vDebutC": self.start_year,
            "vFinC": self.end_year,
            "vLangue": "Anglais",
            "vProgramme": "Aucun critère",
            "vInstitut": "Aucun critère",
            "vDiscipline": "Aucun critère",
            "vSujet": "Aucun critère",
            "vRecherche": "optTitre",
            "vChoix": "Visualiser les projets",
            "TypeRapport": "HTML",
        }
        yield scrapy.FormRequest.from_response(
            response,
            formname="idValideCRSH",
            formdata=formdata,
            callback=self.parse_result_page,
        )

        pass

    def parse_result_page(self, response):
        award_listings = response.css("#lblResultat a::attr(href)").getall()
        for award_url in award_listings:
            yield scrapy.Request(
                response.urljoin(award_url), callback=self.parse_award_page
            )

        # Handle Pagination of Result Pages
        form_section = response.css("#ListeProjet")
        current_page = form_section.css("input#NoPage::attr(value)").get()
        total_pages_text = (
            form_section.css('td[align="center"]::text').getall()[-1].strip()
        )  # Get the last text element
        total_pages_match = re.search(r"of (\d+)", total_pages_text)
        total_pages = total_pages_match.group(1) if total_pages_match else None

        self.logger.debug(f"Index page {current_page} of {total_pages}")

        # Proceed to the next result page
        if total_pages and int(current_page) < int(total_pages):
            next_page = int(current_page) + 1
            yield scrapy.FormRequest.from_response(
                response,
                formname="ListeProjet",
                formdata={"NoPage": str(next_page)},  # Setting the page number
                callback=self.parse_result_page,
            )

    def build_Participant(
        self, name: str, title: str, is_pi: bool = False
    ) -> AwardParticipant:
        """
        Processes a name string into its parts and returns a corresponding AwardParticipant.

        Args:
            name (str): The name to process
            is_PI (bool, optional): Whether the name should be treated as a principal investigator. Defaults to False.

        Returns:
            AwardParticipant: An AwardParticipant object with the name parts filled in.
        """

        # Sees if theres a title in parentheses
        match = re.search(r"\((.*?)\)", name)
        if match:
            title = match.group(1)  # This is the text inside the parentheses
            name = name[
                : match.start()
            ].strip()  # This is the name up until the parentheses

        return AwardParticipant(full_name=name, grant_role=title, is_pi=is_pi)

    def parse_award_page(self, response):
        crawl_ts = datetime.utcnow()

        # Extract source data
        result_table = response.css("body > table:nth-child(2)")
        source_data = {"url": response.url}
        for row in result_table.css("tr"):
            label = row.css("td:first-child span::text").get()
            value = row.css("td:last-child span::text").get()
            if label and value:
                source_data[label.strip()] = value.strip()

        # Source Data Fields:
        # Project Title
        # Program
        # Fiscal Year
        # Competition Year
        # Applicant
        # Organization and Province
        # Amount Received
        # Discipline
        # Area of Research
        # Co-applicant
        # Keywords

        # Format fields for output
        parsed_url = urlparse(response.url)
        params = parse_qs(parsed_url.query)
        id_number = params.get("Cle", [None])[0]

        org_name, province = source_data.get("Organization and Province", "").rsplit(
            ",", 1
        )

        named_participants = []
        applicant = source_data.get("Applicant", "").strip()
        if applicant:
            named_participants.append(
                self.build_Participant(applicant, "Applicant", True)
            )
            pi_name = applicant

        if source_data["Co-applicant"] and source_data["Co-applicant"].strip() != "no co-applicant":
            co_applicants = source_data["Co-applicant"].split("\n")
            for co_applicant in co_applicants:
                named_participants.append(
                    self.build_Participant(co_applicant, "Co-applicant")
                )

        award_amount = source_data.get("Amount Received", None)
        if award_amount:
            award_amount = float(award_amount.replace("$", "").replace(",", ""))
            award_currency = "CAD"
            try:
                award_amount_usd = self.currency_converter.convert(
                    award_amount,
                    award_currency,
                    "USD",
                    date=datetime(int(source_data["Competition Year"]), 1, 1),
                )
            except RateNotFoundError:
                award_amount_usd = None

        award = AwardItem(
            grant_id=f"sshrc_ca:grants::{id_number}",
            source_url=response.url,
            funder_org_name=self.FUNDER_ORG_NAME,
            funder_org_ror_id=self.FUNDER_ORG_ROR_ID,
            recipient_org_name=org_name.strip(),
            recipient_org_location=province.strip(),
            pi_name=pi_name,
            named_participants=named_participants,
            grant_year=int(source_data.get("Competition Year", None)),
            award_amount=award_amount if award_amount else None,
            award_currency=award_currency if award_amount else None,
            award_amount_usd=award_amount_usd if award_amount else None,
            grant_title=source_data.get("Project Title", None),
            grant_description=source_data.get("Keywords", None),
            program_of_funder=f"{source_data['Program']} > {source_data['Discipline']} > {source_data['Area of Research']}",
            raw_source_data=str(source_data),
            source="http://www.outil.ost.uqam.ca/CRSH/RechProj.aspx",
            _crawled_at=crawl_ts,
        )

        yield award
