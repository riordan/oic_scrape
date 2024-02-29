import scrapy
from scrapy.spiders import Spider
from scrapy.selector import Selector
import dateparser
from datetime import datetime
from dateutil.relativedelta import relativedelta
from oic_scrape.items import AwardItem
import re
from attrs import asdict

FUNDER_ROR_ID = "https://ror.org/011x6n313"
FUNDER_NAME = "Leona M. and Harry B. Helmsley Charitable Trust"


class HelmsleyOrgSpider(Spider):
    name = "helmsley.org_grants"
    allowed_domain = ["helmsleytrust.org"]
    start_urls = ["https://helmsleytrust.org/our-grants/"]

    custom_settings = {
        "PLAYWRIGHT_PROCESS_REQUEST_HEADERS": None,
        "HTTPCACHE_ENABLED": False,  # All Playwright scrapers require the HTTPCache be disabled
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 120
        * 1000,  # Use a longer navigation timeout
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
        """
        Crawls all ajax pages of https://helmsleytrust.org/our-grants/ to build the list of grant URLs.
        Then it will crawl each grant URL to extract the grant data.
        """
        # get the page from the response
        page = response.meta["playwright_page"]

        all_grants_urls = set()

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

            # extract links to item pages
            links = selector.css('td[data-title="GRANTEE"] a::attr(href)').extract()
            # add to list of all grants so we can crawl when finished with index
            all_grants_urls.update(links)

            self.logger.debug(
                f"The number of grants found so far: {len(all_grants_urls)}"
            )

            next_button_selector = "span.next:not(.disabled)"
            next_button = await page.query_selector(next_button_selector)
            last_page = await page.query_selector("span.next.disabled")
            self.logger.debug(f"next button context: {next_button}")

            if not last_page and next_button:
                data_page = await next_button.get_attribute("data-page")
                self.logger.debug(f"Requesting data-page {data_page}")
                # await asyncio.sleep(5)
                # Click the button to request data get to the next page
                await page.click(next_button_selector, timeout=60000)
                await page.wait_for_load_state(state="networkidle")
            else:
                self.logger.info("Reached the last index page.")
                break

        # I'm afraid I'm not collecting the last page, also the URL count is massive.
        # Lets just collect the final URLs again and deduplicate.
        content = await page.content()
        selector = Selector(text=content)
        links = selector.css('td[data-title="GRANTEE"] a::attr(href)').extract()
        all_grants_urls.update(links)

        # Deduplicate the list of grant URLs
        grant_urls = list(set(all_grants_urls))

        self.logger.debug(grant_urls)
        self.logger.debug(f"All grant URLS (count: {len(grant_urls)}):")
        await page.close()  # Close the index page

        self.logger.info("Beginning crawl of grant pages.")
        # follow the links by sending them to item processing function
        for url in grant_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                },
                callback=self.crawl_item_page,
                errback=self.errback,
            )
        self.logger.info("Completed crawl of grant pages.")

        # Once we've reached the end, close the page and the context
        self.logger.debug("Handling end of crawl. Closing the page and the context.")

    async def crawl_item_page(self, response):
        # page = response.meta["playwright_page"] # Use this to get the Playwright page context

        self.logger.info(f"Processing item page: {response.url}")
        recipient_org_name = response.css(".headline::text").get()

        # We will select most items based on the <h6>tag</h6> that proceeds the <p>value</p> we care about
        award_date = await self.get_item_value_from_sibling(response, "Date of Award")
        grant_duration = await self.get_item_value_from_sibling(
            response, "Term of Grant"
        )

        award_amount = await self.get_item_value_from_sibling(response, "Amount")

        program_of_funder = await self.get_item_value_from_sibling(response, "Program")
        grant_description = await self.get_item_value_from_sibling(
            response, "Project Title"
        )

        raw_source_data = {
            "url": response.url,
            "recipient_org_name": recipient_org_name,
            "award_date": award_date,
            "term_of_grant": grant_duration,
            "amount": award_amount,
            "project_title": grant_description,
            "program": program_of_funder,
        }

        # Now prepare additional fields that need configuration
        source_url = response.url

        # Get the Grant ID # from the URL
        # https://helmsleytrust.org/grants/association-sante-diabete-20196048/
        _match = re.search(r"(\d+)(?:/)?$", source_url)
        if _match:
            grant_id = f"helmsley:grants::{_match.group(1)}"
        else:
            raise ValueError(f"Could not find grant ID in the URL {source_url}.")
        
        formatted_award_amount = float(re.sub(r"[^\d.]", "", award_amount))

        grant_start_date = dateparser.parse(award_date)
        grant_year = int(grant_start_date.year) if grant_start_date else None
        # Calculate the grant end date based on the grant duration
        duration_in_months = re.search(r"\d+", grant_duration)
        if duration_in_months and grant_start_date:
            duration_in_months = int(duration_in_months.group())
            # Calculate the grant_end_date by adding the duration to the grant_start_date
            grant_end_date = grant_start_date + relativedelta(months=duration_in_months)
        else:
            grant_end_date = None

        award = AwardItem(
            grant_id=grant_id,
            funder_org_name=FUNDER_NAME,
            funder_org_ror_id=FUNDER_ROR_ID,
            recipient_org_name=recipient_org_name,
            grant_year=grant_year,
            grant_duration=grant_duration,
            grant_start_date=grant_start_date,
            grant_end_date=grant_end_date,
            award_amount=formatted_award_amount,
            award_currency="USD",
            award_amount_usd=formatted_award_amount,
            source="helmsleytrust.org",
            source_url=source_url,
            grant_description=grant_description,
            program_of_funder=program_of_funder,
            _crawled_at=datetime.utcnow(),
            raw_source_data=str(raw_source_data),
        )

        yield asdict(award)

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
            raise ValueError(
                f"Could not find {helmsley_heading} on the page {response.url}."
            )

    async def errback(self, failure):
        page = failure.request.meta.get("playwright_page")
        if page is not None:
            await page.close()
            await page.context.close()
