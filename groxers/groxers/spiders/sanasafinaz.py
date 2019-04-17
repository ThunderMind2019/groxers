# -*- coding: utf-8 -*-
import re
import json
from scrapy import Spider, Request

from groxers.items import Groxer
from groxers.tools import cleanse


class SanasafinazSpider(Spider):
    name = 'sanasafinaz'
    allowed_domains = ['sanasafinaz.com']
    start_urls = ['https://www.sanasafinaz.com/']

    def parse(self, response):
        category_links = response.xpath("//div[@id='om']/ul/li/a")
        category_links = category_links[:-2]
        for link in category_links:
            yield Request(link.css('::attr(href)').extract_first(),
                          callback=self.parse_product_links, meta={'category': link.css('span::text').extract()})

    def parse_product_links(self, response):
        product_links = response.xpath(
            "//a[contains(@class, 'product-item-link')]/@href").extract()
        for link in product_links:if '/us/' in link:
            link = link.replace('/us/', '/pk/')
            yield Request(link, self.parse_product_details, meta=response.meta.copy(), meta={'dont_redirect': True})

        next_link = response.xpath("//a[@title='Next']/@href").extract_first()
        if next_link:
            yield Request(next_link, self.parse_product_links, meta=response.meta.copy())

    def parse_product_details(self, response):
        product = Groxer()
        product["name"] = response.xpath("//span[@data-ui-id]/text()").extract_first()
        product["pid"] = response.xpath("//div[@itemprop='sku']/text()").extract_first()
        product["description"] = cleanse(response.xpath("//div[@itemprop='description']//text()").extract())
        product["images"] = response.css("[data-zoom-id]::attr(href)").extract()
        product['category'] = response.meta['category']
        product["attributes"] = self.get_item_attributes(response)
        product["out_of_stock"] = self.get_stock_availablity(response)
        product["skus"] = self.get_item_skus(response)
        product['p_type'] = 'cloth'
        product['source'] = 'sanasafinaz'
        product['brand'] = 'sanasafinaz'
        product["url"] = response.url
        yield product

    def get_stock_availablity(self, response):
        stock = response.xpath("//div[@title='Availability']/span/text()").extract_first().strip()
        return False if stock == "In stock" else True

    def get_item_attributes(self, response):
        detail = response.xpath(
            "//div[@id='product.info.description']//tbody/tr//td/text()").extract()
        detail = [x+y for x, y in zip(detail[0::2], detail[1::2])]
        if detail:
            return {
                "detail": detail,
            }
        else:
            return {}

    def get_item_sizes(self, response):
        size_string = re.findall(
            r'swatchOptions\":\s+(.+?},\"tierPrices\":\[\]}}),', response.text)
        sizes, prices = [], []
        if size_string:
            size_string = size_string[0].strip()
            size_string = size_string + "}"
            json_string = json.loads(size_string)
            if json_string["attributes"]:
                for option in json_string["attributes"]["580"]["options"]:
                    if option["products"] and len(option["products"]) <= 2:
                        sizes.append(option["label"])
                        prices.append(
                            json_string["optionPrices"][option["products"][0]]["finalPrice"]["amount"])

        return sizes, prices

    def get_item_skus(self, response):
        color_name = response.xpath("//td[@data-th='Color']/text()").extract_first()
        if not(color_name):
            color_name = "no"
        currency = response.xpath("//meta[@itemprop='priceCurrency']/@content").extract_first()
        price = response.xpath("//meta[@itemprop='price']/@content").extract_first()
        sizes, prices = self.get_item_sizes(response)
        skus = []
        if sizes:
            for size, amount in zip(sizes, prices):
                skus.append({
                    "color": color_name,
                    "price": amount,
                    "size": size,
                    "currency": currency,
                    "out_of_stock": self.get_stock_availablity(response),
                }.copy())
        else:
            skus.append({
                "color": color_name,
                "size": "one size",
                "price": price.replace(",", '') if price else None,
                "out_of_stock": self.get_stock_availablity(response),
                "currency": currency,
            })
        return skus
