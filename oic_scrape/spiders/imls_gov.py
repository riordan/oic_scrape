import scrapy
from oic_scrape.items import GrantItem
from datetime import datetime

FUNDER_NAME = "Institute of Museum and Library Services"
FUNDER_ROR = "https://ror.org/030prv062"

class ImlsGovSpider(scrapy.Spider):
    name = "imls.gov_grants"

    allowed_domains = ["imls.gov"]
    start_urls = ['https://www.imls.gov/grants/awarded-grants']


    def parse(self, response):
        # Extracting the links to the grant detail pages
        for grant_link in response.css('td.views-field-title a::attr(href)').getall():
            yield response.follow(grant_link, self.parse_grant)

        # Following the pagination link
        next_page = response.css('.pager__item--next a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
    
    def parse_grant(self, response):
        # Extract values

        imls_log_number_raw = response.css('.title--small > span::text').get()
        if imls_log_number_raw:
            imls_log_number = imls_log_number_raw.strip()
        else:
            imls_log_number = None  # Or some default value


        id = f"imls:log_number::{imls_log_number}"
        program_of_funder = response.css('div.field--name-field-program-categories-text .field__item::text').get()
        grant_year = response.css('div.field--name-field-fiscal-year-text .field__item::text').get()

        award_amount_raw = response.css('div.field .field__label:contains("Federal Funds") + .field__item::text').get()
        if award_amount_raw:
                award_amount = award_amount_raw.strip()
        else:
            award_amount = None
        
        award_currency = 'USD'  # Assuming USD for simplicity
        award_amount_usd = award_amount  # Assuming amount is already in USD
        city = response.css('div.field--name-field-city .field__item::text').get()
        state = response.css('div.field--name-field-states .field__item::text').get()
        recipient_org_name = response.css('.field--name-field-institution::text').get()
        recipient_location = f"{city}, {state}"
        funder_name = FUNDER_NAME 
        funder_ror_id = FUNDER_ROR
        grant_description = response.css('div.clearfix:nth-child(4)::text').get() #least bad way of doing this for now?
        _crawled_at = datetime.utcnow()

        # Create an instance of GrantItem
        item = GrantItem(
            grant_id = id,
            program_of_funder=program_of_funder,
            grant_year=grant_year,
            award_amount=award_amount,
            award_currency=award_currency,
            award_amount_usd=award_amount_usd,
            recipient_org_name=recipient_org_name,
            recipient_location=recipient_location,
            grant_description=grant_description,
            funder_name=funder_name,
            funder_ror_id=funder_ror_id,
            source = 'imls.gov',
            _crawled_at=_crawled_at
        )

        # Return the populated item
        yield item