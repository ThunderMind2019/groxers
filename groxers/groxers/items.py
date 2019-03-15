# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class Groxer(Item):
    # define the fields for your item here like:
    name = Field()  #string
    pid = Field()   #string
    brand = Field() #string
    description = Field()   #string
    category = Field()  #list ['main_category', 'sub_category', 'third_optional']
    images = Field()    #list of images
    attributes = Field()    #list of dicts with predefinded attribtus or will result in key value as it is over web
    p_type = Field()    #cloth/groxer
    out_of_stock = Field()  #higher level out_of_stock (if full item out of stock then this will be included as True) otherwise it is present in `skus`
    skus = Field()  #list of dict (product variation with its associated data)
    source = Field()    #product source -> website/brand/company e.g; madinacashandcarry -> mcc
    url = Field()   #product_url
