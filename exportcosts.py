import autocalc
import unitinbasedatafinder
from utils import HIGHEST_UNIT_ID_TO_MAKE_POOL_WITH
import os
import re

def export():
    print(os.getcwd())
    with open("export.csv", "w") as f:
        f.write("id,name,unitcost,comcost,isbadunit\n")
        badunitids = []
        with open("badunits.txt", "r") as badunitfile:
            for line in badunitfile:
                if line.strip() == "":
                    continue
                m = re.match("(\d*)", line)
                if m is not None:
                    badunitids.append(int(m.groups()[0]))
                    print(f"Added {m.groups()[0]} as a bad unit...")
                else:
                    print(f"Warning: badunits.txt has unmatched line: {line}")
        unitinbasedatafinder.loadAllUnitData()


        for x in range(1, HIGHEST_UNIT_ID_TO_MAKE_POOL_WITH + 1):
            assigned = False
            unitcost = 0
            comcost = 0
            name = "???"
            if x % 100 == 0:
                print(f"{x} of {HIGHEST_UNIT_ID_TO_MAKE_POOL_WITH}...")
            try:
                u = unitinbasedatafinder.get(x)
                name = u.name
                if x not in badunitids:
                    if u.unique <= 0 and u.growhp <= 0:
                        if getattr(u, "firstshape", 0) <= 0 and getattr(u, "homeshape", 0) <= 0:
                            pass
                        else:
                            badunitids.append(x)
                    else:
                        badunitids.append(x)
                    unitcost = autocalc.unit(u)
                    comcost = autocalc.commander(u)
                    assigned = True
            except ValueError: # unit not found
                if x not in badunitids:
                    badunitids.append(x)
                pass
            f.write(f"{x},{name},{unitcost},{comcost},{1 if x in badunitids else 0}\n")


if __name__ == "__main__":
    export()