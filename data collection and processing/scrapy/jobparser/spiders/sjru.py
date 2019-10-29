# -*- coding: utf-8 -*-
import scrapy
from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=python']

    def parse(self, response):
        next_page = response.css('a.f-test-link-dalshe::attr(href)').extract_first()
        if not next_page:
            pass
        else:
            yield response.follow(next_page, callback=self.parse)

        vacansy = response.css(
            'div.f-test-vacancy-item a[target="_blank"]::attr(href)').extract()

        for link in vacansy:
            yield response.follow(link, self.vacansy_parse)  # Переходим на страницы вакансий

    # Тут будем передавать только min_salary как массив из кусков текста и далее трансформируем его в pipeline
    def vacansy_parse(self, response):
        name = response.css('div._3MVeX h1::text').extract_first()
        min_salary = response.css('span[class="_3mfro _2Wp8I ZON4b PlM3e _2JVkc"] *::text').extract()
        resource = 'sj'
        link = response.css('link[rel="canonical"]::attr(href)').extract_first()
        yield JobparserItem(name=name, min_salary=min_salary, max_salary=None, link=link, resource=resource)
