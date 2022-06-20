import argparse
import copy
import os
import random
import sys
import math
import traceback
import unitinbasedatafinder
import autocalc
import startsites
import utils
import naming
import struct
import nation
import re
import poptypes

from utils import HIGHEST_UNIT_ID_TO_MAKE_POOL_WITH, _writetoconsole, _listToWords, _recursiveshapesearch, \
    _getshrinkhpchain

ver = "0.0.1"


def generate(**options):
    numnations = options.get("numnations", 50)
    newpoptypes = options.get("newpoptypes", 1)
    modname = options.get("modname", "")
    utils.NATION_ID_START = options.get("startnationid", 120)
    utils.UNIT_ID_START = options.get("startunitid", 3550)
    utils.SITE_ID_START = options.get("startsiteid", 1510)
    fixedseeds = options.get("fixedseeds", "")
    print(f"Fixedseeds: {fixedseeds}")
    if len(fixedseeds) > 0:
        fixedseeds = fixedseeds.split(",")
        numnations = len(fixedseeds)
    else:
        fixedseeds = None
    if modname == "":
        modname = str(random.random())
    outfp = os.path.join(options.get("output", "./output"), f"NonsensicalNovelNations-{modname}.dm")

    with open("log.txt", "w", encoding="u8") as logfile:
        sys.stdout = logfile
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
        _writetoconsole(f"Loading unit data...")
        unitinbasedatafinder.loadAllUnitData()
        _writetoconsole("Building a valid unit pool...")
        unitpool = []
        for x in range(1, HIGHEST_UNIT_ID_TO_MAKE_POOL_WITH + 1):
            try:
                if x not in badunitids:
                    u = unitinbasedatafinder.get(x)
                    if u.unique <= 0 and u.growhp <= 0:
                        if getattr(u, "firstshape", 0) <= 0 and getattr(u, "homeshape", 0) <= 0:
                            unitpool.append(u)
            except ValueError:
                pass
        _writetoconsole(f"Unit pool contains {len(unitpool)} units...")

        seeds = []
        nationnames = []
        modcontent = ""
        with open(outfp, "w") as outf:
            outf.write('#modname "NonsensicalNovelNations-' + modname + '"' + "\n")
            if numnations > 0:
                outf.write("#disableoldnations\n")
                _writetoconsole("Beginning generation...")

                for nationidoffset in range(0, numnations):
                    # This does need to be a deep copy, otherwise pretender stuff will edit the reference in the master
                    # pool which carries over
                    pool = copy.copy(unitpool)
                    if fixedseeds is not None:
                        seed = int(fixedseeds.pop(0))
                    else:
                        seed = struct.unpack("<q", os.urandom(8))[0]
                    nationobj = nation.NationBuilder(pool, seed, **options)
                    modcontent +=  nationobj.modcontent
                    nationnames.append(nationobj.nationname)
                    seeds.append(nationobj.seed)
                    _writetoconsole(f"Created nation {nationobj.nationname}: {nationidoffset + 1} of {numnations},"
                                    f" with seed {seed}...")
                outf.write('#descripion "A NonsensicalNovelNation pack, generated with version ' + ver + '."' + "\n")
                for i, nationname in enumerate(nationnames):
                    seed = str(seeds[i])
                    outf.write(f"-- Nation {nationname} generated with seed {seed}\n")
                outf.write(modcontent)

            if options.get("equipmentresourcecosts", 1):
                _writetoconsole("Beginning equipment resource calculation...")
                outf.write(autocalc.equipmentresourcecosts())

            if newpoptypes:
                _writetoconsole("Beginning new independents...")
                poptypecontent = poptypes.newpoptypes(copy.copy(unitpool), **options)
                outf.write(poptypecontent)

            _writetoconsole(f"Finished writing {outfp}!")




# Stuff to make this usable on a non-CL basis
class Option(object):
    def __init__(self, optname, help="", type=None, default=None, nargs=None, action=None):
        self.optname = optname
        self.type = type
        self.help = help
        self.default = default
        self.nargs = nargs
        self.action = action

    def toArgparse(self, parser):
        kwargs = {"help":self.help, "default":self.default}
        if self.type is not None:
            kwargs["type"] = self.type
        if self.nargs is not None:
            kwargs["nargs"] = self.nargs
        if self.action is not None:
            kwargs["action"] = self.action
        parser.add_argument(self.optname, **kwargs)

    def askInConsole(self):
        print("\n\n-----------------------")
        s = self.help
        if self.type is bool:
            s += " [y/n]"
        print(s)
        if self.type is bool:
            if self.default:
                print("Default: y")
            else:
                print("Default: n")
        elif self.type in [float, int]:
            print(f"Default: {self.default}")
        else:
            if self.default is None:
                print("Default: <NONE>")
            else:
                print(f"Default: {self.default}")
        print("")
        r = input()
        if r.strip() == "":
            return self.default
        if self.type is float:
            try:
                return float(r)
            except:
                print("Could not convert input to a number. Try again!\n")
                return self.askInConsole()
        if self.type is int:
            try:
                return int(r)
            except:
                print("Could not convert input to a number. Try again!\n")
                return self.askInConsole()
        if self.type is bool:
            if r.lower() == "y":
                return True
            elif r.lower() == "n":
                return False
            print("Please enter y or n.")
            return self.askInConsole()

        else:
            return r


def main():
    opts = []

    opts.append(
        Option("-modname", help="Name of the mod to generate. If left blank, a string of random numbers is used instead", type=str,
               default=""))
    opts.append(
        Option("-numnations", help="Number of nations to generate. Ignored if a seed list was provided", type=int,
               default=20))
    opts.append(
        Option("-numunits", help="Number of non-commander units per nation", type=int,
               default=15))
    opts.append(
        Option("-numcommanders", help="Number of commander units per nation", type=int,
               default=10))
    opts.append(
        Option("-pretendercount", help="Number of pretender options per nation", type=int,
               default=25))
    opts.append(
        Option("-maxtotalpathspernation", help="Maximum total sum of all magic paths allowed on one nation,"
                                               " including randoms", type=int,
               default=25))
    opts.append(
        Option("-fixedseeds", help="A list of fixed seeds, separated by spaces, to create", type=str,
               nargs=None, action="store", default=""))
    opts.append(
        Option("-startnationid", help="Nation ID to start generating at", type=int,
               default=120))
    opts.append(
        Option("-startunitid", help="Unit ID to start generating at", type=int,
               default=3550))
    opts.append(
        Option("-startsiteid", help="Site ID to start generating at", type=int,
               default=1510))
    opts.append(
        Option("-output", help="Output folder", type=str,
               default="./output"))



    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(prog=f"NonsensicalNovelNations v{ver}",
                                         description="Creates Dom 5 nations from random vanilla units",
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        for opt in opts:
            opt.toArgparse(parser)

        parser.add_argument("-run",
                            help="Pass this if you want to run command line mode and not be forced into guided interactive!",
                            default=None)
        args = parser.parse_args()
        generate(**vars(args))
    else:
        print(f"NonsensicalNovelNations v{ver}: Procedural generator for Dom5 nations, made up of random vanilla units!")
        print("This program can also be run from command line, pass -h for info.")
        print("Pressing ENTER without writing anything will accept the option's default value.")
        args = {}
        for opt in opts:
            # opt.optname has a leading hyphen
            args[opt.optname[1:]] = opt.askInConsole()

        print("Beginning generation...")
        try:
            generate(**args)
        except:
            _writetoconsole(traceback.format_exc())
            return
        #_writetoconsole("Complete. Press ENTER to exit.")
        _writetoconsole("Complete.")
        #input()


if __name__ == "__main__":
    print(sys.argv)
    main()
