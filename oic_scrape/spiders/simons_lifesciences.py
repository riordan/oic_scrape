import scrapy
from datetime import datetime
from oic_scrape.items import AwardItem, AwardParticipant
import re

FUNDER_ORG_NAME = "Simons Foundation"
FUNDER_ORG_ROR_ID = "https://ror.org/01cmst727"

class SimonsLifeSciencesSpider(scrapy.Spider):
    """
    Spider for Simons Foundation Life Sciences Project Awards
    https://www.simonsfoundation.org/life-sciences/funding-opportunities/project-awards/
    """
    name = "simons.org_life-sciences"
    allowed_domains = ["simonsfoundation.org"]
    start_urls = ["https://www.simonsfoundation.org/life-sciences/funding-opportunities/project-awards/?type=all"]

    def parse(self, response):
        """Parse the main listing page and follow pagination."""
        
        # Process each grant on the current page
        for grant in response.css("article.m-post--tabular"):
            grant_url = grant.css("a.m-post__block-link::attr(href)").get()
            if grant_url:
                yield response.follow(grant_url, callback=self.parse_grant)

        # Follow pagination
        next_page = response.css("li.m-paging__next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_grant(self, response):
        """Parse individual grant pages."""
        crawl_ts = datetime.utcnow()

        # Extract grant details
        title = response.css("h1.o-page-header__title::text").get()
        
        # Extract PI and institution
        pi_info = response.css("div.m-person")
        pi_name = pi_info.css("span.m-person__title::text").get()
        institution = pi_info.css("::text").getall()[-1].strip()
        
        # Extract year
        year_text = response.css("section.m-block-meta p::text").get()
        grant_year = int(year_text) if year_text and year_text.isdigit() else None
        
        # Get subprogram from breadcrumbs
        breadcrumbs = response.css("ul.g-breadcrumbs__nav li a::text").getall()
        subprogram = next((crumb for crumb in breadcrumbs if "Microbial" in crumb), None)
        
        # Create program hierarchy
        program_of_funder = f"Life Sciences > {subprogram}" if subprogram else "Life Sciences"
        
        # Create unique grant ID from URL
        grant_id_match = re.search(r'/funded-project/([^/]+)/?$', response.url)
        grant_id = f"simons:lifesciences::{grant_id_match.group(1)}" if grant_id_match else None

        # Create AwardParticipant for PI
        pi = AwardParticipant(
            full_name=pi_name.strip() if pi_name else None,
            affiliations=[institution] if institution else None,
            grant_role="Principal Investigator",
            is_pi=True
        )

        # Store raw source data
        source_data = {
            "url": response.url,
            "title": title,
            "pi_name": pi_name,
            "institution": institution,
            "year": year_text,
            "subprogram": subprogram
        }

        # Create AwardItem
        award = AwardItem(
            _crawled_at=crawl_ts,
            source="simonsfoundation.org",
            grant_id=grant_id,
            funder_org_name=FUNDER_ORG_NAME,
            funder_org_ror_id=FUNDER_ORG_ROR_ID,
            recipient_org_name=institution,
            pi_name=pi_name,
            named_participants=[pi] if pi_name else None,
            grant_year=grant_year,
            grant_title=title,
            program_of_funder=program_of_funder,
            source_url=response.url,
            raw_source_data=str(source_data),
            _award_schema_version="0.1.1"
        )

        yield award 