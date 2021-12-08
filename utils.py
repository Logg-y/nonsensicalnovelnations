import sys

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