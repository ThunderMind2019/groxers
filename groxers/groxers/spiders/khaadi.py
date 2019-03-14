# -*- coding: utf-8 -*-
import re
import json
import scrapy
from groxers.items import Groxer


class KhaadiSpider(scrapy.Spider):
    name = 'khaadi'
    # allowed_domains = ['https://www.khaadi.com/pk']
    start_urls = ['https://www.khaadi.com/pk/']

    def parse(self, response):
        category_links = response.xpath(
            "//div[@id='om']/ul/li/a/@href").extract()
        category_links = category_links[:-3]
        for link in category_links:
            yield scrapy.Request(link+"?product_list_limit=45", callback=self.parse_product_links)

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
        product["description"] = response.xpath("//div[@itemprop='description']//text()").extract()
        product["images"] = self.get_item_images(response)
        product["attributes"] = self.get_item_attributes(response)
        product["out_of_stock"] = False
        product["skus"] = self.get_item_skus(response)
        product["url"] = response.url
        yield product

    def get_item_images(self, response):
        images = response.xpath(
            "//div[@class='MagicToolboxSelectorsContainer']//img/@src").extract()
        images.append(response.xpath(
            "//img[@itemprop='image']/@src").extract_first())
        return images

    def get_item_attributes(self, response):
        material = response.xpath(
            "//td[@data-th='Material']/text()").extract_first()
        if material:
            return {
                "Material": material,
            }
        else:
            return {}

    def get_item_sizes(self, response):
        size_string = re.findall(r'swatchOptions\":\s+(.+?},\"tierPrices\":\[\]}}),', response.text)
        sizes, prices = [], []
        if size_string:
            size_string = size_string[0].strip()
            size_string = size_string + "}"
            json_string = json.loads(size_string)
            if json_string["attributes"]:
                for option in json_string["attributes"]["142"]["options"]:
                    if option["products"] and len(option["products"]) <= 2:
                        sizes.append(option["label"])
                        prices.append(
                            json_string["optionPrices"][option["products"][0]]["finalPrice"]["amount"])

        return sizes, prices

    def get_item_skus(self, response):
        currency = response.xpath("//meta[@itemprop='priceCurrency']/@content").extract_first()
        color_name = response.xpath("//td[@data-th='Color']/text()").extract_first()
        price = response.xpath("//span[contains(@id, 'product-price-')]/span/text()").extract_first()
        if price:
            price = price.strip(currency).replace(",", "")
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
                "new_price": price,
                "currency_code": currency,
            }
        return color_scheme
