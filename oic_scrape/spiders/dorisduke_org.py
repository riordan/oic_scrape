from typing import Dict, List, Optional
import scrapy
import json
from oic_scrape.items import AwardItem
from datetime import datetime

# NOTE: In the current iteration, this scraper does not handle multiple-listing grant pages
# Examples:
# - https://www.dorisduke.org/grants/what-weve-funded/Grant-Recipients/Talented-Students-in-the-Arts-Initiative----Leading-National-Performing-Arts--Training-Institutions1/
# - https://www.dorisduke.org/grants/what-weve-funded/Grant-Recipients/sickle-cell-diseaseadvancing-cures/
# - https://www.dorisduke.org/grants/what-weve-funded/Grant-Recipients/2020-doris-duke-artist-awards/


FUNDER_ORG_NAME = "Doris Duke Charitable Foundation"
FUNDER_ORG_ROR_ID = "https://ror.org/04n65rp89"

class DorisdukeOrgSpider(scrapy.Spider):
    name = "dorisduke.org_grants"
    source_name = "dorisduke.org"
    source_type = "grants"
    allowed_domains = ["dorisduke.org"]
    start_urls = ["https://www.dorisduke.org/grants/what-weve-funded/"]

    def get_grants(self,response) -> Optional[List[Dict]]:
        """
        Returns the list of grants on a Dorris Duke What We've Funded page

        Grant categories / subcategories are only visible on the indexes and need to be collected
        https://www.dorisduke.org/grants/what-weve-funded/
        https://www.dorisduke.org/grants/what-weve-funded/?1=1&GrantProgramID=5&GrantInitiativeID=0&GrantDate=0&GrantShow=12&GrantSortBy=0#grant-filter
        """
        scripts = response.css('script::text').getall()
        for script in scripts:
            if "var grants = [" in script:
                script_content = script 
        # Extract the relevant portion of the JavaScript
        start_index = script_content.find('var grants = ') + len('var grants = ')
        end_index = script_content.find(';;')  # Assuming ';;' marks the end consistently
        json_data = script_content[start_index:end_index]

        # Load the grants as json
        grants = json.loads(json_data)
        return grants if grants else None
    
    
    def parse(self, response):

        # get our main list of all grants
        all_grants = self.get_grants(response)
  

        # Process the grants
        if all_grants:
            for grant in all_grants:
                grant_url = grant[3]  # Assuming the index is correct
                yield scrapy.Request(response.urljoin(grant_url), callback=self.parse_grant_page)
            
    def parse_grant_page(self, response):
        crawl_ts = datetime.utcnow()
        source_data = {}
        source_data['url'] = response.url
        source_data['recipient_org_name'] = response.css('.ddcf-text--heading-hero-text::text').get()

        award_content = response.css('.ddcf-module--content-wysiwyg')
        content_paragraphs = award_content.css('p')

        source_data['awarded_on'] = content_paragraphs[0].css('::text').get().strip()
        source_data['amount_duration'] = content_paragraphs[1].css('::text').get().strip()

        description = ""
        for paragraph in content_paragraphs[2:-1]:
            paragraph_text = paragraph.css('::text').get()
            if paragraph_text:
                description += paragraph_text.strip() + " "
        if len(description) > 1:
            description = description.strip()
        
        source_data['description'] = description

        source_data['project_url'] = content_paragraphs[-1].css('a::attr(href)').get()

        # Format fields
        date_str = source_data['awarded_on'].replace("Awarded: ", "")
        start_date = datetime.strptime(date_str, "%b %d, %Y")

        amount_str = source_data['amount_duration'].split(" ")[0]
        award_amount = float(amount_str.replace("$", "").replace(",", ""))

        duration = source_data['amount_duration'].split("over ")[-1]

        award = AwardItem(
            _crawled_at = crawl_ts,
            grant_id = f"dorisduke:grants::{source_data['url']}",
            funder_org_name = FUNDER_ORG_NAME,
            funder_org_ror_id = FUNDER_ORG_ROR_ID,
            recipient_org_name = source_data['recipient_org_name'],
            grant_year = start_date.year,
            grant_duration = duration,
            grant_start_date = start_date,
            award_amount = award_amount,
            award_currency = "USD",
            award_amount_usd = award_amount,
            source = "dorrisduke.org",
            source_url = source_data['url'],
            grant_description = source_data['description'],
        )

        yield award
        
