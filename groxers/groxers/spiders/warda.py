# -*- coding: utf-8 -*-
import re
import json

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Spider, Rule, Request

from groxers.items import Groxer
from groxers.tools import cleanse


class WardaSpider(Spider):
    name = 'warda-parser'

    def parse(self, response):
        product = Groxer()
        product["name"] = ' '.join(cleanse(response.css('[itemprop="name"] ::text').extract()))
        product["pid"] = response.css('.variant-sku::text').extract_first()
        product["description"] = cleanse(response.css('#collapse-tab1 ::text').extract())
        product["attributes"] = {}
        product["images"] = [f'https:{i}' for i in response.css(
            '.picture-product ::attr(data-zoom-image)').extract()]
        product["category"] = response.meta.get('category') or ['']
        product["skus"] = self.get_skus(response)
        product["brand"] = 'WARDA'
        product['p_type'] = 'cloth'
        product['source'] = 'warda'
        product["url"] = response.url
        return product

    def get_skus(self, response):
        data = response.css('script:contains("var json_product =")::text').extract_first()
        # import pdb; pdb.set_trace()
        raw_data = re.findall('var json_product\s*=\s*({.*})', data)[0]
        raw_data = json.loads(raw_data)
        skus = []

        try:
            color_index = raw_data['options'].index('Color')
        except:
            color_index = -1
        
        try:
            size_index = raw_data['options'].index('Size')
        except:
            size_index = -1


        for variant in raw_data['variants']:
            attrs = variant['title'].split('/')
            skus.append({
                "color": attrs[color_index] if color_index != -1 else 'no',
                "size": attrs[size_index] if size_index != -1 else 'one size',
                "out_of_stock": False if variant['available'] else True,
                "price": variant['price']/100,
                "currency": 'PKR',
            })

        return skus


class WardaCrawlSpider(CrawlSpider):
    name = 'warda'
    parser = WardaSpider()
    allowed_domains = ['warda.com.pk']
    start_urls = ['https://warda.com.pk/']

    listings_css = ['.mega-menu', '[rel="next"]']
    products_css = ['.product-grid-image']

    rules = (
        Rule(LinkExtractor(restrict_css=listings_css, tags=['a', 'link']), callback='parse'),
        Rule(LinkExtractor(restrict_css=products_css), callback='parse_item'),
    )

    custom_settings = {
        'DOWNLOAD_DELAY': 1.5,
    }

    def parse(self, response):
        category = cleanse(response.css('.breadcrumb ::text').extract())[1:]
        category = [c for c in category if 'Home' not in c and c != '/']
        for req in super().parse(response):
            req.meta['category'] = category
            yield req

    def parse_item(self, response):
        return self.parser.parse(response)
