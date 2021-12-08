import csv
from copy import copy

# unlike with units, there are two files to cache in the name of speed
from typing import Dict

cache = {}
cache2 = {}


class Armour(object):
    def __init__(self, data: Dict[str, str]):
        self.line = data
        self.origid =  int(data["id"])
        self.name = data["name"]
        self.type = int(data["type"])
        self.def_ = int(data["def"])
        self.enc = int(data["enc"])
        self.rcost = int(data["rcost"])

        if self.origid in cache2:
            self.zones = cache2[self.origid]
        else:
            data = r"protections_by_armor.csv"
            with open(data, "r") as f:
                reader = csv.DictReader(f, delimiter="\t")
                for line in reader:
                    armid = int(line["armor_number"])
                    zone = int(line["zone_number"])
                    if armid not in cache2:
                        cache2[armid] = {}
                    cache2[armid][zone] = cache2[armid].get(zone, 0) + int(line["protection"])
            self.zones = cache2[self.origid]
    def __repr__(self):
        return f"Armour({self.name}#{self.origid})"

    @staticmethod
    def from_id(id):
        with open("armors.csv", "r") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for line in reader:
                if int(line["id"]) == id:
                    break
            return Armour.from_line(line)

    @staticmethod
    def from_line(line):
        return Armour(line)

def loadAllUnitData():
    if len(cache) == 0:
        with open("armors.csv", "r") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for line in reader:
                id = int(line["id"])
                cache[id] = Armour.from_line(line).line

def get(id):
    if id in cache:
        return Armour.from_line(copy(cache[id]))
    u = Armour.from_id(id)
    cache[id] = copy(u.line)
    return u