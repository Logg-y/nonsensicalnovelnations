import utils

def effectiveWeaponDamage(weapon, realstr=None):
    isSecondary = False
    secondaryIsAlways = False
    thisweapondmg = 0.0
    while 1:
        dmg = None

        if realstr is not None:
            dmg = weapon.getdamage(realstr)

            # AN, affliction, charm/enslave, planeshift
            if weapon.spec & 128 or weapon.effect % 1000 in [11, 28, 29, 99, 108]:
                dmg = dmg
            elif weapon.spec & 64:
                dmg = (dmg - 5)
            else:
                dmg = (dmg - 10)
        else:
            dmg = weapon.damage

            # AN, affliction, charm/enslave, planeshift
            if weapon.spec & 128 or weapon.effect % 1000 in [11, 28, 29, 99, 108]:
                dmg = (dmg+3) * 2
            elif weapon.spec & 64:
                dmg = (dmg+3) * 1.5

        if weapon.effect % 1000 in utils.DAMAGING_EFFECTS:
            pass
        elif weapon.effect % 1000 in [28, 29, 99, 108, 116, 121, 122]:  # enslave, charm, petrify, planeshift
            dmg = 50  # or any swallowing effect
        elif weapon.effect % 1000 in [46]:  # fatigue poison
            dmg /= 6
        elif weapon.effect % 1000 in [3]:  # fatigue
            dmg /= 4
        elif weapon.effect % 1000 in [11]:  # cause affliction
            dmg = 0
            if weapon.damage & 1: dmg += 3  # disease
            if weapon.damage & 2: dmg += 3  # curse
            if weapon.damage & 4: dmg += 3  # starvation
            if weapon.damage & 8: dmg += 80  # plague
            if weapon.damage & 16: dmg += 3  # lost weapon
            if weapon.damage & 32: dmg += 3  # curse of stones
            if weapon.damage & 64: dmg += 20  # entangle
            if weapon.damage & 128: dmg += 8  # rage
            if weapon.damage & 256: dmg += 5  # decay
            if weapon.damage & 512: dmg += 4  # burning
            if weapon.damage & 1024: dmg += 15  # sleep
            if weapon.damage & 4096: dmg += 8  # blind
            if weapon.damage & 8192: dmg += 20  # bleeding
            if weapon.damage & 16384: dmg += 20  # earthgrip
            if weapon.damage & 65536: dmg += 20  # firebonds
            if weapon.damage & 131072: dmg += 20  # falsefetters
            if weapon.damage & 262144: dmg += 3  # limp
            if weapon.damage & 524288: dmg += 3  # eyeloss
            if weapon.damage & 1048576: dmg += 3  # weakness
            if weapon.damage & 2097152: dmg += 3  # battlefright
            if weapon.damage & 4194304: dmg += 5  # mute
            if weapon.damage & 8388608: dmg += 3  # chestwound
            if weapon.damage & 16777216: dmg += 4  # cripple
            if weapon.damage & 33554432: dmg += 6  # feeblemind
            if weapon.damage & 67108864: dmg += 3  # nhwound
            if weapon.damage & 134217728: dmg += 10  # slimed
            if weapon.damage & 268435456: dmg += 8  # frozen
            if weapon.damage & 536870912: dmg += 20  # webbed
            if weapon.damage & 1073741824: dmg += 5  # armloss
            if weapon.damage & 2147483648: dmg += 20  # headloss
            if weapon.damage & 4294967296: dmg += 5  # shrunk
            if weapon.damage & 17179869184: dmg += 10  # confusion
            if weapon.damage & 1125899906842624: dmg += 20 # net
            if dmg == 0:
                dmg = None
        elif weapon.effect % 1000 in [24, 32, 33, 73, 107, 75]:  # multiplicative damage types
            dmg *= 2
        elif weapon.effect % 1000 in [66]:  # paralysis
            dmg = 30
        elif weapon.effect % 1000 in [67]:  # weakness
            pass
        elif weapon.effect % 1000 in [4]:  # fear type one
            dmg = 8
        elif weapon.effect % 1000 in [134]:  # chain lightning
            dmg *= 3
        elif weapon.effect % 1000 in [128]:  # stun
            dmg = 4
        else:
            print(f"Unknown effect number for weapon {weapon.name}")
            dmg = None

        if dmg is not None:
            if weapon.effect % 1000 == 109 or weapon.effect % 1000 == 139:  # capped and capped poison
                dmg /= 4

            dmg *= max(1, weapon.nratt)

            if weapon.effect % 1000 in [103, 104]:  # life drain or partial
                dmg *= 1.4
            if weapon.aoe > 0:
                dmg *= (weapon.aoe * 1.4)


            if weapon.spec & 4096: dmg /= 2  # MRN
            if weapon.spec & 17592186044416: dmg /= 1.5  # MR hard
            if weapon.spec & 16777216: dmg /= 3.5  # MR easy
            if weapon.spec & 1048576: dmg /= 2  # def negate
            if weapon.spec & 2305843009213693952: dmg /= 3  # MR for half

            # Lingering
            if weapon.effect > 1000:
                dmg *= 2 * (weapon.effect // 1000)

            if weapon.effect % 1000 == 108:  # petrify
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
    return thisweapondmg