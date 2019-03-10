# -*- coding: utf-8 -*-
from scrapy import Spider, Request


class MccSpider(Spider):
    name = 'mcc'
    start_urls = ['http://madinacashandcarry.com/']

    def parse(self, response):
        cat_links = response.css('#cat_accordion a::attr(href)').extract()
        cat_links = [link for link in cat_links if 'javascript' not in link]
        for link in cat_links:
            yield Request(link, self.parse_products)
        
    def parse_products(self, response):
        product_links = response.css('.image a::attr(href)').extract()
        for link in product_links:
            yield Request(link, self.parse_product_details)
        
    def parse_product_details(self, response):
        name = response.css('[itemprop="name"] ::text').extract_first().strip()
        print(name)

