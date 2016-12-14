# -*- coding: utf-8 -*-
import scrapy
import datetime

class PapalTextItem(scrapy.Item):

    url = scrapy.Field()
    html = scrapy.Field()
    text = scrapy.Field()
    pope = scrapy.Field()
    lang = scrapy.Field()
    type = scrapy.Field()
    spec = scrapy.Field()
    year = scrapy.Field()
    date = scrapy.Field()
    base = scrapy.Field()
    filebase = scrapy.Field()
