import csv
import os
from copy import copy, deepcopy
import utils

import weapon
import armour

cache = {}

csv_keys = []

def getMontagSummonAIScore(montagID):
    if montagID == -2:
        return 72 # longdead
    elif montagID == -3:
        return 77 # average of armed and unarmed soulless
    elif montagID == -4:
        return 82 # ghoul, ignoring pischasa for now
    elif montagID == -5:
        return 100 # random animal: a guess as it will vary hugely no matter what is done to aispellmod
    elif montagID == -6:
        return 208 # lesser horror
    elif montagID == -7:
        return 346 # greater horror
    elif montagID == -8:
        return 1200 # doom horror
    elif montagID == -9:
        return 55 # swarm bugs
    elif montagID == -10:
        return 200 # good crossbreed, a guess
    elif montagID == -11:
        return 80 # bad crossbreed, a guess
    elif montagID == -12:
        return 90 # 3% good crossbreed, 97% bad crossbreed
    elif montagID == -13:
        return 95 # adventurers
    elif montagID == -14:
        return 120 # random dungeon creature, a guess
    elif montagID == -15:
        return 77 # more soulless
    raise ValueError(f"No summon AI score defined for montag {montagID}")

# keys which should not be set at all if no value is passed. Otherwise -1 is set
_badkeys = ["siegebonus", "castledef", "patrolbonus", "pathboost", "pathboostuw", "magicboostF", "magicboostA",
            "magicboostW", "magicboostE", "magicboostS", "magicboostD", "magicboostN", "magicboostALL", "foreignmagicboost",
            "pathboostuw", "pathboostland", "percentagepathreduction", "reinvigoration", "fireres", "coldres", "shockres",
            "poisonres", "landreinvigoration", "reformtime"]

class MagePathRandom(object):
    def __init__(self, chance, link, paths):
        self.link: int = link  # amount of levels it gives
        self.paths: int = paths  # path mask
        self.chance: int = chance

    def getPaths(self):
        out = []
        exponent = 0
        while 1:
            if self.paths & (2 ** exponent):
                out.append(utils.MAGIC_PATHS[exponent])
            exponent += 1
            if (2 ** exponent) > self.paths:
                break
        return out

    def __repr__(self):
        return f"MagePathRandom(Paths={self.paths}, link={self.link}, chance={self.chance})"


def getRandomPaths(unit):
    "Return a list of MagePathRandom objects for the given unit"
    out = []
    for n in range(1, 7):
        mask = getattr(unit, f"mask{n}", 0) >> 7
        if mask <= 0:
            break
        chance = getattr(unit, f"rand{n}", 0)
        instances = getattr(unit, f"nbr{n}", 0)
        link = getattr(unit, f"link{n}", 0)
        for i in range(instances):
            out.append(MagePathRandom(chance=chance, link=link, paths=mask))
    return out

class UnitInBaseDataFinder(object):
    def __init__(self):
        self.additionalmodcmds = ""
        self.origid = None
        self.id = None
        self.descr = ""
        # make sure keys are initialised - brand new units otherwise have nothing set
        if len(csv_keys) == 0:
            with open("BaseU.csv", "r") as f:
                reader = csv.DictReader(f, delimiter="\t")
                for line in reader:
                    for k in line.keys():
                        if k not in _badkeys:
                            setattr(self, k, -1)
                            csv_keys.append(k)
                    break
        else:
            for k in csv_keys:
                setattr(self,k, -1)
        self.weapons = []
        self.armours = []

    def __repr__(self):
        return (f"Unit({self.id}, {getattr(self, 'name', '???')})")

    def calcSummonAIScore(self):
        "Return the Illwinter base summon AI score for in an in battle summon of this unit."
        score = 2 * (getattr(self, "att", 0) + getattr(self, "def", 0) + getattr(self, "str", 0) + getattr(self, "hp", 0))
        if getattr(self, "fireshield", 0) > 0 or getattr(self, "trample", 0) > 0:
            score += (getattr(self, "hp") * 4)
        if getattr(self, "ethereal", 0) > 0:
            score += (getattr(self, "hp") * 4)

        secondshape = int(getattr(self, "secondshape", -1))
        if secondshape > 0:
            unit = get(int(secondshape))
            score += unit.calcSummonAIScore()
        return score

    def getOldAgePenalty(self):
        oldagepenalty = 0
        maxage = max(0, getattr(self, "maxage"))
        if maxage <= 0:
            return 0
        startage = max(0, getattr(self, "startage"))
        if maxage < startage: oldagepenalty = 1
        if maxage * 1.2 < startage: oldagepenalty = 2
        if maxage * 1.4 < startage: oldagepenalty = 3
        if maxage * 1.6 < startage: oldagepenalty = 4
        if maxage * 2 < startage: oldagepenalty = 5
        if maxage * 3 < startage: oldagepenalty = 6
        print(f"Startage: {startage}, maxage: {maxage}: penalty = {oldagepenalty}")
        return oldagepenalty

    def unloadRandomPaths(self):
        "Return a copy of the current unit, with random paths offloaded into self.F, self.A, etc..."
        retval = deepcopy(self)
        randoms = getRandomPaths(retval)
        paths = []
        for random in randoms:
            paths = random.getPaths()
            amountadded = (random.link / len(paths)) * random.chance/100
            for path in paths:
                print(f"Add {amountadded} to {path}")
                setattr(retval, path, max(0.0, getattr(retval, path, 0.0)) + amountadded)
        totalpaths = 0
        for path in utils.MAGIC_PATHS:
            if max(0, getattr(retval, path, 0)):
                totalpaths += getattr(retval, path, 0)
        print(f"UnloadRandomPaths: total for {self.__repr__()} is {totalpaths}")
        totalpaths = 0
        cached = cache[self.origid]
        for path in utils.MAGIC_PATHS:
            if max(0, getattr(cached, path, 0)):
                totalpaths += getattr(cached, path, 0)
        print(f"UnloadRandomPaths: cached total for {self.__repr__()} is {totalpaths}")
        totalpaths = 0
        for path in utils.MAGIC_PATHS:
            if max(0, getattr(self, path, 0)):
                totalpaths += getattr(self, path, 0)
        print(f"UnloadRandomPaths: parent total for {self.__repr__()} is {totalpaths}")
        return retval

    def enforcePositiveGoldCost(self):
        "Return any mod text needed to ensure the unit does not cost negative gold"
        gcostattribsMult = {"enchrebate50p":0.5}
        gcostattribsFlat = {"enchrebate50":50, "enchrebate10":10}
        gcostattribsMagnitudeMult = {"mountainrec":1, "deathrec":3, "chaosrec":3}
        realgcost = self.gcost
        for attrib in gcostattribsMult:
            if getattr(self, attrib, 0) > 0:
                realgcost *= getattr(self, attrib, 1.0)
        realeffectsizes = {}
        for attrib in gcostattribsFlat:
            if getattr(self, attrib, 0) > 0:
                realeffectsizes[attrib] = gcostattribsFlat[attrib]
        for attrib in gcostattribsMagnitudeMult:
            if getattr(self, attrib, 0) > 0:
                realeffectsizes[attrib] = getattr(self, attrib, 0) * gcostattribsMagnitudeMult[attrib]

        # of the above, mountainrec cannot currently be cleared via mod commands
        unmoddableCmds = ["mountainrec"]

        retval = ""
        while realgcost <= 0:
            # If any one attribute is enough to make it positive again, use that
            attribToUse = None
            for attrib, size in realeffectsizes.items():
                if attrib not in unmoddableCmds:
                    if realgcost + size >= 0:
                        attribToUse = attrib
                        break
            # Otherwise, go for the biggest.
            if attribToUse is None:
                biggestEffectMagnitude = None
                for attrib, size in realeffectsizes.items():
                    if attrib not in unmoddableCmds:
                        if biggestEffectMagnitude is None or size > biggestEffectMagnitude:
                            biggestEffectMagnitude = size
                            attribToUse = attrib
            if attribToUse is None:
                # Consider raising gcost to offset mountainrec
                if "mountainrec" in realeffectsizes:
                    if realcost + realeffectsizes["mountainrec"] > 0:
                        self.gcost += realeffectsizes["mountainrec"]
                        realgcost += realeffectsizes["mountainrec"]
                        retval += f"-- Added {realeffectsizes['mountainrec']} to base cost to offset mountainrec " \
                                  f"allowing negative cost\n"
                        del realeffectsizes["mountainrec"]
                        continue
                raise ValueError(f"Found no way to make {self.name}#{self.origid} have a positive gcost")

            retval += f"-- Removing to forbid negative cost\n"
            if attribToUse in gcostattribsFlat:
                retval += f"#{attribToUse} -1\n"
            else:
                retval += f"#{attribToUse} 0\n"
            realgcost += realeffectsizes[attribToUse]
            del realeffectsizes[attribToUse]
        return retval
    def getTotalPaths(self, inclholy=True):
        totalpaths = 0.0
        for path in utils.MAGIC_PATHS:
            if max(0, getattr(self, path, 0)) and (path != "H" or inclholy):
                totalpaths += getattr(self, path, 0)
        return totalpaths

    def lowerPathsForPretenderChassis(self):
        unloadedPaths = self.unloadRandomPaths()

        totalPaths = {}
        for path in utils.MAGIC_PATHS:
            totalPaths[path] = totalPaths.get(path, 0) + max(0.0, getattr(unloadedPaths, path, 0.0))
            setattr(self, path, 0)

        del totalPaths["H"]
        print(f"Unit total paths: {totalPaths}")
        # The values of the total paths dict, arranged in ascending order
        pathValuesSorted = sorted(list(totalPaths.values()))
        primaryPaths = []
        while 1:
            bestPathVal = pathValuesSorted.pop(-1)
            addedPath = False
            print(f"Current best path value is {bestPathVal}")
            for path, totalLevels in totalPaths.items():
                if bestPathVal == 0.0:
                    break
                if len(primaryPaths) == 3:
                    break
                if totalLevels == bestPathVal and path not in primaryPaths:
                    print(f"Identified best path as {path}")
                    primaryPaths.append(path)
                    addedPath = True
                    break
            if len(primaryPaths) == 3:
                break
            if addedPath:
                continue
            break
        print(f"Unit primary paths: {primaryPaths}")
        if len(primaryPaths) == 1:
            setattr(self, primaryPaths[0], 3)
        elif len(primaryPaths) == 2:
            setattr(self, primaryPaths[0], 2)
            setattr(self, primaryPaths[1], 1)
        elif len(primaryPaths) == 3:
            setattr(self, primaryPaths[0], 1)
            setattr(self, primaryPaths[1], 1)
            setattr(self, primaryPaths[2], 1)
        return primaryPaths
    def calcPathcost(self):
        startdom = self.calcStartdom()
        size = getattr(self, "ressize", 0)
        if size <= 0:
            size = getattr(self, "size", 0)
        totalpaths = 0
        for path in utils.MAGIC_PATHS:
            if getattr(self, path, 0) > 0:
                totalpaths += 1
        if startdom == 4:
            return 40
        if startdom == 3:
            return 60 - (6 * ((6 - size) + (3 - totalpaths)))
        if startdom == 2:
            return 80 - (12 * ((6 - size) + (3 - totalpaths)))
        if startdom == 1:
            if totalpaths == 0:
                return 15
            else:
                return 5 + (totalpaths * 5)
    def calcStartdom(self):
        if getattr(self, "startdom", 0) > 0:
            return getattr(self, "startdom", 0)
        # This concerns about two units, but non-pretender non-sacred immobiles without shapechanges also get 4
        if getattr(self, "immobile", 0) > 0 and getattr(self, "shapechange", 0) <= 0:
            return 4

        # Titan: size 4+ and hand slots
        # Monster: size 4+
        # Rainbow: everything else
        size = getattr(self, "ressize", 0)
        if size <= 0:
            size = getattr(self, "size", 0)

        if getattr(self, "size", 0) >= 4:
            if getattr(self, "hand", 0) > 0:
                return 3
            return 2
        return 1



    @staticmethod
    def from_id(id):
        with open("BaseU.csv", "r") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for line in reader:
                if int(line["id"]) == id:
                    return UnitInBaseDataFinder.from_line(line)
        raise ValueError(f"Unit {id} not found")

    @staticmethod
    def from_line(line):
        self = UnitInBaseDataFinder()
        self.line = line
        self.params = ["id", "origid", "weapons", "armours", "descr", "uniqueid", "params"]
        id = int(line["id"])
        self.origid = id
        self.id = id
        for k in line.keys():
            try:
                val = int(line[k])
            except:
                val = line[k]
            if (val is None or val == "") and k in _badkeys:
                continue
            if val is None: val = -1
            if val == "": val = -1
            setattr(self, k, val)
            self.params.append(k)
        self.weapons = []
        for x in range(1, 8):
            if getattr(self, f"wpn{x}") > 0:
                self.weapons.append(weapon.get(getattr(self, f"wpn{x}")))

        self.armours = []
        for x in range(1, 5):
            if getattr(self, f"armor{x}") > 0:
                self.armours.append(armour.get(getattr(self, f"armor{x}")))

        self.uniqueid = f"vanilla-{self.id}"

        return self
    def __deepcopy__(self, memo):
        # This deepcopy function is ~13% of total runtime
        # The problem is that a lot of users of unit data don't actually modify anything, which means much
        # of this could be avoided to cut down on that
        out = UnitInBaseDataFinder()
        for param in self.params:
            setattr(out, param, deepcopy(getattr(self, param, memo)))
        return out

def loadAllUnitData():
    # precaching these is likely to save ~5% runtime
    if len(cache) == 0:
        with open("BaseU.csv", "r") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for line in reader:
                id = int(line["id"])
                cache[id] = UnitInBaseDataFinder.from_line(line)
        weapon.loadAllUnitData()
        armour.loadAllUnitData()

def get(id):
    # The file lookup is slow
    # I did just save the file lines, but this was still being slow so deepcopy it is
    if id < 0:
        if id == -2: #longdead
            return get(193)
        if id == -3 or id == -15: #soulless
            return get(197)
        if id == -4: #ghoul
            return get(198)
        if id == -5: #animal (this returns lioness)
            return get(2133)
        if id == -6: #lesser horror
            return get(307)
        if id == -7: #greater horror
            return get(308)
        if id == -8: #doom horror
            return get(651) #eater of dreams
        if id == -9: #bug
            return get(2218) #large beetle
        if id == -10: #good crossbreed
            return get(637) #draco lion
        if id == -11: #bad crossbreed
            return get(461) #touch of leprosy small foulspawn
        if id == -12: #3% good crossbreed
            return get(461)
        if id == -13: #adventurer
            return get(2323)
        raise ValueError(f"Requested montag {id}, no replacement unit is set")
    if id in cache:
        return deepcopy(cache[id])
    u = UnitInBaseDataFinder.from_id(id)
    cache[id] = u
    return deepcopy(u)
