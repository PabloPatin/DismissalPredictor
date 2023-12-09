from abc import ABC


class Worker:
    def __init__(self):
        happiness_rate = 0
        messages = []


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
