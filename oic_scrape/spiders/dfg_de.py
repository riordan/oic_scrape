import scrapy
from scrapy.spiders import SitemapSpider
from datetime import datetime, date
from oic_scrape.items import AwardItem, AwardParticipant
import re

FUNDER_NAME = "Deutsche Forschungsgemeinschaft"
FUNDER_ROR_ID = "https://ror.org/018mejw64"

class DfgDeSpider(SitemapSpider):
    name = "dfg.de_grants"
    allowed_domains = ["gepris.dfg.de"]
    sitemap_urls = ["https://gepris.dfg.de/gepris/sitemap_index.xml"]
    
    # Only follow projekt URLs from sitemap
    sitemap_rules = [
        ('/projekt/', 'parse_grant')
    ]

    # Add politeness delays and concurrency settings
    custom_settings = {
        'DOWNLOAD_DELAY': 3,  # 3 second delay between requests
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,  # Only one request at a time
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 5,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'Mozilla/5.0 (compatible; IOIBot/1.0; +https://investinopen.org/)'
    }

    def parse_grant(self, response):
        """Parse individual grant pages"""
        crawl_ts = datetime.utcnow()
        
        # Extract basic grant information
        title = response.css('h1.facelift::text').get('').strip()
        description = response.css('#projekttext::text').get('').strip()
        
        # Extract project identifier
        project_id = response.css('.projektnummer .value::text').get()
        if project_id:
            project_id = project_id.split('- Project number')[-1].strip()
        
        # Extract program information
        program = response.css('div:contains("DFG-Verfahren") .value::text').get('')
        
        # Store base data to pass through to callback
        base_data = {
            'crawl_ts': crawl_ts,
            'title': title,
            'description': description,
            'project_id': project_id,
            'source_url': response.url,
            'program_of_funder': program.strip() if program else None
        }
        
        # Extract applicant link and follow it
        applicant_link = response.css('div:contains("Applicant") .value a::attr(href)').get()
        if applicant_link:
            return response.follow(
                applicant_link,
                callback=self.parse_applicant_page,
                cb_kwargs=base_data
            )
        
        # If no applicant link, yield with no institution
        return self._create_award(base_data, None)

    def parse_applicant_page(self, response, **base_data):
        """Parse the applicant's page to get their institution"""
        # Extract institution from address
        address_block = response.css('.details p:contains("Adresse") span[style*="inline-block"]::text').getall()
        
        institution = None
        if address_block and not any("keine aktuelle Dienstanschrift" in line for line in address_block):
            # First line of address is institution name
            institution = address_block[0].strip()
        
        return self._create_award(base_data, institution)

    def _create_award(self, base_data, institution):
        """Helper to create award with consistent data"""
        award = AwardItem(
            _crawled_at=base_data['crawl_ts'],
            source="dfg.de",
            grant_id=f"dfg:grants::{base_data['project_id']}",
            funder_org_name=FUNDER_NAME,
            funder_org_ror_id=FUNDER_ROR_ID,
            recipient_org_name=institution if institution else "Institution Not Listed",
            grant_title=base_data['title'],
            grant_description=base_data['description'],
            source_url=base_data['source_url'],
            program_of_funder=base_data['program_of_funder'],
            _award_schema_version="0.1.1"
        )
        
        return award