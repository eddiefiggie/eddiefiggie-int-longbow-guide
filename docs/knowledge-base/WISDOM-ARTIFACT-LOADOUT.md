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
magnitude, but its exact bonus type and calculator integration remain open.

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
Build **11-15-26.4** adds the separately approved bounded multi-source proof
route. It qualifies Chains **Equipment Combustion +142** and **Quality INT +3**
as source-supported recipe derivations, not finished-item tooltips. Separate
host/channel, Legendary recipe and category-definition records are bound with
their actual provenance. The [fresh Ability source](../../evidence/wisdom-loadout/recipe-proof-sources-2026-11-15.json)
explicitly supplies Intelligence membership and attributes/abilities terminology.

The 142 is a complete selected-gear Fire Spell Power contribution only. The INT
result now counts Glabrezu and Chains Quality, but still has seven excluded inputs
and a newly exposed missing Insight/Quality interaction; the complete total
remains null. Fortification is still missing the premise that this Slavers Prefix
is in the general rule's standard-item class. Spot's exact selected-craft type
remains unsupported. Neither incomplete proof is promoted.

Original claim grades and previous source packets remain byte-identical historical
records. Current generated labels identify direct versus recipe-derived support.
Only four of 76 complete level36 result objects change; 72 remain identical, and
all 76 level35 results are unchanged. Before integration, the real new engine
also reproduced all 76 results on unchanged .3 data. The selected recipe,
priorities, numeric/core tuples and seven positive-interaction rules are unchanged;
the calculator changes only by the reviewed bounded qualification dispatcher.

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

Next validation should resolve the remaining Fortification classification, Spot
type, INT interactions and other source/applicability gaps. The original direct
typed-numeric-clause path is preserved for unrelated inputs; the approved
recipe-proof route is limited to four fixed Chains IDs and cannot infer a
stacking edge. Wider inference or different selected components would require
separate review. Five supported magnitudes are not five fully qualified effects
or a validated total-DPS gain. See the [current integration receipt](../../evidence/wisdom-loadout/recipe-proof-integration-2026-11-15.json).

The historical bow model, previous snapshots and original retained captures
remain unchanged. Current generated sections must pass fresh semantic tests;
reversible predecessor tests preserve the prior records rather than certifying
the new selection. Publication requires its own exact-head checks and review.
