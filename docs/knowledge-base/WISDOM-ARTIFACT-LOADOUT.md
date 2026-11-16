# Wisdom-priority loadout with one Minor Artifact

Status: owner-authorized guide implementation, **provisional modeled recipe**.
This document does not claim a merge, deployment, global optimum or complete
mechanics certification. The owner requested the guide and ranked affixes use
the saved loadout data on 15 November 2026.

## One shared selection record

The [selection manifest](../../tools/fixtures/wisdom-loadout/selection.json)
supplies the complete current gear/craft/augment table, modeled values, exact
ranked-affix order and the guide's one-page rows. The small standard-library
builder renders those blocks at build time; the published page remains
self-contained and introduces no live optimizer/API dependency.

The source optimizer is `eddiefiggie/ddo-loadout-optimizer` at
`01e17c1675363458aee46f3765ed6f1b811eb8e3`; comparison guide base is
`5ded199eadbade29dcdb0c1eccfad4758a65c328` (build 11-09-26.5).
The catalog SHA256 is
`b779480ade9e41de8f0c1eeb554a7bd09060a300c8ceb67f6a80c5abfcad08cf`.
The actual Wisdom run finished 45 optimization stages in 271.998 seconds.
Its sole query change from the preceding controlled search is replacing
Dexterity with Wisdom at the same objective position (29 of 32).

The selected practical recipe is
`artifact-wisdom-canonical-spot-luck.json`, SHA256
`37e612b60744e9fb104fdfdc39295c88973568ba3affbd0646c8fe1eb6e73a4d`.
This is a manual derivative of that solve, not another optimal result. It rotates
equal typed craft buckets, fills the unused Chains Spot crafting slot, carries
the preceding practical socket layout forward and trades Festive CON +2 for
Good Luck +3. Raw solved CON 34 becomes practical modeled CON 32, with direct
saves and skills increased by 3. Spot +20 was model-only in that original
comparison. The new crafting addendum supports the Legendary skill-category
magnitude. The later .5 packet adds historical Slavers-family Competence
corroboration, but current-type continuity and calculator qualification remain
open.

## Selected scope and tradeoffs

- Exactly one Minor Artifact: Yeenoghu's Reign. Artifact-type bonuses alone do
  not satisfy the requirement. No new weapon/artifact filigree bonuses are added
  to the displayed gear totals; installed weapon filigrees and shared set/duplicate
  interactions still require reconciliation.
- Primary: Claws Enhancement WIS +15, gear WIS 18 and DEX 6. Celestial Sapphire's
  Nearly Finished ability choice is explicitly unused.
- Optional ring Enhancement DEX +13 would make gear DEX 19, changing no ordinary
  socket or other modeled stat. The selectable DEX recipe is corroborated, but
  its exact +13 is not independently verified. It is not selected or certified.
- No event/limited-time items except the owner's Festive ability-diamond
  exception. Screening is not a promise of ownership, auction stock or exact
  permanent acquisition for every augment. The owner separately accepted an
  [acquisition-evidence exception for HA63 only](DECISIONS.md#approved-acquisition-evidence-exception--15-november-2026):
  Randall Lyric is owner-reported, not independently verified. This accepts the
  procurement evidence gap without adding an event-item exception.
- Calamitous is pinned in the source run. The existing conditional Sinew option
  remains separate and was not solved. The fully filled outfit is ML36 even
  though the new Globe/Treatise bow fills no longer impose Defense +40's ML36.
- Four separate three-piece augment sets replace the old Monolith/Solar source
  arrangement: Dusk Raider, Quickblade, Perfect Silence and Tough Shields.
  Twelve set-augment copies occupy twelve physical sockets. The entire recipe
  occupies 34 of 34 sockets; no source or stacking certification follows from
  physical feasibility alone.

Versus the preceding artifact candidate, the primary recipe changes only
Claws DEX +15 to WIS +15; all other selected crafts and sockets are identical.
Versus Queen BASIC it replaces four equipped items (neck, belt, one ring and
bracers) and changes crafts/augments as shown in the manifest. It preserves the
modeled core offense while adding 8 Deadly, 1 imbue die and 3 flat sneak damage
relative to that guide baseline. These are gear differences, not measured DPS.
Fortification falls from 286 to 226; Acid/Electric Resistance 53 each and Improved
Earthen Guard are lost. It is not an across-the-board survivability upgrade.

## Ability and crafting cautions

For Wisdom-based Spot and Will, apply the ability modifier to the complete
typed score, not the gear subtotal. If a pre-existing Enhancement Wisdom source
has value E, the new whole-score gain is `max(15,E)-E`, assuming other inputs
remain fixed. Only in the no-overlap case does the full 15 translate to 7 or 8
modifier points. Direct Spot is 27 rather than Queen BASIC's 29, so the conditional
net gains are 7/8 versus the prior artifact kit and 5/6 versus Queen BASIC.
Existing buffs can reduce or eliminate that gain. DEX skills and AC likewise
need full-stack and armor-limit reconciliation. Base abilities and feat/skill
selections are unchanged; INT-based offense and Reflex retain their conditions.

An already-finished DEX Claws pair cannot be rerolled under the retained Nearly
Complete rule; a new pair and the recorded 25 Legendary Abyssal Gems are needed
for WIS. Chains must receive its separate Green-slot unlock before the assigned
set augment. Ownership, crafting funds and unlocked artifact slots are not assumed.

Correction to preceding comparison prose: Queen BASIC's Coldlight Runners have
Quality INT +3. The preceding practical artifact candidate and this one use
Quality CON +3 there, with Quality INT +3 supplied by Chains. Both original boots
crafts were therefore not preserved when moving from the guide baseline.

## Evidence boundary and next validation

The [evidence map](../../evidence/wisdom-loadout/README.md) retains the original
run/recipe identities, derivation, source grades, exact checks and limitations.
The practical recipe's 373 internal checks and the optional version's 381 checks
validate catalog construction and arithmetic, not live-game truth. The original
primary-loadout inventory contains 130 affix claims: 93 retained-source supported, 24 corroborated-only,
1 conflicting, 7 conditional/unvalued and 5 model-only. Those labels are not the
guide's stricter `verified` classification.

The [15 November hosted-browser addendum](../../evidence/wisdom-loadout/crafting-browser-2026-11-15.json)
now supports Glabrezu Insight INT +7 directly and the four Chains magnitudes
through the Legendary crafting table. Its evidence map distinguishes exact
item support from category mappings: Chains Fortification's Enhancement type
is a general-rule inference; Combustion is Equipment Fire Spell Power, not
weapon damage; Quality INT uses the Quality Attributes category; and Spot's
Competence type is still unverified for the selected Chains craft.

Build **11-15-26.3** integrated only Glabrezu's exact Insight INT +7 binding,
using the then-unchanged source/value/type validator. The component moved from
excluded to counted, but the complete Intelligence result remained withheld.
At that checkpoint, the other eight INT inputs remained excluded; no new
interaction rule or complete stat total was established. All four Chains
components stayed unknown and excluded.
The [integration record](../../evidence/wisdom-loadout/crafting-integration-2026-11-15.json)
distinguishes their recipe support from the remaining exact typed-effect and
applicability requirements. The targeted Spot check found a generic +20
Competence tooltip on Legendary Keylock Ring, not a finished Chains effect;
it cannot qualify this selected craft. A bounded Wiki search also did not
establish that binding, which is not proof that no source exists.

That is the preserved .3 checkpoint, not the latest qualification state.
Build **11-15-26.4** added the separately approved bounded multi-source proof
route. It qualified Chains **Equipment Combustion +142** and **Quality INT +3**
as source-supported recipe derivations, not finished-item tooltips. Separate
host/channel, Legendary recipe and category-definition records are bound with
their actual provenance. The [fresh Ability source](../../evidence/wisdom-loadout/recipe-proof-sources-2026-11-15.json)
explicitly supplies Intelligence membership and attributes/abilities terminology.

The 142 is a complete selected-gear Fire Spell Power contribution only. At the
.4 checkpoint, the INT result counted Glabrezu and Chains Quality but still had
seven excluded inputs and a newly exposed missing Insight/Quality interaction;
the complete total remained null. Fortification still lacked the premise that
this Slavers Prefix is in the general rule's standard-item class. Spot's exact
selected-craft type remained unsupported. Neither incomplete proof was promoted.

Original claim grades and previous source packets remain byte-identical historical
records. Current generated labels identify direct versus recipe-derived support.
At .4, only four of 76 complete level36 result objects changed; 72 stayed
identical, and all 76 level35 results were unchanged. Before that integration,
the real new engine also reproduced all 76 results on unchanged .3 data. The selected recipe,
priorities, numeric/core tuples and seven positive-interaction rules are unchanged;
the calculator changed only by the reviewed bounded qualification dispatcher.

### Historical .5 checkpoint: seven INT definitions

Build **11-15-26.5** adds the [seven-INT source packet](../../evidence/wisdom-loadout/int-evidence-sources-2026-11-15.json)
and binds seven previously excluded definitions through the unchanged direct
source path: Melancholic +15 Enhancement, Solar +4 Artifact, Lunar +4 Profane,
Festive +2, Dimlight +2 Exceptional, Globe +1 Exceptional and Celestial Sapphire's
native +2 Profane to all abilities. Separate host/socket checks support their
selected placement. No old observation is repaired, no other effect on those
hosts is automatically qualified, and Celestial's optional ability craft stays
empty.

The existing highest-of-type rule keeps Dimlight instead of Globe's INT and
Lunar instead of Celestial's INT. At this .5 checkpoint, the evidence integration
created no new INT or DPS gain. Mixed-type interaction evidence was incomplete,
so modeled gearINT37 did not become a certified combined total or character score.

The new Slavers observation supplies current recipe magnitudes and a source-linked
Legendary Five Rings image showing Spot +22 Competence. The image page displays
19 August 2016; its values and host differ from the selected current Chains +20
craft. That is stronger historical corroboration, not a direct current type
proof. Chains Spot and Fortification remain unknown/excluded, and their other
input/interaction gaps are unchanged. The [new integration receipt](../../evidence/wisdom-loadout/int-evidence-integration-2026-11-15.json)
separates this source support from actual software verification and release
status. The seven existing stacking rules, gear, priorities, numeric/core tuples
and original claim grades remain unchanged.

### Historical .6 checkpoint: bounded selected-gear INT37

The [stacking-source packet](../../evidence/wisdom-loadout/int-stacking-sources-2026-11-15.json)
adds the original audit's genuinely observed positive Tip179 clause and
Fortification paragraph. Build **11-15-26.6** appends only two rules. One admits
exactly ten pairs among the selected Enhancement15, Insight7, Quality3, Profane4
and Festive2 INT members; existing Artifact, Exceptional and same-type rules
remain literal. Seven definitions count and two are suppressed, deriving the
existing **+37 selected-gear INT at level36**. No extra INT, full-character score,
DPS gain or critical-range change is claimed.

Runtime completeness requires the unchanged entire nine-definition INT family
and real source bindings, including suppressed inputs. This prevents an omitted
or altered non-ten-pair member from turning a subset into a complete kit. The
new rule is not a universal different-types default. Its 2022 modification date,
2026 observation and same-family caveat are retained with the bounded
interpretation; no in-game test is claimed.

The separate fresh Enhancement/Insight Fortification rule does not classify
Chains' Prefix or qualify Queen; the older unobserved source stays unchanged.
Historical Five Rings Spot10/22 Competence images, image-page dates predating
the published Slave Lords release, and subsequent item normalization do not
establish current Chains Spot20 typing. Both Chains types remain unresolved.
Only two level36 INT result objects change; the other 74 and all76 level35
results are identical. Selected gear, Minor Artifact, priorities, model values,
original claim grades and exceptions remain unchanged. The
[current integration receipt](../../evidence/wisdom-loadout/int-stacking-integration-2026-11-15.json)
records software verification separately from source and live-game limits.

Optional ring DEX +13 remains an additional unselected gap. Skull CON +15 versus
+16, Queen's incomplete/relayed provenance and exact normal procurement of
Healing Amplification +63 remain visible. The owner has
accepted only the HA63 acquisition-evidence gap, so it no longer blocks retaining
that augment; it remains independently unverified and does not close any other
validation requirement. Live Wiki access was blocked during the original
comparison; the hosted browser worked during this follow-up. Its fresh access
windows do not repair missing original observation metadata. Public Wiki access
also does not establish local-guide rendering QA. Source-qualified item
definitions still require the current ledger's exact provenance and positive
interaction gates before counting.

**Historical recommendation:** The .6/.7 discussion below retains the then-open
Fortification classification and Spot type work. The .9 Chains integration
described later in this record supersedes those gear-family validation items.
The complete offensive/DPS and critical-profile questions remain open.

The subsequent [scoped offensive audit](../../evidence/wisdom-loadout/offensive-mechanics-2026-11-15.json)
supports the selected Flaming imbue's Fire Spell Power applicability and the
Emerald's conditional named-source die contribution. Current prose distinguishes
level30's 4d6/2d6 from 5d6/3d6 with the selected ML34 boots equipped. Those
documentary findings do not change calculator qualification or establish full
character damage, weapon-rider scaling, proc uptime or a current DPS winner.
Next validation should resolve the remaining Fortification classification, Spot
type, and complete offensive interactions/scenarios needed for DPS and
critical-profile claims. The selected INT interaction gap is closed only within
the .6 contract.
The original direct
typed-numeric-clause path is preserved for unrelated inputs; the approved
recipe-proof route is limited to four fixed Chains IDs and cannot infer a
stacking edge. Wider inference or different selected components would require
separate review. Five supported magnitudes are not five fully qualified effects
or a validated total-DPS gain. See the [historical recipe integration receipt](../../evidence/wisdom-loadout/recipe-proof-integration-2026-11-15.json)
and the [historical INT definition receipt](../../evidence/wisdom-loadout/int-evidence-integration-2026-11-15.json).

The historical bow model, previous snapshots and original retained captures
remain unchanged. Current generated sections must pass fresh semantic tests;
reversible predecessor tests preserve the prior records rather than certifying
the new selection. Publication requires its own exact-head checks and review.

## Historical .8 checkpoint — bounded Fortification/Spot evidence

The [fresh 16-observation register](../../evidence/wisdom-loadout/fort-spot-sources-2026-11-15.json)
narrows three of the preceding evidence gaps. Queen's own-item popup supports
its **84 Insight Fortification** definition through the actual label/description
association. The two selected augments supply **4 Morale** and **3 Luck** to
skill checks, and separate Skill/Spot evidence establishes their Spot
applicability. Only the exact Heroism/Luck Spot pair is added; the selected
items, model values and existing INT derivation are unchanged.

| Existing selected placement | Retained level boundary |
| --- | --- |
| Sapphire of Greater Heroism in Legendary Glabrezu Claw Pendant, Green socket index 1 | Augment ML28; host base ML35 |
| Sapphire of Good Luck +3 in Yeenoghu's Reign, Blue socket index 3 | Augment ML28; host base ML35; complete selected fills reach ML36 |

Both augments' own definitions permit those socket colors. The complete outfit
and current ledger applicability floor remain **level 36**; an augment's lower
minimum level does not bypass its host or the full kit. Documented compatibility
does not establish inventory, completed socketing or present acquisition.

The resulting supported subsets are **84 Fortification** and **7 direct Spot**.
Both complete family totals remain `null` because `chains-fortification` and
`chains-spot` remain unknown/excluded. Exact two-ID and three-ID family guards
retain those members. Conditional modeled 226 Fortification and 27 direct Spot
are still incomplete, and the original 130-claim grades and remaining Queen
relay limits are preserved. Whole-character Spot additionally requires ranks,
the modifier from actual total Wisdom and other applicable sources; gear Wisdom
18 and the supported direct subset do not establish a final skill score.

Yeenoghu's Reign remains the sole Minor Artifact. No equipment, craft, socket,
feat/AP choice, priority or historical model result changes; optional ring
DEX +13 remains unselected. The Festive-only event exception and the narrow
HA63 acquisition-evidence exception retain their original limits. This is a
bounded evidence integration, with actual verification recorded in the
[receipt](../../evidence/wisdom-loadout/fort-spot-integration-2026-11-15.json),
not a new optimizer run or additional character gain. The next unresolved
gear-evidence work is current selected-craft type support for both Chains rows
and the remaining Spot pair proofs, alongside the other previously retained
mechanics and acquisition gaps.

## Historical .9 checkpoint — Chains evidence integration

The [Chains type register](../../evidence/wisdom-loadout/chains-type-sources-2026-11-15.json)
closes the two selected-craft classification gaps recorded above. Retained Wiki
Legendary values, shared host applicability and Spot membership combine with
Nexus's exact Legendary Prefix Enhancement and Extra Competence definitions.
The Spot proof uses variant `0x7002C66B`, not the other same-named Bonus recipe.
Nexus's numeric fields are absent; the values are separate Wiki premises.
Its beta status and unestablished recipe-metadata origin/client version remain
part of the proof's limits. This is a bounded source derivation, not an
authenticated in-game item observation.

| Selected family at level 36 | Current evidence-gated sum |
| --- | --- |
| Fortification | Chains 142 Enhancement + Queen 84 Insight = 226% |
| Direct Spot | Chains 20 Competence + Heroism 4 Morale + Luck 3 Luck = +27 |
| Intelligence | Existing +37 selected-gear derivation, unchanged |

Only the two Chains/Heroism and Chains/Luck Spot interactions are added. The
existing Fortification and Heroism/Luck premises and exact family guards remain.
The complete kit still requires level 36; its level-35 results are incomplete.
These sums describe the same gear contributions and do not establish a
whole-character skill score, trap success, damage reduction or additional gain.

The Wisdom selection, Yeenoghu as the sole Minor Artifact, all 32 priorities,
crafts/sockets, feats/AP and historical model results are unchanged. Optional
ring DEX remains unselected; Festive-only and HA63 exceptions retain their exact
limits. Earlier captures, original claim grades, other Queen effects, Skull CON
and the remaining mechanics/acquisition gaps are not regraded by this change.
See the [integration receipt](../../evidence/wisdom-loadout/chains-type-integration-2026-11-15.json)
for actual verification and draft status; no new solve, crafting, purchase,
merge or publication is included.

## Historical .1 checkpoint — Wisdom/Constitution evidence integration

The [frozen audit register](../../evidence/wisdom-loadout/wisdom-con-sources-2026-11-16.json)
supplies eight bounded definition bindings without changing the recipe.
Claws Wisdom 15, native Celestial Profane 2 and Globe Exceptional 1 derive
**18 selected-gear Wisdom** at the full-kit level-36 floor. Queen Insight 7,
Dolorous Quality 3, Solar Artifact 4, native Celestial Profane 2 and Globe
Exceptional 1 derive a **17 Constitution supported subset**. Full Constitution
remains `null`: the Skull is present, conflicting and excluded from every public
pair proof. The complete model cases remain 32 and 33.

The selected placements stay literal: Claws Nearly Complete Wisdom (base/filled
ML 35); Queen Insightful Constitution (35); Coldlight Dolorous Accessory
Constitution (34); Solar Constitution in Reflection Sun socket 0 (augment 30,
host 33); Globe in the Calamitous Purple socket (augment 25, host 34); and native
Celestial Profane abilities (base 29, filled 30). Skull remains base 35/filled 36.
The complete kit remains level 36. Source pages establish slots and requirements;
the manifest establishes occupancy. No owned or installed gear is inferred.

Only Claws/Celestial Wisdom and Queen/boots, Queen/Celestial and boots/Celestial
Constitution pairs are added. Exact three-ID and six-ID guards retain the full
families, including the Skull. Prior INT 37, Fortification 226 and direct Spot 27
remain intact, with full-kit incompleteness at 35. These are standing-gear sums:
Bloodrage is excluded, and Wisdom 18 is not the character's Wisdom score or a
direct addition of 18 to Spot or Will.

The Wisdom selection, Yeenoghu as the sole Minor Artifact, all 32 priorities,
crafts/sockets, feats/AP, historical results, original source grades and prior
snapshots are unchanged. Optional ring DEX remains unselected. Festive-only and
HA63 procurement-evidence exceptions retain their exact scope. The Skull conflict,
other unresolved effects and complete character/HP/Spot/Will/DPS questions remain
visible. The [integration receipt](../../evidence/wisdom-loadout/wisdom-con-integration-2026-11-16.json)
records actual checks and draft status; no new solve, crafting, purchase, merge
or publication is included.

## Current selected-gear Doubleshot integration — build 11-16-26.2

The same recipe now has a bounded source derivation of **35 percentage points
of gear Doubleshot at level 36**: goggles 9 Enhancement, ring 3 Quality, boots
5 Insight, armor 3 Profane and Quickblade 15 Artifact once. Only Quickblade's
qualification and six exact native pair proofs are new; four Quickblade/native
pairs reuse the existing Artifact rule. Full-kit level-35 results stay withheld.

| Exact Quickblade host | Ordinary socket / manifest pointer | Explicit slot mapping | Base → filled item ML |
| --- | --- | --- | --- |
| Legendary Goggles of the Archer | Colorless; `items[2].sockets[2]` | Wiki Eye → selected Goggles | 33 → 36 |
| Legendary Chains | Crafted Green; `items[6].sockets[0]` | Wiki alternate Waist → selected Belt | 28 → 30 |
| Yeenoghu's Reign | Green; `items[11].sockets[1]` | Wiki Wrist → selected Bracers | 35 → 36 |

Each Colorless Quickblade gem is **ML30**. Source rules support these ordinary
Colorless/Green placements; they do not cover Sun, Moon or filigree slots.
The higher host/augment requirement applies, and other selected fills raise
the goggles and bracers to 36. Three distinct hosts must be equipped together;
three inventory copies or more than three copies do not multiply the one
three-piece reward.

Chains first needs its **one** Green-slot upgrade: **100 Legendary Staff
Splinters plus 50 each Legendary Broken Shackles, Chain Links and Broken
Collars**. This is the Legendary recipe, not the Heroic 30/20/20/20 column or an
additional socket. It remains a construction prerequisite, not an ownership or
completed-crafting claim.

A set augment suppresses existing named-set membership on its host. No Quickblade
host receives another selected set augment, and this manifest credits no native
named-set reward on any of them. Chains permits an optional Slavers set upgrade,
but none is selected/credited; no explicit negative inventory fact is inferred.
The goggles' individual 9 Enhancement affix is not a named-set reward. Current
occupancy, source compatibility and an owned item's state remain distinct.

The [source packet](../../evidence/wisdom-loadout/doubleshot-sources-2026-11-16.json)
retains community-source provenance and the bounded Tip 179/Stack interpretation.
Original source grades, previous qualifications, all 32 priorities, sole Minor
Artifact, selected crafts/sockets, feats/AP, exceptions and historical results
remain unchanged. Whole-character Doubleshot, Doublestrike, proc rate and DPS
remain outside this integration. See the [receipt](../../evidence/wisdom-loadout/doubleshot-integration-2026-11-16.json)
for actual precommit checks and draft PR #47 for the delivered head and CI.
No new solve, purchase, crafting, merge or publication is included.
