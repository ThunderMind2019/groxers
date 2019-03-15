# -*- coding: utf-8 -*-
import re
import json
import scrapy
from groxers.items import Groxer


class GulahmedSpider(scrapy.Spider):
    name = 'gulahmed'
    start_urls = ['https://www.gulahmedshop.com']

    def parse(self, response):
        category_links = response.xpath(
            "//a[@class='menu-link']/@href").extract()[:-1]
        for link in category_links:
            yield scrapy.Request(link+"?product_list_limit=100", self.parse_product_links)

    def parse_product_links(self, response):
        product_links = response.xpath(
            "//a[contains(@class, 'product-item-photo')]/@href").extract()
        for link in product_links:
            yield scrapy.Request(link, self.parse_product_details)

        next_link = response.xpath("//a[@title='Next']/@href").extract_first()
        if next_link:
            yield scrapy.Request(next_link, self.parse_product_links)

    def parse_product_details(self, response):
        product = Groxer()
        product["name"] = response.xpath("//span[@data-ui-id]/text()").extract_first()
        product["product_sku"] = response.xpath("//div[@itemprop='sku']/text()").extract_first()
        product["description"] = response.xpath("//div[contains(@class, 'description')]//ul/li/text()").extract()
        product["images"] = self.get_item_images(response)
        product["attributes"] = self.get_item_attributes(response)
        product["out_of_stock"] = self.is_in_stock(response)
        product["skus"] = self.get_item_skus(response)
        product["url"] = response.url
        yield product

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
        image_string = re.findall(
            r'\"data\":\s+(\[.+?ll}]),', response.text)
        images = []
        if image_string:
            image_string = image_string[0].strip()
            json_images = json.loads(image_string)
            for image in json_images:
                images.append(image["full"])

        return images

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
                    if option["products"]:
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
        color_scheme = {}
        if sizes:
            for size, amount in zip(sizes, prices):
                color_scheme[size] = {
                    "new_price": amount["finalPrice"]["amount"],
                    "size": size,
                    "currency_code": currency,
                }
                if prev_price:
                    color_scheme[size]["prev_price"] = amount["oldPrice"]["amount"]
        else:
            color_scheme["no_color_size"] = {
                "new_price": price,
                "currency_code": currency,
            }
            if prev_price:
                color_scheme["no_color_size"]["prev_price"] = prev_price
        return color_scheme
