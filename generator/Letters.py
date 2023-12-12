from abc import ABC
from datetime import datetime

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
