import scrapy


class ChanzuckerbergComSpider(scrapy.Spider):
    name = "chanzuckerberg.com"
    allowed_domains = ["chanzuckerberg.com"]
    start_urls = ["https://chanzuckerberg.com"]

    def parse(self, response):
        pass
