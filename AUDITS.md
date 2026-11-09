# Audit log

This log records source checks against the named DDO wiki pages and internal consistency reviews, with the scope and evidence stated for each entry. Internal reviews do not certify game mechanics. Corrections are listed, not hidden. Found a number that does not match its page? Open an issue with the line and the page.

| Date | Scope | Checked | Found and corrected |
|---|---|---|---|
| 29 Oct 2026 | Enhancements and epic destinies | Every AP/DP cost, rank count, progression gate and prerequisite on the Horizon Walker, Deepwood Stalker, Harper Agent, Arcane Archer, Shiradi Champion, Shadowdancer and Fatesinger pages against every tree table, gate table and by-level table | Deepwood Stalker had 4 AP below its 5-AP gates (tier 2 and the Sneak Attack core); fixed with Favored Defense 1 in place of Thrill of the Hunt rank 3, and the AP-by-level table re-sequenced. All other costs matched. Builder point counters that disagree with the wiki cropped from the tree images |
| 30 Oct 2026 | Mechanics behind Playing it | Reaper difficulty (per-skull table), Reaper race, Monster Champion, PRR, MRR, Dodge bonus, Evasion, Improved Evasion, Fortification, Concealment, Incorporeal, Ghost Touch, Threat, Saving throw, Helpless, Knockdown, Balance, Dungeon Alert, Hireling, Potion, Reaper enhancements, Horizon Walker ability text | No errors in the existing text; the section was rewritten from these pages |
| 30 Oct 2026 | Skills | Spot, Search, Disable Device, Open Lock, Auto-Search, Thieves’ Tools, trap and lock DC tables, Mechanic enhancements, Augment (skill diamonds) | Spot target raised to maximum; Auto-Search, skill-diamond and trapping notes added |
| 30 Oct 2026 | Orphan sweep after the week’s changes | Every section for references to removed or changed material | Six stale lines corrected (Pianissimo level, threat-reducer order, a core name, a contradiction next to the Technician note, three history remarks) |
| 31 Oct 2026 | Endgame kit (INTiana Jones Salt solve) | Four optimizer solves (Appendix); every kit item on its item page: lines, binding, source, Nearly Complete and Sealed options; the ML36 augment values on the Augment table; Woeful Salt on the Viktranium page and the Dinosaur Bone Horn version | The Dinosaur Bone Horn augment the free solve chose is the one-stack Salt (wiki), so the Calamitous was pinned for the eight-stack Woeful Salt. Goggles of the Archer’s Sight Beyond Sight is dodge bypass, not True Seeing. The Skull’s Nearly Complete can be Constitution +16 where the solver treats it as equal to the cloak’s +15. Kit section, milestone table, survivability table, crafted-bow Woeful row, dodge arithmetic and optimizer check rewritten |
| 31 Oct 2026 | Synergy and overlap audit (Build 10-31-26.6 kit) | Every kit line re-checked for bonus type against the synergy table: Fortification, Threat, Doubleshot, Dodge, Marksmanship and Improved Deception pages, and each item and augment page for ability-score types | Six rows rewritten for the new kit (fortification bypass, threat, sneak dice, Displacement, fortification on you, optimizer blind spot) and four added (Greater Marksmanship on three items, ability bonus types, Salt, Doubleshot on items). Overlaps found: the Pendant’s Armor-Piercing and Distant Diversion, two spare Greater Marksmanships, the goggles’ Doubleshot, the Litany’s and Globe’s Intelligence and Constitution parts. No kit pick changes; every overlapped item is carried for another line. Crafted-bow Miserable row now matches the kit |
| 31 Oct 2026 | Bow ladder and filigrees (after forum feedback) | All 35 bow item pages: damage dice and multiplier, enhancement bonus, critical profile, every affix, binding, source, sentience; the Sentient Weapon/Filigrees page for Spines of the Manticore, Wildhunter, Crackshot Negotiator and The Long Shadow; Overfocus, Sustaining Symbiont and Stealth Strike pages | All 35 bows and all four filigree sets matched. One error in the synergy audit: the Overfocus fix was called a sentience jewel; it is the Sustaining Symbiont trinket. Overfocus’s -10 Search and Spot and the trapper’s options added |
| 2 Nov 2026 | Focused Spectral/Sapphire correction | Own item pages: [Spectral Longbow (level 4)](https://ddowiki.com/page/Item:Spectral_Longbow_(level_4)) (revision 722933), [Sapphire Sting](https://ddowiki.com/page/Item:Sapphire_Sting) (revision 700645); [Long Bow table](https://ddowiki.com/page/Longbow) discrepancy; related Keen wording. Revision IDs identify the earlier same-day source check; links open current pages. | Spectral ML/carry level corrected to 4; Sapphire native 19-20/x3, not Keen. Related roadmap, milestone, Ghost Touch and model wording reconciled. Supersedes the 31 October “all 35 bows matched” conclusion for these two items; no full-ladder recertification. No unrelated gear/feat changes. |
| 3 Nov 2026 | Internal feat-description consistency | Repeated instructions compared with the existing heroic feat tables, Legendary Trick Shot eligibility note and Harbinger of Chaos condition in repository main `8e367c4b286a79d92ba7389e1702b0773e7ca2b0`. No new wiki verification; direct access remains unavailable. | Delayed-IPS roadmap aligned to Weapon Finesse 12 / IPS 15 / Weapon Focus 18; Scourge prose aligned to its existing selected schedule and optional Sneak of Shadows at 18. Existing Legendary Trick Shot eligibility and Harbinger alignment caveats repeated in summaries. Selected feats, timing, gear, totals and model unchanged. INT-tome skill budgets, DEX prerequisites, IPS/Watchful Eye grants, Legendary Trick Shot eligibility and Titan’s Blood rationale remain separate source questions. |
| 3 Nov 2026 | Internal model-arithmetic consistency | Alacrity prose against the existing `tools/bowmodel.py` assumption and calculation on main `7de4fa07249869c5aa9be75e0e84a24e31b61719`. Direct [Haste](https://ddowiki.com/page/Haste) retrieval failed with “Failed to fetch restricted URL”; no source revision was obtained. Existing [Ranged Alacrity](https://ddowiki.com/page/Ranged_Alacrity) and Haste quotations are retained guide attributions, not new source verification. | Changed the ratio notation from 20/15 to 1.20/1.15, about +4.35%, and stated the model-assumption scope. Added arithmetic consistency checks; the stacking rule and its Action Boost interaction remain source questions. No model or build-choice changes. |
| 4 Nov 2026 | Lamordia augment handling only | Retained [crafting revision 720728](https://ddowiki.com/index.php?title=Viktranium_Experiment_crafting&oldid=720728), Lamordia Augments and Unslotting sections; exact capture and limits in tools/fixtures/lamordia-handling/README.md. | Added slot compatibility, ML34 and recovery checklist. Partial corpus, no live-game validation or source refresh; recipe costs, stats and model unchanged. |
| 3 Nov 2026 | Sapphire Sting retained-source guardrails | Full browser-rendered DOM capture at 17:29:59.097Z, revision 700645; exact identity and cache limits in `tools/fixtures/sapphire-sting/README.md`. Item table, full enchantment list and selected repeated Guide claims only. | No affirmative item-field mismatch. Qualified “native”/“no Keen” wording to listed profile and absence from the enchantment list. Optional Mythic is not required in the nonexhaustive ladder summary. No attack-speed, stacking, post-Improved-Critical, feat-eligibility or live-game certification; no build/model changes. |
| 4 Nov 2026 | Heroic Calamitous listed purchases | Retained crafting revision 720728 and heroic Dolorous Flames revision 702384; source identities and limitations in tools/fixtures/calamitous-recipe/README.md. | Separated blank and three selected heroic Weapon augment purchases; preserved naming qualifier. No unlisted-cost, availability, bow-stat or live-game certification. |
| 5 Nov 2026 | Heroic purchase checkoff | Existing retained crafting revision 720728 and heroic Dolorous revision 702384, as pinned by recipe tests. | Optional session-only checkboxes sum listed ingredients for unchecked purchases. All 16 combinations tested; no complete-cost, availability, binding or drop claim. Sources, recipe and model unchanged; browser QA pending. |
| 7 Nov 2026 | A-004 internal Fatesinger timing consistency | Comparison timing cell and verdict against this Guide’s existing Levelling roadmap and Destiny points by level rows. No new Wiki or live-game verification. | Summaries now say first Fatesinger purchases at 22, Harmonic Resonance at 24, Pianissimo at 25, and all 14 points bought by 28. Purchase order, cumulative DP, other comparison claims and all build choices remain unchanged. |

## Selected endgame stacking audit — 7 November 2026

Current remote main was verified as `86b096bfaf274b5050b384ece53b9c14e0ae476b` before the isolated local work. The [detailed audit](endgame-stacking-audit.html) binds each counted component to an exact source context and every counted pair to an explicit applicable rule. Separate listing and absence of a prohibition are not evidence of stacking. “Verified” describes documentary support, not live-game behavior.

Fresh supported-browser item and rule observations supplement exact retained Wiki captures. Anonymous page caching, missing original timestamps, source-reported revision metadata and extraction identities are retained. The prior 5 November source count is history, not the current receipt state. No optimizer was rerun or mechanism inferred.

PRR132, MRR72 and flat maximumHP108 are derived selected-gear contributions with direct positive rules. RP44, Doubleshot36, Seeker29, Armor-Piercing76, INT37, CON33, Fortification283 and save combinations stay unverified where a required positive edge is absent. Other effects, procs, conditions and full-build assumptions remain visible. The full fills include ML36 augments, so they are not a legal full-kit assertion at35. This finding is raised for the build owner; no gear swap is made. Cut to the Soul's3 is offensive Dodge bypass, not avoidance.

Selected items/fills and class/feat/AP/DP sections are protected by existing preservation contracts. The historical bow model stays byte-identical and retains its output; its different weapon/craft and level scope does not establish this selected loadout's DPS. New behavioral tests cover calculations, same-type maximums, missing positive edges, source identity/value/type/stat binding, context and qualification regressions, level limits and stale/hidden summaries. Software tests are not game verification.

The newly read generic Nearly Complete revision705751 lists Legendary ability15 while item-specific Skull revision714102 lists16. The component is marked conflicting and excluded from asserted sums; no raid exception, effective solver behavior or changed craft is inferred.

The final provenance repair requires an exact revision and genuine source-bound observation for counted inputs, applied rules and fixed factual summary clauses. Fresh selected receipts close the asserted subtotal chains; two rule observations were recovered from original records. Thirty-three numeric inputs and five other-effect definitions with incomplete provenance are now unknown and excluded; the Fortification interaction rule is ineligible until its capture context is recovered. Their retained wording remains in the unverified log. Current body cross-references now match gear PRR 132 and MRR 72 and no longer assert an absent Heavy Fortification augment.

## Local reconciliation — 8 November 2026

The frozen audit `7d6435e40acca22a8283fdca940f353f25006077` is reconciled onto published main `6d429003a5b22db841cdef23946df9f99b7dbfa7` through the reviewed integrated source `a2eff2564cbc73f49206044995a1a4327c2e1089`. Published A-004 summaries and purchases are retained exactly once. Every snapshot already on main is preserved byte-for-byte, including `versions/11-07-26.2.html`; only the new `11-08-26.1` snapshot is generated. The unpublished audit snapshots remain in their original frozen worktrees and are not imported here.

This is source reconciliation, not a new mechanics audit. The ledger, original source observations/hashes, classifications and evidence limits are unchanged. Its recorded original base remains audit provenance; it is not relabeled as the new reconciliation base. The Skull Constitution conflict remains excluded, and all selected build choices and complete model outputs remain preserved.

A prior native-browser receipt sampled the integrated `a2eff256` candidate on desktop and an approximately 485-pixel-wide ordinary browser viewport. The reconciled current page differs from that source only in its displayed update date/build stamp, and the detailed audit is unchanged. That earlier receipt does not directly certify this new tree. Actual phone/touch rendering, print pagination and exhaustive visual review remain unverified; no new browser session was run for this reconciliation.

## Shadowstrike save condition — 8 November 2026 (local A-019 candidate)

The three curse descriptions now require the struck opponent's failed Fortitude
save. The operative prose preserves the literal DC formula from retained
[Shadowdancer revision 720964](https://ddowiki.com/index.php?title=Shadowdancer&oldid=720964).
[Exact source and regression scope](evidence/shadowstrike-save/README.md) preserve
the missing original observation time. This supersedes the unconditional curse
wording and the 30 October no-errors conclusion only for this omission; it does
not re-audit all Shadowstrike effects or certify current gameplay. Geometry,
ranged damage, all selections and model outputs remain unchanged. Publication
and rendered QA are separate from this local documentary correction.

## Class-specific skill costs — 8 November 2026 (A-018)

The [fresh transmitted source ledger](evidence/class-skill-costs/README.md)
supports current-class 1-point class-skill / 2-point cross-class prices and
named positive examples. Introductory prose, cost cells and life examples now
follow that rule; Scourge's selected Ranger examples are non-exhaustive.
Universal per-skill totals were removed without a new budget calculation.

The normal-browser observations retain anonymous-cache limits and displayed
revision metadata; historical revision pages and live gameplay were not tested.
The implementing executor verified the transmitted ledger's byte identity,
not the separate raw packet. Barbarian Balance and Dark Hunter Spot pricing
remain unresolved; neither omission nor a category proves cross-class pricing.

A-035's first-training and Scourge maximum-rank wording is deliberately outside
this correction. The skill-budget paragraph, selected ranks/priorities and
class progression are unchanged; A-014 and complete allocation feasibility
remain uncertified. Exact reversal preserves the PR #39 page, optional Mechanic
guidance, bow options, scripts/styles and all unrelated content. All earlier
snapshots remain unchanged. Regression checks do not certify game mechanics;
independent review and publication remain separate.

## Queen of Rot BASIC — 9 November 2026 (A-074)

Selection base is main `dbc4dc349173ce61ba2b6818e7cd270735dca0d7`
(build 11-08-26.6). The approved change replaces only Summer’s End with Queen
Nearly Complete Insightful Constitution7 and fills the empty Ring1 Green socket
with Diamond of Spot 22. Complete selected crafts and acquisition guidance are
reconciled in the current table. Calamitous/Sinew conditions, build choices and
historical damage-model outputs stay fixed.

The [A-074 record](docs/knowledge-base/A-074-QUEEN-BASIC.md) documents the relayed
normal-page Queen observation, acquisition infobox harvest and reported study
metadata. Original Queen tooltip bytes/revision and solver artifacts were not
recovered; none was fabricated, and no local solve is claimed. Bonus types for
Queen arithmetic remain model assumptions. The 22-solve report excludes two
failed strict diagnostics from its 20 feasible accepted cases, despite their
reported Optimal statuses.

Current model-only deltas are Doubleshot 36→35, raw PRR 132→133, raw MRR 72→73,
Fortification 283→286 and Will/Reflex/Fortitude 25/25/26→26/26/27. Constitution 32
(generic craft) / 33 (Skull item case), flat HP 108 and other selected modeled
statistics remain unchanged. Freedom of Movement replaces the lost Light
Absorption 24. The model's PRR objective cap 132 does not hide raw 133; MRR uses
whole-character caps. Spot 22 is a source rather than a guaranteed final gain.

The earlier 7 November PRR 132/MRR 72 conclusions below their dated heading apply
to the former kit. The current ledger removes Summer’s End and marks Queen and
Spot inputs unknown. It therefore withholds current combined PRR/MRR as well as
other unsupported combinations. Existing positive-rule and provenance gates,
including Sun/Moon gaps and the Skull 15/16 conflict, remain intact. Original
captures and snapshots are unchanged. A reversible exact A-074 delta allows
older scope contracts to continue checking their original hashes. Regression
results, independent review, browser QA and publication are separate receipts.

## Fixed BASIC selection wording — 9 November 2026 (build 11-09-26.2)

The current recipe called the selected Skull Constitution craft and Epic Purifying
Quiver empty solver slots. Those obsolete assertions are removed. Claws Dexterity
and Calamitous Dimlight now use selected-craft wording instead of attributing
current choices to a solver. The approved BASIC recipe and the existing relayed
study record are the consistency reference; no original study artifact was
recovered or newly verified.

The bow augment row now describes its selected fills and ML36 requirement; the
Gear introduction identifies the Appendix’s optimizer runs as earlier records.
This changes six current explanations, not the equipment, crafts, socket fills,
modeled values or source qualifications. The Skull item-page +16 versus generic
Nearly Complete +15 conflict remains explicit. Historical notes and every
published snapshot, including 11-09-26.1, remain unchanged. The new exact reversal
contract reconstructs the prior published index before existing A-074 and older
scope checks apply; it does not replace their hashes or widen their permissions.

## Skill-training eligibility and heroic ceilings — 9 November 2026 (A-035)

The current Scourge example combined training eligibility with rank price and
claimed no level-1 maximum, then a permanent maximum of 5 after Rogue. The
correction separates those questions: ordinary Ranger 1 cannot train Disable
Device or Open Lock, whereas UMD and Tumble are eligible cross-class with a
level-1 maximum of 2 ranks. Rogue 1 at character level 2 permits the trap skills;
Rogue class-skill ceilings are 5 at that level and character level + 3 through
heroic training. Prices still follow the class being advanced. Other iconic
starts use their actual first-class eligibility; Shadar-kai’s Rogue-first
exception and all class orders remain unchanged.

The [A-035 evidence map](evidence/skill-training-timing/README.md) binds the
correction to the exact committed A-018 transmitted ledger. The local A-018
receipt is a metadata manifest; the original raw browser packet was not
recovered or read here. The cross-class maximum application is identified as a
ledger statement and derived arithmetic, not a locally inspected raw-page
quotation. There is no fresh Wiki or in-game verification. Original ledger,
receipt, dated exclusion history and earlier snapshots remain immutable.

Existing skill priorities, targets, point estimates and other build selections
are preserved. The displayed examples remain partial allocations; all points
must be spent at the current level-up, with no new allocation of remaining
points or complete budget certification. The exact A-035 reversal preserves all
older release hashes, and focused regressions reject stale eligibility/ceiling
claims, incorrect pricing, source upgrades and unrelated changes.
