import scrapy

FUNDER_NAME = "Alfred P. Sloan Foundation"
FUNDER_ROR_ID = "https://ror.org/052csg198"

class SloanOrgSpider(scrapy.Spider):
    name = "sloan.org"
    allowed_domains = ["sloan.org"]
    start_urls = ["https://sloan.org"]

    def parse(self, response):
        # Your code here
        pass
