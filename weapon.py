import csv
from copy import copy

# unlike with units, there are two files to cache in the name of speed
from typing import Dict

cache = {}
cache2 = {}


class Weapon(object):
    def __init__(self, data: Dict[str, str]):
        self.line = data
        self.origid =  int(data["id"])
        self.name = data["name"]
        self.att = int(data["att"])
        self.def_ = int(data["def"])
        self.len = int(data["len"])
        self.nratt = int(data["nratt"])
        self.ammo = int(data["ammo"])
        self.secondaryeffectid = int(data["secondaryeffect"])
        self.secondaryeffect = None
        self.secondaryeffectid = int(data["secondaryeffect"])
        self.secondaryeffect = None
        if self.secondaryeffectid > 0:
            self.secondaryeffect = get(self.secondaryeffectid)
        self.secondaryeffectalwaysid = int(data["secondaryeffectalways"])
        self.secondaryeffectalways = None
        if self.secondaryeffectalwaysid > 0:
            self.secondaryeffectalways = get(self.secondaryeffectalwaysid)

        if self.origid in cache2:
            line = copy(cache2[self.origid])
        else:
            with open("effects_weapons.csv", "r") as f:
                reader = csv.DictReader(f, delimiter="\t")
                for line in reader:
                    if int(line["record_id"]) == self.origid:
                        break
                cache2[self.origid] = copy(line)

        self.effect = int(line["effect_number"])
        self.damage = int(line["raw_argument"])
        self.spec = int(line["modifiers_mask"])

        self.range = line["range_base"]
        if self.range == "":
            self.range = 0
        else:
            self.range = int(self.range)
        self.range_strength = line["range_strength_divisor"]
        if self.range_strength == "":
            self.range_strength = 999
        else:
            self.range_strength = int(self.range_strength)

        self.estrange = self.range + int(14/self.range_strength)
        # this next thing seems to have values corresponding with strenght based range
        # this can also be stuff like AoE for fear effects

        # and now it's all confusing, so take only what I need
        self.aoe = int(line["area_base"])
    def getdamage(self, str):
        stradd = 0
        if self.spec & 1:
            stradd += str
        if self.spec & 288230376151711744:
            stradd += (str / 2)
        if self.spec & 4611686018427387904:
            stradd += (str / 3)
        return self.damage + stradd
    def getrange(self, str):
        return self.range + int(str / self.range_strength)
    def getTurnsOfAmmo(self):
        if self.nratt < 0:
            realnratt = 1 / ((self.nratt * -1))
        else:
            realnratt = 1
        if realnratt < 0:
            raise ValueError(f"Wpn {self.name}#{self.origid} has {realnratt} attacks")
        return self.ammo / realnratt
    def __repr__(self):
        return f"Weapon({self.name}#{self.origid})"

    @staticmethod
    def from_id(id):
        with open("weapons.csv", "r") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for line in reader:
                if int(line["id"]) == id:
                    break
            return Weapon.from_line(line)

    @staticmethod
    def from_line(line):
        return Weapon(line)

def loadAllUnitData():
    if len(cache) == 0:
        with open("weapons.csv", "r") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for line in reader:
                id = int(line["id"])
                cache[id] = Weapon.from_line(line).line


def get(id):
    if id in cache:
        return Weapon.from_line(copy(cache[id]))
    u = Weapon.from_id(id)
    cache[id] = copy(u.line)
    return u