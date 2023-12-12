from Letters import LetterBase

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