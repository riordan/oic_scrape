from datetime import datetime
import scrapy
from oic_scrape.items import AwardItem

FUNDER_ORG_NAME = "Gordon and Betty Moore Foundation"
FUNDER_ORG_ROR_ID = "https://ror.org/006wxqw41"

class MooreOrgSpider(scrapy.Spider):
    name = "moore.org"
    allowed_domains = ["moore.org"]
    start_urls = ["https://www.moore.org/grants?showAll=true"]

    def parse(self, response):
        grant_urls = response.css('.grant-tiles a.button-white-teal::attr(href)').getall()
        for url in grant_urls:
            yield response.follow(url, self.parse_grant)


    def parse_grant(self, response):

        crawl_ts = datetime.utcnow()
        source_data = {
            "url": response.url,
        }
        # We use the CSS Selector preceeding the element we're looking for (in this case Grant Name) and then use the sibling selector to get the value
        source_data['grant_name'] = response.css('span:contains("Grant Name:") ~ h3::text').get()
        source_data['organization'] = response.css('div.bottom > div> h4 > a::text').get()
        source_data['date_awarded'] = response.css('div.bottom:nth-child(1) > ul:nth-child(1) > li:nth-child(1) > div:nth-child(2) > span:nth-child(1)::text').get()
        source_data['amount'] = response.css('div.bottom:nth-child(1) > ul:nth-child(1) > li:nth-child(2) > div:nth-child(2) > span:nth-child(1)::text').get()
        source_data['term'] = response.css('div.bottom:nth-child(1) > ul:nth-child(1) > li:nth-child(3) > div:nth-child(2) > span:nth-child(1)::text').get()
        source_data['grant_id'] = response.css('div.bottom:nth-child(1) > ul:nth-child(1) > li:nth-child(4) > div:nth-child(2) > span:nth-child(1)::text').get()
        source_data['funding_area'] = response.css('div.bottom:nth-child(1) > ul:nth-child(1) > li:nth-child(5) > div:nth-child(2) > span:nth-child(1)::text').get()

        source_data['description'] = response.css('.grant-detail-mid-content > div:nth-child(1) > p:nth-child(1)::text').get().strip()

        date_awarded = datetime.strptime(source_data['date_awarded'], '%b %Y')
        year_awarded = date_awarded.year
        amount = float(source_data['amount'].replace("$", "").replace(",", ""))

        award = AwardItem(
            _crawled_at = crawl_ts,
            grant_id=f"moore.org_{source_data['grant_id']}",
            funder_org_name=FUNDER_ORG_NAME,
            recipient_org_name=source_data['organization'],
            funder_org_ror_id=FUNDER_ORG_ROR_ID,
            source_url=source_data['url'],
            source="moore.org",
            grant_year = year_awarded,
            grant_duration=source_data['term'],
            award_amount=amount,
            award_currency="USD",
            award_amount_usd=amount,
            grant_title=source_data['grant_name'],
            grant_description=source_data['description'],
            program_of_funder=source_data['funding_area'],
            raw_source_data=str(source_data)
        )

        yield award
