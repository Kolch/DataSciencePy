from pprint import pprint
from lxml import html
import requests

main_link = ('https://www.mail.ru')

# req = requests.get(main_link+'/afisha/new/city/1/')

f = open('html.html', 'r')

root = html.fromstring(f.read())

news_titles = root.xpath("//div[@class='news-item__inner']/a[not(contains(@class, 'i-color-black i-inline'))]/text()")
pprint(news_titles)


