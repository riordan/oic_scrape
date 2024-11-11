import scrapy
from datetime import datetime, date
from typing import Optional
import re
from oic_scrape.items import AwardItem, AwardParticipant

FUNDER_ORG_NAME = "James S. McDonnell Foundation"
FUNDER_ORG_ROR_ID = "https://ror.org/03dy4aq19"

class JsmfOrgSpider(scrapy.Spider):
    name = "jsmf_org_grants"
    allowed_domains = ["grants.jsmf.org"]
    start_urls = [
        f"https://grants.jsmf.org/results.php?general2=&submit=Search&year[]={year}"
        for year in range(1998, 2024)
    ]

    def parse(self, response):
        """Parse the search results page for a given year."""
        # Extract number of results for validation
        results_text = response.css("#showlinks p::text").get()
        if results_text:
            num_results = int(re.search(r"Search Results: (\d+)", results_text).group(1))
        
        # Parse each grant row
        for grant in response.xpath("//table[@class='table table-striped table-sm']/tr[position()>1]"):
            # Extract data from the listing
            grant_info = grant.css("td")[0]
            grant_details = grant.css("td")[1]
            
            # Get the grant URL and follow to detailed page
            grant_url = grant_info.css("a::attr(href)").get()
            if grant_url:
                yield response.follow(
                    grant_url,
                    callback=self.parse_grant_page,
                    meta={
                        "listing_data": {
                            "org_name": grant_info.css("strong::text").get(),
                            "researcher": grant_info.xpath(".//text()").re_first(r"\n(.*?)<br"),
                            "program": grant_info.xpath(".//text()").re_first(r"Program: (.*?)<br"),
                            "doi": grant_info.css("small a::text").get(),
                            "year": grant_details.xpath(".//text()").re_first(r"(\d{4})"),
                            "amount": grant_details.xpath(".//text()").re_first(r"\$([0-9,]+)"),
                            "country": grant_details.xpath(".//text()").re_first(r"\n(.*)$"),
                        }
                    }
                )

    def parse_grant_page(self, response):
        """Parse an individual grant page."""
        listing_data = response.meta["listing_data"]
        
        # Extract detailed grant information
        grant_info = response.css("#showlinks p::text").getall()
        grant_info = [text.strip() for text in grant_info if text.strip()]
        
        # Extract duration if available
        duration = None
        for info in grant_info:
            if "Duration:" in info:
                duration = info.split("Duration:")[-1].strip()
        
        # Get description paragraphs if they exist
        description = " ".join([
            p.strip() for p in response.css("p[style='padding-top:25px;']::text").getall()
        ])
        
        # Create AwardParticipant for the researcher if available
        named_participants = []
        researcher_name = listing_data["researcher"]
        if researcher_name:
            researcher = AwardParticipant(
                full_name=researcher_name.strip(),
                is_pi=True,
                affiliations=[listing_data["org_name"]],
                grant_role="Principal Investigator"
            )
            named_participants.append(researcher)

        # Format the award amount
        amount = float(listing_data["amount"].replace(",", "")) if listing_data["amount"] else None

        # Create the AwardItem
        award = AwardItem(
            _crawled_at=datetime.utcnow(),
            source="grants.jsmf.org",
            grant_id=f"jsmf:grants::{response.url.split('/')[-2]}",
            funder_org_name=FUNDER_ORG_NAME,
            funder_org_ror_id=FUNDER_ORG_ROR_ID,
            recipient_org_name=listing_data["org_name"],
            pi_name=researcher_name,
            named_participants=named_participants,
            grant_year=int(listing_data["year"]),
            grant_duration=duration,
            award_amount=amount,
            award_currency="USD" if amount else None,
            award_amount_usd=amount,
            source_url=response.url,
            grant_description=description if description else None,
            program_of_funder=listing_data["program"],
            raw_source_data=str(listing_data),
            _award_schema_version="0.1.1"
        )
        
        yield award 