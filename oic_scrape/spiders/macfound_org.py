import scrapy
from scrapy.spiders import SitemapSpider
from datetime import datetime
from oic_scrape.items import AwardItem
import re

FUNDER_NAME = "John D. and Catherine T. MacArthur Foundation"
FUNDER_ROR_ID = "https://ror.org/00dxczh48"

class MacfoundSpider(SitemapSpider):
    name = "macfound.org_grants"
    allowed_domains = ["macfound.org"]
    sitemap_urls = ["https://www.macfound.org/sitemap.xml"]
    sitemap_rules = [
        (r'/grantee/[^/]+-\d+/$', 'parse_grantee'),
    ]
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        #'DOWNLOAD_DELAY': 1,
    }

    def parse_grantee(self, response):
        """Parse a grantee profile page containing one or more grants."""
        
        # Extract grantee-level data
        recipient_name = response.css('section.gtee-profile-banner h1::text').get()
        recipient_location = response.css('div.gtee-profile-banner__place::text').get()
        
        # Process each grant in the timeline
        for grant in response.css('div.gtee-profile__timeline .card-item'):
            # Extract and clean year/duration
            year_text = grant.css('div.card-item--year strong::text').get()
            year_match = re.search(r'(\d{4})\s*(?:\((.*?)\))?', year_text)
            if year_match:
                year = int(year_match.group(1))
                duration = year_match.group(2)
            
            # Extract and clean amount
            amount_text = grant.css('div.card-item--amt strong::text').get()
            amount = float(re.sub(r'[^\d.]', '', amount_text)) if amount_text else None
            
            # Extract program and description
            program = grant.css('div.card-item--title a::text').get()
            description = grant.css('div.card-item--desc p::text').get()
            
            # Generate unique grant ID from URL and year
            grantee_id = response.url.split('/')[-2]
            grant_id = f"macfound::{grantee_id}::{year}"
            
            # Create source data dictionary
            source_data = {
                'url': response.url,
                'recipient_name': recipient_name,
                'recipient_location': recipient_location,
                'year_text': year_text,
                'amount_text': amount_text,
                'program': program,
                'description': description
            }

            yield AwardItem(
                _crawled_at=datetime.utcnow(),
                source="macfound.org",
                grant_id=grant_id,
                funder_org_name=FUNDER_NAME,
                funder_org_ror_id=FUNDER_ROR_ID,
                recipient_org_name=recipient_name,
                recipient_org_location=recipient_location,
                grant_year=year,
                grant_duration=duration,
                award_amount=amount,
                award_currency="USD" if amount else None,
                award_amount_usd=amount,
                source_url=response.url,
                grant_description=description,
                program_of_funder=program,
                raw_source_data=str(source_data),
                _award_schema_version="0.1.1"
            )