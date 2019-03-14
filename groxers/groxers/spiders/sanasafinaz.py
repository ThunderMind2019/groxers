# -*- coding: utf-8 -*-
import re
import json
import scrapy
from groxers.items import Groxer


class SanasafinazSpider(scrapy.Spider):
    name = 'sanasafinaz'
    # allowed_domains = ['https://www.sanasafinaz.com']
    start_urls = ['https://www.sanasafinaz.com/']

    def parse(self, response):
        category_links = response.xpath("//div[@id='om']/ul/li/a/@href").extract()
        category_links = category_links[:-2]
        for link in category_links:
            yield scrapy.Request(link, callback=self.parse_product_links)

    def parse_product_links(self, response):
        product_links = response.xpath(
            "//a[contains(@class, 'product-item-link')]/@href").extract()
        for link in product_links:
            yield scrapy.Request(link, self.parse_product_details)

        next_link = response.xpath("//a[@title='Next']/@href").extract_first()
        if next_link:
            yield scrapy.Request(next_link, self.parse_product_links)

    def parse_product_details(self, response):
        product = Groxer()
        product["name"] = response.xpath("//span[@data-ui-id]/text()").extract_first()
        product["product_sku"] = response.xpath("//div[@itemprop='sku']/text()").extract_first()
        product["description"] = response.xpath("//div[@itemprop='description']//text()").extract()
        product["images"] = response.xpath("//div[@class='slideset']//img/@src").extract()
        product["attributes"] = self.get_item_attributes(response)
        product["out_of_stock"] = self.get_stock_availablity(response)
        product["skus"] = self.get_item_skus(response)
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
            color_name = "no_color"
        currency = response.xpath("//meta[@itemprop='priceCurrency']/@content").extract_first()
        price = response.xpath("//meta[@itemprop='price']/@content").extract_first()
        sizes, prices = self.get_item_sizes(response)
        color_scheme = {}
        if sizes:
            for size, amount in zip(sizes, prices):
                color_scheme[color_name+"_"+size] = {
                    "color": color_name,
                    "new_price": amount,
                    "size": size,
                    "currency_code": currency,
                }
        else:
            color_scheme[color_name] = {
                "color": color_name,
                "new_price": price.replace(",", ''),
                "currency_code": currency,
            }
        return color_scheme
