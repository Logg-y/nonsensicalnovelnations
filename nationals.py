import copy
import csv
import re

from typing import (
    Dict,
    List, Union,
)

spellids = []
weaponids = []
siteids = []
monsterids: List[int] = []
eventcodes = []
montagids = []
nationids = []

def read_mods(modstring):
    global monsterids, weaponids, spellids, eventcodes, montagids, siteids, nationids
    mods = modstring.strip().split(",")
    monsterids = [3499]
    weaponids = [799]
    siteids = [1499]
    spellids = [1299]
    eventcodes = [-299]
    montagids = [1000]
    nationids = [120]
    for mod in mods:
        mod = mod.strip()
        if mod == "":
            continue
        with open(mod, "r", encoding="u8") as f:
            for line in f:
                if "--" in line:
                    line = line[0:line.find("--")].strip()
                line = line.strip()
                if line == "": continue

                m = re.match("#newmonster (\\d+)", line)
                if m is None:
                    m = re.match("#selectmonster (\\d+)", line)
                if m is not None:
                    unitid = int(m.groups()[0])
                    print(f"Parsed newmonster {unitid}")
                    if unitid not in monsterids:
                        monsterids.append(unitid)
                elif line.startswith("#newmonster"):
                    newid = max(monsterids) + 1
                    monsterids.append(newid)

                m = re.match("#montag (\\d+)", line)
                if m is not None:
                    newid = int(m.groups()[0])
                    montagids.append(newid)
                    print(f"Parsed montag {newid}")

                m = re.match("#code (.+)", line)
                if m is None:
                    m = re.match("#code2 (.+)", line)
                if m is None:
                    m = re.match("#codedelay (.+)", line)
                if m is None:
                    m = re.match("#codedelay2 (.+)", line)
                if m is not None:
                    newid = int(m.groups()[0])
                    eventcodes.append(newid)
                    print(f"Parsed event code {newid}")

                m = re.match("#newspell (\\d+)", line)
                if m is None:
                    m = re.match("#selectspell (\\d+)", line)
                if m is not None:
                    newid = int(m.groups()[0])
                    spellids.append(newid)
                    print(f"Parsed spell {newid}")
                elif line.startswith("#newspell"):
                    newid = max(spellids) + 1
                    print(f"Parsed spell with implied id {newid}")
                    spellids.append(newid)

                m = re.match("#newweapon (\\d+)", line)
                if m is None:
                    m = re.match("#selectweapon (\\d+)", line)
                if m is not None:
                    newid = int(m.groups()[0])
                    weaponids.append(newid)
                elif line.startswith("#newweapon"):
                    newid = max(weaponids) + 1
                    weaponids.append(newid)

                m = re.match("#newsite\\W+(\\d+)", line)
                if m is None:
                    m = re.match("#selectsite\\W+(\\d+)", line)
                if m is not None:
                    newid = int(m.groups()[0])
                    if newid not in siteids:
                        siteids.append(newid)
                elif line.startswith("#newsite"):
                    newid = max(siteids) + 1
                    siteids.append(newid)

                m = re.match("#selectnation (\\d+)", line)
                if m is not None:
                    nationid = int(m.groups()[0])
                    print(f"Parsed selectnation {nationid}")
                    if nationid not in nationids:
                        nationids.append(nationid)

                m = re.match("#newnation", line)
                if m is not None:
                    newid = -1
                    while newid in nations:
                        newid -= 1
                    print(f"Parsed newnation, assigned id {newid}")
                    if newid not in nations:
                        nations[newid] = Nation(newid)
                    currentnation = nations[newid]


