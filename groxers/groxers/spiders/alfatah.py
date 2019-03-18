# -*- coding: utf-8 -*-
from scrapy import Spider, Request

from groxers.items import Groxer


class AlfatahSpider(Spider):
    name = 'alfatah'
    start_urls = ['http://alfatah.pk/']

    excluded_category = '/fruits-vegetables'

    def parse(self, response):
        main_categories = response.xpath('//span[@class=""]/..')[3:]
        all_links = []
        for cat in main_categories:
            if 'has-children' in cat.xpath('./../../@class').extract_first():
                for li in cat.xpath('./../../ul/li'):
                    if 'has-children' in li.xpath('./@class').extract_first():
                        all_links.extend(li.xpath('./ul//a/@href').extract())
                    else:
                        all_links.extend(li.xpath('./span/a/@href').extract())
            else:
                all_links.extend(cat.xpath('./@href').extract())

        for link in all_links:
            if self.excluded_category not in link:
                yield Request(
                    url=link, callback=self.parse_product_links,
                )
            
    def parse_product_links(self, response):
        for link in response.css('.product-image::attr(href)').extract():
            yield Request(
                url=link, callback=self.parse_product,
            )
        
        next_page = response.css('[title="Next"]::attr(href)').extract_first()
        if next_page:
            yield Request(
                url=next_page, callback=self.parse_product_links,
            )

    def parse_product(self, response):
        product = Groxer()
        id_brand = response.css('p.green::text').extract()
        product['pid'] = id_brand.pop(0)
        product['brand'] = id_brand.pop(0) if id_brand else ''
        product['name'] = response.css('.product-name>h1::text').extract_first()
        product['description'] = response.css('.std.gray::text').extract_first()
        product['attributes'] = self.get_attributes(response)
        product['images'] = response.css('#cloudZoom::attr(href)').extract()
        product['skus'] = self.get_skus(response)
        product['source'] = 'alfatah'
        product['p_type'] = 'groxer'
        product['url'] = response.url
        yield product
    
    def get_skus(self, response):
        skus = []

        sku = {}.copy()
        raw_price = response.xpath('//*[@class="product-shop"]//*[contains(@id, "product-price")]//text()').extract()
        price = [p.strip() for p in raw_price if p.strip()][0]
        sku['price'] = price.replace(',', '').replace('Rs', '').strip()
        prev_price = response.xpath('//*[@class="product-shop"]//*[contains(@id, "old-price")]//text()').extract_first()

        if prev_price:
            sku['prev_price'] = prev_price.replace(',', '').replace('Rs', '').strip()
        
        sku['color'] = 'no'
        sku['size'] = 'one size'
        sku['currency'] = 'PKR'
        sku['out_of_stock'] = False if 'In stock' in response.css('.in-stock>span::text').extract_first() else True
        skus.append(sku)
        return skus
    
    def get_attributes(self, response):
        raw_desclaimer = response.css('.product-disclaimer ::text').extract()
        desclaimer = [d.strip() for d in raw_desclaimer if d.strip()]
        return {
            'desclaimer': desclaimer,
        }.copy()
