import scrapy
from scrapy.spiders import Spider
from scrapy.selector import Selector
import dateparser

FUNDER_ROR_ID = "https://ror.org/011x6n313"
FUNDER_NAME = "Leona M. and Harry B. Helmsley Charitable Trust"


class HelmsleyOrgSpider(Spider):
    name = "helmsley.org_grants"
    allowed_domain = ["helmsleytrust.org"]
    start_urls = ["https://helmsleytrust.org/our-grants/"]

    custom_settings = {
        "PLAYWRIGHT_PROCESS_REQUEST_HEADERS": None,
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                },
                callback=self.parse,
                errback=self.errback,
            )

    async def parse(self, response):
        # get the page from the response
        page = response.meta["playwright_page"]

        #  Since the item index page remains the same and loads in new content
        # we will loop over the index page until we reach the end.
        while True: 
            # some wait method to wait for
            # the desired load state
            await page.wait_for_load_state()

            # get page content
            content = await page.content()
            # transform into a Selector
            selector = Selector(text=content)

            # extract llinks to item pages
            links = selector.css('td[data-title="GRANTEE"] a::attr(href)').extract()

            # follow the links by sending them to item processing function
            for itemLink in links:
                yield scrapy.Request(
                    itemLink,
                    meta={"playwright": True},
                    callback=self.crawl_item_page,
                    errback=self.errback,
                )

            # get the next page link
            nextButton = selector.css(".next")
            if (nextButton.css(".next.disabled") or not nextButton):
                break
            else:
                # Get Proceed to the next page and do it again.                
                await nextButton.click()
                # wait method
                await page.wait_for_timeout(3 * 1000)

        # Once we've reached the end, close the page and the context

        await page.close()
        await page.context.close()

    async def crawl_item_page(self, response):

        
        recipient_org_name = response.css('.headline::text').get()

        # We will select most items based on the <h6>tag</h6> that proceeds the <p>value</p> we care about
        award_date = await self.get_item_value_from_sibling(response, "Date of Award")
        grant_start_date = dateparser.parse(award_date)
        grant_year = grant_start_date.strftime('%Y') if grant_start_date else None
        grant_duration = await self.get_item_value_from_sibling(response, "Term of Grant")

        award_amount = await self.get_item_value_from_sibling(response,"Amount")

        program_of_funder = await self.get_item_value_from_sibling(response, "Program")
        grant_description = await self.get_item_value_from_sibling(response, "Project Title")

        


        data = {
            'funder_name': FUNDER_NAME,
            'funder_ror_id': FUNDER_ROR_ID,
            'recipient_org_name': recipient_org_name,
            'grant_start_date': grant_start_date,
            'grant_year': grant_year,
            'grant_duration': grant_duration, # Calculate the end-date
            'award_amount': award_amount,
            'award_currency': 'USD',
            'grant_description': grant_description,
            'program_of_funder': program_of_funder,
        }

        yield data
        

    async def get_item_value_from_sibling(self, response, helmsley_heading):
        """
        Returns the value from the helmsley item page by selecting the next sibling
        of the h6 tag that contains the helmsley_heading.
        e.g. `<h6>Date of Award</h6> <p>02.08.2023</p>` returns `02.08.2023`.
          """
        h6 = response.css(f"h6:contains('{helmsley_heading}')")
        if h6:
            value = h6.xpath("following-sibling::p[1]/text()").get()
            return value
        else:
            raise ValueError(f"Could not find {helmsley_heading} on the page {response.url}.")

    async def errback(self, failure):
        page = failure.request.meta.get("playwright_page")
        if page is not None:
            await page.close()
            await page.context.close()
