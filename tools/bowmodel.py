"""Per-shot expected damage model for longbows on the INT Longbow build.
All item numbers from the DDO wiki Long Bow page / item pages. Build crit layers from the guide.
Assumptions (labelled in the guide):
 - 100% critical confirmation; Ranged Power ignored (equal factor for every bow)
 - flat per-hit add (INT mod x1.5, Deadly, misc) by level: see FLAT
 - on-hit dice counted once per hit, not multiplied by crits; on-crit dice counted on crits
 - Haste SLA always up: item Ranged Alacrity 20% is worth (1.20/1.15) over the hasted baseline
 - Doubleshot pool by level (Manyshot 1.5x BAB + feats/trees + kit) : see DSPOOL; a bow's own
   Doubleshot adds to the pool and shots = 1 + pool
"""
AVG = {'1d8':4.5,'1d8+2':6.5,'1d8+3':7.5,'1d10':5.5,'2d6':7.0}
FLAT = {8:8,12:12,15:15,18:18,22:28,25:35,29:42,31:45,35:55}
DSPOOL = {8:0.12,12:0.17,15:0.22,18:0.27,22:0.45,25:0.60,29:0.75,31:0.85,35:1.09}

def layers(level):
    n = 1               # natural 20
    mult = 3
    hi = 0              # extra multiplier on 19-20 rolls
    pbs = 1             # Point Blank Shot +1 (Threat range page)
    ic = 1 if level >= 9 else 0
    fey = 1 if level >= 14 else 0
    ca = 1 if level >= 21 else 0
    n += pbs + ic + fey + ca
    mult += fey + ca + (1 if level >= 27 else 0)   # Patience
    hi += (1 if level >= 24 else 0) + (1 if level >= 30 else 0)  # Overwhelming Critical, Lore of the Hunt
    return n, mult, hi, ic

def dmg(bow, level):
    W, die, enh, prof, elas, onhit, oncrit, ra, ds = bow
    n, mult, hi, ic = layers(level)
    if prof == 'base19': n += 1
    if prof == 'keen' and not ic: n += 1
    if elas: hi += 1
    base = W*AVG[die] + enh + FLAT[level]
    # rolls: 20 and 19 get 'hi'; other threat rolls get mult
    total = 0.0
    for roll in range(1,21):
        if roll > 20-n:   # threat
            m = mult + (hi if roll >= 19 else 0)
            total += m*base + oncrit
        else:
            total += base
    per_hit = total/20 + onhit
    speed = (1+ra)/1.15 if ra >= 0.15 else 1.0
    shots = 1 + DSPOOL[level] + ds
    return per_hit*speed*shots, n/20, per_hit

# name: (W, die, enh, profile, elasticity, onhit avg, oncrit avg, RA, DS)
BANDS = {
 8: [('Silver Longbow (base 19-20)',(1,'1d10',3,'base19',0,0,0,0,0)),
     ('Cheap Shot L5 (Keen, DS 3%)',(1,'1d8',2,'keen',0,0,0,0,0.03)),
     ('Sapphire Sting (Keen, RA 10%)',(1,'1d8',3,'keen',0,0,0,0.10,0)),
     ('Calamitous Longbow + Melancholic 2d6',(1,'1d8',4,'none',0,7,0,0,0))],
 12:[('Thornlord (Piercing 3, DS 2%)',(1,'1d8+2',5,'none',0,10.5,0,0,0.02)),
     ('Silver Longbow (base 19-20)',(1,'1d10',3,'base19',0,0,0,0,0)),
     ('Duergarcraft Longbow (L11)',(1.5,'1d8',5,'none',0,0,0,0,0)),
     ('Alchemical Longbow (L12)',(3,'1d8',5,'none',0,0,0,0,0))],
 15:[('Alchemical Longbow',(3,'1d8',5,'none',0,0,0,0,0)),
     ('Bow of Sinew (base 19-20, Elasticity)',(2,'1d8',5,'base19',1,0,0,0,0)),
     ('Twisted Willow (Keen, Elasticity)',(2,'1d8',5,'keen',1,0,0,0,0))],
 18:[('Alchemical Longbow',(3,'1d8',5,'none',0,0,0,0,0)),
     ('Shining Reliquary Longbow',(2.6,'1d8',5,'none',0,0,0,0,0)),
     ('Bow of Sinew (base 19-20, Elasticity)',(2,'1d8',5,'base19',1,0,0,0,0))],
 22:[('Epic Thornlord (base 19-20, Piercing 4, DS 3%)',(3,'1d8+2',6,'base19',0,14,0,0,0.03)),
     ('Thunder-Forged Alloy Longbow (L22)',(4.6,'1d8',9,'none',0,0,0,0,0)),
     ('Alchemical Longbow',(3,'1d8',5,'none',0,0,0,0,0))],
 25:[('Pinion (L23, base 19-20, RA 20%, Shrieking 2d6)',(3.6,'2d6',7,'base19',0,7,0,0.20,0)),
     ('Thunder-Forged Alloy Longbow',(4.6,'1d8',9,'none',0,0,0,0,0)),
     ('Epic Thornlord (base 19-20, Piercing 4, DS 3%)',(3,'1d8+2',6,'base19',0,14,0,0,0.03))],
 29:[('Aerania (Keen, RA 20%, Elasticity)',(4.8,'1d8+3',15,'keen',1,0,0,0.20,0)),
     ('Chaosbow (L28, RA 20%, Elasticity)',(4.6,'1d8+3',15,'none',1,0,0,0.20,0)),
     ('Pinion (base 19-20, RA 20%, Shrieking)',(3.6,'2d6',7,'base19',0,7,0,0.20,0)),
     ('Thunder-Forged Alloy Longbow',(4.6,'1d8',9,'none',0,0,0,0,0))],
 31:[('Eon (Keen, RA 20%)',(5.2,'1d8+3',15,'keen',0,0,0,0.20,0)),
     ('Legendary Thornlord (L30, Piercing 6, DS 4%)',(5,'1d8+2',15,'none',0,21,0,0,0.04)),
     ('Attuned Bone Longbow + Meltscale 15d6',(5.2,'1d8+3',15,'none',0,52.5,0,0,0)),
     ('Dinosaur Bone Longbow + Meltscale 15d6',(5.2,'1d8+2',15,'none',0,52.5,0,0,0)),
     ('Aerania (Keen, RA 20%, Elasticity)',(4.8,'1d8+3',15,'keen',1,0,0,0.20,0))],
 35:[('Aeon, the Blazing Reign (L33, RA 20%, Elasticity)',(5.6,'1d8+3',15,'none',1,0,0,0.20,0)),
     ('Legendary Cataclysmic + Woeful Shadow + Melancholic 16d6',(5.8,'1d8+3',15,'none',0,56,0,0.20,0.03)),
     ('Legendary Cataclysmic + Woeful Shadow (no Melancholic)',(5.8,'1d8+3',15,'none',0,0,0,0.20,0.03)),
     ('Legendary Demon\'s Arc (L35, Elasticity, Revel in Blood 16d6 on crit)',(6,'1d8+3',16,'none',1,0,56,0,0)),
     ('The Faceless Lord\'s Reach (L35, Elasticity, Revel in Blood)',(6,'1d8+3',16,'none',1,0,56,0,0)),
     ('Legendary Demogorgon\'s Sinew (L35, Elasticity)',(6,'1d8+3',16,'none',1,0,0,0,0)),
     ('Legendary Duergarcraft (L35, Piercing 7, Stabbing 16 on crit)',(6,'1d8+2',16,'none',0,24.5,56,0,0)),
     ('Legendary Oozing Hunger (L35, Acidic 7)',(6,'1d8+3',16,'none',0,24.5,0,0,0)),
     ('Longbow of the Undying Age (L33)',(6.1,'1d8+3',15,'none',0,0,0,0,0)),
     ('Legendary Ship-Siege Bow (L36, Keen, Fiery 7)',(6.2,'1d8+2',15,'keen',0,24.5,0,0,0))],
}
if __name__ == '__main__':
    for lvl, bows in BANDS.items():
        n, mult, hi, ic = layers(lvl)
        print(f"\n== Level {lvl}: build crit {21-n}-20 x{mult} (+{hi} on 19-20), flat +{FLAT[lvl]}, DS pool {DSPOOL[lvl]:.0%}")
        rows = sorted(((dmg(b,lvl), name) for name,b in bows), reverse=True)
        top = rows[0][0][0]
        for (d, pc, ph), name in rows:
            print(f"  {d:7.1f}  ({d/top*100:5.1f}%)  threat {pc:.0%}  per-hit {ph:6.1f}  {name}")
