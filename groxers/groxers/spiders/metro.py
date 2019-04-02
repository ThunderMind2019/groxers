# -*- coding: utf-8 -*-
import json

from scrapy import Spider, Request, FormRequest
from scrapy import Selector

from groxers.items import Groxer


class MetroSpider(Spider):
    name = 'metro'

    def start_requests(self):
        formdata = {"action":"menulist","cityid":"2"}
        yield FormRequest(
            url='https://metro-online.pk/dashboard/apinew/nonfood/menulist.php',
            callback=self.parse_categories, body=json.dumps(formdata),
            method='POST'
        )

    def parse_categories(self, response):
        raw_categories = json.loads(response.text)['menulist'][2:]

        for i in range(len(raw_categories)):
            cat = raw_categories[i]

            if 'frozen-food' in cat['url']:
                levelone = []

                for one in cat['levelone']:
                    if 'Frozen Ready to Cook' in one['mname'] or 'Frozen Vegetables' in one['mname']:
                        levelone.append(one)

                cat['levelone'] = levelone
                raw_categories[i] = cat

        for cat in raw_categories:
            ones = cat['levelone']

            formdata = {"limit":5000,"brandcode":0,"price":"0-0","sortby":0,"see":0,"start":0,"specialoffer":0,"cityid":"2"}

            for link in ones:
                twos = link.get('leveltwo')
                for t_link in twos:
                    data = formdata.copy()
                    data["level"] = 3
                    data["category"] = t_link['url'].split('/')[-1]
                    yield FormRequest(
                        url='https://metro-online.pk/dashboard/apinew/nonfood/productlist.php',
                        callback=self.parse_product_codes, method='POST',
                        body=json.dumps(data), dont_filter=True,
                    )

                if not twos:
                    data = formdata.copy()
                    data["level"] = 2
                    data["category"] = link['url'].split('/')[-1]
                    yield FormRequest(
                        url='https://metro-online.pk/dashboard/apinew/nonfood/productlist.php',
                        callback=self.parse_product_codes, method='POST',
                        body=json.dumps(data), dont_filter=True,
                    )

    def parse_product_codes(self, response):
        raw_products = json.loads(response.text)

        if not raw_products.get('totalproductcount'):
            return

        for product in raw_products['products']:
            formdata = {"productcode":"{}".format(product['product_code']),"cityid":"2"}.copy()
            yield FormRequest(
                url='https://metro-online.pk/dashboard/apinew/productdetail.php',
                callback=self.parse_product, body=json.dumps(formdata), method='POST',
                dont_filter=True
            )

    def parse_product(self, response):
        raw_product = json.loads(response.text)

        if raw_product.get('redirect'):
            return

        product = Groxer()
        product['pid'] = raw_product['product_code'].strip()
        product['name'] = raw_product['product_name'].strip()
        product['brand'] = raw_product['brand_name'].strip()
        product['images'] = [raw_product['images']]
        product['description'] = self.get_description(raw_product)
        product['skus'] = self.get_skus(raw_product)
        product['attributes'] = {}.copy()
        product['source'] = 'metro'
        product['p_type'] = 'groxer'
        product['url'] = f'https://metro-online.pk/detail/{raw_product["product_url"].replace("//", "/")}'
        yield product

    def get_skus(self, raw_product):
        skus = []
        sku = {}.copy()
        sku['color'] = 'no'
        sku['size'] = 'one size'
        sku['price'] = int(raw_product['product_price'])
        if int(raw_product['product_sale_price']) != 0:
            sku['prev_price'] = int(raw_product['product_sale_price']) + sku['price']

        sku['out_of_sku'] = False if 'In Stock' in raw_product['stocklvel'] else True
        sku['currency'] = 'PKR'

        skus.append(sku)

        return skus

    def get_description(self, raw_product):
        desc = raw_product['product_desc']

        if not desc:
            return ''

        raw_desc = Selector(text=desc)
        raw_desc = raw_desc.xpath('.//text()').extract()
        raw_desc = [desc.strip() for desc in raw_desc if desc.strip()]
        raw_desc = ' '.join(raw_desc).replace('\xa0', '')
        desc = ' '.join(raw_desc.split(' '))
        return desc
