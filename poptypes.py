import autocalc
import copy
import random
import unitinbasedatafinder
import utils

THRONES = {1:["The Throne of the Second Age", "The Throne of War", "The Throne of Night", "The Throne of Beasts", "The Throne of Thorns",
              "The Throne of Flames", "The Throne of Ice", "The Throne of Storms", "The Throne of Might",
              "The Throne of the Stars", "The Throne of Stability", "The Throne of the Deeps", "The Throne of Pearls",
              "The Throne of Bones", "The High Throne", "The Throne of Law", "The Throne of Zeal", "The Brass Throne",
              "The Coral Throne", "The Throne of Pestilence", "The Lower Throne", "The Throne of Spring",
              "The Throne of Summer", "The Throne of Autumn", "The Throne of Winter"],
           2:["The Throne of the First Age", "The Throne of Gaia", "The Crystal Throne", "The Iron Throne", "The Silver Throne",
              "The Golden Throne", "The Throne of Bureaucracy", "The Throne of Knowledge", "The Throne of Life",
              "The Throne of Death", "The Throne of Fortune", "The Throne of Misfortune", "The Inner Throne",
              "The Outer Throne", "The Throne of the Moon", "The Throne of Fire", "The Throne of Earth",
              "The Throne of Air", "The Throne of Water", "The Throne of the Churning Ocean"],
           3:["The Throne of Splendour", "The Throne of the Pantokrator", "The Throne of Abundance",
              "The Throne of Eternal Suffering", "The Throne of the Sun", "The Throne of Sorcery", "The Throne of Elements",
              "The Shattered Throne", "The Throne of Creation", "The Throne of Destiny"]}

def _validateAdditionalreqs(unit, additionalreqs, bannedtraits, selectionfunction):
    valid = True
    if additionalreqs is not None:
        valid = False
        for req in additionalreqs:
            if getattr(unit, req, 0) > 0:
                valid = True
                break
        if not valid:
            return False
    if bannedtraits is not None:
        for req in bannedtraits:
            if getattr(unit, req, 0) > 0:
                return False
    if selectionfunction is not None:
        return selectionfunction(unit)
    return valid

def _unitCountToEventModCommand(count):
    if count == 1: return "1unit"
    elif count < 3: return "1d3units"
    elif count < 6: return "1d6units"
    elif count < 8: return "2d6units"
    elif count < 10: return "3d6units"
    elif count < 13: return "4d6units"
    elif count < 16: return "5d6units"
    elif count < 19: return "6d6units"
    elif count < 22: return "7d6units"
    elif count < 25: return "8d6units"
    elif count < 28: return "9d6units"
    elif count < 31: return "10d6units"
    elif count < 34: return "11d6units"
    elif count < 37: return "12d6units"
    elif count < 40: return "13d6units"
    elif count < 43: return "14d6units"
    elif count < 46: return "15d6units"
    elif count < 49: return "16d6units"
    return "16d6units"


# Modified version of the national PD generation
def selectTwoUnitsAndOneCompatibleCommander(pool, fallbackcom, fallbackunits, maxpaths=2.4, additionalreqs=None,
                                            bannedtraits=None, commanderfilterfunction=None, unitfilterfunction=None):
    "If set, any attribute in the additional requirements list must exist with a >0 value to be valid"
    possibleUnits = []
    attempt = 0
    while 1:
        if len(possibleUnits) < 2:
            attempt += 1
            if attempt == 1:
                # Select a unit
                for unit in pool:
                    uid = unit.id
                    if getattr(unit, "holy", 0) > 0:
                        continue
                    if not _validateAdditionalreqs(unit, additionalreqs, bannedtraits, unitfilterfunction):
                        continue
                    possibleUnits.append((uid, unit))
            elif attempt == 2:
                for unit in pool:
                    uid = unit.id
                    if not _validateAdditionalreqs(unit, additionalreqs, bannedtraits, unitfilterfunction):
                        continue
                    possibleUnits.append((uid, unit))
            else:
                fallbackone = fallbackunits[0]
                fallbacktwo = fallbackunits[1]
                possibleUnits = [unitinbasedatafinder.get(fallbackone), unitinbasedatafinder.get(fallbacktwo)]
            random.shuffle(possibleUnits)

        selectedUID, selectedUnit = copy.deepcopy(possibleUnits.pop(0))
        selectedUID2, selectedUnit2 = copy.deepcopy(possibleUnits.pop(0))
        print(f"Try to find commander for units: {selectedUnit.name}, {selectedUnit2.name}")
        # Try and find a commander that can lead this
        commandersToCheck = pool[:]
        random.shuffle(commandersToCheck)
        leadership = ["leader"]
        for selected in [selectedUnit, selectedUnit2]:
            if getattr(selected, "undead", 0) > 0 or getattr(selected, "demon", 0) > 0:
                leadership.append("undeadleader")
            if getattr(selected, "magicbeing", 0) > 0:
                leadership.append("magicleader")

        chosenCommander = None

        while 1:
            if len(commandersToCheck) == 0:
                if attempt == 3:
                    commandersToCheck = unitinbasedatafinder.get(fallbackcom)
                    attempt += 1
                elif attempt == 4:
                    raise ValueError("For some reason the fallback combination invalid")
                else:
                    break
            currentCommander = copy.deepcopy(commandersToCheck.pop(0))
            commanderUID = currentCommander.id
            print(f"Check commander {currentCommander.name}")
            lacksLeadership = False
            for leadershiptype in leadership:
                if not getattr(currentCommander, leadershiptype, 0) > 0:
                    lacksLeadership = True
                    break
            if lacksLeadership:
                print(f"Commander is missing required leadership")
                continue
            if not _validateAdditionalreqs(currentCommander, additionalreqs, bannedtraits, commanderfilterfunction):
                continue
            unloadedPaths = currentCommander.unloadRandomPaths()
            totalpaths = unloadedPaths.getTotalPaths(True)
            if totalpaths >= maxpaths:
                continue

            chosenCommander = currentCommander
            break

        if chosenCommander is None:
            continue
        break
    return (commanderUID, selectedUID, selectedUnit, selectedUID2, selectedUnit2, chosenCommander)

class Poptype(object):
    def __init__(self, id):
        self.id = id
        self.units = []
        self.commanders = []
        self.unitobjs = []
        self.commanderobjs = []


    def addUnits(self, items):
        commanderUID, selectedUID, selectedUnit, selectedUID2, selectedUnit2, chosenCommander = items
        self.units.append(selectedUID)
        self.units.append(selectedUID2)
        self.commanders.append(commanderUID)
        self.unitobjs.append(selectedUnit)
        self.unitobjs.append(selectedUnit2)
        self.commanderobjs.append(chosenCommander)
    def writeInfoText(self):
        # Could be a one liner, but that's more than a bit of a syntax atrocity...
        # So doing the kinda nasty list comps separately
        commandernames = ', '.join([f"{x.name}#{x.id}" for x in self.commanderobjs])
        unitnames = ', '.join([f"{x.name}#{x.id}" for x in self.unitobjs])
        poptypetext = f"--Poptype {self.id}:\n\t--Commanders: {commandernames}\n\t--Units: {unitnames}\n"
        return poptypetext
    def writeModContent(self, **options):
        self.newunitids = []
        self.newcommanderids = []
        modcontent = ""
        for unit in self.unitobjs:
            gcost = autocalc.unit(unit)
            unit.gcost = int(round(gcost * options.get("indieunitgoldcostmultiplier", 1.2), 0))
            ret = utils.modCommandsForNewUnit(unit, iscom=False, additionalModCmds=f"-- Unit for poptype: {unit.name}\n")
            modcontent += ret[0] + "\n"
            self.newunitids.append(ret[1])
        for unit in self.commanderobjs:
            gcost = autocalc.commander(unit)
            unit.gcost = int(round(gcost * options.get("indiecommandergoldcostmultiplier", 1.2), 0))
            ret = utils.modCommandsForNewUnit(unit, iscom=True,
                                              additionalModCmds=f"-- Commander for poptype: {unit.name}\n")
            modcontent += ret[0] + "\n"
            self.newcommanderids.append(ret[1])
        modcontent += f"#selectpoptype {self.id}\n#clearrec\n#cleardef\n"
        modcommandsuffixes = ["", "b", "c"]
        for unitindex, newunitid in enumerate(self.newunitids):
            if unitindex < 2:
                suffix = modcommandsuffixes[unitindex]
                unit = self.unitobjs[unitindex]
                modcontent += f"#defunit1{suffix} {newunitid}\n"
                gcost = autocalc.scorechassiscombat(unit)
                gcost = max(2, gcost)
                multiplicity = max(1, int(110 / gcost))
                modcontent += f"#defmult1{suffix} {multiplicity}\n"
            modcontent += f"#addrecunit {newunitid}\n"
        for commindex, newcommid in enumerate(self.newcommanderids):
            if commindex == 0:
                modcontent += f"#defcom1 {newcommid}\n"
            modcontent += f"#addreccom {newcommid}\n"
        modcontent += "#end\n\n"
        return modcontent
    def writeEventContent(self, req_rare, **options):
        eventcontent = f"-- Event for poptype {self.id}\n"
        eventcontent += "#newevent\n#rarity 5\n#req_indepok 1\n#req_pop0ok\n#req_pregame\n"
        eventcontent += "#notext\n#nolog\n#req_capital 0\n"
        eventcontent += '#req_nomonster "NNN Indie Dummy"' + "\n"
        eventcontent += '#stealthcom "NNN Indie Dummy"' + "\n"
        eventcontent += f"#req_rare {req_rare}\n"
        if self.id > 80:
            eventcontent += "#req_land 0\n"
        else:
            eventcontent += "#req_land 1\n"
        eventcontent += f"#setpoptype {self.id}\n"
        gold = options.get("goldperindieprovince", 500)
        goldPerCommanderType = gold / len(self.newcommanderids)
        # 1 or 2 of each commander type
        for index, commanderid in enumerate(self.newcommanderids):
            commander = self.commanderobjs[index]
            unitstartindex = 2 * index
            numOfThisCommander = random.randint(1, 2)
            if commander.gcost * 2 > goldPerCommanderType:
                numOfThisCommander = 1
            goldRemaining = goldPerCommanderType - (commander.gcost * numOfThisCommander)
            goldPerUnitType = goldRemaining/2
            for commanderattempt in range(0, numOfThisCommander):
                eventcontent += f"#com {commanderid}\n"
                itemquality = random.choice([None, None, 1, 1, 1, 1, 2, 2, 3, 4])
                if itemquality is not None:
                    eventcontent += f"#addequip {itemquality}\n"
                for unitTypeIndex in range(0, 2):
                    unitid = self.newunitids[unitstartindex + unitTypeIndex]
                    unitobj = self.unitobjs[unitstartindex + unitTypeIndex]
                    numUnits = int(round(goldPerUnitType/(unitobj.gcost*numOfThisCommander)))
                    if commanderattempt == 0:
                        numUnits = max(1, numUnits)
                    if numUnits > 0:
                        # avoid starvation, but you can only do this to one commander
                        if numUnits * numOfThisCommander > 50 and commanderattempt == 0 and unitTypeIndex == 0:
                            eventcontent += '#msg "Give broth to avoid starvation [Enormous Cauldron of Broth]"' + "\n"
                            eventcontent += "#magicitem 9\n"
                        eventcommand = _unitCountToEventModCommand(numUnits)
                        eventcontent += f"#{eventcommand} {unitid}\n"
        eventcontent += "#end\n\n"
        return eventcontent

def newpoptypes(mainpool, **options):
    poptypes = []
    for landpoptypeid in range(1, 81):
        if landpoptypeid % 10 == 0:
            utils._writetoconsole(f"Beginning land poptype {landpoptypeid} of 80...")
        pool = copy.copy(mainpool)
        # 1-2 commander types
        # 2-4 unit types
        # Any may not exceed 2.4 total paths (ballpark for amazon mages)
        poptype = Poptype(landpoptypeid)
        numberCommanders = random.randint(1, 2)
        unitfilter = lambda x: autocalc.unit(x) >= 3
        # Must avoid generic pd being demon/undead
        for com in range(0, numberCommanders):
            bannedTraits = ["aquatic"]
            if com == 0:
                bannedTraits = ["undead", "magicbeing", "demon", "aquatic"]
            items = selectTwoUnitsAndOneCompatibleCommander(pool, 34, (18, 17), options.get("standardindiemaxpaths", 2.4),
                                                            None, bannedTraits, unitfilterfunction=unitfilter)
            poptype.addUnits(items)
        poptypes.append(poptype)
        #break

    utils._writetoconsole(f"Beginning UW poptypes...")
    for waterpoptypeid in range(81, 101):
        pool = copy.copy(mainpool)
        # 1-2 commander types
        # 2-4 unit types
        # Any may not exceed 2.4 total paths (ballpark for amazon mages)
        poptype = Poptype(waterpoptypeid)
        numberCommanders = random.randint(1, 2)
        for com in range(0, numberCommanders):
            bannedTraits = None
            if com == 0:
                bannedTraits = ["undead", "magicbeing", "demon"]
            items = selectTwoUnitsAndOneCompatibleCommander(pool, 34, (18, 17),
                                                            options.get("standardindiemaxpaths", 2.4),
                                                            ["amphibian", "pooramphibian", "aquatic"], bannedTraits,
                                                            unitfilterfunction=unitfilter)

            poptype.addUnits(items)
        poptypes.append(poptype)
        #break

    utils._writetoconsole(f"Writing mod code for poptypes...")
    poptypeinfotext = ""
    poptypemodtext = f"#selectmonster {utils.UNIT_ID_START}\n#copystats 284\n#copyspr 284\n#hp 1\n#mr 30\n#landdamage 100\n"
    utils.UNIT_ID_START += 1
    poptypemodtext += '#name "NNN Indie Dummy"' + "\n"
    poptypemodtext += "#uwdamage 100\n#amphibian\n#end\n\n"
    poptypeeventtext = "-- Blow up all independents on the map, violently\n"
    for x in range(0, 10):
        poptypeeventtext += "#newevent\n#rarity 5\n#req_pregame\n#req_indepok 1\n#req_pop0ok\n"
        poptypeeventtext += "#notext\n#nolog\n#req_capital 0\n#strikeunits 999\n#end\n\n"

    for poptype in poptypes:
        if poptype.id < 81:
            desiredprobability = 100/(81-poptype.id)
        else:
            realn = poptype.id - 80
            desiredprobability = 100/(21-realn)
        poptypeinfotext += poptype.writeInfoText()
        poptypemodtext += poptype.writeModContent(**options)
        poptypeeventtext += poptype.writeEventContent(max(1, int(desiredprobability)), **options)

    # Thrones! Each one wants different extra defenders, I guess

    # I also need to do a land version and a UW version

    throneoutput = additionalThroneDefenders(mainpool, **options)
    poptypemodtext += throneoutput[0]
    poptypeeventtext += throneoutput[1]

    out = poptypeinfotext + poptypemodtext + poptypeeventtext
    return out

def additionalThroneDefenders(mainpool, **options):
    # lv1: some 2-5 path normal mages
    # lv2: maybe rainbow pretender chassis
    # lv3: a magically beefed up dom 2+ pretender chassis plus some sidekick(s)

    # Kinda need: 1) Mage/commander component 2) Troop

    # Mages:
        # Possbilities: 1) anything at random
        # 2) any startdom 4 pretender chassis or other immobile unit
        # Could be literally anything. It would be quite funny to see tens of low level mages on a throne...
        # Pick a mage -> decide how much pathboosting it's getting -> see how many you can afford

    # Troops:
        # Possibilities: 1) anything at random, but set min gold cost appropriately 2) dominion 2+ nonimmobile pretender chassis

    modcontent = ""
    eventcontent = ""

    for throneLevel, throneList in THRONES.items():
        utils._writetoconsole(f"Beginning defenders for level {throneLevel} thrones...")
        # 2**(thronelevel-1) is how Illwinter adjust throne indie strength
        goldForThroneAddition = options.get("throneindiegold", 800) * (2**(throneLevel - 1))
        for throneName in throneList:
            pool = copy.copy(mainpool)
            # The gold cost split could go any way it wants...
            percentageCommanderComponent = random.randint(18, 82) / 100
            percentageTroopComponent = 1.0 - percentageCommanderComponent
            for req_land in range(0, 2):
                eventstarttext = f"#newevent\n#rarity 5\n#req_pregame\n#req_indepok 1\n#req_pop0ok\n#notext\n#nolog\n#req_site 1\n"
                eventstarttext += '#msg "Spawn additional defenders for throne [' + throneName + ']"' + "\n"
                eventstarttext += f"#req_land {req_land}\n"

                # Gold constraints, make sure there is enough for one of each unit
                mageGoldLimit = max(120, goldForThroneAddition * percentageCommanderComponent)
                unitGoldLimit = max(100, goldForThroneAddition * percentageTroopComponent * 0.5)
                unitMinGoldCost = max(3.0, unitGoldLimit / 50)

                immobileMages = False
                haspathfilter = lambda x: x.unloadRandomPaths().getTotalPaths(False) > 0
                magefilter = lambda x: (haspathfilter(x) and autocalc.commander(x) <= mageGoldLimit)
                if random.random() < 0.15*throneLevel:
                    immobileMages = True
                    magefilter = lambda x: (haspathfilter(x) and autocalc.commander(x) <= mageGoldLimit and
                                            (getattr(x, "startdom", 0) >= 4 or getattr(x, "immobile", 0) > 0))
                pretenderChassisUnits = False
                unitfilter = lambda x: (haspathfilter(x) and unitMinGoldCost <= autocalc.unit(x) <= unitGoldLimit and
                                        getattr(x, "immobile", 0) <= 0)
                if random.random() < 0.15*throneLevel:
                    pretenderChassisUnits = True
                    unitfilter = lambda x: (haspathfilter(x) and unitMinGoldCost <= autocalc.unit(x) <= unitGoldLimit
                                            and getattr(x, "startdom", 0) >= 2 and getattr(x, "immobile", 0) <= 0)

                print(f"Defenders for {throneName} with reqland {req_land} has {mageGoldLimit} for mages and"
                      f" {unitGoldLimit} for units")

                bannedtraits = None
                requiredtraits = ["amphibian", "pooramphibian", "aquatic"]
                if req_land == 1:
                    bannedtraits = ["aquatic"]
                    requiredtraits = None



                items = selectTwoUnitsAndOneCompatibleCommander(pool, 34, (18, 17), 999.0, requiredtraits,
                                                                bannedtraits, magefilter, unitfilter)
                commanderUID, selectedUID, selectedUnit, selectedUID2, selectedUnit2, chosenCommander = items

                # How many of these commanders are we going to have?

                gcost = autocalc.commander(chosenCommander)
                maxNumCommanders = max(1, int(round(mageGoldLimit/gcost, 0)))
                custommagicModCommands = ""
                # Try to adjust paths by adding randoms until gcost becomes that number of commanders
                desiredNumCommanders = random.randint(1, maxNumCommanders)
                if maxNumCommanders > 1:
                    # There are various ways we could add randoms:
                    # 1) Between the paths the chassis is guaranteed to have, if any
                    # 2) Between all the paths the chassis can get, if any
                    # 3) Between all the paths the chassis can't currently get, because illwinter sometimes does this
                    attempts = [1, 2, 3]
                    random.shuffle(attempts)

                    guaranteedpaths = []
                    randomedpaths = []
                    inaccessiblepaths = []
                    for index, path in enumerate(utils.MAGIC_PATHS):
                        if getattr(chosenCommander, path, 0) > 0 and path != "H":
                            guaranteedpaths.append(index)
                    unloadedPaths = chosenCommander.unloadRandomPaths()
                    for index, path in enumerate(utils.MAGIC_PATHS):
                        if getattr(chosenCommander, path, 0) > 0.0 and path != "H":
                            if index not in guaranteedpaths:
                                randomedpaths.append(index)
                    for index, path in enumerate(utils.MAGIC_PATHS):
                        if index not in guaranteedpaths and index not in randomedpaths and path != "H":
                            inaccessiblepaths.append(index)

                    while len(attempts) > 0:
                        additiontype = attempts.pop(0)

                        if additiontype == 3:
                            if len(attempts) > 0 and random.random() < 0.75:
                                attempts.append(3)
                                continue

                        workingcopy = copy.deepcopy(chosenCommander)

                        # MagePathRandom.paths expects flags of 2 ** <path id>
                        if additiontype == 1:
                            randompaths = guaranteedpaths
                        elif additiontype == 2:
                            randompaths = randomedpaths
                        elif additiontype == 3:
                            randompaths = inaccessiblepaths

                        paths = 0
                        for path in randompaths:
                            paths += 2 ** path
                        # Try another method if there's nothing to add
                        if paths == 0:
                            continue
                        newRandom = unitinbasedatafinder.MagePathRandom(100, 1, paths)
                        if not newRandom.addToUnit(workingcopy):
                            # can't add any more randoms to this unit
                            break

                        # If successful, reshuffle the attempt types and continue until none of the three methods works
                        if autocalc.commander(workingcopy) * desiredNumCommanders <= mageGoldLimit:
                            print(f"Addition successful, new gold cost {autocalc.commander(workingcopy) * desiredNumCommanders} "
                                  f"<= limit of {mageGoldLimit}")
                            attempts = [1, 2, 3]
                            random.shuffle(attempts)
                            chosenCommander = workingcopy
                            # Illwinter wants the above pathmasks << 7
                            custommagicModCommands += f"#custommagic {paths << 7} 100\n"
                        else:
                            print(f"Addition failed, new gold cost {autocalc.commander(workingcopy) * desiredNumCommanders} "
                                  f" > limit of {mageGoldLimit}")

                desiredNumCommanders = max(1, int(round(mageGoldLimit / autocalc.commander(chosenCommander), 0)))
                addequipvalue = 4
                indepspells = 7
                if desiredNumCommanders > 3:
                    addequipvalue = 3
                    indepspells = 6
                if desiredNumCommanders > 8:
                    addequipvalue = 2
                    indepspells = 5
                if desiredNumCommanders > 14:
                    addequipvalue = 1

                chosenCommander.gcost = round(gcost * options.get("indiecommandergoldcostmultiplier", 1.2), 0)
                ret = utils.modCommandsForNewUnit(chosenCommander, iscom=True,
                                                  additionalModCmds=custommagicModCommands +
                                                                    f"#nowish 1\n#indepspells {indepspells}\n"
                                                                    f"-- Commander throne defender: {chosenCommander.name}\n")
                modcontent += ret[0] + "\n"
                newcommanderID = ret[1]

                eventcontent += eventstarttext
                eventcontent += f"#com {newcommanderID}\n"
                eventcontent += f"#addequip {addequipvalue}\n"

                for unit in (selectedUnit, selectedUnit2):
                    gcost = autocalc.unit(unit)
                    unit.gcost = round(gcost * options.get("indieunitgoldcostmultiplier", 1.2), 0)
                    ret = utils.modCommandsForNewUnit(unit, iscom=False,
                                                      additionalModCmds=f"-- Unit throne defender: {unit.name}\n")
                    modcontent += ret[0] + "\n"
                    newunitid = ret[1]
                    quantity = max(1, int(round(unitGoldLimit/unit.gcost, 0)))
                    eventcontent += f"#{_unitCountToEventModCommand(quantity)} {newunitid}\n"
                eventcontent += "#end\n\n"
                eventcontent += eventstarttext


                # Intentionally adding (desiredNumCommanders-1) - the first needs to pick up the units
                for additionalcommander in range(1, desiredNumCommanders):
                    if additionalcommander % 5 == 0:
                        eventcontent += "#end\n\n"
                        eventcontent += eventstarttext
                    eventcontent += f"#com {newcommanderID}\n"
                    eventcontent += f"#addequip {addequipvalue}\n"

                eventcontent += "#end\n\n"


    return (modcontent, eventcontent)
