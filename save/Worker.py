from datetime import date, time, datetime, timedelta
from random import random, gauss, choice, randint
import csv

from settings import *
from generator.test_settings import *

from external_addresses import EXTERNAL_ADDRESSES

from Letters import AskLetter, PlainLetter, LetterBase
from Params import Params
from Mailbox import Mailbox

from DbModels import Employee, session


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
