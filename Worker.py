from abc import ABC
from dataclasses import dataclass
from datetime import date, timedelta
import csv


@dataclass
class Params:
    ...


class Worker:
    def __init__(self, full_name, mailbox):
        self.name = full_name
        self.mail = mailbox
        self.happiness_rate = 0
        self.incoming_messages = []
        self.outgoing_messages = []
        self.params = Params()
        self.__set_default_params()

    def __repr__(self):
        return f'{self.name}, {self.mail}'

    def __set_default_params(self):
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
    def __init__(self, workers: list[Worker], start_date: date, end_date: date):
        self.date = start_date
        self.end_date = end_date
        self.workers = workers

    def __next__(self):
        if self.date < self.end_date:
            self.date += timedelta(days=1)
            return self
        else:
            raise StopIteration()

    def __iter__(self):
        return self

    def __repr__(self):
        return self.date.strftime("%Y-%m-%d")



if __name__ == '__main__':
    workers = []
    with open('test_names.csv', encoding='utf-8') as file:
        for row in csv.DictReader(file):
            workers.append(Worker(**row))

    loop = Mainloop(workers[:5], start_date=date(day=1, month=1, year=2015), end_date=date(day=1, month=2, year=2015))
    for day in loop:
        print(day)