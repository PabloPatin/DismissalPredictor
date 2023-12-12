from abc import ABC
from datetime import date, time, datetime, timedelta
from random import random, gauss, choice, randint
import csv

from settings import *
from test_settings import *

from external_addresses import EXTERNAL_ADDRESSES

from DbModels import Employee, session

Address = str


class LetterBase(ABC):
    def __init__(self):
        self.text: str = ''
        self.sender: Address = None
        self.recipient: Address = None
        self.copy: list[Address] = None
        self.hidden_copy: list[Address] = None
        self.send_datetime: datetime = None
        self.read_datetime: datetime = None
        self.is_answer: bool = False

    def __repr__(self):
        if self.is_answer:
            return f'\n{self.send_datetime.isoformat(" ")}\nПисьмо от {self.sender}, ответ для {self.recipient}\n{self.text}'
        else:
            return f'\n{self.send_datetime.isoformat(" ")}\nПисьмо от {self.sender} для {self.recipient}\n{self.text}'

    def generate_text(self, length):
        self.text = 'a' * length

    def set_info(self, sender, recipient, copy=None, hidden_copy=None, is_answer=False):
        self.sender = sender
        self.recipient = recipient
        self.copy = copy
        self.hidden_copy = hidden_copy
        self.is_answer = is_answer

    def send(self, dt):
        self.send_datetime = dt

    def read(self, dt):
        self.read_datetime = dt


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

        avg_message_len - среднее количество символов в письме
        avg_message_len_deviation - стандартное отклонение от среднего количества символов в письме

    Для ответов на письма:
        answer_plain_letter_chance - вероятность ответа на обычное письмо
        answer_ask_letter_chance - вероятность ответить на письмо с вопросом

        answer_using_ask - вероятность ответить вопросительным письмом
        answer_speed_modifier - модификатор скорости ответа на письмо
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
        self.answer_using_ask = 40 / 100
        self.avg_message_len = 80
        self.avg_message_len_deviation = 50
        self.answer_speed_modifier = 2

        self.work_day_start = self.__time_to_sec(WORK_DAY_START)
        self.work_day_end = self.__time_to_sec(WORK_DAY_END)
        self.work_period = self.work_day_end - self.work_day_start
        self.send_deviation = self.work_period // 2
        self.work_day_middle = self.work_day_start + self.work_period // 2


class Mailbox:
    """Класс почтового ящика - помогает сортировать письма"""

    def __init__(self, address):
        self.address = address
        self.outgoing = []
        self.incoming = []

    def __repr__(self):
        return self.address

    def unwatched(self) -> list[LetterBase]:
        res = list(filter(lambda x: x.read_datetime is None, self.incoming))
        return res


class Worker:
    """Класс Worker иммитирует поведение сотрудника"""
    workers: list['Worker'] = []

    def __new__(cls, *args, **kwargs):
        worker = super(Worker, cls).__new__(cls)
        cls.workers.append(worker)
        return worker

    def __init__(self, full_name: str, mailbox: str, params: Params = None):
        self.name = full_name
        self.happiness_rate = 0
        self.mailbox = Mailbox(mailbox)
        self.params = params if params else Params()

    def __repr__(self):
        return f'{self.name} - {self.mailbox}'

    @staticmethod
    def _check_chance(chance):
        return random() < chance

    def _randomize_message_count(self):
        message_count = gauss(self.params.avg_send_messages, self.params.avg_messages_deviation)
        if message_count < 0:
            return 0
        else:
            return round(message_count)

    def _randomize_message_length(self):
        message_len = gauss(self.params.avg_message_len, self.params.avg_message_len_deviation)
        if message_len < MIN_MESSAGE_LEN:
            return MIN_MESSAGE_LEN
        else:
            return round(message_len)

    def _randomise_time(self, deviation_modifier, min_time=0) -> time | bool:
        send_time = int(gauss(self.params.work_day_middle, self.params.send_deviation * deviation_modifier)) % (
                3600 * 24)
        if send_time < min_time:
            return False
        send_time = time(hour=send_time // 3600, minute=send_time % 3600 // 60)
        return send_time

    def _see_message(self, letter: LetterBase, current_date: date) -> bool:
        received_time = letter.send_datetime.time()
        received_time = received_time.hour + 60 * received_time.minute + 3600 * received_time.second
        seen_time = self._randomise_time(1 / self.params.answer_speed_modifier, min_time=received_time)
        if seen_time:
            letter.read_datetime = datetime.combine(time=seen_time, date=current_date)
            return True
        else:
            return False

    def _generate_letter(self, current_date: date) -> LetterBase:
        if self._check_chance(self.params.ask_letter_chance):
            letter = AskLetter()
        else:
            letter = PlainLetter()

        if self._check_chance(self.params.other_letter_chance):
            address = choice(EXTERNAL_ADDRESSES)
        else:
            address = choice(self.workers).mailbox.address

        letter_time = datetime.combine(time=self._randomise_time(DEVIATION_MODIFIER), date=current_date)
        letter.set_info(sender=self.mailbox.address, recipient=address)
        letter.generate_text(self._randomize_message_length())
        letter.send(letter_time)
        return letter

    def _generate_answer_letter(self, letter: LetterBase):
        if self._check_chance(self.params.answer_using_ask):
            answer_letter = AskLetter()
        else:
            answer_letter = PlainLetter()
        address = letter.sender
        letter_time = letter.read_datetime + timedelta(minutes=randint(2, 8))
        answer_letter.set_info(sender=self.mailbox.address, recipient=address, is_answer=True)
        answer_letter.generate_text(self._randomize_message_length())
        answer_letter.send(letter_time)
        return answer_letter

    def send_messages(self, current_date: date) -> list[LetterBase]:
        """Посылает сообщения, согласно установленным параметрам"""
        letters = []
        message_count = self._randomize_message_count()
        for msg in range(message_count):
            letter = self._generate_letter(current_date)
            letters.append(letter)
        return letters

    def answer_message(self, letter: LetterBase, current_date: date) -> LetterBase | None:
        if not self._see_message(letter, current_date):
            return None
        if letter.is_answer:
            chance = self.params.answer_ask_letter_chance
        else:
            chance = self.params.answer_plain_letter_chance
        if self._check_chance(chance):
            answer_letter = self._generate_answer_letter(letter)
            return answer_letter
        else:
            return None


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
            # self.workers = self.load_workers_from_csv(WORKERS_FILE)
            self.workers = self.load_workers_from_postgresql_database()
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

    @staticmethod
    def load_workers_from_postgresql_database():
        workers = []
        for worker in session.query(Employee).all():
            workers.append(Worker(
                worker.name,
                worker.email
            ))
        return workers

if __name__ == '__main__':
    loop = Mainloop(start_date=date(day=1, month=1, year=2015),
                    end_date=date(day=3, month=1, year=2015))

    loop.start_loop()
    result = loop.messages
    print(loop.messages)

    with open(TEST_DATA_FILE, mode='w', encoding='utf-8') as csv_file:
        fieldnames = result[0].__dict__.keys()
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for data in result:
            writer.writerow(data.__dict__)  # Записываем строки данных
