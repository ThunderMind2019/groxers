# -*- coding: utf-8 -*-
import scrapy


class JSpider(scrapy.Spider):
    name = 'j.'
    start_urls = ['https://junaidjamshed.com/']

    def parse(self, response):
        print(response.url)
