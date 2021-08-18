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
    def __init__(self, path_to_card):
        self.path = path_to_card

    def choose_one(self) -> Row:
        with open(self.path+"-COPY.txt", "r+") as file:
            data = [l for l in file.readlines() if l != "\n"]

            if len(data) == 0:   # if we alreay read all rows
                source_file = open(self.path+".txt", "r")
                data = source_file.read()
                file.write(data)
                data = [l for l in data.split("\n") if l != "\n"]
                source_file.close()  # copy all source card to the copy

        random_row_ind = random.randint(0, len(data)-1)

        row = Row([random_row_ind, data[random_row_ind]])  # Card has been shuffled 
        del data[random_row_ind]  # delete row in the card copy
        
        with open(self.path+"-COPY.txt", "w") as file:
            file.write("\n".join(data))

        return row

    def __repr__(self):
        with open(self.path+".txt", "r") as file:
            data = file.read()
        
        if len(data) > 4096: 
            data = data[:4092] + "..."

        return data