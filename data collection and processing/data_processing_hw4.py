# Для этого задания БД не использовалась, поэтому при каждом использовании программы, делается новый запрос к страницам.
# Соответственно при каждом вызове программы информация обновляется.

from pprint import pprint
from lxml import html
import requests
import pandas as pd
from datetime import datetime

pd.set_option('display.width', 420)
pd.set_option('display.max_columns', 10)


class NewsCollector:
    def __init__(self):
        self.MAIL_NEWS = []
        self.LENTA_NEWS = []
        self.NEWS_DF = pd.DataFrame()

    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'
    mail_main_link = 'https://www.mail.ru'
    lenta_main_link = 'https://lenta.ru'

    def scan_mail_news(self):
        req = requests.get(self.mail_main_link, headers={'User-Agent': self.USER_AGENT})
        root = html.fromstring(req.text)

        # Новость из заголовка
        header_new_title = root.xpath("//div[@class='news-item o-media news-item_media news-item_main']//h3/text()")
        header_new_link = root.xpath("//div[@class='news-item o-media news-item_media news-item_main']//a/@href")
        if len(header_new_title) > 0:
            temp = dict()
            temp['title'] = header_new_title[0].replace(u'\xa0', u' ')
            temp['link'] = header_new_link[0]
            temp['resource'] = self.mail_main_link
            temp['time'] = datetime.now().strftime("%d-%m-%Y %H:%M")
            self.MAIL_NEWS.append(temp)

        # Все остальные
        news_titles = root.xpath(
            "//div[@class='news-item__inner']/a[not(contains(@class, 'i-color-black i-inline'))]/text()")
        news_links = root.xpath(
            "//div[@class='news-item__inner']/a[not(contains(@class, 'i-color-black i-inline'))]/@href")

        for i in range(len(news_links)):
            temp = dict()
            temp['title'] = news_titles[i].replace(u'\xa0', u' ')
            temp['link'] = news_links[i]
            temp['resource'] = self.mail_main_link
            temp['time'] = datetime.now().strftime("%d-%m-%Y %H:%M")
            self.MAIL_NEWS.append(temp)

    def scan_lenta_news(self):
        req = requests.get(self.lenta_main_link, headers={'User-Agent': self.USER_AGENT})
        root = html.fromstring(req.text)

        # Новость из заголовка
        header_new_title = root.xpath("//div[@class='first-item']//h2/a/text()")
        header_new_link = root.xpath("//div[@class='first-item']//h2/a/@href")
        header_new_time = root.xpath("//div[@class='first-item']//h2/a/time/text()")

        if len(header_new_title) > 0:
            temp = dict()
            temp['title'] = header_new_title[0].replace(u'\xa0', u' ')
            temp['link'] = self.lenta_main_link + header_new_link[0]
            temp['resource'] = self.lenta_main_link
            temp['time'] = datetime.now().strftime("%d-%m-%Y") + " " + header_new_time[0]
            self.LENTA_NEWS.append(temp)

        # Все остальные новости
        news_titles = root.xpath(
            "//section[@class='row b-top7-for-main js-top-seven']//div[@class='item']//a/text()")
        news_links = root.xpath(
            "//section[@class='row b-top7-for-main js-top-seven']//div[@class='item']//a/@href")
        dates = root.xpath("//section[@class='row b-top7-for-main js-top-seven']//div[@class='item']//a/time/text()")

        for i in range(len(news_titles)):
            temp = dict()
            temp['title'] = news_titles[i].replace(u'\xa0', u' ')

            if news_links[i][0] == "/":
                temp['link'] = self.lenta_main_link + news_links[i]
            else:
                temp['link'] = news_links[i]

            temp['resource'] = self.lenta_main_link
            temp['time'] = datetime.now().strftime("%d-%m-%Y") + " " + dates[i]
            self.LENTA_NEWS.append(temp)

    def get_news(self):
        self.scan_mail_news()
        self.scan_lenta_news()
        temp = self.LENTA_NEWS + self.MAIL_NEWS
        self.NEWS_DF = pd.DataFrame(temp)

    def show_news(self, flag):
        self.get_news()

        if flag == 1:
            pprint(self.NEWS_DF)
        elif flag == 2:
            pprint(self.NEWS_DF[self.NEWS_DF['resource'] == "https://lenta.ru"])
        elif flag == 3:
            pprint(self.NEWS_DF[self.NEWS_DF['resource'] == "https://www.mail.ru"])
        else:
            pass
        print("\n")
        self.main()

    def main(self):
        print("Ваши возможности:")
        print("1 - Собрать и посмортреть новости с обоих сайтов")
        print("2 - Собрать и посмортреть новости с 'lenta.ru'")
        print("3 - Собрать и посмортреть новости с 'mail.ru'")
        _input = input('Выберете номер варианта:')
        try:
            _input = int(_input)
            if _input == 1:
                self.show_news(flag=1)
            elif _input == 2:
                self.show_news(flag=2)
            elif _input == 3:
                self.show_news(flag=3)
            else:
                print("Такого варианта нет ! Попробуем еще раз...")
                self.main()
        except ValueError:
            print('Вы ввели не цифру! Попробуем еще раз...')
            self.main()


nc = NewsCollector()
nc.main()
