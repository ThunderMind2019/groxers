# -*- coding: utf-8 -*-
import json
from parsel import Selector
import math
from groxers.items import Groxer
import scrapy


class WardaSpider(scrapy.Spider):
    name = 'warda'
    start_urls = ['https://warda.com.pk/']

    def parse(self, response):
        yield scrapy.Request("https://fishry.azure-mobile.net/tables/collection?$filter=((collectionVisibility%20eq%20true)%20and%20(storeID%20eq%20%279E713197-7647-4B52-BDF1-AB5B2F0C27D2%27))&$top=1000", headers={"X-ZUMO-APPLICATION": "egepBriQNqIKWucZFzqpQOMwdDmzfs16"},
                             callback=self.parse_collections)

    def parse_collections(self, response):
        json_data = json.loads(response.body)
        storeID = json_data[0]["storeID"]
        for collection in json_data:
            collection_id = collection["id"]
            form_data = {
                "storeID": storeID,
                "take": "5000",
                "skip": "0",
                "status": "true",
                "collection_id[]": collection_id,
            }
            yield scrapy.FormRequest("https://fishry-api-live.azurewebsites.net/collection_request",
                                     formdata=form_data, callback=self.parse_items, dont_filter=True)

    def parse_items(self, response):
        json_items = json.loads(response.body)
        for item in json_items:
            product = Groxery()
            product["name"] = item["productName"]
            product["product_sku"] = item["productSKU"]
            product["description"] = self.parse_description(item)
            product["category"] = self.parse_category(item)
            product["images"] = self.parse_images(item)
            product["attributes"] = self.parse_attributes(item)
            product["out_of_stock"] = True if item["inventoryQuantity"] <= 1 else False
            product["skus"] = self.parse_skus(item)
            product["url"] = "https://warda.com.pk/product/" + item["productUrl"]
            yield product

    def parse_description(self, item):
        description_html = Selector(item["productDescription"])
        return description_html.xpath("//text()").extract()

    def parse_category(self, item):
        product_collection_list = item["productCollectionsList"].split(",")
        product_collections = item["productCollections"].replace("\\", '')
        product_collections = json.loads(product_collections)
        return product_collections[product_collection_list[0]]["name"]

    def parse_images(self, item):
        product_images = item["productImage"].replace("\\", '')
        product_images = json.loads(product_images)
        return [product_images[counter]["Image"] for counter in product_images]

    def parse_attributes(self, item):
        multi_options = item["productMultiOptionsList"].replace("\\", '')
        multi_options = json.loads(multi_options)
        attributes = dict()
        for option in multi_options:
            selected = option["optionSelected"]
            selected = option[selected] if selected == "custom" else selected
            if selected != "Color" and selected != "Size" and selected != "Colors":
                attributes[selected] = [value["value"]
                                        for value in option["value"]]
        return attributes

    def parse_skus(self, item):
        product_collection_list = item["productCollectionsList"].split(",")
        product_collections = item["productCollections"].replace("\\", '')
        product_collections = json.loads(product_collections)
        prev_price = item["productPrice"]
        discount = 0
        if len(product_collections) > 1:
            discount = product_collections[product_collection_list[1]]["url"].split(
                "-")[0]
            new_price = prev_price - \
                math.ceil(((prev_price/100)*float(discount)))
        else:
            new_price = prev_price
        multi_options = item["productMultiOptionsList"].replace("\\", '')
        multi_options = json.loads(multi_options)
        all_sizes = []
        color_name = "no color"
        with_inner = []
        for option in multi_options:
            selected = option["optionSelected"]
            selected = option[selected] if selected == "custom" else selected
            if selected == "Color" or selected == "Colors":
                color_name = option["value"][0]["value"].strip()
            if selected == "Size":
                all_sizes = [value["value"] for value in option["value"]]
            if selected == "With Inner/Slip":
                with_inner = [value["value"].strip()
                              for value in option["value"]]
        colors = {}
        if all_sizes:
            avail_sizes = []
            varients = item["productVarients"].replace("\\", '')
            varients = json.loads(varients)
            for varient in varients:
                try:
                    qty = int(varient["inventoryQuantity"])
                except:
                    qty = 0
                if qty > 0:
                    size = (el for el in varient["name"] if el in all_sizes)
                    avail_sizes.append(next(size, None))
            colors[color_name] = {
                "color": color_name,
                "prev_price": prev_price,
                "new_price": new_price,
                "currency_code": "PKR",
            }
            if avail_sizes:
                colors[color_name]["available_sizes"] = avail_sizes
        elif with_inner:
            varients = item["productVarients"].replace("\\", '')
            varients = json.loads(varients)
            for varient in varients:
                with_slip = varient["name"][len(varient["name"])-1]
                try:
                    prev_price = int(varient["price"])
                    new_price = prev_price - \
                        math.ceil(((prev_price/100)*float(discount)))
                    with_slip = varient["name"][len(varient["name"])-1]
                    colors[color_name+"_"+with_slip] = {
                        "color": color_name,
                        "with Inner/Slip": with_slip,
                        "available": "Yes",
                        "prev_price": prev_price,
                        "new_price": new_price,
                        "currency_code": "PKR",
                    }
                    qty = int(varient["inventoryQuantity"])
                    if qty > 0:
                        colors[color_name+"_"+with_slip]["available"] = "yes"
                    else:
                        colors[color_name+"_"+with_slip]["available"] = "no"
                except:
                    colors[color_name+"_"+with_slip]["available"] = "no"                    
        else:
            colors[color_name] = {
                "color": color_name,
                "prev_price": prev_price,
                "new_price": new_price,
                "currency_code": "PKR",
            }
        return colors