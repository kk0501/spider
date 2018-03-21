# -*- coding: utf-8 -*-

import scrapy
import json
from scrapy_template.items import ScrapyTemplateItem


class ExampleSpider(scrapy.Spider):
    name = 'example'
    allowed_domains = ['example.com']
    start_urls = ['http://example.com/']

    custom_settings = {
        'ITEM_PIPELINES': {
            'scrapy_template.pipelines.ScrapyTemplatePipeline': 200
        }
    }

    def start_requests(self):
        urls = [
            'https://example.com/test',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        product_urls = response.xpath(
            '//div[contains(@class,"product-gridlist")]//div[@class="product-item"]/div[@class="details"]/h2[1]/a/@href'
        ).extract()

        for product_url in product_urls:
            full_url = response.urljoin(product_url)
            req = scrapy.Request(full_url, callback=self.parse_product)
            req.meta['category'] = response.url
            yield req

    def parse_product(self, response):
        product = ScrapyTemplateItem()
        product['category'] = response.meta['category']
        product['name'] = ''
        product['color'] = ''
        product['images'] = ''
        product['price'] = ''
        product['url'] = response.url

        details = response.xpath('//div[contains(@class,"productdetail")]')
        names = details.xpath(
            './/div[@class="producttitle"]/div[@class="product-name"]//text()'
        ).extract()
        if len(names) > 0:
            product['name'] = names[0].strip()

        colors = details.xpath(
            './/div[@class="producttitle"]/div[@class="productcolor-name"]//text()'
        ).extract()
        if len(colors) > 0:
            product['color'] = colors[0].strip()

        prices = details.xpath(
            './/div[@class="product-prices"]//div[@class="product-price"]/span/text()'
        ).extract()
        if len(prices) > 0:
            product['price'] = prices[0].strip()

        imgs = details.xpath(".//div[@id='detailslider']/img/@src").extract()
        if len(imgs) > 0:
            product['images'] = json.dumps(imgs)

        rel_urls = set(
            details.xpath('.//li[@class="productcolor-item "]//a/@href')
            .extract())
        for rel_url in rel_urls:
            full_url = response.urljoin(rel_url)
            req = scrapy.Request(full_url, callback=self.parse_product)
            req.meta['category'] = response.meta['category']
            yield req

        yield product
