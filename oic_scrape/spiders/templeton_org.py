from scrapy.spiders import SitemapSpider
from oic_scrape.items import AwardItem, AwardParticipant
from datetime import datetime, UTC
import json

FUNDER_ORG_NAME = "John Templeton Foundation"
FUNDER_ORG_ROR_ID = "https://ror.org/035tnyy05"

class TempletonOrgSpider(SitemapSpider):
    name = "templeton.org_grants"
    allowed_domains = ["templeton.org"]
    sitemap_urls = ["https://www.templeton.org/sitemap_index.xml"]
    sitemap_rules = [
        (r'^https?://www\.templeton\.org/grant/[^/]+/?$', 'parse_grant')  # Matches URLs like https://www.templeton.org/grant/<grant-slug>
    ]

    def parse_grant(self, response):
        crawl_ts = datetime.now(UTC)

        # Extract grant details
        grant_id = self.extract_text(response, ".grant-meta-bucket:contains('Grant ID') .small-meta")
        grant_title = response.css("h1::text").get(default="").strip()
        grant_description = response.css(".grant-content p::text").get(default="").strip()
        
        # Extract and process amount
        amount_str = self.extract_text(response, ".grant-meta-bucket:contains('Grant Amount') .small-meta")
        award_amount = self.parse_amount(amount_str)

        # Extract project leaders
        project_leaders = self.extract_text(response, ".grant-meta-bucket:contains('Project Leader') .small-meta")
        pi_names = [name.strip() for name in project_leaders.split(',') if name.strip()]

        # Extract recipient organization
        recipient_org_name = self.extract_text(response, ".grant-meta-bucket:contains('Grantee') .small-meta")

        # Extract program
        program_of_funder = self.extract_text(response, ".grant-meta-bucket:contains('Funding Area') .small-meta")

        # Create raw_source_data dictionary
        raw_source_data = {
            "url": response.url,
            "grant_id": "templeton_org::" + grant_id,
            "grant_title": grant_title,
            "project_leaders": project_leaders,
            "recipient_org_name": recipient_org_name,
            "amount": amount_str,
            "program": program_of_funder,
            "description": grant_description,
        }

        # Create AwardParticipant objects for project leaders
        named_participants = [
            AwardParticipant(
                full_name=name,
                is_pi=True,
                affiliations=[recipient_org_name],
                grant_role="Project Leader"
            ) for name in pi_names
        ]

        award = AwardItem(
            _crawled_at=crawl_ts,
            source="templeton.org",
            grant_id=f"templeton:grants::{grant_id}",
            funder_org_name=FUNDER_ORG_NAME,
            funder_org_ror_id=FUNDER_ORG_ROR_ID,
            recipient_org_name=recipient_org_name,
            pi_name=pi_names[0] if pi_names else None,
            named_participants=named_participants,
            award_amount=award_amount,
            award_currency="USD" if award_amount else None,
            award_amount_usd=award_amount,
            source_url=response.url,
            grant_title=grant_title,
            grant_description=grant_description,
            program_of_funder=program_of_funder,
            raw_source_data=json.dumps(raw_source_data) if isinstance(raw_source_data, dict) else raw_source_data,
            _award_schema_version="0.1.1"
        )

        yield award

    def extract_text(self, response, css_selector):
        return response.css(f"{css_selector}::text").get(default="").strip()

    def parse_amount(self, amount_str):
        if amount_str:
            try:
                return float(amount_str.replace("$", "").replace(",", ""))
            except ValueError:
                self.logger.warning(f"Could not parse award amount: {amount_str}")
        return None