from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient


# Обработка цены
def prepare_price(_price):
    return int(''.join(filter(str.isdigit, _price)))


# Подготовка ссылки
def prepare_link(_link):
    if _link[0] == "/":
        return f"https://www.mvideo.ru/{_link}"
    else:
        return _link


# Mongo
client = MongoClient('localhost', 27017)
db = client['mvideo']
DB = db.top_sales

# Driver
chrome_options = Options()
chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome(options=chrome_options)

driver.get('https://www.mvideo.ru/')
assert "М.Видео" in driver.title

WebDriverWait(driver, 5).until(
            ec.element_to_be_clickable(
                (By.XPATH,
                 "/html[1]/body[1]/div[1]/div[1]/div[3]/div[4]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/a[5]")))

# Ищем все кнопки под контейнером с хитами
a_array = driver.find_elements_by_xpath(
    '/html[1]/body[1]/div[1]/div[1]/div[3]/div[4]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/a')
last_elem = len(a_array)

# Получаем доступ к последней кнопке
elem = driver.find_element_by_xpath(
    f'/html[1]/body[1]/div[1]/div[1]/div[3]/div[4]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/a[{last_elem}]')
elem.click()

# Получаем список элементов "Хитов"
li_array = driver.find_elements_by_xpath(
    '/html[1]/body[1]/div[1]/div[1]/div[3]/div[4]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/ul/li')
li_count = len(li_array)

# Цикл вместо таймаута
while li_count < 6:
    li_array = driver.find_elements_by_xpath(
        '/html[1]/body[1]/div[1]/div[1]/div[3]/div[4]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/ul/li')
    li_count = len(li_array)

# Достаем данные из каждого элемента массива
for i in range(li_count):
    i += 1
    temp_dir = {}
    link_to_li = \
        f'/html[1]/body[1]/div[1]/div[1]/div[3]/div[4]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/ul/li[{i}]'

    title = driver.find_element_by_xpath(f'{link_to_li}//h4').get_attribute('title')

    price = driver.find_element_by_xpath(f'{link_to_li}//div[@class="c-pdp-price__current"]').get_attribute('innerHTML')
    price = prepare_price(price)

    link = driver.find_element_by_xpath(f'{link_to_li}//h4/a').get_attribute('href')
    link = prepare_link(link)

    temp_dir['link'] = link
    temp_dir['title'] = title
    temp_dir['price'] = price
    DB.insert_one(temp_dir)

driver.quit()
