# Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта
#
# Вакансия для поиска и кол-во страниц для сканирования задаются в конструкторе класса для удобства
#
# У программы две функции:
#
# 1) Посмотреть какие вакансии уже есть в БД, если их нет программа предлагает просканировать
# сайт и сразу показывает результат.
#
# 2) Просканировать сайт на наличие новой или обновленной информации по вакансиям,
# если найдены изменения в ценах уже записанных в БД вакансий это будет выведено на экран, так же если будут найдены
# новые вакансии они будут выведены.
#
# Чтобы протестировать обновление информации: через консоль mongo поменяйте значение зарплат для какой нибудь вакансии
# и затем запустите скрипт.
#
# Чтобы протестировать добавление новых вакансий: 1) очистите БД 2) запустите скрипт
# 3) поменяйте значение "pages_to_scan" в конструкторе класса на большее чем стоит в данный момент 4) запустите скрипт.


from pymongo import MongoClient
from bs4 import BeautifulSoup as bs
import requests
import time
from pprint import pprint


class DataCollector:

    HH_VACANCIES = []
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko)' \
                 ' Chrome/35.0.1916.47 Safari/537.36'
    HH_MAIN_LINK = "https://hh.ru"

    client = MongoClient('localhost', 27017)
    db = client['vacancies']
    DB_python = db.v_python

    def __init__(self):
        self.search_title = "python"
        self.pages_to_scan = 2

    def salary_dev(self, salary):
        salary = salary.replace(u'\xa0', u'')
        min_s = ''
        max_s = ''

        if salary.__contains__('от'):
            # только минимальная цена
            min_s = ''.join(x for x in salary if x.isdigit())
            max_s = 'none'

        elif salary.__contains__('По'):
            min_s = 'none'
            max_s = 'none'

        elif salary.__contains__('до'):
            # только максимальная цена
            max_s = ''.join(x for x in salary if x.isdigit())
            min_s = 'none'

        elif salary.__contains__('-'):
            # вся цена
            dev_s = salary.split("-")
            min_s = dev_s[0]
            max_s = ''.join(x for x in dev_s[1] if x.isdigit())

            # SALARY STRING TO INT
            try:
                min_s = int(min_s)
            except ValueError:
                pass
            try:
                max_s = int(max_s)
            except ValueError:
                pass

        return min_s, max_s

    def scan_hh(self, html):
        temp_array = []
        parsed_html = bs(html, 'lxml')
        vacancy_block = parsed_html.findAll('div', {'class': 'vacancy-serp-item'}, recursive='false')
        next_link = parsed_html.find('a', {'class': 'HH-Pager-Controls-Next'})
        if not next_link:
            next_link = ''
        else:
            next_link = next_link['href']

        for vacancy in vacancy_block:
            vacancy_dir = {}
            v_title = vacancy.find('a').getText()
            v_link = vacancy.find('a')['href']
            v_salary = vacancy.find('div', {'class': 'vacancy-serp-item__compensation'})
            if not v_salary:
                v_min_salary = 'none'
                v_max_salary = 'none'
            else:
                v_salary = v_salary.getText(strip=True)
                v_min_salary, v_max_salary = self.salary_dev(v_salary)

            vacancy_dir['max_salary'] = v_max_salary
            vacancy_dir['min_salary'] = v_min_salary
            vacancy_dir['title'] = v_title
            vacancy_dir['link'] = v_link
            vacancy_dir['site'] = 'HH'
            temp_array.append(vacancy_dir)

        return temp_array, next_link

    def get_hh_data(self, flag):
        # Флаг нужен для использования функции для записи собранных данных в БД или просто для обновления массива данных

        request_hh = requests.get(self.HH_MAIN_LINK + "/search/vacancy?area=1&st=searchVacancy&text=" +
                                  self.search_title, headers={'User-Agent': ''})
        html_hh = request_hh.text

        for i in range(self.pages_to_scan):
            temp, next_link = self.scan_hh(html_hh)
            self.HH_VACANCIES += temp
            time.sleep(1)
            if next_link == '':
                break
            else:
                request = requests.get(self.HH_MAIN_LINK + next_link, headers={'User-Agent': self.USER_AGENT})
                html_hh = request.text

        if flag:
            self.DB_python.insert_many(self.HH_VACANCIES)

    def show_hh_v(self):
        count_obj = self.DB_python.count_documents({})
        if count_obj > 0:
            objects = self.DB_python.find()
            for obj in objects:
                print(obj)
        else:
            _input = input('Пока в БД нет данных. Хотите просканировать сайт и записать данные? (Y/N)')
            if (_input == 'Y') or (_input == 'y'):
                self.get_hh_data(flag=True)
                self.show_hh_v()
            else:
                print('Ну тогда, до свидания !(')

    def check_for_new_vacancies(self):
        count_obj = self.DB_python.count_documents({})
        if count_obj > 0:
            self.get_hh_data(flag=False)
            objects = self.DB_python.find()
            self.compare_data(objects, self.HH_VACANCIES)

            # Сравниваем кол-во данных в БД с данными вновь полученными.
            if count_obj < len(self.HH_VACANCIES):
                self.find_new_v()
            else:
                print('Найдено новых вакансий: 0')
        else:
            _input = input('Пока в БД нет данных. Хотите просканировать сайт и записать данные? (Y/N)')
            if (_input == 'Y') or (_input == 'y'):
                self.get_hh_data(flag=True)
                self.show_hh_v()
            else:
                print('Ну тогда, до свидания !(')

    # Ищем новые вакансии
    def find_new_v(self):
        counter = 0
        temp = []
        for i in self.HH_VACANCIES:
            row = self.DB_python.find_one({'link': i['link']})
            if not row:
                counter += 1
                self.DB_python.insert_one(i)
                temp.append(i)
        print(f'Найдено новых вакансий:{counter}')

        if len(temp) > 0:
            print("Новые вакансии:")
            for k in temp:
                print('----------------')
                pprint(k)
                print('----------------')

    # Сравниваем данные из БД и новые полученные данные на изменение зарплат
    def compare_data(self, db_data, new_data):
        counter = 0
        temp = []
        for i in db_data:
            _t = {}
            for j in new_data:
                if i['link'] == j['link']:
                    if (i['max_salary'] == j['max_salary']) and (i['min_salary'] == j['min_salary']):
                        pass
                    else:
                        counter += 1
                        self.DB_python.update_many({'link': i['link']}, {'$set': {'max_salary': j['max_salary']}})
                        self.DB_python.update_many({'link': i['link']}, {'$set': {'min_salary': j['min_salary']}})
                        _t['title'] = i['title']
                        _t['old_min'] = i['min_salary']
                        _t['old_max'] = i['max_salary']
                        _t['new_min'] = j['min_salary']
                        _t['new_max'] = j['max_salary']
                        temp.append(_t)
        print(f'Количество изменений в данных:{counter}')
        if len(temp) > 0:
            print('Изменения:')
            for k in temp:
                print('-------------------------')
                print(f"Вакансия:{k['title']}")
                print("Старые зарплаты:")
                print(f"Min:{k['old_min']}, Max:{k['old_max']}")
                print("Новые зарплаты:")
                print(f"Min:{k['new_min']}, Max:{k['new_max']}")
                print('--------------------------')

    def main(self):
        print('Варианты действий:')
        print('1 - Просмотреть имеющиеся данные в БД')
        print('2 - Просканировать сайт на наличие новой или обновленной информации по вакансиям')
        _input = input('Введите цифру варианта:')
        try:
            _input = int(_input)
            if _input == 1:
                self.show_hh_v()
            elif _input == 2:
                self.check_for_new_vacancies()
            else:
                print('Такого варианта нет!')
                self.main()
        except ValueError:
            print('Вы ввели не цифру! Попробуем еще раз...')
            self.main()


dc = DataCollector()
dc.main()
