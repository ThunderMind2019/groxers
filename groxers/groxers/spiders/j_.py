# -*- coding: utf-8 -*-
import re
import json

from scrapy.http import Request, FormRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Spider, Rule

from groxers.items import Groxer
from groxers.tools import cleanse


class JSpider(Spider):
    name = 'j.-parser'

    def parse(self, response):
        product = Groxer()
        product["name"] = response.css('.page-title > span::text').extract_first()
        product["pid"] = response.css('[itemprop="sku"]::text').extract_first()
        product["description"] = cleanse(response.css('[itemprop="description"] ::text').extract())
        product["attributes"] = {row.css('th::text').extract_first(): [row.css('td::text').extract_first()]
                                 for row in response.css('#product-attribute-specs-table tr')}
        product["images"] = self.get_images(response)
        product["category"] = self.get_category(response)
        product["skus"] = self.get_skus(response)
        product["brand"] = 'J.'
        product['p_type'] = 'cloth'
        product['source'] = 'j.'
        product["url"] = response.url
        return product

    def get_category(self, response):
        data = response.css('script:contains("var dlObjects =")::text').extract_first()
        cat = response.css('[data-th="Product Category"]::text').extract() or []
        return [re.findall('category":"(.*?)"', data)[0].replace('\\', '')] + cat

    def get_images(self, response):
        data = json.loads(response.css('script:contains("mage/gallery/gallery")::text').extract_first())
        return [img['full'] for img in data['[data-gallery-role=gallery-placeholder]']['mage/gallery/gallery']['data']]

    def get_skus(self, response):
        data = response.css('script:contains("var dlObjects =")::text').extract_first()
        price = response.css('[data-price-type="finalPrice"]::attr(data-price-amount)').extract_first()
        prev_price = response.css('[data-price-type="oldPrice"]::attr(data-price-amount)').extract_first()
        currency = response.xpath("//meta[@itemprop='priceCurrency']/@content").extract_first()

        color = response.css("td[data-th='Color']::text").extract_first()
        if not(color):
            color = "no"

        common_sku = {
            "color": color,
            "price": price,
            "prev_price": prev_price,
            "currency": currency,
            "size": "one size",
        }

        data = response.css(
            'script:contains("Magento_Swatches/js/swatch-renderer")::text').extract_first()
        if not data:
            common_sku["out_of_stock"] = False
            return [common_sku]

        data = json.loads(data)['[data-role=swatch-options]']['Magento_Swatches/js/swatch-renderer']
        attrs = data['jsonConfig']['attributes']

        if not attrs:
            common_sku["out_of_stock"] = False
            return [common_sku]

        attr_type = 'size' if attrs.get('963') else 'color'
        available_sizes = list(data['jsonSwatchConfig'].values())[0].keys()

        skus = []
        for size in list(attrs.values())[0]['options']:
            sku = common_sku.copy()
            if attr_type == 'size':
                sku["size"] = size['label']
            else:
                sku['color'] = size['label']
            sku["out_of_stock"] = False if size['id'] in available_sizes else True
            skus.append(sku)
        return skus

class JCrawler(CrawlSpider):
    name = 'j.'
    parser = JSpider()
    allowed_domains = ['junaidjamshed.com']
    start_urls = ['https://www.junaidjamshed.com/']
    currency_url = 'https://www.junaidjamshed.com/directory/currency/switch/'

    listings_css = ['.magicmenu', '.page']
    products_css = ['.product-item-photo']

    rules = (
        Rule(LinkExtractor(restrict_css=listings_css), callback='parse'),
        Rule(LinkExtractor(restrict_css=products_css), callback='parse_item'),
    )

    def start_requests(self):
        payload = {
            'currency': 'PKR',
            'uenc': 'aHR0cHM6Ly93d3cuanVuYWlkamFtc2hlZC5jb20vamxhd24tcy0xOS0wODItcy1mbHV0dGVyLWN5YW4uaHRtbA,,',
            'form_key': 'SzmTLWFevFseoeyM',
        }
        return [FormRequest(self.currency_url, formdata=payload)]

    def parse_item(self, response):
        return self.parser.parse(response)
