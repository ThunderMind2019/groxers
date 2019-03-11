# -*- coding: utf-8 -*-
from scrapy import Spider, Request

from groxers.items import Groxer


class MccSpider(Spider):
    name = 'mcc'
    start_urls = ['http://madinacashandcarry.com/']

    perishable_foods = ['89']

    def parse(self, response):
        cat_links = response.css('#cat_accordion a::attr(href)').extract()
        cat_links = [link for link in cat_links if 'javascript' not in link]
        for link in cat_links:
            if link.split('/')[-1] not in self.perishable_foods:
                yield Request(link, self.parse_products)
        
    def parse_products(self, response):
        product_links = response.css('.image a::attr(href)').extract()
        for link in product_links:
            yield Request(link, self.parse_product_details)
        
        next_link = response.css('[rel="next"]::attr(href)').extract_first()
        if next_link:
            yield Request(next_link, self.parse_products)
        
    def parse_product_details(self, response):
        groxery = Groxer()
        groxery['pid'] = response.css('#menu_id2::attr(value)').extract_first()
        groxery['name'] = response.css('#menu_name2::attr(value)').extract_first()
        groxery['images'] = response.css('.product-info .image .img-responsive::attr(src)').extract()
        groxery['sub_category'] = response.css('a[style]::text').extract()[-1]
        groxery['source'] = 'mcc'
        groxery['url'] = response.url

        groxery['brand'] = ''
        groxery['description'] = ''
        groxery['attributes'] = []
        groxery['skus'] = self.skus(response)
        return groxery
    
    def skus(self, response):
        skus = []

        sku = {}.copy()
        sku['color'] = 'No color'
        sku['size'] = 'one size'
        sku['currency'] = 'PKR'
        sku['price'] = response.css('.price-box .price-new::text').extract_first().replace('Rs.', '').strip()
        sku['prev_price'] = response.css('.price-box .price-old::text').extract_first().replace('Rs.', '').strip()
        skus.append(sku)
        return skus

