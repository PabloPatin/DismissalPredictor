from DbModels import *
from random import choice
import csv

if __name__ == '__main__':
    departments = ['Продажи', 'Специальный', 'Рабочий']
    positions = ['Работник', 'Менеджер']
    workers = []
    with open('workers.csv', encoding='utf-8') as file:
        for row in csv.DictReader(file):
            Employee.add_employee(row['full_name'], email=row['mailbox'], department=choice(departments),
                                  position=choice(positions))
    session.commit()
    session.close()