# A-074 — Queen of Rot BASIC

The selected endgame recipe replaces Cloak of Summer’s End (level 36) with
[The Queen of Rot](https://ddowiki.com/page/Item:The_Queen_of_Rot), selecting
Nearly Complete: Insightful Constitution +7, and puts Diamond of Spot +22 in
Legendary Ring of Unnatural Accuracy’s formerly empty Green socket. The diamond
is Colorless, ML36, with a +22 Competence Spot source; its acquisition route is
unknown. No vendor, final skill increase or trap success is inferred.

Every other selected item and craft remains fixed. Calamitous and Legendary
Demogorgon’s Sinew remain alignment alternatives. There are 33 physical sockets
(24 ordinary and nine Sun/Moon), of which 28 are occupied. All Sun/Moon gems are
Legendary. Offhand is empty and the quiver has no sockets. There are eight fixed
accessory craft selections, plus four weapon crafts only when Calamitous is used.
The complete outfit and either filled bow require character level 36.

The [current table](../../index.html#endgame-kit-ml35-36) is the complete recipe.
BASIC does not select the optional imbue package, an Emerald, Imbued Infusions,
Heart Shard, Bloody Boulder, a Quality CON-to-damage swap, or any class, feat,
enhancement or destiny change.

## Evidence and provenance

The current Spot type is corrected from Enhancement to Competence using the
[transmitted exact own-item excerpt and retained Competence rule](../../evidence/spot-diamond-type/README.md).
This corrects the explanatory label only; the reported study and modeled values
are unchanged. Missing original item bytes and observation context keep the
ledger component unknown and excluded from subtotals.

This document is an implementation record of relayed study results and approved
choices. It is **not an original browser capture, exact source transcript, solver
artifact or independently reproduced solve**. No original study files are
reconstructed from summaries.

- The Queen’s normal Wiki page was reportedly observed around 00:07 UTC on
  9 November 2026: ML35; Terror of the Demon Lords end chest; Bound to Character
  on Acquire; Sheltering 41, Resistance 13, Insightful Fortification 84, Freedom
  of Movement; explicit Nearly Complete Insightful Constitution +7; Green,
  Yellow and Sun sockets. Reported footer: 19 September 2026, Update 81.3;
  anonymous cache up to 12 hours. Original page bytes, an exact revision permalink
  and every effect tooltip/type were not recovered. These are paraphrased relay
  observations, not quotations or source-certified types.
- The retained 8 November raid-item harvest independently identifies
  Queen ML35, the cloak slot and Terror of the Demon Lords end chest; it does not
  supply Queen’s own effect tooltips or category classification. The original
  harvest is not materialized as evidence in this repository.
- Existing [endgame evidence](../../tools/fixtures/endgame-evidence/README.md),
  [stacking receipts](../../evidence/endgame-stacking/README.md) and
  [bow-choice source limits](../../evidence/endgame-bow-options/README.md) retain
  their original identities. They are not relabeled as fresh observations of
  Queen. Historical source files and prior snapshots remain unchanged.
- Acquisition locations and quest-pack relations below were approved from
  retained item/quest infobox harvests. Not every quest page was freshly opened.
  They are acquisition guidance, not guarantees of drops, ownership, access,
  current availability or complete crafting costs.

The current component ledger marks Queen/Spot additions unknown and excludes
them from certified totals. Queen bonus types in the comparison are **model
assumptions** pending original tooltip evidence. The unchanged source provenance
and positive-interaction gates apply, including Sun/Moon combinations. Removing
Summer’s End removes its components from the current ledger; its exact captures
remain historical evidence. Flat HP108 remains supported independently of Queen.

## Reported study and model-only comparison

Reported optimizer source commit:
[`b43ed69c6d3f9912101ac47e4fcbe995b8298d41`](https://github.com/eddiefiggie/ddo-loadout-optimizer/commit/b43ed69c6d3f9912101ac47e4fcbe995b8298d41).
Reported run interval: 9 November 2026, 00:07:17–00:07:58 UTC; 22 solves,
1,022 phases, seed 0, zero MIP gap. Review accepted 20 feasible cases and rejected
two strict diagnostics retaining Doubleshot 36 / Light Absorption 24 despite
“Optimal” statuses. Those diagnostics are not evidence that BASIC preserves
those old values. This implementation does not claim its own rerun.

For either bow against the same bow with the old cloak:

| Modeled gear contribution | Summer’s End → Queen BASIC |
|---|---|
| Doubleshot | 36 → 35: Enhancement 9 + Quality 3 + Insight 5 + Artifact 15 + Profane 3 |
| Constitution | Generic-craft case 32 → 32; Skull item-page case 33 → 33 |
| Raw PRR | 132 → 133: max(Defense 40, modeled Queen 41) + Profane 30 + Artifact 30 + Insight 21 + Quality 11 |
| Raw MRR | 72 → 73: max(Defense 40, modeled Queen 41) + Insight 21 + Quality 11; armor cap applies to total character MRR |
| Fortification | 283 → 286: Enhancement 162 + max(Insight 81, modeled Queen 84) + Quality 40 |
| Will / Reflex / Fortitude | 25/25/26 → 26/26/27: modeled Resistance 13 replaces 12 |
| Flat HP | 108 → 108: False Life 60 + Vitality 48; no CON-derived or temporary HP included |
| Other modeled values | INT 37 Calamitous / 36 Sinew, RP 44, Seeker 29, Armor-Piercing 76, Deadly 12, Accuracy 33, Dodge 16, Healing Amplification 63, DEX 28 unchanged |
| Utility | Gain Freedom of Movement; lose Light Absorption 24; add Spot 22 Competence source |

The optimizer’s PRR objective cap 132 does not cap raw PRR 133. Light armor has a
base MRR cap 100; independently established cap increases and other character
contributions must be applied before claiming effective whole-character MRR.
The Skull’s own retained item page lists CON 16 while generic Nearly Complete
lists 15. The craft choice stays fixed; neither case is elevated to a verified
mixed-type total. KTA and Insightful Deadly take the higher applicable Insight
damage value, not both. Sinew loses net 1 modeled gear INT because Globe 1 remains
when Dimlight 2 is absent. Lawful negative-level, control-save and immunity limits
stay intact; there is no universal DPS, paralysis or proc claim.

The reported exact BASIC configurations contain zero Minor Artifacts in the
optimizer catalog. The model’s maximum-one constraint permits zero; it is not an
exactly-one requirement. This is relayed catalog metadata, not a source-certified
negative classification for every selected item. Retained ring notes identify
Unnatural Accuracy and Earth and Sky as not Minor Artifacts; no such exact
negative observation is claimed for every other item, including Queen. Artifact
bonus type on gems or Monolith does not establish Minor Artifact item status.
Filigrees were excluded from the study; no artifact redesign or global optimum
is implied.

## Acquisition and crafting routes

Base item minimum levels below are not the filled-item level.

| Item | ML | Location / pack |
|---|---:|---|
| Calamitous | 34 | Ludendorf City Hall, Viktranium Experiment crafting / Chill of Ravenloft |
| Legendary Demogorgon’s Sinew | 35 | Back to the Abyss, end chest / Terror of Demogorgon |
| Light Armor of the Warblade’s Reflection | 33 | Ritual Table after Threats Old and New / Magic of Myth Drannor |
| Skull of the Horned King | 35 | Terror of the Demon Lords, end chest / Terror of Demogorgon |
| Goggles of the Archer | 33 | Book Burning, end chest / Magic of Myth Drannor |
| Pendant of Subtle Pain | 31 | Temple of Elemental Evil: Lower Temple Complex, end chest / The Temple of Elemental Evil |
| Abyssal Compass | 35 | Strange Catalyst Forge, Gravenhollow / Terror of Demogorgon, with Vale of Twilight precursor |
| Queen of Rot | 35 | Terror of the Demon Lords, end chest / Terror of Demogorgon |
| Unbreakable Cord | 34 | Relentless, end chest / Chill of Ravenloft |
| Ring of Unnatural Accuracy | 32 | Pilgrims’ Peril, end chest / ILLITHID INVASION |
| The Earth and the Sky | 31 | Temple of Elemental Evil: Depths of the Temple, end chest / The Temple of Elemental Evil |
| Burrowing Claws | 35 | The Darklake, Depthdigger’s chest / Terror of Demogorgon |
| Coldlight Runners | 34 | A Light in the Attic, end chest / Chill of Ravenloft |
| Bracers of the Battlerager | 33 | Threats Old and New, raid warded chest / Magic of Myth Drannor |
| Epic Purifying Quiver | 29 | Oath of Vengeance **Legendary**, end chest / Mists of Ravenloft |

Calamitous’s blank costs 25 each of four Legendary Bleak parts; all four selected
weapon crafts cost additional ingredients. The existing
[listed budget](../../index.html#legendary-bow-subtotal) remains unchanged.

Armor crafting uses Legendary Light Armor of the Warblade, 120 Barrier Fragments
and Sigil of the Warblade. The base armor is a rare end-chest drop in The Key to
the Mythal; the sigil comes from Threats Old and New.

Compass crafting uses Legendary Planar Compass, Legendary Abyssal Catalyst and
five Legendary Abyssal Gems. The catalyst comes from For Want of a Heart, end
chest. Legendary Planar Compass is ML29 from To Curse the Sky, The Vale of
Twilight; its exact chest is unknown. The finished Abyssal Compass is ML35.

## Reflection clarification

The retained Shadow Striker tooltip on
[Reflection revision 685449](https://ddowiki.com/index.php?title=Item:Light_Armor_of_the_Warblade%27s_Reflection&oldid=685449)
gives 3% Profane Doubleshot and 20% Enhancement ranged attack speed. Its exact
context is `evidence/endgame-stacking/final-provenance-receipts.json`,
`records[8].tooltips[2]`, observed 7 November 2026 at 20:08:31.322 UTC.
[Legendary Solar Doubleshot revision 691766](https://ddowiki.com/index.php?title=Item:Solar_Gem_of_Doubleshot_(Legendary)&oldid=691766)
gives 15% Artifact Doubleshot: `fresh-2026-11-07.json`, `receipts[6].text`,
observed 19:30:09.809 UTC. Both files are under the existing stacking-evidence
directory; their exact hashes and contexts remain in the component ledger.

The retained [Artifact bonus rule](https://ddowiki.com/page/Artifact_bonus)
(revision 636950, observed 2 November 2026 at 05:38:21.810 UTC) says:
“This bonus stacks with all other bonuses.” Its exact context is
`tools/fixtures/endgame-evidence/retained/INTiana-DDO-Wiki-bonus-rules-01-evidence.json`,
`source_receipts.artifact_competence_exceptional.sources[0].exact_source_sections[0].following_paragraph`.
That explicit positive rule supports the **two-source 3 + 15 = 18 Doubleshot
percentage-point contribution**. It does not establish an 18% DPS gain or certify
the full modeled gear Doubleshot 35; other pairwise interactions remain unknown.
The selected Lunar Constitution, Intelligence, Physical Protection and Ranged
Power descriptions and selected Monolith set description list no Doubleshot or
attack-speed contribution. This is a statement about those retained descriptions,
not a universal claim about every Moon gem or Artifact bonus.

The retained [Enhancement bonus rule](https://ddowiki.com/page/Enhancement_bonus)
(revision 699462) explicitly names Haste among attack-speed sources and applies
the highest applicable bonus. Armor’s Enhancement speed and Haste therefore do
not add; this check does not establish Haste’s current magnitude. The actual
retained record is `evidence/endgame-stacking/retained-selected.json`, index 2,
observed 2 November 2026 at 01:45:04.528–01:45:09.911 UTC; local SHA-256
`eed0083b8454a40a249acf5b0c3b93714e68ee496a857e889c724bc0e278dc78`.
It preserves original-package hash
`259e067cfd0a6bfb72111b44b177454ea060750a48ace2e2d8a4c9a58b7aa89a`
and pointer `pages[4]`. The source uses normalized whitespace and reports
permalink metadata; that is not a separate historical-endpoint read. No retained
source bytes, selected equipment, full-kit evidence gates or damage-model outputs
change in this clarification.

## Implementation checks

The exact A-074 replacement contract reconstructs build 11-08-26.6 before applying
older scope hashes. Separate tests cover the selected recipe, 33/28 socket
counts, modeled maximums and deltas, source-gate exclusions, and mutation rejection.
The historical bow model is unchanged. The generated audit, print reference and
new snapshot must match their builders. Software checks do not certify DDO
mechanics; independent review, browser QA, merge and deployment are separate.
