# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class Groxer(Item):
    # define the fields for your item here like:
    name = Field()
    pid = Field()
    brand = Field()
    description = Field()
    category = Field()
    sub_category = Field()
    images = Field()
    attributes = Field()
    out_of_stock = Field()
    skus = Field()
    source = Field()
    url = Field()
