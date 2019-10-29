# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient
import re


class JobparserPipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.scrapy_vacansy

    def process_item(self, item, spider):
        if spider.name == 'sjru':
            salary_str = ''
            for i in item['min_salary']:
                salary_str += i

            min_s, max_s = self.salary_dev(salary_str)
            item["min_salary"] = min_s
            item["max_salary"] = max_s

        else:
            if not item["min_salary"]:
                pass
            else:
                try:
                    item["min_salary"] = int(item["min_salary"])
                except ValueError:
                    pass

            if not item["max_salary"]:
                pass
            else:
                try:
                    item["max_salary"] = int(item["max_salary"])
                except ValueError:
                    pass

        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

    # Функция из ранее написанной программы для форматирования строки с ценой
    def salary_dev(self, salary):
        salary = salary.replace(u'\xa0', u'')
        min_s = ''
        max_s = ''

        if salary.__contains__('от'):
            # только минимальная цена
            min_s = ''.join(x for x in salary if x.isdigit())
            max_s = None

        elif salary.__contains__('По'):
            min_s = None
            max_s = None

        elif salary.__contains__('до'):
            # только максимальная цена
            max_s = ''.join(x for x in salary if x.isdigit())
            min_s = None

        elif salary.__contains__('—'):
            # вся цена
            dev_s = salary.split('—')
            min_s = dev_s[0]
            max_s = ''.join(x for x in dev_s[1] if x.isdigit())

        else:
            digit = int(re.search(r'\d+', salary).group())
            min_s = digit
            max_s = digit

        # SALARY STRING TO INT
        if not min_s:
            pass
        else:
            try:
                min_s = int(min_s)
            except ValueError:
                pass
        if not max_s:
            pass
        else:
            try:
                max_s = int(max_s)
            except ValueError:
                pass
        return min_s, max_s
