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
    def __init__(self, path, context):
        self.path = path
        self.num = context.user_data["num"]

    def choose_one(self) -> Row:
        with open(self.path+".txt", "r") as file:
            data = [l for l in file.readlines() if l != "\n"]

        return Row([
            self.num,
            data[self.num % len(data)]
        ])
        
    def __repr__(self):
        with open(self.path+".txt", "r") as file:
            data = file.read()
        
        if len(data) > 4096: 
            data = data[:4092] + "..."

        return data