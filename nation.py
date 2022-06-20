import naming
import random
import autocalc
import utils
import math
import unitinbasedatafinder
import copy

class NationBuilder(object):
    def __init__(self, pool, seed, **options):
        # PRNG seed for this nation
        self.seed = seed
        random.seed(seed)
        # List of Units to pick from, shuffled according to the nation seed
        self.pool = pool
        random.shuffle(self.pool)

        # List of all recruitable Unit objects for units/commanders, respectively
        self.addrecunit = []
        self.addreccom = []

        # Lists of different things to do with kinds of national units/commanders: TODO are these all needed?
        self.caponlymages_unitobjs = []
        self.caponlyunits_unitobjs = []
        self.caponlymages_ids = []
        self.caponlyunits_ids = []
        self.strcommanders = {}
        self.recruitableunits = []
        self.nonCapOnlyCmdrUnitIDs = []
        self.recruitableunitsIdsToUnitObjs = {}
        self.nonCapOnlyCmdrUnitIDsToUnitObjs = {}
        self.allUnitIDsToUnitObjs = {}
        self.allCmdrIDsToUnitObjs = {}
        self.realPretenderUnitIDs = []

        self.nationname = None
        self.nationid = None
        self.startSiteNames = []
        self.primaryPath = None
        self.modcontent = ""

        self.nationDescr = '#descr "A Nonsensical Novel Nation! Generated with seed ' + str(seed) + "\n"

        self.collectCommandersFromPool(**options)
        self.collectUnitsFromPool(**options)
        self.prepareStartSites()
        self.selectPretendersFromPool(**options)

        self.nationid = utils.NATION_ID_START
        utils.NATION_ID_START += 1

        # Pd and start army must go inside the selectnation block
        self.modcontent += f"#selectnation {self.nationid}\n"
        self.selectPDAndStartArmy()

        self.assembleModContent()

    def assembleModContent(self):
        self.nationname = naming.getNationName()
        self.modcontent += '#name "' + self.nationname + '"' + "\n"
        epithet = self.getEpithet()
        self.modcontent += '#epithet "' + epithet + '"' + "\n"
        self.modcontent += "#era 2\n"
        # Unfortunately this is the only way I know to make pretenders be all the custom ones
        self.modcontent += "#homerealm 1\n"
        nordicGodIDs = [250, 269, 401, 501, 657, 1098, 1229, 1379, 1561, 2206, 2234, 2239, 2448, 2449, 2800, 2801, 2802,
                        2803, 3086]
        for nordicGod in nordicGodIDs:
            self.modcontent += f"#delgod {nordicGod}\n"
        self.modcontent += '#descr "' + self.nationDescr.strip() + '"' + "\n"
        summary = self.writeSummary()
        self.modcontent += '#summary "' + summary.strip() + '"' + "\n"
        for pretenderID in self.realPretenderUnitIDs:
            self.modcontent += f"#addgod {pretenderID}\n"
        for startsiteName in self.startSiteNames:
            self.modcontent += '#startsite "' + startsiteName + '"' + "\n"
        self.modcontent += \
            "#color " + str(random.random()) + " " + str(random.random()) + " " + str(random.random()) + "\n"
        self.modcontent += "#secondarycolor " + str(random.random()) + " " + str(random.random()) + " " + str(
            random.random()) + "\n"
        for id_ in self.recruitableunits:
            self.modcontent += f"#addrecunit {id_}\n"
        for id_ in self.nonCapOnlyCmdrUnitIDs:
            self.modcontent += f"#addreccom {id_}\n"
        self.modcontent += "#end\n\n"

    def getPrimaryPaths(self):
        "Returns the highest paths the nation has access to. Returns 1-3 such values, depending on what is available"
        primaryPaths = []
        totalPaths = self.getMaximumPathAccess()
        del totalPaths["H"]
        pathValuesSorted = sorted(list(totalPaths.values()))
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
            # If we get here, there are not enough mages for all the paths
            # so either settle with what we have or make something up out of a lack of better options
            if len(primaryPaths) == 0:
                primaryPaths.append(utils.MAGIC_PATHS[random.randint(0, 7)])
            break
        return primaryPaths

    def prepareStartSites(self):
        # Start sites should provide 5 gems
        idsToInclude = self.caponlymages_ids + self.caponlyunits_ids

        # Identify up to three primary paths
        totalPaths = self.getMaximumPathAccess()
        del totalPaths["H"]
        print(f"Nation total paths: {totalPaths}")
        # The values of the total paths dict, arranged in ascending order
        pathValuesSorted = sorted(list(totalPaths.values()))
        primaryPaths = self.getPrimaryPaths()
        print(f"Selected primary paths: {primaryPaths}")
        self.primaryPath = primaryPaths[0]
        # shallow copy
        sitePaths = primaryPaths[:]
        sitePaths.append("H")
        random.shuffle(sitePaths)

        numSites = max(1, min(4, math.ceil(len(idsToInclude) / 4)))
        outputText = ""
        self.startSiteNames = []
        for siteindex in range(0, numSites):
            outputText += f"#selectsite {utils.SITE_ID_START}\n"
            utils.SITE_ID_START += 1

            sitename = naming.getSiteName(sitePaths)

            self.startSiteNames.append(sitename)
            outputText += '#name "' + sitename + '"' + "\n"
            outputText += f"#level {random.randint(0, 4)}\n"
            outputText += "#rarity 5\n"
            if siteindex == 0:
                # Gems.
                if len(primaryPaths) == 3:
                    gemQuantities = [2, 2, 1]
                elif len(primaryPaths) == 2:
                    gemQuantities = [3, 2]
                else:
                    gemQuantities = [5]
                for index, pathLabel in enumerate(primaryPaths):
                    pathConstant = utils.MAGIC_PATHS.index(pathLabel)
                    outputText += f"#gems {pathConstant} {gemQuantities[index]}\n"
            for unitIndex in range(0, 4):
                if len(idsToInclude) == 0:
                    break
                idToInclude = idsToInclude.pop(0)
                iscom = idToInclude in self.caponlymages_ids
                if iscom:
                    outputText += f"#homecom {idToInclude}\n"
                else:
                    outputText += f"#homemon {idToInclude}\n"
            # Path for the site, could be any primary or holy
            pathLabel = sitePaths.pop(0)
            # ensure this does not attempt to pop from empty list
            if len(sitePaths) == 0:
                sitePaths = primaryPaths[:]
                random.shuffle(sitePaths)
            pathConstant = utils.MAGIC_PATHS.index(pathLabel)
            outputText += f"#path {pathConstant}\n"

            outputText += "#end\n\n"

        self.modcontent += outputText

    def collectUnitsFromPool(self, **options):
        numunits = options.get("numunits", 15)
        unitsadded = 0
        for x in range(0, numunits):
            unit = copy.deepcopy(self.pool.pop(0))
            print(f"Add unit to nation: {unit}")
            self.addrecunit.append(unit)

        for unit in self.addrecunit:
            gcost = autocalc.unit(unit)
            unit.gcost = gcost
            ret = utils.modCommandsForNewUnit(unit, iscom=False, additionalModCmds=f"-- Unit for nation: {unit.name}\n")
            self.modcontent += ret[0]
            self.allUnitIDsToUnitObjs[ret[1]] = unit
            if gcost >= 50:
                self.caponlyunits_ids.append(ret[1])
                self.caponlyunits_unitobjs.append(unit)
            else:
                self.recruitableunits.append(ret[1])
                self.recruitableunitsIdsToUnitObjs[ret[1]] = unit

    def collectCommandersFromPool(self, numcommanders, **options):
        numcommanders = options.get("numcommanders", 10)
        nationTotalpaths = 0.0
        commandersadded = 0
        # Constraints:
        # 1 stealthy commander
        # 1 commander with 80+ ldr
        # 1 commander with priest levels
        # 1 commander with 1 or 2 total nonholy path levels
        # 1 commander with 4+ nonholy path levels
        # Total nonholy paths (incl random weightings) cannot exceed options["maxtotalpathspernation"]

        # Commanders costing 350+ gold or that have 6+ paths get the cap only treatment
        # Commanders with 5+ paths get str

        # Units costing 50+ gold get the cap only treatment
        stealthconstraint = False
        leaderconstraint = False
        priestconstraint = False
        lessermageconstraint = False
        bigmageconstraint = False
        while len(self.addreccom) < numcommanders:
            if len(self.pool) == 0:
                print(f"No more commanders in pool! ")
            unit = copy.deepcopy(self.pool.pop(0))
            if commandersadded == 0:
                if unit.stealthy <= 0:
                    continue
            elif commandersadded == 1 and not leaderconstraint:
                if unit.leader < 80:
                    continue
            elif commandersadded == 2 and not priestconstraint:
                if unit.H <= 0:
                    continue

            unloadedPaths = unit.unloadRandomPaths()
            totalpaths = unloadedPaths.getTotalPaths(False)

            if nationTotalpaths + totalpaths > options.get("maxtotalpathspernation", 15):
                continue

            # Getting a big mage first can fill up the total paths per nation and make it unable to find a lesser mage
            # because taking it would push it over the max total
            if not lessermageconstraint and (totalpaths > 2.0):
                if nationTotalpaths + totalpaths > options.get("maxtotalpathspernation", 15) - 2:
                    continue

            if commandersadded == 3 and not lessermageconstraint:
                if not (totalpaths > 0.0 and totalpaths <= 2.0):
                    continue
            if commandersadded == 4 and not bigmageconstraint:
                if totalpaths < 4.0:
                    continue
            if unit.stealthy >= 0:
                stealthconstraint = True
                print(f"{unit.name} fits stealth constraint")
            if unit.leader >= 80:
                leaderconstraint = True
                print(f"{unit.name} fits leader constraint")
            if unit.H >= 1:
                priestconstraint = True
                print(f"{unit.name} fits priest constraint")
            if totalpaths > 0 and totalpaths <= 2.0:
                lessermageconstraint = True
                print(f"{unit.name} fits lesser mage constraint")
            if totalpaths >= 4:
                bigmageconstraint = True
                print(f"{unit.name} fits big mage constraint")

            print(f"Add cmdr to nation: {unit}")
            nationTotalpaths += totalpaths

            self.addreccom.append(unit)
            if totalpaths >= 6.0:
                self.caponlymages_unitobjs.append(unit)
            if totalpaths >= 5.0:
                self.strcommanders[unit] = 4
            if totalpaths >= 10:
                self.strcommanders[unit] = 6
            commandersadded += 1

        for unit in self.addreccom:
            gcost = autocalc.commander(unit)
            unit.gcost = gcost
            additional = f"-- Commander for nation: {unit.name}\n"
            if unit in self.strcommanders:
                additional += f"#rpcost {self.strcommanders[unit]}\n"
            ret = utils.modCommandsForNewUnit(unit, iscom=True, additionalModCmds=additional)
            self.modcontent += ret[0]
            newUnitID = ret[1]
            self.allCmdrIDsToUnitObjs[newUnitID] = unit
            if gcost >= 350:
                self.caponlymages_unitobjs.append(newUnitID)
                self.caponlymages_ids.append(newUnitID)
            elif unit in self.caponlymages_unitobjs:
                self.caponlymages_ids.append(newUnitID)
            else:
                self.nonCapOnlyCmdrUnitIDs.append(newUnitID)
                self.nonCapOnlyCmdrUnitIDsToUnitObjs[newUnitID] = unit

    def searchForSacredsAndRangedWeapons(self):
        self.hasRangedWeapon = False
        self.recAnywhereSacredNames = []
        self.capOnlySacredNames = []

        for uid, unit in self.allUnitIDsToUnitObjs.items():
            if not self.hasRangedWeapon:
                for weapon in unit.weapons:
                    if weapon.getrange(unit.str) >= 1:
                        self.hasRangedWeapon = True
                        break
            if getattr(unit, "holy", 0) > 0:
                if uid in self.caponlyunits_ids:
                    self.capOnlySacredNames.append(naming.pluraliseUnitName(unit))
                else:
                    self.recAnywhereSacredNames.append(naming.pluraliseUnitName(unit))

    def selectPretendersFromPool(self, **options):
        pretenderCount = options.get("pretendercount", 25)
        limitPerDomscore = math.floor(pretenderCount / 2.5)
        unitlist = []
        additionalmodcmdlist = []
        numberOfPretendersByStartdom = {}
        while len(unitlist) < pretenderCount:
            unit = copy.deepcopy(self.pool.pop(0))
            # These things that mean a unit should not be a pretender...
            if getattr(unit, "holy", 0) > 0:
                continue
            if getattr(unit, "H", 0) > 0:
                continue
            if getattr(unit, "singlebattle", 0) > 0:  # This crashes the game
                continue
            if getattr(unit, "defector", 0) > 0:
                continue
            if getattr(unit, "deserter", 0) > 0:
                continue
            if getattr(unit, "horrordeserter", 0) > 0:
                continue

            primaryPaths = unit.lowerPathsForPretenderChassis()
            startdom = unit.calcStartdom()
            if numberOfPretendersByStartdom.get(startdom, 0) > limitPerDomscore:
                print(f"Discard {unit}: too many for this domscore")
                continue

            if startdom == 1:
                # Set all path levels to 1
                for path in utils.MAGIC_PATHS:
                    if getattr(unit, path, 0) > 0:
                        print(f"Pretender start paths: Set {path} of {unit} to 1")
                        setattr(unit, path, 1)

            additionalCmds = f"#startdom {startdom}\n"
            additionalCmds += f"#pathcost {unit.calcPathcost()}\n"
            if getattr(unit, "mr", 0) < 18:
                additionalCmds += "#mr 18\n"
            if getattr(unit, "mor", 0) < 30:
                additionalCmds += "#mor 30\n"
            additionalCmds += "#clearmagic\n"
            for pathConstant, path in enumerate(utils.MAGIC_PATHS):
                if getattr(unit, path, 0) > 0:
                    additionalCmds += f"#magicskill {pathConstant} {getattr(unit, path)}\n"

            gcost = autocalc.commander(unit)
            if gcost >= 380:
                continue
            unit.gcost = gcost

            numberOfPretendersByStartdom[startdom] = numberOfPretendersByStartdom.get(startdom, 0) + 1
            unitlist.append(unit)
            additionalmodcmdlist.append(additionalCmds)

        for index, pretenderunit in enumerate(unitlist):
            additionalModCmds = additionalmodcmdlist[index]
            additionalModCmds += f"-- Pretender for nation: {pretenderunit.name}\n"
            ret = utils.modCommandsForNewUnit(pretenderunit, iscom=True, additionalModCmds=additionalModCmds)
            self.modcontent += ret[0]
            self.realPretenderUnitIDs.append(ret[1])

    def getMaximumPathAccess(self):
        pathLevels = {}
        for uid, unit in self.allCmdrIDsToUnitObjs.items():
            unloaded = unit.unloadRandomPaths()
            for path in utils.MAGIC_PATHS:
                if getattr(unloaded, path, 0) > 0:
                    pathLevels[path] = max(pathLevels.get(path, 0.0), getattr(unloaded, path))
        print(f"Max path access: {pathLevels}")
        return pathLevels

    def getEpithet(self):
        primaryPath = self.primaryPath
        if random.random() < 0.1:
            primaryPath = "H"
        commanderGoldCosts = sorted([com.gcost for com in self.addreccom])
        index = -1
        epithet = None
        while 1:
            if len(commanderGoldCosts) == 0:
                raise ValueError("Couldn't produce a legal epithet for nation.")
            goldcost = commanderGoldCosts.pop(-1)
            for com in self.addreccom:
                if com.gcost == goldcost:
                    epithet = naming.getEpithet(com, self.primaryPath)
                    if epithet is not None:
                        break
            if epithet is not None:
                break
        return epithet

    def getMagicSummaryText(self, pathLevels):
        summary = ""
        pathsToCommentOn = utils.MAGIC_PATHS[:]
        pathsToCommentOn.remove("H")
        thresholds = {4.9: "Masterful", 3.9: "Mighty", 2.9: "Strong", 1.9: "Moderate", 0.9: "Weak", 0.01: "Minor"}
        for threshold in reversed(sorted(thresholds.keys())):
            pathsForThisThreshold = []
            for path in pathsToCommentOn:
                level = pathLevels.get(path, 0.0)
                if level >= threshold:
                    pathsForThisThreshold.append(path)
            if len(pathsForThisThreshold) > 0:
                for path in pathsForThisThreshold:
                    pathsToCommentOn.remove(path)
                nameList = [utils.REAL_PATH_NAMES[x] for x in pathsForThisThreshold]
                summary += f" {thresholds[threshold]} "
                summary += utils._listToWords(nameList)
                summary += "."
        return summary

    def writeSummary(self):
        summary = "Race: Unknown.\nMilitary: All kinds of units."

        self.searchForSacredsAndRangedWeapons()

        if not self.hasRangedWeapon:
            summary += " No ranged weapons."
        if len(self.capOnlySacredNames) + len(self.recAnywhereSacredNames) == 0:
            summary += " No sacred units."
        if len(self.capOnlySacredNames) > 0:
            summary += f" May recruit holy {utils._listToWords(self.capOnlySacredNames)} in the capital."
        if len(self.recAnywhereSacredNames) > 0:
            summary += f" May recruit holy {utils._listToWords(self.recAnywhereSacredNames)} in any fort."
        summary += "\nMagic:"

        pathLevels = self.getMaximumPathAccess()

        summary += self.getMagicSummaryText(pathLevels)

        summary += "\n"
        if pathLevels.get("H", 1) >= 4.0:
            summary += "Priests: Legendary."
        elif pathLevels.get("H", 1) >= 3.0:
            summary += "Priests: Strong"
        elif pathLevels.get("H", 1) >= 2.0:
            summary += "Priests: Moderate"
        else:
            summary += "Priests: Weak"
        return summary

    def selectTwoUnitsAndOneCompatibleCommander(self, fallbackcom, fallbackunits):
        possibleUnits = []
        attempt = 0
        while 1:
            if len(possibleUnits) < 2:
                attempt += 1
                if attempt == 1:
                    # Select a unit
                    for uid, unit in self.recruitableunitsIdsToUnitObjs.items():
                        if getattr(unit, "holy", 0) > 0:
                            continue
                        possibleUnits.append((uid, unit))
                elif attempt == 2:
                    for uid, unit in self.recruitableunitsIdsToUnitObjs.items():
                        possibleUnits.append((uid, unit))
                else:
                    fallbackone = fallbackunits[0]
                    fallbacktwo = fallbackunits[1]
                    possibleUnits = [(fallbackone, unitinbasedatafinder.get(fallbackone)),
                                     (fallbacktwo, unitinbasedatafinder.get(fallbacktwo))]
                random.shuffle(possibleUnits)

            selectedUID, selectedUnit = possibleUnits.pop(0)
            selectedUID2, selectedUnit2 = possibleUnits.pop(0)
            print(f"Try to find commander for units: {selectedUnit.name}, {selectedUnit2.name}")
            # Try and find a commander that can lead this
            commandersToCheck = self.possiblePDCommanders[:]
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
                        commandersToCheck = [(fallbackcom, unitinbasedatafinder.get(fallbackcom))]
                        attempt += 1
                    elif attempt == 4:
                        raise ValueError("For some reason the combination of indie commander and archers is invalid")
                    else:
                        break
                commanderUID, currentCommander = commandersToCheck.pop(0)
                print(f"Check commander {currentCommander.name}")
                lacksLeadership = False
                for leadershiptype in leadership:
                    if not getattr(currentCommander, leadershiptype, 0) > 0:
                        lacksLeadership = True
                        break
                if lacksLeadership:
                    print(f"Commander is missing required leadership")
                    continue
                chosenCommander = currentCommander
                break

            if chosenCommander is None:
                continue
            break
        return (commanderUID, selectedUID, selectedUnit, selectedUID2, selectedUnit2, chosenCommander)

    def selectPDAndStartArmy(self):
        # PD and/or wall commander: pick a random commander that costs 100- gold that has 40+ ldr
        # Wall units can be anything, so long as it has a ranged attack and isn't sacred
        # PD and start units can be anything, so long as it isn't sacred
        cmdrType = None
        pdTroopType = None
        wallCmdrType = None
        wallType = None

        possibleUnits = []
        self.possiblePDCommanders = []

        for uid, cmdr in self.nonCapOnlyCmdrUnitIDsToUnitObjs.items():
            realgcost = autocalc.commander(cmdr, forTempUnits=True)
            if realgcost <= 100:
                self.possiblePDCommanders.append((uid, cmdr))

        if len(self.possiblePDCommanders) == 0:
            mingoldcost = min(autocalc.commander(com, forTempUnits=True) for com in self.nonCapOnlyCmdrUnitIDsToUnitObjs.values())
            for uid, cmdr in self.nonCapOnlyCmdrUnitIDsToUnitObjs.items():
                if autocalc.commander(cmdr, forTempUnits=True) == mingoldcost:
                    self.possiblePDCommanders.append((uid, cmdr))
                    break

        out = ""
        detailstext = ""
        # Attempt to get a wall unit/commander pair
        attempt = 0
        while 1:
            if len(possibleUnits) == 0:
                attempt += 1
                if attempt == 1:
                    # Select a wall unit.
                    for uid, unit in self.recruitableunitsIdsToUnitObjs.items():
                        if getattr(unit, "holy", 0) > 0:
                            continue
                        for weapon in unit.weapons:
                            range = weapon.getrange(unit.str)
                            if range >= 7:
                                possibleUnits.append((uid, unit))
                                break
                elif attempt == 2:
                    # Try sacred archers, then take literally anything
                    for uid, unit in self.recruitableunitsIdsToUnitObjs.items():
                        for weapon in unit.weapons:
                            range = weapon.getrange(unit.str)
                            if range >= 7:
                                possibleUnits.append((uid, unit))
                                break
                elif attempt == 3:
                    for uid, unit in self.recruitableunitsIdsToUnitObjs.items():
                        possibleUnits.append((uid, unit))
                else:
                    # Get stinking indie archers.
                    possibleUnits = [(17, unitinbasedatafinder.get(17))]
                random.shuffle(possibleUnits)
                if len(possibleUnits) == 0:
                    continue

            selectedUID, selectedUnit = possibleUnits.pop(0)
            # Try and find a commander that can lead this
            commandersToCheck = self.possiblePDCommanders[:]
            random.shuffle(commandersToCheck)
            leadership = "leader"
            if getattr(selectedUnit, "undead", 0) > 0 or getattr(selectedUnit, "demon", 0) > 0:
                leadership = "undeadleader"
            elif getattr(selectedUnit, "magicbeing", 0) > 0:
                leadership = "magicleader"

            chosenCommander = None

            while 1:
                if len(commandersToCheck) == 0:
                    if attempt == 4:
                        # Get a plain indie commander to go with your indie archers
                        commandersToCheck = [(34, unitinbasedatafinder.get(34))]
                        attempt += 1
                    elif attempt == 5:
                        raise ValueError("For some reason the combination of indie commander and archers is invalid")
                    else:
                        break
                commanderUID, currentCommander = commandersToCheck.pop(0)
                if not getattr(currentCommander, leadership, 0) > 0:
                    continue
                chosenCommander = currentCommander
                break

            if chosenCommander is None:
                continue

            # Work out multiplicity for the units...
            gcost = autocalc.scorechassiscombat(selectedUnit)
            gcost = max(2, gcost)
            multiplicity = max(1, int(100 / gcost))
            out += f"#wallcom {commanderUID}\n"
            out += f"#wallunit {selectedUID}\n"
            out += f"#wallmult {multiplicity}\n"
            detailstext += f"Fort Wall Defenders: {multiplicity}x {selectedUnit.name}, Commander: {chosenCommander.name}\n"

            break

        # Regular PD: #defcom1, #defunit1, #defunit1b
        # Here both units' leadership (in additional to standard leadership for indies units) needs to be respected by defcom1

        commanderUID, selectedUID, selectedUnit, selectedUID2, selectedUnit2, chosenCommander = self.selectTwoUnitsAndOneCompatibleCommander(
            34, (18, 17))

        out += f"#defcom1 {commanderUID}\n"
        out += f"#defunit1 {selectedUID}\n"
        gcost = autocalc.scorechassiscombat(selectedUnit)
        gcost = max(2, gcost)
        multiplicity = max(1, int(100 / gcost))
        out += f"#defmult1 {multiplicity}\n"
        out += f"#defunit1b {selectedUID2}\n"
        gcost = autocalc.scorechassiscombat(selectedUnit2)
        gcost = max(2, gcost)
        multiplicity2 = max(1, int(100 / gcost))
        out += f"#defmult1b {multiplicity2}\n"
        detailstext += f"Global PD commander: {chosenCommander.name}\n"
        detailstext += f"National PD units (unforted at 20+ PD, or forts at any PD): {multiplicity}x {selectedUnit.name} per 10 PD," \
                       f" {multiplicity2}x {selectedUnit2.name} per 10 PD\n"

        # Fort 20+ PD: #defcom2, #defunit2, #defunit2b
        commanderUID, selectedUID, selectedUnit, selectedUID2, selectedUnit2, chosenCommander = self.selectTwoUnitsAndOneCompatibleCommander(
             44, (28, 38))
        out += f"#defcom2 {commanderUID}\n"
        out += f"#defunit2 {selectedUID}\n"
        gcost = autocalc.scorechassiscombat(selectedUnit)
        gcost = max(2, gcost)
        multiplicity = max(1, int(100 / gcost))
        out += f"#defmult2 {multiplicity}\n"
        out += f"#defunit2b {selectedUID2}\n"
        gcost = autocalc.scorechassiscombat(selectedUnit2)
        gcost = max(2, gcost)
        multiplicity2 = max(1, int(100 / gcost))
        out += f"#defmult2b {multiplicity2}\n"
        detailstext += f"PD commander for forts at 20+ PD: {chosenCommander.name}\n"
        detailstext += f"National PD units (forts at 20+ PD): {multiplicity}x {selectedUnit.name} per 10 PD," \
                       f" {multiplicity2}x {selectedUnit2.name} per 10 PD\n"

        # Start units: #startcom, #startunittype1, #startunitnbrs1, #startunittype2, #startunitnbrs2, #startscount
        # Once again, need one commander compatible with two unit types
        commanderUID, selectedUID, selectedUnit, selectedUID2, selectedUnit2, chosenCommander = self.selectTwoUnitsAndOneCompatibleCommander(
            44, (28, 38))

        out += f"#startcom {commanderUID}\n"
        out += f"#startunittype1 {selectedUID}\n"
        gcost = autocalc.scorechassiscombat(selectedUnit)
        gcost = max(2, gcost)
        multiplicity = max(1, int(200 / gcost))
        out += f"#startunitnbrs1 {multiplicity}\n"
        out += f"#startunittype2 {selectedUID2}\n"
        gcost = autocalc.scorechassiscombat(selectedUnit2)
        gcost = max(2, gcost)
        multiplicity2 = max(1, int(200 / gcost))
        out += f"#startunitnbrs2 {multiplicity2}\n"
        detailstext += f"Starting commander: {chosenCommander.name}\n"
        detailstext += f"Starting units: {multiplicity}x {selectedUnit.name}, {multiplicity2}x {selectedUnit2.name}\n"

        # Scout.
        attempt = 0
        commandersToCheck = []
        scoutCmdrID = None
        while 1:
            attempt += 1
            commandersToCheck = self.possiblePDCommanders[:]
            if attempt > 3:
                scoutCmdrID = 426  # indie scout
                cmdr = unitinbasedatafinder.get(426)
                break
            for comID, cmdr in commandersToCheck:
                if attempt > 1 or getattr(cmdr, "stealthy", 0) > 0:
                    scoutCmdrID = comID
                    break
            if scoutCmdrID is not None:
                break
        out += f"#startscout {scoutCmdrID}\n"
        detailstext += f"Starting scout: {cmdr.name}\n"
        self.modcontent += out
        self.nationDescr += detailstext
