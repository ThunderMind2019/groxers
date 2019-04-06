# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import requests

from scrapy.exceptions import DropItem
from groxers.settings import PRODUCT_API

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
        item_type = item['p_type']
        item_cat = ' '.join(item['category'] + [item['name']])
        item_cat = item_cat.lower()
        sub_cat = get_sub_category(item_cat, item_type)

        if sub_cat:
            item['category'] = [get_main_category(sub_cat, item_type), sub_cat.title()]
        elif item_type =='cloth':
            item['category'] = ["Women's Clothing", 'Other']
        else:
            item['category'] = ['Miscellaneous', 'Other']

        return item


class UploadProduct(object):

    def process_item(self, item, spider):
        api = PRODUCT_API
        if 'http' not in api:
            api = 'http://{}'.format(api)

        headers = {
            "Content-Type": "application/json",
        }
        res = requests.post(
            url=api,
            data=json.dumps(dict(item)),
            headers=headers,
        )

        return item
