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
        'DOWNLOAD_DELAY': 1,  # Reduced from 3 to 1 second
        'CONCURRENT_REQUESTS_PER_DOMAIN': 4,  # Increased from 1 to 4 concurrent requests
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,  # Reduced from 5 to 1
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,  # Increased from 1.0 to 2.0
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'Mozilla/5.0 (compatible; IOIBot/1.0; +https://investinopen.org/)',
        # Error handling settings
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 3,  # Retry failed requests up to 3 times
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429],  # Common error codes to retry
        'DOWNLOAD_TIMEOUT': 30,  # Timeout after 30 seconds
        'CONCURRENT_REQUESTS': 16,  # Global concurrent request limit
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
        
        # Extract all applicants
        applicants = []
        applicant_links = response.css('div:contains("Applicant") .value a')
        for link in applicant_links:
            applicant_data = {
                'name': link.css('::text').get('').strip(),
                'url': link.css('::attr(href)').get()
            }
            applicants.append(applicant_data)
        
        # Store base data to pass through to callback
        base_data = {
            'crawl_ts': crawl_ts,
            'title': title,
            'description': description,
            'project_id': project_id,
            'source_url': response.url,
            'program_of_funder': program.strip() if program else None,
            'applicants': applicants
        }
        
        # Follow first applicant link if available
        if applicants:
            return response.follow(
                applicants[0]['url'],
                callback=self.parse_applicant_page,
                cb_kwargs=base_data
            )
        
        return self._create_award(base_data, None, [])

    def parse_applicant_page(self, response, **base_data):
        """Parse the applicant's page to get their institution and create participant"""
        # Extract institution from address
        address_block = response.css('.details p:contains("Adresse") span[style*="inline-block"]::text').getall()
        
        institution = None
        if address_block and not any("keine aktuelle Dienstanschrift" in line for line in address_block):
            institution = address_block[0].strip()
        
        # Create participant for current applicant
        current_applicant = base_data['applicants'][0]
        participant = AwardParticipant(
            full_name=current_applicant['name'],
            is_pi=True,  # All DFG applicants are considered PIs
            affiliations=[institution] if institution else None,
            grant_role="Applicant",  # German: "Antragsteller"
            identifiers={"dfg_person_id": current_applicant['url'].split('/')[-1]} if current_applicant['url'] else None
        )
        
        # Remove processed applicant and follow next if available
        remaining_applicants = base_data['applicants'][1:]
        if remaining_applicants:
            base_data['applicants'] = remaining_applicants
            return response.follow(
                remaining_applicants[0]['url'],
                callback=self.parse_applicant_page,
                cb_kwargs={
                    **base_data,
                    'institution': institution,
                    'participants': [participant]
                }
            )
        
        # All applicants processed
        return self._create_award(
            base_data,
            institution,
            [participant]
        )

    def _create_award(self, base_data, institution, participants):
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
            pi_name=participants[0].full_name if participants else None,
            named_participants=participants,
            _award_schema_version="0.1.1"
        )
        
        return award