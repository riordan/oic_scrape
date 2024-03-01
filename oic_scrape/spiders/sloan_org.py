import scrapy
import re

from oic_scrape.items import AwardItem, AwardParticipant
from datetime import datetime

FUNDER_ORG_NAME = "Alfred P. Sloan Foundation"
FUNDER_ORG_ROR_ID = "https://ror.org/052csg198"


class SloanSpider(scrapy.Spider):
    source_name = "sloan.org"
    source_type = "grants"
    name = f"{source_name}_{source_type}"

    def start_requests(self):
        url = "https://sloan.org/grants-database?page=1"
        yield scrapy.Request(url)

    def parse(self, response):
        """
        @url https://sloan.org/grants-database?page=1
        @returns items 0 10
        @scrapes grant_id funder_name funder_ror_id recipient_org_name pi_name grant_year award_amount award_currency award_amount_usd source grant_description program_of_funder _crawled_at
        """

        crawl_ts = datetime.utcnow()

        for grant in response.xpath(
            "//div[@class='database-grants']/ul[@class='data-list']/li"
        ):
            # Get the core grant data:
            permalink_rel = grant.css("a.permalink::attr(href)").get()
            permalink_url = response.urljoin(permalink_rel)
            grantee = grant.css("div.grantee").re(r"</span>(.*)\n\t</div>")[0]
            amount = grant.css("div.amount").re(r"</span>(.*)\n\t</div>")[0]
            city = grant.css("div.city").re(r"</span>(.*)\n\t</div>")[0]
            year = grant.css("div.year").re(r"</span>(.*)\n\t</div>")[0]
            description = grant.css("div.brief-description > p").get(default=None)
            # Get the weird things that are hard to extract, then assign them
            kv = {"Sub-program": None, "Program": None, "Investigator": None}
            for label in grant.css("ul.col li"):
                k = label.css("span.label").get(default=None).strip()
                v = label.css("li").re(r"</span>\s*(.*)\s*</li>")[0]
                kv[k] = v
            program = kv["Program"]
            sub_program = kv["Sub-program"]
            investigator = kv["Investigator"]

            source_data = {
                "permalink_url": permalink_url,
                "grantee": grantee,
                "amount": amount,
                "city": city,
                "year": year,
                "description": description,
                "program": program,
                "sub_program": sub_program,
                "investigator": investigator,
            }

            # additional formatting
            gid_match = re.search("/grant-detail/(.*)", permalink_rel)
            grant_id = gid_match.group(1) if gid_match else None
            program_of_funder = (
                f"{kv['Program']} > {kv['Sub-program']}"
                if kv["Sub-program"]
                else kv["Program"]
            )
            award_amount = float(re.sub(r"\D", "", amount))

            pi = AwardParticipant(
                full_name=str(investigator),
                affiliations=[grantee],
                grant_role="Investigator",
                is_pi=True,
            )

            award = AwardItem(
                _crawled_at=crawl_ts,
                source="https://sloan.org/fellows-database",
                grant_id=f"sloan:grants::{grant_id}",
                funder_org_name=FUNDER_ORG_NAME,
                recipient_org_name=grantee,
                funder_org_ror_id=FUNDER_ORG_ROR_ID,
                pi_name=pi.full_name,
                named_participants=[pi],
                grant_year=int(year) if year else None,
                award_amount=award_amount,
                award_currency="USD",
                award_amount_usd=award_amount,
                source_url=permalink_url,
                grant_description=description,
                program_of_funder=program_of_funder,
                raw_source_data=str(source_data),
                _award_schema_version="0.1.0",
            )

            yield award

        next_page = response.css("a.pager-right::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)


class SloanResearchFellowSpider(scrapy.Spider):
    """
    Spider for the Sloan Research Fellowships
    https://sloan.org/fellows-database
    """

    source_name = "sloan.org"
    source_type = "research-fellowships"
    name = "sloan.org_research-fellowships"

    def start_requests(self):
        # Because we only have the index page, the only way to have a deterministic URL to spot-check a record is for us to use ascending pages by year
        url = "https://sloan.org/fellows-database?dynamic=1&order_by=approval_year&order_by_direction=asc&limit=10&page=1"
        yield scrapy.Request(url)

    def parse(self, response):
        """
        @url https://sloan.org/fellows-database?dynamic=1&order_by=approval_year&order_by_direction=asc&limit=10&page=1
        @returns items 0 10
        """
        crawl_ts = datetime.utcnow()

        for fellow in response.xpath(
            "//div[@class='database-fellows']/ul[@class='data-list']/li"
        ):
            # Get all the elements
            first_name = fellow.css("div.first-name *::text").getall()
            last_name = fellow.css("div.last-name *::text").getall()
            university = fellow.css("div.university *::text").getall()
            field = fellow.css("div.field *::text").getall()
            year = fellow.css("div.year *::text").getall()
            url = response.url

            # Join the extracted text elements:
            first_name = first_name[-1].strip() if first_name else None
            last_name = last_name[-1].strip() if last_name else None
            university = university[-1].strip() if university else None
            field = field[-1].strip() if field else None
            year = year[-1].strip() if year else None

            source_data = {
                "first_name": first_name,
                "last_name": last_name,
                "university": university,
                "field": field,
                "year": year,
                "url": url,
            }

            fellow = AwardParticipant(
                full_name=f"{first_name} {last_name}",
                first_name=first_name,
                last_name=last_name,
                affiliations=[university],
                grant_role="Sloan Research Fellow",
                is_pi=True,
            )

            award = AwardItem(
                _crawled_at=crawl_ts,
                source="https://sloan.org/fellows-database",
                grant_id=f"ioi::sloan.org:fellows::{year}-{last_name}-{first_name}",
                funder_org_name=FUNDER_ORG_NAME,
                funder_org_ror_id=FUNDER_ORG_ROR_ID,
                recipient_org_name=university,
                pi_name=fellow.full_name,
                named_participants=[fellow],
                grant_year=int(year),
                grant_duration="1 year",
                source_url=url,
                program_of_funder=f"Sloan Research Fellowship > {field}",
                raw_source_data=str(source_data),
                _award_schema_version="0.1.0",
            )

            yield award

        next_page = response.css("a.pager-right::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
