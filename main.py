from generator.Loops import Mainloop
from generator.test_settings import TEST_DATA_FILE
from datetime import date
import csv

from DbModels import session, Employee
from generator.Worker import Worker

workers = []
for worker in session.query(Employee).all():
    workers.append(Worker(
        worker.name,
        worker.email
    ))
loop = Mainloop(workers=workers, start_date=date(day=1, month=1, year=2015), end_date=date(day=10, month=1, year=2015))

loop.start_loop()
result = loop.messages
print(loop.messages)

with open(TEST_DATA_FILE, mode='w', encoding='utf-8') as csv_file:
    fieldnames = result[0].__dict__.keys()
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for data in result:
        writer.writerow(data.__dict__)  # Записываем строки данных


