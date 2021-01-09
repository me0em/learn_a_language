import random


class Row:
    """ Class represents one line from any dictionary file
    """
    def __init__(self, raw):
        self.raw = raw
        self.index = raw[0]
        self.string = raw[1]
        self.original_lang = self.string.split(" :: ")[0]
        self.russian_lang = self.string.split(" :: ")[1]


class Card:
    def __init__(self, path):
        self.path = path

    def choose_one(self) -> Row:
        with open(self.path+".txt", "r") as file:
            data = [l for l in file.readlines() if l != "\n"]
        return Row(
            random.choice(
                [(i, data[i]) for i in range(len(data))]
            )
        )
