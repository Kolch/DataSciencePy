# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.loader.processors import MapCompose, TakeFirst
import scrapy


def cleaner_photo(values):
    if values[:2] == '//':
        return f'http:{values}'
    return values


def price_to_int(price):
    try:
        _price = int(price)
        return _price
    except ValueError:
        pass


def prepare_string(values):
    if values != " ":
        values = values.replace(u'\xa0', u'')
        return values


class AvitoparserItem(scrapy.Item):
    _id = scrapy.Field()
    price = scrapy.Field(input_processor=MapCompose(price_to_int), output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    params_keys = scrapy.Field(input_processor=MapCompose(prepare_string))
    params_values = scrapy.Field(input_processor=MapCompose(prepare_string))
    title = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(cleaner_photo))
