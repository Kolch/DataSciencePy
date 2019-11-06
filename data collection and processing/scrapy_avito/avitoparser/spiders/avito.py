# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from avitoparser.items import AvitoparserItem
from scrapy.loader import ItemLoader


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/moskva/avtomobili']

    def parse(self, response: HtmlResponse):
        ads_links = response.xpath('//div[@class="serp-vips-item "]//div[@class="description"]/h3/a/@href |'
        '//div[@class="item item_table clearfix js-catalog-item-enum item-with-contact js-item-extended"]//h3/a/@href')\
            .extract()

        for link in ads_links:
            yield response.follow(link, self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        # photos = response.xpath('//div[contains(@class, "gallery-img-wrapper")]
        # //div[contains(@class, "gallery-img-frame")]/@data-url').extract()
        # temp = AvitoparserItem(photos=photos)
        # yield temp

        # title = response.xpath('//span[@class="title-info-title-text"]/text()').extract_first()
        # print(title)

        loader = ItemLoader(item=AvitoparserItem(), response=response)
        loader.add_xpath('title',
                         '//span[@class="title-info-title-text"]/text()')
        loader.add_xpath('link', '//link[@rel="canonical"]/@href')
        loader.add_xpath('price',
                         '//span[@itemprop="price"]/@content')
        loader.add_xpath('photos',
                '//div[contains(@class, "gallery-img-wrapper")]//div[contains(@class, "gallery-img-frame")]/@data-url')

        loader.add_xpath('params_keys', '//ul[@class="item-params-list"]/li/span[@class="item-params-label"]/text()')
        loader.add_xpath('params_values', '//ul[@class="item-params-list"]/li/text()')
        yield loader.load_item()
