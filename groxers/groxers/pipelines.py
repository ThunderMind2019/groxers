# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from scrapy.exceptions import DropItem
from groxers.tools import category_map

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
        import pdb;pdb.set_trace()
        item_cat = item['category'].lower()
        for category, keywords in category_map.items():
            for keyword in sorted(keywords, key=len, reverse=True):
                if keyword in item_cat:
                    item['category'] = category
                    return item
        item['category'] = 'Miscellaneous'
        return item
