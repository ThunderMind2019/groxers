# -*- coding: utf-8 -*-
import re
import json

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Spider, Rule, Request

from groxers.items import Groxer


class JSpider(Spider):
    name = 'j.-parser'

    def parse(self, response):
        product = Groxer()
        product["name"] = response.css('.page-title > span::text').extract_first()
        product["pid"] = response.css('[itemprop="sku"]::text').extract_first()
        product["description"] = [d.strip() for d in response.css('[itemprop="description"] ::text').extract()]
        product["attributes"] = {row.css('th::text').extract_first(): row.css('td::text').extract_first()
                                 for row in response.css('#product-attribute-specs-table tr')}
        product["images"] = self.get_images(response)
        product["category"] = self.get_category(response)
        product["skus"] = self.get_skus(response)
        product["brand"] = 'J.'
        product["url"] = response.url
        return product

    def get_category(self, response):
        data = response.css('script:contains("var dlObjects =")::text').extract_first()
        return re.findall('category":"(.*?)"', data)[0].replace('\\', '')

    def get_images(self, response):
        data = json.loads(response.css('script:contains("mage/gallery/gallery")::text').extract_first())
        return [img['full'] for img in data['[data-gallery-role=gallery-placeholder]']['mage/gallery/gallery']['data']]

    def get_skus(self, response):
        data = response.css('script:contains("var dlObjects =")::text').extract_first()
        price = re.findall('price":"(.*?)"', data)[0]
        currency = response.xpath("//meta[@itemprop='priceCurrency']/@content").extract_first()
        
        color = response.css("td[data-th='Color']::text").extract_first()
        if not(color):
            color = "no_color"

        data = response.css(
            'script:contains("Magento_Swatches/js/swatch-renderer")::text').extract_first()
        if not data:
            return {color: {
                "color": color,
                "new_price": price.replace(",", ''),
                "currency_code": currency,
            }}

        data = json.loads(data)['[data-role=swatch-options]']['Magento_Swatches/js/swatch-renderer']
        raw_sizes = data['jsonConfig']['attributes']['963']['options']
        available_sizes = data['jsonSwatchConfig']['963'].keys()

        skus = {}
        for size in raw_sizes:
            skus[f'{color}_{size["label"]}'] = {
                "color": color,
                "size": size['label'],
                "out_of_stock": False if size['id'] in available_sizes else True,
                "new_price": price,
                "currency_code": currency,
            }

        return skus

class JCrawler(CrawlSpider):
    name = 'j.'
    parser = JSpider()
    allowed_domains = ['junaidjamshed.com']
    start_urls = ['https://www.junaidjamshed.com/']

    listings_css = ['.magicmenu', '.page']
    products_css = ['.product-item-photo']

    rules = (
        Rule(LinkExtractor(restrict_css=listings_css), callback='parse'),
        Rule(LinkExtractor(restrict_css=products_css), callback='parse_item'),
    )

    def start_requests(self):
        cookies = {'countrycurrency': 'PKR'}
        return [Request(self.start_urls[0], cookies=cookies)]

    def parse_item(self, response):
        return self.parser.parse(response)
