# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyTemplateItem(scrapy.Item):
    # define the fields for your item here like:
    category = scrapy.Field()
    name = scrapy.Field()
    color = scrapy.Field()
    images = scrapy.Field()
    price = scrapy.Field()
    url = scrapy.Field()
