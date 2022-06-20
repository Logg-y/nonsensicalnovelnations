import sys
import autocalc
import math
import unitinbasedatafinder

SITE_ID_START = 1510
NATION_ID_START = 120
HIGHEST_UNIT_ID_TO_MAKE_POOL_WITH = 3600
UNIT_ID_START = 3700

MAGIC_PATHS = ["F", "A", "W", "E", "S", "D", "N", "B", "H"]
REAL_PATH_NAMES = {"F":"Fire", "A":"Air", "W":"Water", "E":"Earth", "S":"Astral", "D":"Death", "N":"Nature", "B":"Blood",
                   "H":"Holy"}

SITE_NAMES = []

DAMAGING_EFFECTS = [2,
7,
24,
32,
33,
56,
73,
74,
75,
96,
103,
104,
105,
106,
107,
109,
122,
134,
139,
142]


def _writetoconsole(line):
    """Because PyInstaller and PySimpleGUI don't play nice unless specifying STDIN as well, I had to make
    this be converted to exe with --window to avoid the console coming up.
    For some reason after doing that, sys.stderr has to be flushed after every line to allow the GUI process
    to pick it up"""
    if not line.endswith("\n"):
        line += "\n"
    sys.stderr.write(line)
    sys.stderr.flush()


def _listToWords(list):
    out = ""
    if len(list) == 0:
        return ""
    if len(list) == 1:
        return list[0]
    for index, item in enumerate(list):
        if index == 0:
            out += item
            continue
        if len(list) - 1 == index:
            out += f" and {item}"
            return out
        else:
            out += f", {item}"


def _recursiveshapesearch(unit, output=None):
    if output is None:
        shapelist = [unit.origid]
    else:
        shapelist = output
    if unit.origid not in shapelist:
        shapelist.append(unit.origid)
    altshapes = ["shapechange", "forestshape", "plainshape", "homeshape", "domshape", "notdomshape", "springshape",
                 "summershape", "autumnshape", "wintershape", "landshape", "watershape", "firstshape", "secondshape",
                 "secondtmpshape"]
    for shape in altshapes:
        attribval = getattr(unit, shape, 0)
        if attribval > 0:
            if attribval in shapelist:
                continue
            shapelist.append(attribval)
            shapelist = _recursiveshapesearch(unitinbasedatafinder.get(attribval), shapelist)
    return shapelist


def _getshrinkhpchain(unit):
    for attrib in ["shrinkhp", "xpshape", "labpromotion"]:
        attribval = getattr(unit, attrib, 0)
        if attribval > 0:
            return [attribval] + _getshrinkhpchain(unitinbasedatafinder.get(attribval))
    return []


def modCommandsForNewUnit(unit, iscom=False, additionalModCmds=""):
    global UNIT_ID_START
    "Prepare .dm mod commands for the given unit. Returns (mod commands, \
    primary ID (not secondshapes etc) of the copied unit)"
    out = ""
    returnval_unit_id = None
    allshapes = _recursiveshapesearch(unit)
    numberOfIDsNeededPerUnit = {}
    vanillaAltshapeIDsToNewIDs = {}
    for uid in allshapes:
        shrinkchain = _getshrinkhpchain(unitinbasedatafinder.get(uid))
        numberOfIDsNeededPerUnit[uid] = max(1, len(shrinkchain) + 1)

    for shape in allshapes:
        vanillaAltshapeIDsToNewIDs[shape] = UNIT_ID_START
        UNIT_ID_START += numberOfIDsNeededPerUnit[shape]

    additionalModCmds += unit.enforcePositiveGoldCost()

    for shape in allshapes:
        out += f"#selectmonster {vanillaAltshapeIDsToNewIDs[shape]}\n"
        out += f"#copystats {shape}\n"
        out += f"#copyspr {shape}\n"
        # Make it not a pretender
        if getattr(unit, "startdom", 0) > 0:
            out += f"#homerealm 9\n"
            out += f"#startdom 0\n"
        if unit.aquatic >= 0:
            out += "#amphibian\n"
        if unit.triplegod >= 0:
            out += "#triplegod 0\n"
        if unit.heatrec > -1:
            out += "#heatrec 0\n"
        if unit.coldrec > -1:
            out += "#coldrec 0\n"
        if not iscom:
            out += "#noslowrec\n"
        # latehero seemingly confers uniqueness so also needs to go
        if getattr(unit, "latehero", 0) > 0:
            out += "#latehero 0\n"
        out += f"#rcost {autocalc.unitrcost(unit)}\n"
        out += additionalModCmds

        out += f"#gcost {int(unit.gcost)}\n"
        if not iscom:
            # not clearing magic seems to inflate RP costs of mages
            out += "#clearmagic\n"
            # Rec point adjustment
            if unit.startage > 0 and math.sqrt(unit.startage * 4) > unit.gcost:
                out += f"#rpcost {int(unit.gcost + math.sqrt(unit.startage / 2))}\n"
        altshapes = ["shapechange", "forestshape", "plainshape", "homeshape", "domshape", "notdomshape",
                     "springshape",
                     "summershape", "autumnshape", "wintershape", "landshape", "watershape", "firstshape",
                     "secondshape",
                     "secondtmpshape"]
        unitForThisShape = unitinbasedatafinder.get(shape)
        for altshapeattrib in altshapes:
            attribval = getattr(unitForThisShape, altshapeattrib, 0)
            if attribval > 0:
                out += f"#{altshapeattrib} {vanillaAltshapeIDsToNewIDs[attribval]}\n"
        out += "#end\n"
        if returnval_unit_id is None:
            returnval_unit_id = vanillaAltshapeIDsToNewIDs[shape]
        if numberOfIDsNeededPerUnit[shape] > 1:
            out += f"-- This unit has {numberOfIDsNeededPerUnit[shape] - 1} shrinkhp or xpshapes that must follow it"
            for index, chainshape in enumerate(shrinkchain):
                shapeUnitObj = unitinbasedatafinder.get(chainshape)
                out += f"#selectmonster {vanillaAltshapeIDsToNewIDs[shape] + index + 1}\n"
                out += f"#copystats {chainshape}\n"
                out += f"#copyspr {chainshape}\n"
                out += f"#rcost {autocalc.unitrcost(unit)}\n"
                if getattr(shapeUnitObj, "latehero", 0) > 0:
                    out += "#latehero 0\n"
                if shapeUnitObj.aquatic >= 0:
                    out += "#amphibian\n"
                if shapeUnitObj.triplegod >= 0:
                    out += "#triplegod 0\n"
                # not clearing magic seems to inflate RP costs of mages
                if iscom:
                    out += f"#gcost {int(unit.gcost)}\n"
                else:
                    out += f"#gcost {int(unit.gcost)}\n"
                    out += "#clearmagic\n"
                    out += "#noslowrec\n"
                out += "#end\n"
    out += "\n\n"

    return (out, returnval_unit_id)