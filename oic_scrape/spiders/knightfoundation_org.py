import scrapy
import json
from datetime import datetime
from oic_scrape.items import AwardItem, AwardParticipant

class KnightOrgSpider(scrapy.Spider):
    name = "knightfoundation_org_grants"
    allowed_domains = ["knightfoundation.org"]
    start_urls = ["https://knightfoundation.org/wp-json/knight-foundation-app/v1/grants?per_page=100&page=1&_locale=user"]
    
    def parse(self, response):
        data = json.loads(response.body)
        for grant in data:
            yield self.parse_grant(grant)
        
        # Check for next page
        current_page = int(response.url.split('page=')[1].split('&')[0])
        next_page = current_page + 1
        next_url = f"https://knightfoundation.org/wp-json/knight-foundation-app/v1/grants?per_page=100&page={next_page}&_locale=user"
        
        # Stop at page 50 or when no more grants are returned
        if next_page <= 50 and len(data) > 0:
            yield scrapy.Request(next_url, callback=self.parse)

    def parse_grant(self, grant):
        # Prepare comments
        comments = []
        if grant.get('challenges'):
            comments.append(f"Challenges: {', '.join(grant['challenges'])}")
        if grant.get('communities'):
            comments.append(f"Communities: {', '.join(grant['communities'])}")
            
        # Prepare named participants
        named_participants = None
        if grant.get('grantees'):
            named_participants = [
                AwardParticipant(
                    full_name=grantee['post_title'],
                    grant_role="Grantee",
                    identifiers={"post_id": str(grantee['ID'])}
                )
                for grantee in grant['grantees']
            ]
            
        # Parse start date if available
        grant_start_date = None
        if grant.get('started_on'):
            grant_start_date = datetime.strptime(grant['started_on'], "%Y-%m-%dT%H:%M:%S%z").date()

        # Create AwardItem with all fields set at initialization
        return AwardItem(
            _crawled_at=datetime.utcnow(),
            source="Knight Foundation",
            grant_id=f"knight_foundation::{grant['id']}",
            funder_org_name="John S. and James L. Knight Foundation",
            recipient_org_name=grant['grantees'][0]['post_title'] if grant['grantees'] else "Unknown",
            
            # Optional fields
            grant_title=grant['name'],
            grant_description=grant['description'],
            award_amount=float(grant['amount']) if grant['amount'] else None,
            award_amount_usd=float(grant['amount']) if grant['amount'] else None,
            award_currency='USD',
            grant_start_date=grant_start_date,
            grant_year=grant_start_date.year if grant_start_date else None,
            program_of_funder='>'.join([program['name'] for program in grant.get('programs', [])]),
            comments=' | '.join(comments) if comments else None,
            named_participants=named_participants,
            raw_source_data=json.dumps(grant),
            source_url=f"https://knightfoundation.org/grants/{grant['slug']}/",
            recipient_org_location=', '.join(grant['communities']) if grant.get('communities') else None
        )