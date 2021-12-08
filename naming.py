import random
import utils
import re

generalSitenameFormats = ["ADJECTIVE OBJECT", "OBJECT of DESCRIPTOR"]

adjectives = {
    "F":["Fiery", "Blazing", "Charring", "Infernal", "Combusting", "Flaming", "Glowing", "Scintillating", "Warming",
         "Ashen", "Scalding", "Burning", "Incendiary", "Crimson"],
    "A":["Breezy", "Airy", "Wafting", "Tempestuous", "Stormy", "Blowing", "Atmospheric", "Windy", "Thundery", "Shocking",
         "Electrified", "Stormy"],
    "W":["Wet", "Frozen", "Icy", "Watery", "Damp", "Dewy", "Frosty", "Flooded", "Aqueous", "Humid", "Moist", "Rainy",
         "Saturated", "Snowy", "Tidal"],
    "E":["Crystalline", "Rocky", "Earthen", "Stone", "Solid", "Mineral", "Metallic", "Sandy", "Basalt", "Marble",
         "Fossilised", "Golden", "Silver", "Igneous", "Iron", "Steel"],
    "S":["Astral", "Stellar", "Celestial", "Cosmic", "Lunar", "Solar", "Meteoric", "Heavenly", "Otherworldly", "Mystical",
         "Mindbending", "Moonlit", "Arcane", "Temporal", "Spacial", "Eclipsed"],
    "D":["Deathly", "Expired", "Dead", "Deceased", "Expired", "Lifeless", "Terminated", "Grave", "Black", "Dark", "Dusk",
         "Gloomy", "Haunted", "Dying", "Pestilent"],
    "N":["Natural", "Leafed", "Wooden", "Coral", "Druidic", "Thorned", "Flowering", "Herbal", "Primal", "Vigorous",
         "Evergreen"],
    "B":["Bloodsoaked", "Bloody", "Bloodsplattered", "Damned", "Demonic", "Horrific", "Sacrificial", "Flayed", "Tortured",
         "Deformed", "Sanguine"],
    "H":["Divine", "Sacred", "Holy", "Sanctified"],
}

objects = {
    "F": ["Pyre", "Blaze", "Conflagration", "Embers", "Flames", "Inferno", "Beacon", "Ruby", "Volcano"],
    "A": ["Diamond", "Breeze", "Tempest", "Storm", "Wind", "Gust", "Gale", "Squall"],
    "W": ["Blizzard", "Basin", "Aquifer", "Brook", "Iceberg", "Brine", "Canal", "Channel", "Drain", "Drizzle", "Geyser",
          "Ice", "Icicle", "Lake", "Lagoon", "Pond", "Pool", "Reservoir", "Snowstorm", "Rainshower", "Swamp",
          "Waterfall", "Wetlands", "River", "Sapphire", "Harbour"],
    "E": ["Agate", "Amethyst", "Aquamarine", "Coal", "Garnet", "Geode", "Gravel", "Jade", "Magma", "Mineral", "Boulder",
          "Rock", "Stone", "Sands", "Cave", "Mountain", "Cliffs"],
    "S": ["Pearl", "Star", "Eclipse", "Moonbeams", "Crater", "Lights", "Gateway", "Distortion", "Portal", "Maze", "Mirror",
          "Nexus"],
    "D": ["Bones", "Grave", "Tomb", "Battlefield", "Mausoleum", "Ruins", "Catacombs", "Gallows", "Sarcophagus"],
    "N": ["Emerald", "Forest", "Tree", "Oak", "Willow", "Yew", "Field", "Fungus", "Oasis", "Valley", "Woodland", "Grove",
          "Glen"],
    "B": ["Abattoir", "Slaughterhouse", "Torture Chamber", "Altar", "Circle", "Statue"],
    "H": ["Palace", "Monastery", "Shrine", "City", "Castle", "Cathedral", "Temple", "Halls", "Sanctum"],
}

descriptors = {
    "F": ["Arsonists", "Ashes", "Pyres", "Flames", "Fire", "Heat", "Ignition", "Pyromania", "Smoke", "Rubies"],
    "A": ["Diamonds", "Tempests", "Storms", "Winds", "Breezes", "Gusts", "Gales", "Zephyrs", "Thunder", "Lightning"],
    "W": ["Blizzards", "Icebergs", "Geysers", "Ice", "Icicles", "Lakes", "Lagoons", "Ponds", "Pools", "Seas",
          "Snowstorms", "Rainshowers", "Swamps", "Waterfalls", "Rivers", "Condensation", "Downpours", "Evaporation",
          "Humidity", "Hoarfrost", "Frost", "Precipitation", "Snow", "Streams", "Tides", "Water", "Waves", "Sapphires"],
    "E": ["Rock", "Sands", "Stones", "Minerals", "Basalt", "Marble", "Granite", "Clay", "Gold", "Silver", "Iron", "Steel",
          "Magma", "Caverns"],
    "S": ["Stars", "the Moon", "the Sun", "Meteors", "the Heavens", "The Void", "Time", "Space", "Beyond", "Insanity"],
    "D": ["Death", "Unlife", "Tombs", "Catacombs", "Darkness", "Dark Rites", "Ghouls", "Gloom", "Bones", "Ghosts",
          "the Necromancers", "Skulls", "Corpses", "Coffins", "the Lost", "Souls", "Doom", "Demise", "Shades", "Pestilence",
          "Disease", "the Dead"],
    "N": ["Emeralds", "Forests", "Life", "Trees", "Lives", "Oaks", "Acorns", "Fields", "Fungus", "Fertility", "Ivy",
          "the Wild", "the Land"],
    "B": ["Blood", "Slaves", "Slaughter", "Torture", "the Flayed", "Devils", "Demons", "Fiends", "Pain", "Agony",
          "Disfigurement", "Bloodstains", "Knives", "Murder"],
    "H": ["the Divine", "Sanctity", "Light", "Martyrs", "Revelations", "the Holy", "the Sacred", "Justice",
          "Righteousness"],
}

def getSiteName(paths):
    format = random.choice(generalSitenameFormats)
    adj = random.choice(adjectives[random.choice(paths)])
    obj = random.choice(objects[random.choice(paths)])
    descr = random.choice(descriptors[random.choice(paths)])
    out = format.replace("ADJECTIVE", adj)
    out = out.replace("OBJECT", obj)
    out = out.replace("DESCRIPTOR", descr)
    if out in utils.SITE_NAMES:
        return getSiteName(paths)
    return out

def pluraliseUnitName(unit):
    unitname = unit.name
    suffix = ""
    if " of" in unit.name:
        splitpoint = unitname.find(" of")
        suffix = unitname[splitpoint:]
        unitname = unitname[:splitpoint]
    if unitname[-1] == "y":
        unitname = unitname[:-1] + "ies"
    if unitname[-1] != "s":
        unitname += "s"
    unitname = unitname + suffix
    return unitname

epithets = [
 "ADJECTIVE Rise of the UNITTYPES",
 "ADJECTIVE Rule of the UNITTYPES",
 "ADJECTIVE Reign of the UNITTYPES",
 "ADJECTIVE Empire of the UNITTYPES",
 "ADJECTIVE Kingdom of the UNITTYPES",
 "ADJECTIVE Return of the UNITTYPES",
 "ADJECTIVE Age of the UNITTYPES",
 "ADJECTIVE Cult of the UNITTYPES",
 "Last of the UNITTYPES",
 "ADJECTIVE City of the UNITTYPES",
 "ADJECTIVE Monarchy of the UNITTYPES",
 "ADJECTIVE Era of the UNITTYPES",
 "Faith in UNITTYPES",
 "ADJECTIVE Sons of UNITTYPES",
 "ADJECTIVE Emergence of the UNITTYPES",
 "ADJECTIVE Arrival of the UNITTYPES",
 "ADJECTIVE Coming of the UNITTYPES",
 "ADJECTIVE UNITTYPES",
 ]

epithetsFixednames = [
    "ADJECTIVE Rise of UNITTYPE",
    "ADJECTIVE Rule of UNITTYPE",
    "ADJECTIVE Reign of UNITTYPE",
    "ADJECTIVE Empire of UNITTYPE",
    "ADJECTIVE Kingdom of UNITTYPE",
    "ADJECTIVE Return of UNITTYPE",
    "ADJECTIVE Cult of UNITTYPE",
    "ADJECTIVE City of UNITTYPE",
    "ADJECTIVE Monarchy of UNITTYPE",
    "ADJECTIVE Era of UNITTYPE",
    "ADJECTIVE Faith in UNITTYPE",
    "Sons of UNITTYPE",
    "ADJECTIVE Emergence of UNITTYPE",
    "ADJECTIVE Arrival of UNITTYPE",
    "ADJECTIVE Coming of UNITTYPE",
]

def getEpithet(unit, path, recursion=0):
    epithet = random.choice(epithets)
    adj = random.choice(adjectives[path])
    fixedname = getattr(unit, "fixedname", None)
    if isinstance(fixedname, str):
        epithet = random.choice(epithetsFixednames)
        epithet = epithet.replace("ADJECTIVE", adj)
        epithet = epithet.replace("UNITTYPE", fixedname)
    else:
        unitname = pluraliseUnitName(unit)
        epithet = epithet.replace("UNITTYPES", unitname)
        epithet = epithet.replace("ADJECTIVE", adj)

    if len(epithet) > 37:
        if recursion > 900:
            #raise ValueError(f"Couldn't produce a short enough epithet: path = {path} and unit = {unit.name}#{unit.origid}")
            return None
        return getEpithet(unit, path, recursion+1)

    return epithet

long = []
short = []
suffix = []

def getNationName():
    if len(long) == 0:
        with open("long.txt") as f:
            for line in f:
                long.append(line.strip())
        with open("short.txt") as f:
            for line in f:
                short.append(line.strip())
        with open("suffix.txt") as f:
            for line in f:
                suffix.append(line.strip())
    name = ""
    numpartsremaining = random.choice([2, 2, 3, 3, 3, 3, 4, 4, 4, 5])

    choiceIsShort = False
    while 1:
        if numpartsremaining == 1:
            name += random.choice(suffix)
            break
        if choiceIsShort:
            name += random.choice(short)
        else:
            name += random.choice(long)
        choiceIsShort = not choiceIsShort
        numpartsremaining -= 1
    name = name[0].upper() + name[1:]
    return name

if __name__ == "__main__":
    with open("out.txt", "w") as f:
        for x in range(0, 200):
            f.write(getNationName() + "\n")