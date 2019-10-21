# 1) Необходимо собрать информацию о вакансиях на вводимую должность
# (используем input или через аргументы) с сайта superjob.ru и hh.ru.
# Приложение должно анализировать несколько страниц сайта(также вводим через input или аргументы).
# Получившийся список должен содержать в себе минимум:
#
#     *Наименование вакансии
#     *Предлагаемую зарплату (отдельно мин. и отдельно макс.)
#     *Ссылку на саму вакансию
#     *Сайт откуда собрана вакансия


# Описание
# Логика выполнения задания: имеется 4 функции, одна для работы со строкой цены(разбитие на категории), и по одной для
# сбора данных с каждого из двух сайтов. И главная функция, вводом пользователя получаем наименовании вакансии
# и кол-во страниц для сканирования. Затем двумя циклами(по одному на каждый сайт) получаем данные.


from bs4 import BeautifulSoup as bs
import requests
import time
import pandas as pd

pd.set_option('display.width', 320)
pd.set_option('display.max_columns', 10)


# Функция для работы со строкой цены
def salary_dev(salary):

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
    return min_s, max_s


# Get HH data
def scrape_hh(html, vacancies):
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
            v_salary = v_salary.getText()
            v_min_salary, v_max_salary = salary_dev(v_salary)

        vacancy_dir['title'] = v_title
        vacancy_dir['link'] = v_link
        vacancy_dir['min_salary'] = v_min_salary
        vacancy_dir['max_salary'] = v_max_salary
        vacancy_dir['site'] = 'HH'
        vacancies.append(vacancy_dir)

    return vacancies, next_link


# Get SJ data
def scrape_sj(html, vacancies):
    main_link = "https://www.superjob.ru"
    parsed_html = bs(html, 'lxml')
    vacancy_block = parsed_html.findAll('div', {'class': 'f-test-vacancy-item'}, recursive='false')

    next_link = parsed_html.find('a', {'class': 'f-test-button-dalshe'})
    if not next_link:
        next_link = ''
    else:
        next_link = next_link['href']

    for vacancy in vacancy_block:
        vacancy_dir = {}
        v_title = vacancy.find('div', {'class': 'PlM3e'})
        links = vacancy.findAll('a', {'class': 'icMQ_'}, recursive='false')
        v_salary = vacancy.find('span', {'class': 'f-test-text-company-item-salary'}).getText()
        v_link = ''
        v_min_salary, v_max_salary = salary_dev(v_salary)

        for link in links:
            href = link['href']
            if href.__contains__('vakansii'):
                v_link = href
                break
            else:
                continue

        if not v_title:
            continue
        else:
            v_title = v_title.getText()
            v_link = main_link + v_link

            # SALARY CHECK
            if (v_max_salary == '') and (v_min_salary == ''):
                _salary = vacancy.find('span', {'class': 'f-test-text-company-item-salary'})
                spans = _salary.findChildren()
                if len(spans) > 2:
                    v_min_salary = spans[0].getText()
                    v_max_salary = spans[2].getText()
                else:
                    v_max_salary, v_min_salary = spans[0].getText(), spans[0].getText()

            # write data to array
            vacancy_dir['title'] = v_title
            vacancy_dir['link'] = v_link
            vacancy_dir['site'] = 'SJ'
            vacancy_dir['min_salary'] = v_min_salary
            vacancy_dir['max_salary'] = v_max_salary
            vacancies.append(vacancy_dir)

    return vacancies, next_link


def main():
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko)' \
                 ' Chrome/35.0.1916.47 Safari/537.36'
    hh_main_link = "https://hh.ru"
    sj_main_link = "https://www.superjob.ru"
    text = input('Введите наименование вакансии для поиска:')
    n = int(input('Введите число страниц для сбора данных:'))
    result = []

    # HeadHunter staring data
    request_hh = requests.get(hh_main_link+"/search/vacancy?area=1&st=searchVacancy&text="+text,
                              headers={'User-Agent': ''})
    html_hh = request_hh.text

    # HeadHunter
    for i in range(n):
        temp, next_link = scrape_hh(html_hh, [])
        result = result + temp
        time.sleep(1)
        if hh_main_link == '':
            break
        else:
            request = requests.get(hh_main_link+next_link, headers={'User-Agent': user_agent})
            html_hh = request.text

    # SuperJobs staring data
    request_sj = requests.get(sj_main_link + "/vacancy/search/?keywords=" + text, headers={'User-Agent': user_agent})
    html_sj = request_sj.text
    # SuperJobs
    for i in range(n):
        temp, next_link = scrape_sj(html_sj, [])
        result = result + temp
        time.sleep(1)
        if sj_main_link == '':
            break
        else:
            request = requests.get(sj_main_link+next_link, headers={'User-Agent': ''})
            html_sj = request.text
    return result


data = main()
df = pd.DataFrame(data)
print(df)
