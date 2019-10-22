# Для этого задания данные были взяты с помощью кода из предыдущего задания и сохранены в формате .pkl
# Файл также приложен.
# В файле хранятся вакансии по запросу "python"

from pymongo import MongoClient
import pandas as pd

data = pd.read_pickle('vacancies.pkl')
print("-----DATA INFO-------")
print(data.info())
print("---------------------")

client = MongoClient('localhost', 27017)
db = client['v_python']
v_python = db.v_python

# Закомментировал строку, чтобы не записывать данные каждый раз.
# v_python.insert_many(data.to_dict('records'))

# Запрос на интересующую пользователя зарплату и вывод.
# Так как в данных есть пропущенные значения зарплат или только одна из двух(минимальная или максимальная),
# нужно использовать двойное условие "ИЛИ".


def search_by_salary():
    _input = input('Введите интересующую вас минимальную зарплату по вакансии для вывода:')
    try:
        salary = int(_input)
        objects = v_python.find({'$or': [{'min_salary': {'$gte': salary}}, {'max_salary': {'$gte': salary}}]},
                                {'title', 'site', 'min_salary', 'max_salary'})

        # Тут проверяем еще раз, если минимальная зарплата есть, но она меньше заданной - нам это не нужно.
        for obj in objects:
            if (obj['min_salary']) != 'none' and (obj['min_salary']) < salary:
                pass
            else:
                print(obj)
    except ValueError:
        print("Вы ввели не число !")
        search_by_salary()


search_by_salary()
