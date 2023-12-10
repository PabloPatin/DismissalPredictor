from abc import ABC
from datetime import date, time, datetime, timedelta
from random import random, gauss, choice
import csv

from settings import *
from test_settings import *

from external_addresses import EXTERNAL_ADDRESSES


class LetterBase(ABC):
    def __init__(self):
        self.text = ''
        self.sender = None
        self.recipient = None
        self.copy = None
        self.hidden_copy = None
        self.send_datetime = None
        self.read_datetime = None
        self.have_answer = False

    def generate_text(self, length):
        self.text = 'a' * length

    def set_info(self, sender, recipient, copy=None, hidden_copy=None):
        self.sender = sender
        self.recipient = recipient
        self.copy = copy
        self.hidden_copy = hidden_copy

    def send(self, dt):
        self.send_datetime = date

    def read(self, dt):
        self.read_datetime = date

    def answer(self):
        self.have_answer = True


class PlainLetter(LetterBase):
    ...


class AskLetter(LetterBase):
    def generate_text(self, length):
        self.text = 'a' * (length - 1) + '?'


class Params:
    """Параметры отвечают за вероятности отправки писем и интенсивность взаимодействия сотрудника с почтой.

    Для отправки писем по собственной инициативе:
        avg_messages - среднее количество отправляемых сотрудником писем
        avg_messages_deviation - стандартное отклонение от среднего количества отправляемых сотрудником писем

        ask_letter_chance - вероятность того, что письмо вопросительное (иначе обычное)
        other_letter_chance - вероятность того, что письмо послано на внешний адрес

        avg_letter_len - среднее количество символов в письме
        avg_letter_len_deviation - стандартное отклонение от среднего количества символов в письме

    Для ответов на письма:
        answer_plain_letter_chance - вероятность ответа на обычное письмо
        answer_ask_letter_chance - вероятность ответить на письмо с вопросом
    """

    @staticmethod
    def __time_to_sec(t: time):
        return t.hour * 3600 + t.minute * 60 + t.second

    def __init__(self):
        self.avg_send_messages = 2
        self.avg_messages_deviation = 2
        self.ask_letter_chance = 60 / 100
        self.other_letter_chance = 20 / 100
        self.answer_plain_letter_chance = 30 / 100
        self.answer_ask_letter_chance = 80 / 100
        self.avg_letter_len = 40
        self.avg_letter_len_deviation = 15

        self.work_day_start = self.__time_to_sec(WORK_DAY_START)
        self.work_day_end = self.__time_to_sec(WORK_DAY_END)
        self.work_period = self.work_day_end - self.work_day_start
        self.send_deviation = self.work_period // 2
        self.work_day_middle = self.work_day_start + self.work_period // 2


class Worker:
    """Класс Worker иммитирует поведение сотрудника"""
    workers = []

    def __new__(cls, *args, **kwargs):
        worker = super(Worker, cls).__new__(cls)
        cls.workers.append(worker)
        return worker

    def __init__(self, full_name: str, mailbox: str, params: Params = None):
        self.name = full_name
        self.mail = mailbox
        self.happiness_rate = 0
        self.incoming_messages = []
        self.outgoing_messages = []
        self.params = params if params else Params()

    def __repr__(self):
        return f'{self.name}, {self.mail}'

    def _randomize_message_count(self):
        message_count = gauss(self.params.avg_send_messages, self.params.avg_messages_deviation)
        if message_count < 0:
            return 0
        else:
            return round(message_count)

    def _randomise_send_time(self, deviation_modifier):
        send_time = int(gauss(self.params.work_day_middle, self.params.send_deviation * deviation_modifier)) % (
                3600 * 24)
        send_time = time(hour=send_time // 3600, minute=send_time % 3600 // 60)
        return send_time

    def _generate_letter(self, current_date) -> LetterBase:
        is_ask = random()
        if is_ask < self.params.ask_letter_chance:
            letter = AskLetter()
        else:
            letter = PlainLetter()
        is_other = random()
        if is_other < self.params.other_letter_chance:
            addres = choice(EXTERNAL_ADDRESSES)
        else:
            addres = choice(self.workers)
        letter_time = datetime.combine(time=self._randomise_send_time(DEVIATION_MODIFIER), date=current_date)
        letter.set_info(sender=self.mail, recipient=addres)
        letter.send(letter_time)
        return letter

    def send_messages(self, current_date: date) -> list[LetterBase]:
        """Посылает сообщения, согласно установленным параметрам """
        letters = []
        message_count = self._randomize_message_count()
        for msg in range(message_count):
            letter = self._generate_letter(current_date)
            letters.append(letter)
        return letters


class Mainloop:
    def __init__(self, start_date: date, end_date: date, workers: list[Worker] = None):
        # Установка периода генерации
        self.date = start_date - timedelta(days=1)
        self.end_date = end_date

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

    # Подготовка к ежедневному циклу событий
    def day_preparing(self):
        for worker in self.workers:
            self.messages.append(worker.send_messages(self.date))

    def __repr__(self):
        return self.date.strftime("%Y-%m-%d")

    @staticmethod
    def load_workers_from_csv(file_name):
        workers = []
        with open(file_name, encoding='utf-8') as file:
            for row in csv.DictReader(file):
                workers.append(Worker(**row))
        return workers


if __name__ == '__main__':
    workers = []
    with open('workers.csv', encoding='utf-8') as file:
        for row in csv.DictReader(file):
            workers.append(Worker(**row))

    loop = Mainloop(workers=workers[:2], start_date=date(day=1, month=1, year=2015),
                    end_date=date(day=1, month=2, year=2015))

    loop.start_loop()
