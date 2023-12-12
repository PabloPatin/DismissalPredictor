import csv
from datetime import date, timedelta

from .test_settings import WORKERS_FILE


from .Worker import Worker
from .Letters import LetterBase


class DayLoop:
    def __init__(self, date: date, workers: list[Worker]):
        self.date = date
        self.workers = workers
        self.daily_messages: list[LetterBase] = []

    def _find_worker_by_address(self, address: str) -> Worker | None:
        for worker in self.workers:
            if worker.mailbox.address == address:
                return worker
        return None

    def day_preparing(self):
        for worker in self.workers:
            self.daily_messages += worker.send_messages(self.date)
        self.daily_messages.sort(key=lambda letter: letter.send_datetime)

    def start_day(self) -> list[LetterBase]:
        for message in self.daily_messages:
            worker = self._find_worker_by_address(message.sender)
            worker.mailbox.outgoing.append(message)
            worker = self._find_worker_by_address(message.recipient)
            if worker is not None:
                worker.mailbox.incoming.append(message)
                answer_message = worker.answer_message(message, self.date)
                if answer_message is not None:
                    self.daily_messages.append(answer_message)
        return self.daily_messages


class Mainloop:
    def __init__(self, start_date: date, end_date: date, workers: list[Worker] = None):
        # Установка периода генерации
        self.date = start_date - timedelta(days=1)
        self.end_date = end_date

        # Подгрузка рабочих
        if not workers:
            self.workers = self.load_workers_from_csv(WORKERS_FILE)
            # self.workers = self.load_workers_from_postgresql_database()
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
            new_day = DayLoop(day.date, self.workers)
            for worker in self.workers:
                new_day.daily_messages += worker.mailbox.unwatched()
            new_day.day_preparing()
            self.messages += new_day.start_day()

    def __repr__(self):
        return self.date.strftime("%Y-%m-%d")

    @staticmethod
    def load_workers_from_csv(file_name):
        workers = []
        with open(file_name, encoding='utf-8') as file:
            for row in csv.DictReader(file):
                workers.append(Worker(**row))
        return workers
