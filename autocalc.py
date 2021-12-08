import math
import csv
import unitinbasedatafinder
import utils


# This is NOT Illwinter's implementation of autocalc.
# This is instead an implementation I made solely for the use of this mod, and it is probably quite wrong
# but Illwinter autocalc doesn't apply to units, and makes a mess of some of the more exotic commanders in the game...

# Attributes:

# shapechange

# shapechange	firstshape	secondshape	secondtmpshape	landshape	watershape	forestshape	plainshape	xpshape	prophetshape	homeshape

# paths (needs to link to final chassis a bit)

# enc	reinvigoration	bonusspells	F	A	W	E	S	D	N	B	H	rand1	nbr1	link1	mask1	rand2	nbr2	link2	mask2	rand3	nbr3	link3	mask3	rand4	nbr4	link4	mask4	prec	stormimmune	assassin	seduce	succubus	corrupt	forgebonus	fixforgebonus	mastersmith	alch	gemprod	researchbonus	drainimmune	inspiringres	crossbreeder	pathboost	allrange	leper	popkill	heretic	elegist		fixedresearch	divineins	lamialord	preanimator	dreanimator	magicboostF	magicboostA	magicboostW	magicboostE	magicboostS	magicboostD	magicboostN	magicboostALL	startitem	spreaddom	battlesum5	rand5	nbr5	link5	mask5	rand6	nbr6	link6	mask6	mummification	diseaseres	raiseonkill	raiseshape	sendlesserhorrormult	xploss	theftofthesunawe	incorporate	blessbers	dragonlord	slothresearch	elementrange	sorceryrange	firerange	astralrange	landreinvigoration	naturerange	reincarnation	foreignmagicboost	startaff	ivylord	spellsinger	magicstudy	alchemy	researchwithoutmagic	tmpastralgems	tmpfiregems	mountedbeserk	landenc	pathboostuw	pathboostland	percentpathreduction	randomspell	uncurableaffliction	stygianguide	end

armourdata = {}

drntable = {-15: 0.0076, -14:0.01, -13: 0.014, -12: 0.019, -11: 0.026, -10: 0.034, -9: 0.046, -8:0.062, -7:0.082,
            -6: 0.11, -5: 0.14, -4: 0.18, -3: 0.24, -2: 0.3, -1: 0.38, 0: 0.46, 1: 0.54, 2: 0.62, 3: 0.7, 4: 0.76,
            5: 0.82, 6: 0.86, 7:0.89, 8: 0.92, 9: 0.94, 10: 0.95, 11: 0.97, 12: 0.97, 13: 0.98, 14: 0.986, 15: 0.99}

def getdrn(value):
    realval = max(-15, min(15, int(value)))
    return drntable[realval]


def prot(armour, natural):
	return natural + armour - (natural*armour/40)

def getarmourprot(unit):
    global armourdata
    bodyprot = 0
    headprot = 0

    for x in range(1, 5):
        armid = getattr(unit, f"armor{x}", "")
        if armid != "":
            armdata = armourdata.get[armid]
            headprot += armdata.get(1, 0) + armdata.get(6, 0)
            bodyprot += math.floor((armdata.get(2, 0) + (armdata.get(3, 0) + armdata.get(4, 0)) / 2) / 2) + armdata.get(
                6, 0)

    armprot = math.floor(((bodyprot * 4) + headprot) / 5)
    return armprot

def _getpowermagnitude(unit):
    ret = 0.0
    if getattr(unit, "stormpower", 0) > 0:
        ret += getattr(unit, "stormpower", 0)/2
    if getattr(unit, "darkpower", 0) > 0:
        ret += getattr(unit, "darkpower", 0)/2
    if getattr(unit, "firepower", 0) > 0:
        ret += getattr(unit, "firepower", 0)
    if getattr(unit, "coldpower", 0) > 0:
        ret += getattr(unit, "coldpower", 0)
    if getattr(unit, "chaospower", 0) > 0:
        ret += getattr(unit, "chaospower", 0)
    if getattr(unit, "magicpower", 0) > 0:
        ret += getattr(unit, "magicpower", 0)
    if getattr(unit, "yearturn", 0) > 0:
        ret += getattr(unit, "yearturn", 0)/3
    return ret

def _getoffense(unit, realstr, realprec):

    maxammoturns = 0
    totalweapondmg = 0.0
    for weapon in unit.weapons:
        maxammoturns = max(weapon.getTurnsOfAmmo(), maxammoturns)
    for weapon in unit.weapons:
        isSecondary = False
        secondaryIsAlways = False
        thisweapondmg = 0.0
        while 1:
            dmg = None

            dmg = weapon.getdamage(realstr)

            # AN, affliction, charm/enslave, planeshift
            if weapon.spec & 128 or weapon.effect % 1000 in [11, 28, 29, 99, 108]:
                dmg = dmg
            elif weapon.spec & 64:
                dmg = (dmg - 5)
            else:
                dmg = (dmg - 10)

            if weapon.effect % 1000 in utils.DAMAGING_EFFECTS:
                pass
            elif weapon.effect % 1000 in [28, 29, 99, 108, 116, 121, 122]: # enslave, charm, petrify, planeshift
                dmg = 30 # or any swallowing effect
            elif weapon.effect % 1000 in [46]: # fatigue poison
                dmg /= 6
            elif weapon.effect % 1000 in [3]: # fatigue
                dmg /= 4
            elif weapon.effect % 1000 in [11]: # cause affliction
                dmg = 0
                if weapon.damage & 1: dmg += 3      #disease
                if weapon.damage & 2: dmg += 3      #curse
                if weapon.damage & 4: dmg += 3      #starvation
                if weapon.damage & 8: dmg += 40     #plague
                if weapon.damage & 16: dmg += 3     #lost weapon
                if weapon.damage & 32: dmg += 3     #curse of stones
                if weapon.damage & 64: dmg += 6     #entangle
                if weapon.damage & 128: dmg += 8    #rage
                if weapon.damage & 256: dmg += 5    #decay
                if weapon.damage & 512: dmg += 4    #burning
                if weapon.damage & 1024: dmg += 4   #sleep
                if weapon.damage & 4096: dmg += 8   #blind
                if weapon.damage & 8192: dmg += 8   #bleeding
                if weapon.damage & 16384: dmg += 6      #earthgrip
                if weapon.damage & 65536: dmg += 6      #firebonds
                if weapon.damage & 131072: dmg += 6     #falsefetters
                if weapon.damage & 262144: dmg += 3     #limp
                if weapon.damage & 524288: dmg += 3     #eyeloss
                if weapon.damage & 1048576: dmg += 3    #weakness
                if weapon.damage & 2097152: dmg += 3    #battlefright
                if weapon.damage & 4194304: dmg += 5    #mute
                if weapon.damage & 8388608: dmg += 3    #chestwound
                if weapon.damage & 16777216: dmg += 4   #cripple
                if weapon.damage & 33554432: dmg += 6   #feeblemind
                if weapon.damage & 67108864: dmg += 3   #nhwound
                if weapon.damage & 134217728: dmg += 5  #slimed
                if weapon.damage & 268435456: dmg += 4  #frozen
                if weapon.damage & 536870912: dmg += 5  #webbed
                if weapon.damage & 1073741824: dmg += 5 #armloss
                if weapon.damage & 2147483648: dmg += 10    #headloss
                if weapon.damage & 4294967296: dmg += 5     #shrunk
                if weapon.damage & 17179869184: dmg += 5    #confusion
                if weapon.damage & 1125899906842624: dmg += 5    #net
                if dmg == 0:
                    dmg = None
            elif weapon.effect % 1000 in [24, 32, 33, 73, 107, 75]:  # multiplicative damage types
                dmg *= 2
            elif weapon.effect % 1000 in [66]: # paralysis
                dmg /= 5
            elif weapon.effect % 1000 in [67]: # weakness
                pass
            elif weapon.effect % 1000 in [4]: # fear type one
                dmg = weapon.getdamage(realstr)
            elif weapon.effect % 1000 in [134]: # chain lightning
                dmg *= 3
            elif weapon.effect % 1000 in [128]: # stun
                dmg = 4
            else:
                print(f"Unknown effect number for weapon {weapon.name}")
                dmg = None


            if dmg is not None:

                if weapon.effect % 1000 == 109 or weapon.effect % 1000 == 139: # capped and capped poison
                    dmg /= 4

                dmg *= max(1, weapon.nratt)

                if weapon.effect % 1000 in [103, 104]: #life drain or partial
                    dmg *= 1.4
                if weapon.aoe > 0:
                    dmg *= (weapon.aoe * 1.25)
                if weapon.ammo > 0:
                    if weapon.getTurnsOfAmmo() < 5:
                        dmg *= (weapon.getTurnsOfAmmo() / 5)
                elif weapon.ammo == 0 and maxammoturns >= 10 and not isSecondary:
                    # You probably won't be using your melee so much
                    dmg *= 0.8

                range = weapon.getrange(realstr)
                if range > 1:
                    dmg *= getdrn((realprec + weapon.att) - (range/5))

                if weapon.spec & 4096: dmg /= 2  # MRN
                if weapon.spec & 17592186044416: dmg /= 1.5  # MR hard
                if weapon.spec & 16777216: dmg /= 3.5  # MR easy
                if weapon.spec & 1048576: dmg /= 2  # def negate
                if weapon.spec & 2305843009213693952: dmg /= 3 # MR for half

                # Lingering
                if weapon.effect > 1000:
                    dmg *= 2 * (weapon.effect // 1000)

                if weapon.effect % 1000 == 108: #petrify
                    dmg /= 3

                if isSecondary and (secondaryIsAlways == False):
                    dmg /= 2

            if dmg is not None:
                thisweapondmg += dmg

            if weapon.secondaryeffectalways is not None:
                weapon = weapon.secondaryeffectalways
                isSecondary = True
                continue

            if weapon.secondaryeffect is not None:
                weapon = weapon.secondaryeffect
                isSecondary = True
                secondaryIsAlways = False
                continue

            break

        dmgcontribution = thisweapondmg
        print(f"Weapon damage for {weapon.name} and parents was {thisweapondmg}, contribution = {dmgcontribution},"
              f"damage w/ str = {weapon.getdamage(realstr)}")
        totalweapondmg += dmgcontribution

    if getattr(unit, "trample", 0) > 0:
        wpnmult = 1/(8 - unit.size)
        totalweapondmg *= wpnmult
        print(f"Multiplied weapon damage by {wpnmult} due to trample")
        trampledmg = 2*unit.size * 9 # 5 + this, but is AP, plus extra for hit rate and aoe
        if getattr(unit, "trampleswallow", 0):
            trampledmg *= 1.5
        print(f"Trample added {trampledmg} dmg")
        totalweapondmg += trampledmg

    if getattr(unit, "raiseonkill", 0) > 0:
        mult = 1.0 + getattr(unit, "raiseonkill", 0)/300
        print(f"raiseonkill gave mult {mult}")
        totalweapondmg *= mult
    print(f"Final weapon dmg is {totalweapondmg}")
    return totalweapondmg

def _getrealdef(unit):
    realdef = int(getattr(unit, "def", 0) - (max(0, getattr(unit, "berserk")) * 0.8))
    shielddef = 0
    shieldprot = 0
    for armour in unit.armours:
        if armour.type == 4:  # shields
            shielddef += armour.def_ - armour.enc
            shieldprot += armour.zones[5]  # shield zone
    if shielddef != 0 or shieldprot != 0:
        additionaldef = 0.8 * shielddef * getdrn(shieldprot)
        print(f"Shield added {additionaldef} def, new def = {realdef + additionaldef}")
        realdef += additionaldef
        # shieldcost = realmaxhp/2 * shieldhitmult * getdrn(shieldprot)

    if getattr(unit, "mounted", 0) > 0:
        realdef += 3

    if getattr(unit, "illusion", 0) > 0:
        realdef += 3

    if getattr(unit, "eyeloss", 0) > 0:
        realdef += 2 + getattr(unit, "eyeloss", 0)/2

    if getattr(unit, "petrify", 0) > 0:
        realdef += 4 + getattr(unit, "petrify", 0)/2

    maxawe = max(0, getattr(unit, "awe", 0), getattr(unit, "sunawe", 0), getattr(unit, "animalawe", 0)/2,
                 getattr(unit, "haltheretic", 0)/2)
    if maxawe > 0:
        realdef += 3
        realdef += (maxawe / 2)

    if getattr(unit, "unsurr", 0) > 0:
        realdef += (getattr(unit, "unsurr", 0)/2)

    if getattr(unit, "slimer", 0) > 0:
        realdef += 2 + (getattr(unit, "slimer", 0)/2)

    if getattr(unit, "entangle", 0) > 0:
        realdef += 3 + (getattr(unit, "entangle", 0)/2)

    if getattr(unit, "mindslime", 0) > 0:
        realdef += 2 + (min(30, getattr(unit, "mindslime", 0))/4)

    if getattr(unit, "sleepaura", 0) > 0:
        realdef += 2 + (min(30, getattr(unit, "sleepaura", 0))/4)

    if getattr(unit, "invisible", 0) > 0:
        realdef += 5

    if getattr(unit, "unseen", 0) > 0:
        realdef += 3

    realdef += _getpowermagnitude(unit)

    return realdef

def _getrealatt(unit):
    realatt = int(unit.att + (max(0, getattr(unit, "berserk")) * 0.8))
    realatt -= unit.getOldAgePenalty()
    realatt += _getpowermagnitude(unit)
    return realatt

def _getrealstr(unit):
    realstr = int(unit.str + (max(0, getattr(unit, "berserk")) * 0.8))
    realstr -= unit.getOldAgePenalty()
    realstr += _getpowermagnitude(unit)
    return realstr

def _getrealenc(unit):
    realenc = int(unit.enc + (max(0, getattr(unit, "berserk")) * 0.5))
    realenc += unit.getOldAgePenalty()
    realenc -= getattr(unit, "reinvigoration", 0)
    realenc -= getattr(unit, "landreinvigoration", 0)
    realenc += max(0, getattr(unit, "landenc", 0))
    return realenc

def _getrealmor(unit):
    realmor = min(20, unit.mor + max(0, getattr(unit, "moralebonus", 0)))
    if getattr(unit, "berserk", 0) > 0:
        realmor = max(realmor, 20)
    return realmor

def _getrealmaxhp(unit):
    oldagepenalty = unit.getOldAgePenalty()
    realmaxhp = int(getattr(unit, "hp") * (1 - (oldagepenalty * 0.05)))

    if getattr(unit, "undying", 0) > 0:
        realmaxhp += getattr(unit, "undying", 0)

    totalregen = max(0, getattr(unit, "regeneration", 0)) + max(0, getattr(unit, "uwregen", 0))
    totalregen += max(0, getattr(unit, "incorporate", 0))
    if totalregen > 0:
        regenvalue = 0.3 * totalregen * 2 ** ((realmaxhp - 10)/40)
        print(f"Regen increased max hp from {realmaxhp} to {realmaxhp + regenvalue}")
        realmaxhp += regenvalue

    if getattr(unit, "ethereal", 0) > 0:
        realmaxhp *= 1.4

    return realmaxhp

def _getrealprot(unit, commandermode=False):
    natprot = getattr(unit, "prot", 0)
    invuln = getattr(unit, "invulnerable", 0)
    if invuln * 2/3 > natprot:
        natprot = invuln

    headprot = 0
    bodyprot = 0
    for armour in unit.armours:
        headprot += armour.zones.get(1, 0) + armour.zones.get(6, 0)
        bodyprot += math.floor((armour.zones.get(2, 0) + (armour.zones.get(3, 0) +
                                                          armour.zones.get(4, 0))/2)/2) + armour.zones.get(6, 0)
    armprot = math.floor(((bodyprot * 4) + headprot) / 5)
    if commandermode:
        armprot=max(12, armprot)
    realprot = natprot + armprot - (natprot * armprot/40)

    realprot += max(0, getattr(unit, "iceprot", 0)) * 1.5
    if getattr(unit, "slashres", 0) > 0:
        realprot *= 7/6
    if getattr(unit, "pierceres", 0) > 0:
        realprot *= 7/6
    if getattr(unit, "bluntres", 0) > 0:
        realprot *= 7/6
    return realprot

def _callForOtherShapes(unit, func, retval, altshapelist, donotaddsecondshapes=False):
    # Shape changers.
    # Things to consider the highest only
    altshapes = ["shapechange", "forestshape", "plainshape", "homeshape", "domshape", "notdomshape", "springshape",
                 "summershape", "autumnshape", "wintershape", "landshape", "watershape", "firstshape"]
    for attrib in altshapes:
        attribval = getattr(unit, attrib, 0)
        if attribval > 0:
            if attribval in altshapelist:
                continue
            altshapelist.append(attribval)
            newshapescore = func(unitinbasedatafinder.get(attribval), altshapelist)
            print(f"Using {retval} or {attrib}'s {newshapescore}, whichever is higher")
            retval = max(retval, newshapescore)

    # Things to add everything up
    addshapes = ["secondshape", "secondtmpshape"]
    for attrib in addshapes:
        attribval = getattr(unit, attrib, 0)
        if attribval > 0:
            if attribval in altshapelist:
                continue
            altshapelist.append(attribval)
            newshapescore = func(unitinbasedatafinder.get(attribval), altshapelist)
            if donotaddsecondshapes:
                print(f"Using {retval} or {attrib}'s {newshapescore}, whichever is higher")
                retval = max(retval, newshapescore)
            else:
                print(f"{retval} increased by {attrib}'s {newshapescore}")
                retval += newshapescore
    return retval

def _scorechassiscombat(unit, altshapes=None, commandermode=False):
    if altshapes is None:
        altshapelist = [unit.origid]
    else:
        altshapelist = altshapes
        print(f"Alt shape list: {altshapelist}")
    if unit.origid not in altshapelist:
        altshapelist.append(unit.origid)

    print(f"Begin chassis score for unit {unit.id}: {unit.name}")
    realmr = unit.mr
    realprec = unit.prec

    oldagepenalty = unit.getOldAgePenalty()
    realprec -= (oldagepenalty/2)

    realatt = _getrealatt(unit)
    realdef = _getrealdef(unit)
    realstr = _getrealstr(unit)
    realenc = _getrealenc(unit)
    realmor = _getrealmor(unit)
    realmaxhp = _getrealmaxhp(unit)

    # Initially I tried exponentials, but this made defstacked cav (eg vans) score really really highly: ~220g
    # This cubic function is less extreme, and also flips negative at (skill - 10) < 7

    #attdrn = 2 ** ((realatt - 10)/4)
    #defdrn = 2 ** ((realdef - 10)/4)
    #mrdrn = 2 ** ((realmr - 12)/5)
    #mordrn = 2 ** ((realmor - 10)/4)

    attdrn = 1 + 3 * ((realatt - 10)/15)**3 + (realatt - 10)/4
    defdrn = 1 + 3 * ((realdef - 10)/15)**3 + (realdef - 10)/4
    mrdrn = 1 + 3 * ((realmr - 12)/18)**3 + (realmr - 12)/4
    mordrn = 1 + 3 * ((realmor - 10)/18)**3 + (realmor - 12)/6

    attcost = math.sqrt(realmaxhp) * attdrn * 0.7
    defcost = math.sqrt(realmaxhp) * defdrn * 0.7
    if getattr(unit, "mounted", 0) > 0:
        print(f"Is mounted, increased def cost from {defcost}")
        # halved harass penalty
        defcost *= 3
    #strcost = 22/8 * realmaxhp * (realstr - 10)
    enccost = 1/10 * math.sqrt(realmaxhp) * (3 - realenc)
    mrcost = 1/5 * math.sqrt(realmaxhp) * mrdrn
    # This hopefully encompasses general ease of being repelled as well as routing issues
    morcost = 1/3 * math.sqrt(realmaxhp) * mordrn

    # This should be based primarily on weapons (so things with good weapons do a bit better, or supernatural abilities
    # like drake fire score really highly)

    offense = _getoffense(unit, realstr, realprec)
    # This is probably a bit disjointed, but men in robes with fists are REALLY bad
    if offense >= 0.0:
        offensedrn = offense ** 0.5
    else:
        offensedrn = offense
    offensecost = (realmaxhp ** 0.6) * offensedrn * 0.3
    print(f"Total offense cost: {offensecost}")
    print(f"Attcost: {attcost}")
    print(f"Defcost: {defcost}")
    print(f"Enccost: {enccost}")
    print(f"Mrcost: {mrcost}")
    print(f"Morcost: {morcost}")

    realprot = _getrealprot(unit, commandermode)

    #natprotval = 2 ** ((realprot - 15)/7)
    realprot -= 8
    natprotval = ((realprot/20)**3) + (realprot/16)

    natprotcost = math.sqrt(realmaxhp) * natprotval * 1
    print(f"protcost: {natprotcost}")

    retval = attcost + defcost + enccost + mrcost + morcost + natprotcost + offensecost

    if getattr(unit, "fear", 0) >= 5:
        fearval = 2 ** ((getattr(unit, "fear", 0) - 5)/15)
        fearcost = 1/2 * math.sqrt(realmaxhp) * fearval
        print(f"Fearcost: {fearcost}")
        retval += fearcost

    totalaura = max(0, getattr(unit, "heat", 0), getattr(unit, "cold", 0), getattr(unit, "uwheat", 0))
    if totalaura > 0:
        auraval = 2 ** ((totalaura - 3)/10)
        auracost = 1 / 2 * math.sqrt(realmaxhp) * auraval
        print(f"Temperature aura cost: {auracost}")
        retval += auraval

    totalaura = max(0, getattr(unit, "disbelieve", 0))
    if totalaura > 0:
        auraval = 2 ** ((totalaura - 3)/10)
        auracost = 1 / 2 * math.sqrt(realmaxhp) * auraval
        print(f"Disbelieve aura cost: {auracost}")
        retval += auraval

    if getattr(unit, "fireshield", 0) > 0:
        abilityval = 2 ** ((getattr(unit, "fireshield", 0) - 5)/5)
        abilitycost = 1/2 * math.sqrt(realmaxhp) * abilityval
        print(f"Fireshield cost: {abilitycost}")
        retval += abilitycost

    if getattr(unit, "curseluckshield", 0) > 0:
        abilityval = 2 ** ((getattr(unit, "curseluckshield", 0))/3)
        abilitycost = 1/3 * math.sqrt(realmaxhp) * abilityval
        print(f"curseluckshield cost: {abilitycost}")
        retval += abilitycost

    if getattr(unit, "horrormark", 0) > 0:
        abilityval = 2 ** ((getattr(unit, "horrormark", 0))/3)
        abilitycost = 1/3 * math.sqrt(realmaxhp) * abilityval
        print(f"horrormark cost: {abilitycost}")
        retval += abilitycost

    if getattr(unit, "uwfireshield", 0) > 0:
        abilityval = 2 ** ((getattr(unit, "fireshield", 0) - 5)/5)
        abilitycost = 1/2 * math.sqrt(realmaxhp) * abilityval
        print(f"uwfireshield cost: {abilitycost}")
        retval += abilitycost

    if getattr(unit, "acidshield", 0) > 0:
        abilityval = 2 ** ((getattr(unit, "acidshield", 0) - 5)/5)
        abilitycost = 1/2 * math.sqrt(realmaxhp) * abilityval
        print(f"acidshield cost: {abilitycost}")
        retval += abilitycost

    if getattr(unit, "poisonarmor", 0) > 0:
        abilityval = 2 ** ((getattr(unit, "poisonarmor", 0))/20)
        abilitycost = 1/2 * math.sqrt(realmaxhp) * abilityval
        print(f"Poisonbarbs cost: {abilitycost}")
        retval += abilitycost

    if getattr(unit, "poisonskin", 0) > 0:
        abilityval = 2 ** ((getattr(unit, "poisonarmor", 0))/30)
        abilitycost = 1/3 * math.sqrt(realmaxhp) * abilityval
        print(f"Poisonbarbs cost: {abilitycost}")
        retval += abilitycost

    if getattr(unit, "curseattacker", 0) > 0:
        abilityval = 2 ** ((getattr(unit, "curseattacker", 0))/2)
        abilitycost = 1/8 * math.sqrt(realmaxhp) * abilityval
        print(f"curseattacker cost: {abilitycost}")
        retval += abilitycost

    if getattr(unit, "banefireshield", 0) > 0:
        abilityval = 2 ** ((getattr(unit, "banefireshield", 0)-2)/4)
        abilitycost = 1/2 * math.sqrt(realmaxhp) * abilityval
        print(f"Banefireshield cost: {abilitycost}")
        retval += abilitycost

    if getattr(unit, "damagerev", 0) > 0:
        abilityval = 2 ** (getattr(unit, "damagerev", 0))
        abilitycost = math.sqrt(realmaxhp) * abilityval
        print(f"Damage reversal cost: {abilitycost}")
        retval += abilitycost

    if getattr(unit, "poisoncloud", 0) > 0:
        abilityval = 2 ** ((getattr(unit, "poisoncloud", 0) - 3) / 4)
        abilitycost = 1 / 2 * math.sqrt(realmaxhp) * abilityval
        print(f"Poisoncloud cost: {abilitycost}")
        retval += abilitycost

    if getattr(unit, "diseasecloud", 0) > 0:
        abilityval = 2 ** ((getattr(unit, "diseasecloud", 0) - 5)/5)
        abilitycost = 1/2 * math.sqrt(realmaxhp) * abilityval
        print(f"Diseasecloud cost: {abilitycost}")
        retval += abilitycost

    print(f"Total for {unit.name}#{unit.id} before mods: {retval}")
    if getattr(unit, "holy", 0) > 0 or getattr(unit, "autoblessed", 0) > 0:
        retval *= 1.7
    if getattr(unit, "undead", 0) > 0:
        retval *= 0.75
    if getattr(unit, "animal", 0) > 0:
        retval *= 0.85
    if getattr(unit, "coldblood", 0) > 0:
        retval *= 0.9
    if getattr(unit, "flying", 0) > 0 or getattr(unit, "blessfly", 0) > 0:
        retval *= 1.2
    if getattr(unit, "startingaff", 0) > 0: # these are all either blind or lost eye, in any case they are pretty bad
        retval *= 0.7
    if getattr(unit, "startaff", 0) > 0:
        retval *= 1.00 - (getattr(unit, "startaff", 0) * 0.003)
    if getattr(unit, "teleport", 0) > 0:
        retval *= 1.25
    if getattr(unit, "darkvision", 0) > 0:
        retval *= 1.00 + (getattr(unit, "darkvision", 0) * 0.0005)
    if getattr(unit, "ironvul", 0) > 0:
        retval *= 1.00 - (getattr(unit, "ironvul", 0) * 0.005)
    if getattr(unit, "spiritsight", 0) > 0:
        retval *= 1.02
    if getattr(unit, "singlebattle", 0) > 0:
        retval *= 0.5
    if getattr(unit, "stupid", 0) > 0:
        retval *= 0.7
    if getattr(unit, "ethereal", 0) > 0:
        retval *= 1.4
    if getattr(unit, "reform", 0) > 0:
        survivalchance = 1 - (getattr(unit, "reform", 0)/100)
        retval *= 1/survivalchance
    for resist in ["fireres", "coldres", "poisonres", "shockres"]:
        addition = retval * math.sqrt(max(0, getattr(unit, resist, 0.0))/2)/50
        print(f"{resist} added {addition}")
        retval += addition
    restotal = getattr(unit, "fireres", 0) + getattr(unit, "coldres", 0) + \
               getattr(unit, "poisonres", 0) + getattr(unit, "shockres", 0)
    retval *= 1.00 + (restotal * 0.005)
    if getattr(unit, "deathcurse", 0) > 0:
        retval += 8
    for x in range(1, 6):
        attrib = f"battlesum{x}"
        if getattr(unit, attrib, 0) > 0:
            addition = 2.5 * x * _scorechassiscombat(unitinbasedatafinder.get(getattr(unit, attrib, 0)))
            print(f"{attrib} added {addition}")
            retval += addition
    for x in range(1, 6):
        attrib = f"batstartsum{x}"
        if getattr(unit, attrib, 0) > 0:
            addition = x * _scorechassiscombat(unitinbasedatafinder.get(getattr(unit, attrib, 0)))
            print(f"{attrib} added {addition}")
            retval += addition

    for x in range(1, 10):
        attrib = f"batstartsum{x}d6"
        if getattr(unit, attrib, 0) > 0:
            addition = 3 * x * _scorechassiscombat(unitinbasedatafinder.get(getattr(unit, attrib, 0)))
            print(f"{attrib} added {addition}")
            retval += addition
    attrib = f"batstartsum1d3"
    if getattr(unit, attrib, 0) > 0:
        addition = 1.5 * x * _scorechassiscombat(unitinbasedatafinder.get(getattr(unit, attrib, 0)))
        print(f"{attrib} added {addition}")
        retval += addition

    if getattr(unit, "deathfire", 0) > 0:
        addition = 2*math.sqrt(getattr(unit, "deathfire", 0))
        print(f"deathfire added {addition}")
        retval += addition

    if getattr(unit, "deathdisease", 0) > 0:
        addition = 2*math.sqrt(getattr(unit, "deathdisease", 0))
        print(f"deathdisease added {addition}")
        retval += addition

    if getattr(unit, "deathparalyze", 0) > 0:
        addition = 2*math.sqrt(getattr(unit, "deathparalyze", 0))
        print(f"deathparalyze added {addition}")
        retval += addition

    retval = _callForOtherShapes(unit, _scorechassiscombat, retval, altshapelist)



    print(f"Total for {unit.name}#{unit.id} after mods: {retval}\n\n")
    return max(1, retval)

def _scorechassisnoncombat(unit, altshapes=None):
    if altshapes is None:
        altshapelist = [unit.origid]
    else:
        altshapelist = altshapes
    if unit.origid not in altshapelist:
        altshapelist.append(unit.origid)

    retval = 0.0

    if getattr(unit, "taxcollector", 0) > 0:
        retval += 1
    if getattr(unit, "patrolbonus", 0) > 0:
        retval += getattr(unit, "patrolbonus", 0)
    if getattr(unit, "nobadevents", 0) > 0:
        retval += getattr(unit, "nobadevents", 0)/5
    if getattr(unit, "leper", 0) > 0:
        attribval = getattr(unit, "leper", 0)
        if getattr(unit, "stealthy", 0) > 0:
            retval += attribval
        else:
            retval -= attribval
    if getattr(unit, "resources", 0) > 0:
        retval += getattr(unit, "resources", 0)/10
    if getattr(unit, "iceforging", 0) > 0:
        retval += getattr(unit, "iceforging", 0)/10
    if getattr(unit, "castledef", 0) > 0:
        retval += getattr(unit, "castledef", 0)/5
    if getattr(unit, "siegebonus", 0) > 0:
        retval += getattr(unit, "siegebonus", 0)/10
    if getattr(unit, "defenceorganiser", 0) > 0:
        retval += getattr(unit, "defenceorganiser", 0)
    if getattr(unit, "supplybonus", 0) > 0:
        retval += getattr(unit, "supplybonus", 0)/30
    if float(getattr(unit, "incunrest", 0)) > 0:
        attribval = float(getattr(unit, "incunrest", 0))
        if getattr(unit, "stealthy", 0) > 0:
            retval += attribval
        else:
            retval -= attribval
    if getattr(unit, "popkill", 0) > 0:
        attribval = getattr(unit, "popkill", 0)
        if getattr(unit, "stealthy", 0) > 0:
            retval += attribval/5
        else:
            retval -= attribval/10
    if getattr(unit, "heretic", 0) > 0:
        attribval = getattr(unit, "heretic", 0)
        if getattr(unit, "stealthy", 0) > 0:
            retval += attribval*6
        else:
            retval -= attribval*3
    if getattr(unit, "corpseeater", 0) > 0:
        retval += 30
    if getattr(unit, "spreaddom", 0) > 0:
        retval += getattr(unit, "spreaddom", 0) * 200
    if getattr(unit, "comslave", 0) > 0:
        retval += 40
    if getattr(unit, "stealthy", 0) > 0:
        retval += 1
    if getattr(unit, "heal", 0) > 0:
        retval += 1
    if getattr(unit, "noheal", 0) > 0:
        retval -= 1
    if getattr(unit, "bringeroffortune", 0) not in [0, -1]:
        retval += getattr(unit, "bringeroffortune", 0) * 10
    if getattr(unit, "falsearmy", 0) > 0 or getattr(unit, "falsearmy", 0) <= -2:
        retval += 1

    print(f"Noncombat chassis score: {retval}")
    retval = _callForOtherShapes(unit, _scorechassisnoncombat, retval, altshapelist)
    return retval

def _scoremiscunitonly(unit, score, altshapes=None):
    if altshapes is None:
        altshapelist = [unit.origid]
    else:
        altshapelist = altshapes
    if unit.origid not in altshapelist:
        altshapelist.append(unit.origid)

    retval = score

    if getattr(unit, "undisciplined", 0) > 0:
        retval *= 0.8
    if getattr(unit, "formationfighter", 0) > 0:
        retval *= 1.08
    if getattr(unit, "immobile", 0) > 0:
        retval *= 0.5
    if getattr(unit, "bodyguard", 0) > 0:
        retval *= 1.0 + (getattr(unit, "bodyguard", 0) * 0.02)
    if getattr(unit, "skirmisher", 0) > 0:
        retval *= 1.0 + (getattr(unit, "skirmisher", 0) * 0.04)

    callable = lambda x, y, z=score: _scoremiscunitonly(x, z, y)
    retval = _callForOtherShapes(unit, callable, retval, altshapelist, donotaddsecondshapes=True)
    print(f"Misc unit score: {retval}")
    return retval

def _scorechassiscmdronly(unit, score, altshapes=None):
    if altshapes is None:
        altshapelist = [unit.origid]
    else:
        altshapelist = altshapes
    if unit.origid not in altshapelist:
        altshapelist.append(unit.origid)

    retval = score

    if getattr(unit, "assassin", 0) > 0:
        retval += 80
    if getattr(unit, "seduce", 0) > 0:
        retval += 75
    if getattr(unit, "succubus", 0) > 0:
        retval += 70
    if getattr(unit, "corrupt", 0) > 0:
        retval += 120
    if getattr(unit, "beckon", 0) > 0:
        retval += 70
    if getattr(unit, "scalewalls", 0) > 0:
        retval += 20

    if getattr(unit, "hand", 0) == 0:
        retval *= 0.8
    if getattr(unit, "hand", 0) > 2:
        retval *= 1.2
    if getattr(unit, "head", 0) > 1:
        retval *= 1.05
    if getattr(unit, "head", 0) == 0:
        retval *= 0.9
    if getattr(unit, "body", 0) == 0:
        retval *= 0.8
    if getattr(unit, "foot", 0) == 0:
        retval *= 0.95
    if getattr(unit, "crownonly", 0) > 0:
        retval *= 0.95
    if getattr(unit, "immobile", 0) > 0:
        retval *= 0.8

    if getattr(unit, "spy", 0) > 0:
        retval += 15

    if getattr(unit, "onebattlespell", 0) > 0:
        spellid = getattr(unit, "onebattlespell", 0)
        if spellid == 66: # darkness
            retval += 100
        if spellid == 95: # swarm
            retval += 30
        if spellid == 70: #heat from hell (buer)
            retval += 100
        if spellid == 79: #rain
            retval += 50
        if spellid == 62: #foul vapors (telkhines)
            retval += 150

    callable = lambda x, y, z=score: _scorechassiscmdronly(x, z, y)
    retval = _callForOtherShapes(unit, callable, retval, altshapelist, donotaddsecondshapes=True)
    print(f"Cmdr chassis score: {retval}")
    return retval

def _scoremisccmdronly(unit, score, altshapes=None):
    if altshapes is None:
        altshapelist = [unit.origid]
    else:
        altshapelist = altshapes
    if unit.origid not in altshapelist:
        altshapelist.append(unit.origid)

    retval = score

    if getattr(unit, "autohealer", 0) > 0:
        retval += 15
    if getattr(unit, "autodishealer", 0) > 0:
        retval += 8
    if getattr(unit, "insane", 0) > 0:
        retval *= 1.0 - (getattr(unit, "insane", 0)/200)
    if getattr(unit, "shatteredsoul", 0) > 0:
        retval *= 1.0 - (getattr(unit, "shatteredsoul", 0)/200)
    gemprodstring = getattr(unit, "gemprod", "")
    gemprodtotal = 0
    if not isinstance(gemprodstring, int):
        while len(gemprodstring) > 0:
            curr = gemprodstring[:2]
            gemprodstring = gemprodstring[2:]
            gemprodtotal += int(curr[0])
        if gemprodtotal > 0:
            retval += 110 * gemprodtotal


    if getattr(unit, "makepearls", 0) > 0:
        retval += 5
    if getattr(unit, "carcasscollector", 0) > 0:
        retval += 5

    if getattr(unit, "summon", 0) > 0:
        unittype = getattr(unit, "summon", 0)
        qty = getattr(unit, "n_summon", 1)
        retval += unitscore(unitinbasedatafinder.get(unittype)) * 5 * qty

    if getattr(unit, "autosum", 0) > 0:
        unittype = getattr(unit, "autosum", 0)
        qty = getattr(unit, "n_autosum", 1)
        retval += unitscore(unitinbasedatafinder.get(unittype))  * 5 * qty

    if getattr(unit, "turmoilsummon", 0) > 0:
        unittype = getattr(unit, "turmoilsummon", 0)
        retval += unitscore(unitinbasedatafinder.get(unittype))  * 25 # assuming qty = 5

    if getattr(unit, "templetrainer", 0) > 0:
        unittype = getattr(unit, "templetrainer", 0)
        retval += unitscore(unitinbasedatafinder.get(unittype))  * 1

    if getattr(unit, "coldsummon", 0) > 0:
        unittype = getattr(unit, "coldsummon", 0)
        retval += unitscore(unitinbasedatafinder.get(unittype))  * 5 # assuming qty = 1

    if getattr(unit, "wintersummon1d3", 0) > 0:
        unittype = getattr(unit, "wintersummon1d3", 0)
        retval += unitscore(unitinbasedatafinder.get(unittype))  * 1/6

    if getattr(unit, "spreaddeath", 0) > 0:
        if getattr(unit, "stealthy", 0) > 0:
            retval += 20
        else:
            retval -= 20
    if getattr(unit, "spreadgrowth", 0) > 0:
        retval += 20
    if getattr(unit, "spreadchaos", 0) > 0:
        if getattr(unit, "stealthy", 0) > 0:
            retval += 10
        else:
            retval -= 10
    if getattr(unit, "spreadorder", 0) > 0:
        retval += 10
    if getattr(unit, "mason", 0) > 0:
        retval += 25
    if getattr(unit, "onisummon", 0) > 0:
        abilityvalue = getattr(unit, "onisummon", 0)/100
        onivalue = unitscore(unitinbasedatafinder.get(1836)) * 15
        retval += (abilityvalue * onivalue)
    if getattr(unit, "reanimpriest", 0) > 0:
        addition = (getattr(unit, "H", 0) * 40)
        for path in utils.MAGIC_PATHS:
            if max(0, getattr(unit, path, 0)) > 0 and path != "H":
                addition -= getattr(unit, path, 0) * 10
        addition = max(0, addition)
        retval += addition
    if getattr(unit, "slaver", 0) > 0:
        retval += 50
    if getattr(unit, "heathensummon", 0) > 0:
        retval += 50
    if getattr(unit, "plaguedoctor", 0) > 0:
        retval += 40
    if getattr(unit, "insanify", 0) > 0:
        retval += 80




    callable = lambda x, y, z=score: _scoremisccmdronly(x, z, y)
    retval = _callForOtherShapes(unit, callable, retval, altshapelist, donotaddsecondshapes=True)
    print(f"Misc cmdr score: {retval}")
    return retval

def _universalmultipliers(unit, altshapes=None):
    if altshapes is None:
        altshapelist = [unit.origid]
    else:
        altshapelist = altshapes
        print(f"Alt shape list: {altshapelist}")
    if unit.origid not in altshapelist:
        altshapelist.append(unit.origid)

    retval = 1.0
    reformtime = 3 + getattr(unit, "reformtime", 0)

    if getattr(unit, "domimmortal", 0) > 0:
        retval += 0.7
        if reformtime == 2:
            retval += 0.2
        if reformtime == 1:
            retval += 0.4

    if getattr(unit, "immortal", 0) > 0:
        retval += 1.5
        if getattr(unit, "immortalrespawn", 0) > 0:
            retval -= 0.8
        elif reformtime == 2:
            retval += 0.5
        elif reformtime == 1:
            retval += 1.0

    if getattr(unit, "homesick", 0) > 0:
        turnstodeath = 100/getattr(unit, "homesick", 0)
        retval -= max(1, 5-turnstodeath) * 0.2


    if getattr(unit, "horrordeserter", 0) > 0:
        retval -= getattr(unit, "horrordeserter", 0)/100

    if getattr(unit, "defector", 0) > 0:
        retval -= getattr(unit, "defector", 0)/70

    retval = _callForOtherShapes(unit, _universalmultipliers, retval, altshapelist, donotaddsecondshapes=True)

    return retval



# id	name	wpn1	wpn2	wpn3	wpn4	wpn5	wpn6	wpn7	armor1	armor2	armor3	armor4	rt	reclimit	basecost	rcost	size	ressize	hp	prot	mr	mor	str	att	def	prec	enc	mapmove	ap	ambidextrous	mounted	reinvigoration	leader	undeadleader	magicleader	startage	maxage	hand	head	body	foot	misc	crownonly	pathcost	startdom	bonusspells	F	A	W	E	S	D	N	B	H	rand1	nbr1	link1	mask1	rand2	nbr2	link2	mask2	rand3	nbr3	link3	mask3	rand4	nbr4	link4	mask4	holy	inquisitor	mind	inanimate	undead	demon	magicbeing	stonebeing	animal	coldblood	female	forestsurvival	mountainsurvival	wastesurvival	swampsurvival	cavesurvival	aquatic	amphibian	pooramphibian	float	flying	stormimmune	teleport	immobile	noriverpass	sailingshipsize	sailingmaxunitsize	stealthy	illusion	spy	assassin	patience	seduce	succubus	corrupt	heal	immortal	domimmortal	reinc	noheal	neednoteat	homesick	undisciplined	formationfighter	slave	standard	inspirational	taskmaster	beastmaster	bodyguard	waterbreathing	iceprot	invulnerable	slashres	bluntres	pierceres	shockres	fireres	coldres	poisonres	voidsanity	darkvision	blind	animalawe	awe	haltheretic	fear	berserk	cold	heat	fireshield	banefireshield	damagerev	poisoncloud	diseasecloud	slimer	mindslime	reform	regeneration	reanimator	poisonarmor	petrify	eyeloss	ethereal	ethtrue	deathcurse	trample	trampswallow	stormpower	firepower	coldpower	darkpower	chaospower	magicpower	winterpower	springpower	summerpower	fallpower	forgebonus	fixforgebonus	mastersmith	resources	autohealer	autodishealer	alch	nobadevents	event	insane	shatteredsoul	leper	taxcollector	gem	gemprod	chaosrec	pillagebonus	patrolbonus	castledef	siegebonus	incprovdef	supplybonus	incunrest	popkill	researchbonus	drainimmune	inspiringres	douse	adeptsacr	crossbreeder	makepearls	pathboost	allrange	voidsum	heretic	elegist	shapechange	firstshape	secondshape	secondtmpshape	landshape	watershape	forestshape	plainshape	xpshape	unique	fixedname	special	nametype	summon	n_summon	autosum	n_autosum	batstartsum1	batstartsum2	domsummon	domsummon20	raredomsummon	bloodvengeance	bringeroffortune	realm1	realm2	realm3	batstartsum3	batstartsum4	batstartsum5	batstartsum1d6	batstartsum2d6	batstartsum3d6	batstartsum4d6	batstartsum5d6	batstartsum6d6	turmoilsummon	coldsummon	scalewalls	deathfire	uwregen	shrinkhp	growhp	transformation	startingaff	fixedresearch	divineins	lamialord	preanimator	dreanimator	mummify	onebattlespell	fireattuned	airattuned	waterattuned	earthattuned	astralattuned	deathattuned	natureattuned	bloodattuned	magicboostF	magicboostA	magicboostW	magicboostE	magicboostS	magicboostD	magicboostN	magicboostALL	eyes	heatrec	coldrec	spreadchaos	spreaddeath	corpseeater	poisonskin	bug	uwbug	spreadorder	spreadgrowth	startitem	spreaddom	battlesum5	acidshield	drake	prophetshape	horror	enchrebate50p	latehero	sailsize	uwdamage	landdamage	rpcost	buffer	rand5	nbr5	link5	mask5	rand6	nbr6	link6	mask6	mummification	diseaseres	raiseonkill	raiseshape	sendlesserhorrormult	xploss	theftofthesunawe	incorporate	hpoverslow	blessbers	dragonlord	curseattacker	uwheat	slothresearch	horrordeserter	mindvessel	elementrange	sorceryrange	older	disbelieve	firerange	astralrange	landreinvigoration	naturerange	beartattoo	horsetattoo	reincarnation	wolftattoo	boartattoo	sleepaura	snaketattoo	appetite	astralfetters	foreignmagicboost	templetrainer	infernoret	kokytosret	addrandomage	unsurr	combatcaster	homeshape	speciallook	aisinglerec	nowish	bugreform	mason	onisummon	sunawe	spiritsight	defenceorganiser	invisible	startaff	ivylord	spellsinger	magicstudy	triplegod	triplegodmag	unify	triple3mon	yearturn	fortkill	thronekill	digest	indepmove	unteleportable	reanimpriest	stunimmunity	entangle	alchemy	woundfend	singlebattle	falsearmy	summon5	ainorec	researchwithoutmagic	slaver	autocompete	deathparalyze	adventurers	cleanshape	reqlab	reqtemple	horrormarked	changetargetgenderforseductionandseductionimmune	corpseconstruct	guardianspiritmodifier	isashah	iceforging	isayazad	isadaeva	blessfly	plant	clockworklord	commaster	comslave	minsizeleader	snowmove	swimming	stupid	skirmisher	ironvul	heathensummon	unseen	illusionary	reformtime	immortalrespawn	nomovepen	wolf	dungeon	graphicsize	twiceborn	aboleth	tmpastralgems	localsun	tmpfiregems	defiler	mountedbeserk	lanceok	startheroab	minprison	uwfireshield	saltvul	landenc	plaguedoctor	curseluckshield	pathboostuw	pathboostland	noarmormapmovepenalty	farthronekill	hpoverflow	indepstay	polyimmune	horrormark	deathdisease	allret	percentpathreduction	aciddigest	beckon	slaverbonus	carcasscollector	mindcollar	labpromotion	mountainrec	indepspells	enchrebate50	summon1	randomspell	deathpower	deathrec	norange	insanify	reanimator	defector	nohof	batstartsum1d3	enchrebate10	undying	moralebonus	uncurableaffliction	autoblessed	wintersummon1d3	stygianguide	end
pathcost_multipliers = {"enc":0.99, "reinvigoration":1.01, "bonusspells":1.2, "stormimmune":1.05, "stormpower":1.02,
                        "assassin":1.2, "seduce":1.03, "succubus":1.03, "corrupt":1.03, "forgebonus":1.01,
                        "fixforgebonus":1.1, "mastersmith":1.1, "alchemy":1.002, "allrange":1.1, "leper":0.98,
                        "popkill":0.999, "heretic":0.95, "blessbers":0.75, "elementrange":1.05, "sorceryrange":1.05,
                        "firerange":1.02, "astralrange":1.02, "landreinvigoration":1.01, "naturerange":1.02,
                        "reincarnation":1.01, "tmpastralgems":1.05, "tmpfiregems":1.05, "mountedberserk":0.9,
                        "landenc":0.99, "randomspell":0.99, "immobile":0.3}
pathcost_additions = {"researchbonus":4, "crossbreeder":0.3, "lamialord":0.5, "dragonlord":1, "slothresearch":6,
                      "ivylord":1, "magicstudy":8, "stygianguide":0.05, "elegist":7, "fixedresearch":2,
                      "dreanimator":2, "inquisitor":7, "douse":5}

PATH_LEVEL_EXPONENT = 1.3

def commander(unit, forTempUnits=False):
    # Stuff to consider:
    # paths
    # leadership
    # chassis
    # standalone abilities (eg reanimator priest)
    print(f"Begin commander autocalc for {unit}")
    unloadedPaths = unit.unloadRandomPaths()
    for path in utils.MAGIC_PATHS:
        if getattr(unloadedPaths, f"magicboost{path}", 0) != 0:
            setattr(unloadedPaths, path, getattr(unloadedPaths, path, 0.0) + getattr(unloadedPaths, f"magicboost{path}", 0))
    for attrib in ["foreignmagicboost", "pathboostland", "pathboostuw", "magicboostALL"]:
        if getattr(unloadedPaths, attrib, 0) != 0:
            for path in utils.MAGIC_PATHS:
                if getattr(unloadedPaths, path, 0) > 0:
                    setattr(unloadedPaths, path, getattr(unloadedPaths, path) + getattr(unloadedPaths, attrib))

    pathpoints = 0.0
    for path in utils.MAGIC_PATHS:
        if path != "H":
            addition = max(0.0, getattr(unloadedPaths, path, 0.0)) ** PATH_LEVEL_EXPONENT
            pathpoints += addition
            print(f"Path {path} added {addition} pathpoints")
        else:
            addition = max(0.0, getattr(unloadedPaths, "H", 0.0)/3)
            pathpoints += addition
            print(f"Path {path} added {addition} pathpoints")
    # h1 gets +1
    if pathpoints > 0.0:
        pathpoints = max(1.0, pathpoints)
    path_cost = 30 * pathpoints
    print(f"Base path cost: {path_cost}: has {pathpoints} pathpoints")

    for attrib, value in pathcost_additions.items():
        attribval = getattr(unit, attrib, 0.0)
        if attribval != -1 and attribval != 0 and attribval != 0.0:
            addition = attribval * value
            path_cost += addition
            print(f"Attrib {attrib} flat adds {addition}")
    for attrib, value in pathcost_multipliers.items():
        attribval = getattr(unit, attrib, 0.0)
        if attribval != -1 and attribval != 0 and attribval != 0.0:
            magnitude = abs(attribval)
            mult = 1.0
            for x in range(0, magnitude):
                mult = mult * value
            path_cost = mult * path_cost
            print(f"Attrib {attrib} multiplies by {mult}, now {path_cost}")

    if getattr(unit, "berserk", 0) > 0: # the magnitude of berserk doesn't matter
        path_cost *= 0.8
    if getattr(unit, "startitem", 0) > 0:
        startitem = getattr(unit, "startitem")
        if startitem in [410, 411, 412]: #dragon pearls
            path_cost += 40
        if startitem == 269: # slave collar
            path_cost = 0

    path_cost = max(0.0, path_cost)
    print(f"path cost before chassis tweak: {path_cost}")


    leadership_cost = max(0.0, getattr(unit, "leader", 0)) * 0.1
    leadership_cost += max(0.0, getattr(unit, "waterbreathing", 0)) * 0.1
    leadership_cost += max(0.0, getattr(unit, "inspirational", 0)) * 10
    leadership_cost += max(0.0, getattr(unit, "taskmaster", 0)) * 3
    leadership_cost += max(0.0, getattr(unit, "beastmaster", 0)) * 3
    leadership_cost += max(0.0, min(getattr(unit, "leader", 0), getattr(unit, "sailingshipsize", 0))) * 0.002
    print(f"Leadership cost: {leadership_cost}")

    if not forTempUnits:
        chassis_cost = 10 + _scorechassiscombat(unit, commandermode=True) + _scorechassisnoncombat(unit)
        chassis_cost = _scoremisccmdronly(unit, chassis_cost)
        chassis_cost = _scorechassiscmdronly(unit, chassis_cost)
    else:
        chassis_cost = 10 + _scorechassiscombat(unit, commandermode=True)

    print(f"chassis cost: {chassis_cost}")
    mult = chassis_cost / 300
    path_cost += (path_cost * mult)
    print(f"added path cost multiplied by {mult}, now {path_cost}")

    universalmult = _universalmultipliers(unit)
    print(f"universal mult: {universalmult}")

    if not forTempUnits:
        retval = (path_cost + chassis_cost + leadership_cost)*universalmult
    else:
        retval = (path_cost + chassis_cost + leadership_cost)
    retval = int(round(retval, 0))
    print(f"Final cmdr score: {retval}\n\n\n")
    return max(1, retval)


def unit(unit):
    chassis = _scorechassiscombat(unit) + _scorechassisnoncombat(unit)
    chassis = _scoremiscunitonly(unit, chassis)
    universalmult = _universalmultipliers(unit)
    print(f"universal mult: {universalmult}")
    retval = chassis * universalmult
    retval = int(round(retval, 0))
    print(f"Final unit score: {retval}\n\n\n")
    return max(1, retval)

unitscore = unit
