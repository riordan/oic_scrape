import scrapy
import json
from datetime import datetime, timedelta
from oic_scrape.items import AwardItem, AwardParticipant
from urllib.parse import urlencode

class NasaGrantsSpider(scrapy.Spider):
    name = "nasa_nssc_grants"
    allowed_domains = ["www3.nasa.gov"]
    base_url = "https://www3.nasa.gov/api/2/grants/_search"
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'HTTPCACHE_ENABLED': True,
        'HTTPCACHE_EXPIRATION_SECS': 60 * 60 * 24  # Cache for 24 hours
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_date = datetime(2006, 1, 1)
        self.end_date = datetime.now()
        self.current_date = self.start_date

    def start_requests(self):
        while self.current_date < self.end_date:
            next_date = self.current_date + timedelta(days=30)
            yield self.create_request(self.current_date, next_date)
            self.current_date = next_date

    def create_request(self, start_date, end_date):
        params = {
            'sort': 'grant_number:asc',
            'from': 0,
            'size': 10000,
            '_source_include': 'purchase_request_number,grant_number,pgrp_center,proposal_title,principal_investigator,technical_representative,institution_name,award_date,pop_start_date,pop_end_date,case_state,pr_task,program_title',
            'q': f'award_date:[{start_date.strftime("%Y-%m-%d")} TO {end_date.strftime("%Y-%m-%d")}] AND pgrp_center:* AND case_state:*'
        }
        url = f"{self.base_url}?{urlencode(params)}"
        return scrapy.Request(url, callback=self.parse, headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

    def parse(self, response):
        data = json.loads(response.body)
        for hit in data.get('hits', {}).get('hits', []):
            source = hit.get('_source', {})
            
            award = AwardItem(
                _crawled_at=datetime.now(),
                source="NASA",
                grant_id=f"NASA::{source.get('grant_number')}",
                funder_org_name="National Aeronautics and Space Administration",
                funder_org_ror_id="https://ror.org/027ka1x80",
                recipient_org_name=source.get('institution_name'),
                pi_name=source.get('principal_investigator'),
                grant_title=source.get('proposal_title'),
                program_of_funder=source.get('program_title'),
                #award_date=datetime.strptime(source.get('award_date'), "%Y-%m-%d").date() if source.get('award_date') else None,
                grant_start_date=datetime.strptime(source.get('pop_start_date'), "%Y-%m-%d").date() if source.get('pop_start_date') else None,
                grant_end_date=datetime.strptime(source.get('pop_end_date'), "%Y-%m-%d").date() if source.get('pop_end_date') else None,
                source_url="https://www3.nasa.gov/centers/nssc/forms/grant-status-form",
                raw_source_data=json.dumps(source),
                grant_year=int(source.get('award_date')[:4]) if source.get('award_date') else None,
                _award_schema_version="0.1.1"
            )

            # Add named participants
            named_participants = []
            if source.get('principal_investigator'):
                named_participants.append(AwardParticipant(
                    full_name=source['principal_investigator'],
                    is_pi=True,
                    grant_role="Principal Investigator"
                ))
            if source.get('technical_representative'):
                named_participants.append(AwardParticipant(
                    full_name=source['technical_representative'],
                    is_pi=False,
                    grant_role="Technical Officer"
                ))
            if named_participants:
                award.named_participants = named_participants

            yield award