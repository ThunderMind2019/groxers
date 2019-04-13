# -*- coding: utf-8 -*-
from scrapy import Spider, Request

from groxers.items import Groxer
from groxers.tools import cleanse


class MccSpider(Spider):
    name = 'mcc'
    # allowed_domains = ['madinacashandcarry.com']
    start_urls = ['http://144.76.174.7/mcc2/']

    excluded_categories = ['20', '81', '85', '91']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
    }

    def parse(self, response):
        cat_links = response.css('#cat_accordion a::attr(href)').extract()
        cat_links = [link for link in cat_links if 'javascript' not in link]
        for link in cat_links:
            if link.split('/')[-1] not in self.excluded_categories:
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
        groxery['category'] = cleanse(response.css('[itemprop="title"] ::text').extract())
        groxery['source'] = 'mcc'
        groxery['url'] = response.url
        groxery['brand'] = 'Madina C&C'
        groxery['description'] = []
        groxery['attributes'] = {}.copy()
        groxery['p_type'] = 'groxer'
        groxery['skus'] = self.skus(response)
        return groxery

    def skus(self, response):
        skus = []

        sku = {}.copy()
        sku['color'] = 'no'
        sku['size'] = 'one size'
        sku['currency'] = 'PKR'
        sku['price'] = response.css('.price-box .price-new::text').extract_first().replace('Rs.', '').strip()
        sku['prev_price'] = response.css('.price-box .price-old::text').extract_first().replace('Rs.', '').strip()
        sku['out_of_stock'] = False
        skus.append(sku)
        return skus

