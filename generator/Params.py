from datetime import time
from random import gauss

from .test_settings import WORK_DAY_START, WORK_DAY_END


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
