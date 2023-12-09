from abc import ABC
from datetime import date, time, timedelta
from random import randint, gauss
import csv

from settings import *
from test_settings import *


class Params:
    """Параметры отвечают за вероятности отправки писем и интенсивность взаимодействия сотрудника с почтой.
    Все вероятности обозначаются в процентах.
    Вероятности перемножаются, тоесть если сотрудник отправил первое письмо с вероятностью p, то второе он отправит с вероятностью p**2

    send_plain_letter_corp - вероятность отправки обычного письма другому сотруднику
    send_plain_letter_other - вероятность отправки обычного письма другому сотруднику
    extra_day_chance_corp - вероятность дня усиленной переписки внутри компании у сотрудника
    extra_day_chance_other - вероятность дня усиленной переписки вне компании у сотрудника
    extra_day_modifier - на сколько процентов повышается вероятность отправки
    """

    def __init__(self):
        # вероятность отправки
        self.send_plain_letter_corp = randint(40, 50)
        self.send_plain_letter_other = randint(20, 40)
        self.extra_day_chance_corp = 3
        self.extra_day_chance_other = 5
        self.extra_day_modifier = randint(200, 300)


class Worker:
    def __init__(self, full_name, mailbox):
        self.name = full_name
        self.mail = mailbox
        self.happiness_rate = 0
        self.incoming_messages = []
        self.outgoing_messages = []
        self.params = Params()

    def __repr__(self):
        return f'{self.name}, {self.mail}'

    @staticmethod
    def count_random(percent, modifier):
        for i in range(100):
            ...

    def send_messages(self):
        ...



class LetterBase(ABC):
    def __init__(self):
        self.text = ''
        self.sender = None
        self.recipient = None
        self.copy = None
        self.hidden_copy = None
        self.send_date = None
        self.read_date = None
        self.have_answer = False

    def generate_text(self, length):
        self.text = 'a' * length

    def set_info(self, sender, recipient, copy=None, hidden_copy=None):
        self.sender = sender
        self.recipient = recipient
        self.copy = copy
        self.hidden_copy = hidden_copy

    def send(self, date):
        self.send_date = date

    def read(self, date):
        self.read_date = date

    def answer(self):
        self.have_answer = True


class PlainLetter(LetterBase):
    ...


class AskLetter(LetterBase):
    def generate_text(self, length):
        self.text = 'a' * (length - 1) + '?'


class Mainloop:
    def __init__(self, start_date: date, end_date: date, workers: list[Worker] = None):
        # Установка периода генерации
        self.date = start_date - timedelta(days=1)
        self.end_date = end_date

        # Задание параметров рабочего дня
        self.work_day_start = self.__time_to_sec(WORK_DAY_START)
        self.work_day_end = self.__time_to_sec(WORK_DAY_END)
        self.work_period = self.work_day_end - self.work_day_start
        self.send_deviation = self.work_period // 2
        self.work_day_middle = self.work_day_start + self.work_period // 2

        # Подгрузка рабочих
        if not workers:
            self.workers = self.load_workers_from_csv(WORKERS_FILE)
        else:
            self.workers = workers

        # Инициализация сообщений
        self.messages = []

    def __next__(self):
        if self.date < self.end_date:
            self.date += timedelta(days=1)
            return self
        else:
            raise StopIteration()

    def __iter__(self):
        return self

    def start_loop(self):
        for day in self:
            day.day_preparing()
            ...

    #Подготовка к ежедневному циклу событий
    def day_preparing(self):
        for worker in self.workers:
            self.messages.append(worker.send_messages())

    def __repr__(self):
        return self.date.strftime("%Y-%m-%d")

    @staticmethod
    def __time_to_sec(t: time):
        return t.hour * 3600 + t.minute * 60 + t.second

    def randomise_send_time(self):
        send_time = int(gauss(self.work_day_middle, self.send_deviation)) % (3600 * 24)
        send_time = time(hour=send_time // 3600, minute=send_time % 3600 // 60)
        return send_time

    @staticmethod
    def load_workers_from_csv(file_name):
        workers = []
        with open(file_name, encoding='utf-8') as file:
            for row in csv.DictReader(file):
                workers.append(Worker(**row))
        return workers


if __name__ == '__main__':
    workers = []
    with open('test_names.csv', encoding='utf-8') as file:
        for row in csv.DictReader(file):
            workers.append(Worker(**row))

    loop = Mainloop(workers=workers[:5], start_date=date(day=1, month=1, year=2015),
                    end_date=date(day=1, month=2, year=2015))
    # loop = Mainloop(start_date=date(day=1, month=1, year=2015),
    #                 end_date=date(day=1, month=2, year=2015))

    loop.start_loop()

    for i in range(100):
        print(loop.randomise_send_time())
