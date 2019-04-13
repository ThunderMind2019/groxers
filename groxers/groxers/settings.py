# -*- coding: utf-8 -*-

BOT_NAME = 'groxers'

PROD_IP = 'localhost:5000'

SPIDER_MODULES = ['groxers.spiders']
NEWSPIDER_MODULE = 'groxers.spiders'


USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'

ROBOTSTXT_OBEY = False

DOWNLOAD_DELAY = 1

ITEM_PIPELINES = {
   'groxers.pipelines.FilterDuplicate': 300,
   'groxers.pipelines.IdentifyCategory': 400,
   'groxers.pipelines.UploadProduct': 500,
}

# Product API
PRODUCT_API = PROD_IP + '/api/products/update'
