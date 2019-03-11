# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from scrapy.exceptions import DropItem


class FilterDuplicate(object):
    def __init__(self):
        self.pid = set()

    def process_item(self, item, spider):
        if item['pid'] in self.pid:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.pid.add(item['pid'])
            return item
