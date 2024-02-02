import scrapy
from scrapy_playwright.page import PageMethod
FUNDER_ROR = "https://ror.org/04jsh2530"
FUNDER_NAME = "Andrew W. Mellon Foundation"


class MellonOrgSpider(scrapy.Spider):
    name = "mellon.org_grants"
    allowed_domains = ["mellon.org"]
        
    def start_requests(self):
       url = "https://www.mellon.org/grant-database"
       yield scrapy.Request(
           url,
           meta=dict(
               playwright=True,
               playwright_include_page=True,
               errback=self.errback,
               playwright_page_methods=[
                   PageMethod("wait_for_selector", ".mf-VB"),
                   PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                   PageMethod("wait_for_selector", ".mf-VB:nth-child(51)"),  # 10 per page
               ]
           ),
       )

    async def parse(self, response):
        pass

# Selector for the core grants table: .mf-VB
    
    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()