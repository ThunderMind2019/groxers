# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from scrapy.exceptions import DropItem
from groxers.tools import get_sub_category, get_main_category

class FilterDuplicate(object):
    def __init__(self):
        self.pid = set()

    def process_item(self, item, spider):
        if item['pid'] in self.pid:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.pid.add(item['pid'])
            return item


class IdentifyCategory(object):

    def process_item(self, item, spider):
        item_cat = ' '.join(item['category'] + [item['name']])
        item_cat = item_cat.lower()
        sub_cat = get_sub_category(item_cat)
        if sub_cat:
            item['category'] = [get_main_category(sub_cat), sub_cat.title()]
            return item
        if spider.clothing_website:
            item['category'] = ["Women's Clothing", 'Other']
        else:
            item['category'] = ['Miscellaneous', 'Other']
        return item
