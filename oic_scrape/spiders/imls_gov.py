import scrapy
from scrapy.selector import Selector
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
        program_of_funder = response.css('div.field--name-field-program-categories-text .field__item::text').get()
        grant_year = response.css('div.field--name-field-fiscal-year-text .field__item::text').get()
        award_amount = response.css('div.field .field__label:contains("Federal Funds") + .field__item::text').get()
        award_currency = 'USD'  # Assuming USD for simplicity
        award_amount_usd = award_amount  # Assuming amount is already in USD
        city = response.css('div.field--name-field-city .field__item::text').get()
        state = response.css('div.field--name-field-states .field__item::text').get()
        recipient_location = f"{city}, {state}"
        grant_description = response.css('div.grant-body .text-formatted .field__item::text').get()
        funder_name = FUNDER_NAME 
        funder_ror_id = FUNDER_ROR
        _crawled_at = datetime.utcnow()

        # Create an instance of GrantItem
        item = GrantItem(
            program_of_funder=program_of_funder,
            grant_year=grant_year,
            award_amount=award_amount,
            award_currency=award_currency,
            award_amount_usd=award_amount_usd,
            recipient_location=recipient_location,
            grant_description=grant_description,
            funder_name=funder_name,
            funder_ror_id=funder_ror_id,
            _crawled_at=_crawled_at
        )

        # Return the populated item
        yield item