import utils
import weapon
import armour
from .common import effectiveWeaponDamage

# Automatically calculate resource costs for units and equipment.
# Currently Illwinter autocalc adds a bit to some units, but for the most part sloth 3 is a no-brain pick
# as "exotic" units typically cost 1 resource. This is due to having no equipment, or armour/weapons that have no
# resource cost defined due to not normally being on any recruitable chassis.

def calculateWeaponAdditionalRCost(weapon):
    if weapon.rcost > 0:
        return 0.0
    dmg = effectiveWeaponDamage(weapon)
    basedmg = max(0, dmg-5)
    basecost = basedmg ** 0.9
    print(f"Basecost for {weapon.name} = {basecost} from {basedmg} base dmg")

    # Stats
    if weapon.range <= 1:
        stattotal = weapon.att + weapon.def_
        if stattotal < 90:
            statcost = max(0, stattotal) ** 1.2
            print(f"Stat toal of {stattotal} adds {statcost}")
            basecost += statcost

    # Length takes a bit more resources, unless it can't be used to repel
    if weapon.spec & 137438953472:
        # This roughly doubles base cost for length 5 weapons
        basecost *= 1.0 + (weapon.len**2.2) / 30
        print(f"Basecost for {weapon.name} after length = {basecost}")

    # Unrepellable is good too
    if weapon.spec & 35184372088832:
        basecost *= 1.2
        print(f"Basecost for {weapon.name} after unrepellable = {basecost}")

    # So's magic
    if weapon.spec & 72057594037927936:
        basecost *= 2.5
        print(f"Basecost for {weapon.name} after magic damage = {basecost}")

    # Massive reduce for intrinsic
    if weapon.spec & 134217728:
        basecost *= 0.1
        print(f"Basecost for {weapon.name} after intrinsic = {basecost}")

    # AP/AN are in the damage calculator
    basecost = int(round(basecost, 0))
    return basecost

def calculateArmourAdditionalRCost(armour):
    if armour.rcost > 0:
        return 0.0
    # Tempted to say only prot and item type matter here
    # shield
    if armour.type == 4:
        # Complicated because parry exists
        parry = armour.def_ - armour.enc
        cost = (armour.prot*0.06)**3 * (parry*0.35)**2
    # body
    elif armour.type == 5:
        # 9 prot -> 3
        # 12 prot -> 7
        # 18 prot -> 17
        # 21 prot -> 25
        cost = (armour.prot * 0.17) ** 2.5
    # helm
    elif armour.type == 6:
        # A pretty steep curve.
        # 16 prot magical -> 3
        # 18 prot nonmagical -> 3
        # 21 prot nonmagical -> 5
        # 14 prot nonmagical -> 1
        cost = (armour.prot * 0.08) ** 3.3
    else:
        print(f"unknown armour type {armour.type} for {armour.name}#{armour.origid}")
        return 0

    cost = int(round(cost, 0))
    # I guess magic should probably add x%, but will try without and see how it goes
    print(f"Rcost for armour {armour.name} with prot {armour.prot} = {cost}, zones = {armour.zones}")
    return cost

def unitrcost(unit):
    if unit.rcost < 1 or unit.rcost > 1:
        return unit.rcost

    hptimesprot = unit.hp * unit.prot
    rcost = int(round(hptimesprot ** 0.5, 0))
    return rcost

def equipmentresourcecosts():
    out = ""
    for wpnid in range(0, 763):
        wpn = weapon.get(wpnid)
        rcost = calculateWeaponAdditionalRCost(wpn)
        if rcost > 0.0:
            out += f"#selectweapon {wpnid}\n"
            out += f"#rcost {rcost}\n"
            out += "#end\n\n"

    for armid in range(0, 251):
        arm = armour.get(armid)
        rcost = calculateArmourAdditionalRCost(arm)
        if rcost > 0.0:
            out += f"#selectarmor {wpnid}\n"
            out += f"#rcost {rcost}\n"
            out += "#end\n\n"

    return out