# Wisdom-priority loadout: evidence map

This packet connects the selected guide recipe to the completed optimizer
analysis. It is a **derived record**, not a new optimizer solve, browser capture,
in-game test or certification of all mechanics. The guide renders the recipe,
modeled comparison and exact ranked-affix order from the
[shared selection manifest](../../tools/fixtures/wisdom-loadout/selection.json).

## Records and what they establish

| Record | Purpose | What it does not establish |
| --- | --- | --- |
| [Startup receipt](startup.json) | Repository identity, clean starting checkout, independently checked immutable base and authorized scope. | Permission to merge or publish; live-site verification. |
| [Actual production run](production.json) | Exact query, optimizer/catalog identities and the completed 45-stage, 271.998-second solve. | That the subsequent practical recipe is another solve or the unchanged optimum. |
| [Selected practical recipe](loadout.json) | Fourteen items, exact crafts, ordinary augments, set placements and the manual derivation. | Live-game stacking correctness or a measured DPS improvement. |
| [Derivation and comparison](derivation.json) | The original 373-check construction/arithmetic receipt, all eight floors, recipe differences and three-way modeled comparison. | Source certification or guaranteed whole-character scores. |
| [Claim inventory](claims.json) | All 130 selected affix claims and their retained-source, corroboration, conflict, conditional or model-only grades. | Equivalence to the guide ledger's stricter `verified` status. |
| [Source-review record](sources.json) | Bounded prior source audits, retained excerpts, exclusion screening and unresolved acquisition/crafting limits. | A fresh observation timestamp for old material or proof of auction availability. |
| [Implementation verification](verification.json) | Exact tested file identities, 258 passing regression tests, preserved history, static links and the recorded browser-start permission block. | Browser layout, live-game mechanics, remote CI, merge or deployment success. |
| [Draft mechanics corrections](corrections.json) | Later bounded claim corrections, exact retained pointers, publisher corroboration and unchanged-selection scope for build 11-15-26.2. | Repair of missing original observations, new counted bonuses, a new optimizer solve or a published release. |

The records retain both the **original file identities and SHA256 hashes** and
the hashes of these compact, path-sanitized extraction files. These are distinct:
the original output hash does not claim that an extraction is byte-identical to
the full solver output. The manifest verifies the committed extraction hashes
before rendering. Original full analysis files are identified for provenance;
the guide does not silently substitute a new run for them.

## Selected scope

The primary is the Wisdom-priority practical derivative with **Yeenoghu's Reign
as its only Minor Artifact**. Burrowing Claws selects Enhancement Wisdom +15;
Celestial Sapphire's Nearly Finished choice is unused. The catalog gear
contributions are WIS 18 and DEX 6. Optional ring DEX +13, and its modeled DEX 19
result, remain separate and unselected. Calamitous is the pinned bow; Sinew was
not explored by this run. The fully socketed outfit requires level 36.

The user excludes event and limited-time items, except Festive ability
diamonds. Only Festive Intelligence +2 is selected here. Exclusion screening is
not proof that the user owns an item or that an auction currently has it. Any
unresolved permanent procurement route remains a factual limitation, not an
implied additional exception. The one explicit acquisition-evidence exception
below changes acceptance of that risk, not the item's evidence classification.

### Owner-approved HA63 acquisition-evidence exception

On 15 November 2026, the owner reported that Randall Lyric appears to offer
**Sapphire of Healing Amplification +63 (ML36)** and accepted the missing
independent acquisition evidence as an exception. Under the
[scoped decision](../../docs/knowledge-base/DECISIONS.md#approved-acquisition-evidence-exception--15-november-2026),
that procurement question is no longer a blocker to retaining this exact
augment. The vendor remains owner-reported, not independently verified; no
location, price, current stock or observation metadata is inferred.

This is not permission for other event/limited-time gear and is not new mechanics
evidence. All effect, type, stacking and applicability checks, other evidence
gaps and publication requirements remain unchanged. The original JSON receipts
and generated guide's unverified-procurement wording remain accurate records of
the source limitation; they are not rewritten into a verification claim.

## Arithmetic is not mechanics certification

The manifest validator independently recomputes catalog highest-of-type
arithmetic and checks the exact query, crafts, physical socket placements,
artifact count, manual changes and selected comparison. It does not model
full-character ability overlaps, critical range, sustained DPS, proc uptime,
filigree interactions, armor limits or every source interaction.

The [current stacking ledger](../../tools/fixtures/endgame-stacking/ledger.json)
and its unchanged source/value/type/positive-interaction validator remain the
authority for source-qualified subtotals. In particular:

- Retained support for Claws WIS +15 is not a fabricated observation timestamp.
- Glabrezu Insightful INT +7 and Chains Fortification +142, Combustion +142,
  Quality INT +3 and Spot +20 remain exact-value gaps.
- Skull CON +15 versus +16 remains a conflict, with separate sensitivity values.
- Queen's retained relay limitations remain open. Exact ordinary procurement of
  Healing Amplification +63 remains independently unverified, with the specific
  owner-approved acquisition-evidence exception above; it is not an open
  procurement blocker for retaining this augment.
- Optional ring Enhancement DEX +13 is model-only, not part of primary totals.
- Equal subtotals from new items or set augments do not inherit the old sources'
  certification. No new artifact/weapon filigree benefit is counted.

The previous guide is retained as [build 11-09-26.5](../../versions/11-09-26.5.html).
The first Wisdom implementation is retained as
[build 11-15-26.1](../../versions/11-15-26.1.html); its dated verification receipt
applies to those original bytes, not automatically to the later correction.
Original captures, historical snapshots and bow-model fixtures are preserved.
See the [implementation note](../../docs/knowledge-base/WISDOM-ARTIFACT-LOADOUT.md)
for the selected tradeoffs and validation boundary. Publication remains a
separate exact-head review and deployment step.

Retained Wiki excerpts are attributed to [DDO Wiki contributors](https://ddowiki.com/)
through the article/revision links in the source records and retain the
[CC BY-SA 2.5 license](https://creativecommons.org/licenses/by-sa/2.5/).
No missing capture or observation metadata is supplied by that attribution.
