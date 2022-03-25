import json
import os


class Unit:
    def __init__(self, name, parts):
        self.parts = parts
        self.name = name

    def __str__(self):
        return f"{self.name} : {self.parts} "

    def __repr__(self):
        return f"{self.name} : {self.parts} "


class UnitReader:

    def __init__(self):
        self.entries = []

    def read(self, directory):
        files = os.listdir(directory)
        for file in files:
            f = open(directory + file)
            x = json.load(f)
            name = os.path.basename(f.name).replace(".json", '')
            self.entries.append(Unit(name, x[name]))

    def getAll(self, lang):
        res = []
        for e in self.entries:
            res.append({e.name: e.parts[lang]})

        return res

    def getUnit(self, unit, lang):
        return [y.parts[lang] for y in list(filter(lambda x: x.name == unit, self.entries))][0]
