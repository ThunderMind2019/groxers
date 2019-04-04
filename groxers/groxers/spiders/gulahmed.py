# -*- coding: utf-8 -*-
import re
import json
from scrapy import Spider, Request

from groxers.items import Groxer
from groxers.tools import cleanse


class GulahmedSpider(Spider):
    name = 'gulahmed'
    allowed_domains = ['gulahmedshop.com']
    start_urls = ['https://www.gulahmedshop.com']

    def parse(self, response):
        category_links = response.xpath(
            "//a[@class='menu-link']")[:-1]
        for link in category_links:
            yield Request(link.css('::attr(href)').extract_first(), self.parse_product_links,
                                 meta={'category': cleanse(link.css('span::text').extract())})

    def parse_product_links(self, response):
        product_links = response.xpath(
            "//a[contains(@class, 'product-item-photo')]/@href").extract()
        for link in product_links:
            yield Request(link, self.parse_product_details, meta=response.meta.copy())

        next_link = response.xpath("//a[@title='Next']/@href").extract_first()
        if next_link:
            yield Request(next_link, self.parse_product_links, meta=response.meta.copy())

    def parse_product_details(self, response):
        product = Groxer()
        product["name"] = response.xpath("//span[@data-ui-id]/text()").extract_first()
        product["pid"] = response.xpath("//div[@itemprop='sku']/text()").extract_first()
        product["description"] = self.get_item_description(response)
        product["images"] = self.get_item_images(response)
        product['category'] = response.meta['category']
        product['brand'] = 'Gul Ahmed'
        product["attributes"] = self.get_item_attributes(response)
        product["skus"] = self.get_item_skus(response)
        product['p_type'] = 'cloth'
        product['source'] = 'gulahmed'
        product["url"] = response.url
        yield product

    def get_item_description(self, response):
        raw_desc = response.xpath("//div[contains(@class, 'description')]/div//text()").extract()
        raw_desc = [desc.strip() for desc in raw_desc if desc.strip()]
        return ' '.join(raw_desc)

    def is_in_stock(self, response):
        stock = response.xpath("//div[@title='Availability']/span/text()").extract_first().strip()
        return False if stock == "In stock" else True

    def get_item_attributes(self, response):
        attrib = response.xpath(
            "//td[@data-th='Manufacturer']/text()").extract_first()
        attributes = {}
        attributes["Manufacturer"] = attrib
        return attributes

    def get_item_images(self, response):
        return response.css('a[data-image]::attr(data-image)').extract()

    def get_item_sizes(self, response):
        size_string = re.findall(
            r'swatchOptions\":\s+(.+?},\"tierPrices\":\[\]}}),', response.text)
        sizes, prices = [], []
        if size_string:
            size_string = size_string[0].strip()
            size_string = size_string + "}"
            json_string = json.loads(size_string)
            if json_string["attributes"]:
                for option in json_string["attributes"]["141"]["options"]:
                    if option.get('products'):
                        sizes.append(option["label"])
                        prices.append(
                            json_string["optionPrices"][option["products"][0]])

        return sizes, prices

    def get_item_skus(self, response):
        currency = response.xpath("//meta[@itemprop='priceCurrency']/@content").extract_first()
        price = response.xpath("//span[contains(@id, 'product-price-')]/span/text()").extract_first()
        if price:
            price = price.strip().strip(currency).replace(",", "")
        prev_price = response.xpath("//span[contains(@id, 'old-price-')]/span/text()").extract_first()
        if prev_price:
            prev_price = prev_price.strip().strip(currency).replace(",", '')
        sizes, prices = self.get_item_sizes(response)
        skus = []
        if sizes:
            for size, amount in zip(sizes, prices):
                sku = {}.copy()
                sku['color'] = 'no'
                sku['size'] = size
                sku['price'] = amount["finalPrice"]["amount"]
                sku['currency'] = currency
                sku['out_of_stock'] = self.is_in_stock(response)
                if prev_price:
                    sku["prev_price"] = amount["oldPrice"]["amount"]

                skus.append(sku)
        else:
            sku = {}.copy()
            sku['color'] = 'no'
            sku['size'] = 'one size'
            sku['price'] = price
            sku['currency'] = currency
            sku['out_of_stock'] = self.is_in_stock(response)

            if prev_price:
                sku["prev_price"] = prev_price

            skus.append(sku)

        return skus
