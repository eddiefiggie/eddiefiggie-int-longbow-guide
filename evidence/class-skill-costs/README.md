# Class-specific skill costs (A-018)

The [Skills section](../../index.html#skills) now uses the class currently being
advanced to explain rank prices: 1 skill point for a class skill, 2 for a
cross-class skill when it can be trained. Named positive examples replace the
universal past-life-class prices. Existing selected skills, priorities, targets,
class progression and the aggregate budget paragraph remain unchanged.

## Source receipt and limits

[source-ledger.md](source-ledger.md) is the independent source reader's ledger,
transmitted through the parent task on 8 November 2026. It records 16 normal
DDO Wiki page observations from 22:54:13.364 to 22:58:13.594 UTC, plus the
published Guide at 22:54:00.435 UTC. The Guide establishes the starting text,
not game mechanics. Displayed oldids are metadata; historical revision URLs
were not opened. Anonymous cache notices range up to 17 hours; Balance's
literal negative cache age is not a freshness guarantee. No in-game test was
performed.

The implementing executor read this transmitted ledger, **not** the separate
raw JSON packet. The parent reports reading and hash-checking that packet.
[receipt.json](receipt.json) separates reported raw-packet metadata from local
verification: the retained ledger has one final LF (12,204 bytes, SHA256
`40321e74f4fa57542cb41b529284a9ae1c326064f4d26f5dc40fd5cb654b8eac`).
Adding one LF reproduces the reported 12,205-byte original SHA256
`5d119d732c93a730ffd30f8ccebdbeb72bb579f083c6a7b9be43b96d50b86bf0`.
This verifies the ledger transfer, not the raw packet or current gameplay.

The historical A-018/GS08/GS09 files were described in the task but were not
materialized or read here. Their missing bytes, timestamps and source pointers
have not been reconstructed; this correction uses the fresh transmitted ledger.

## Claim map

| Corrected claim | Literal source support |
|---|---|
| Prices follow the class being advanced; a previous class level affects maximum ranks separately | Skill point and Cross-class skill; Class skill defines 1 point/rank versus 2 points/rank |
| Search costs 1/rank on Ranger, Dark Hunter, Alchemist, Rogue and Artificer levels | Search's own named class-skill list |
| Disable Device costs 1/rank on Artificer, Dark Hunter and Rogue levels | Disable Device's own list; first-training eligibility is outside this edit |
| UMD costs 1/rank on Artificer, Bard, Rogue, Warlock and Alchemist levels | Use Magic Device's own list; Bard and Warlock class pages also list it |
| Tumble costs 1/rank on Bard, Monk and Rogue levels | Tumble's own list |
| Spot costs 1/rank on Alchemist, Artificer, Druid, Monk, Ranger and Rogue levels | Spot's own list |
| Balance costs 1/rank on Alchemist, Bard, Monk and Rogue levels | Balance's own list; Barbarian remains unresolved below |
| Jump and Listen can also be 1-point purchases after Ranger; Bluff is not universally 2 | Direct Rogue, Ranger, Bard, Warlock and Monk class-page lists as applicable; the conditional rule supplies other prices without asserting unknown membership |
| Open Lock costs 1/rank on Rogue levels | Rogue class-page list; other levels use their own class/cross-class price when trainable |
| Racial-life prices apply on each Rogue level; Scourge's seven selected examples are non-exhaustive | Rogue and Ranger class lists; Ranger also lists Heal and Swim, neither newly selected |

These are named positive examples, **not exhaustive class/archetype lists**:

- The older Class skill matrix ticks **Barbarian Balance**, while Balance's own
  list omits it. This pass does not resolve the conflict or label Barbarian
  cross-class by omission.
- **Dark Hunter Spot** appears as a category but not in Spot's prose list.
  That category does not establish its purchase price. Search and Disable
  Device name Dark Hunter explicitly; ordinary Ranger is not interchangeable.
- Arcane Trickster categories do not establish base-class/archetype equivalence.
  The matrix has 15 base-class columns and is not an all-archetype reference.
- Fighter Jump is supported by the matrix in this ledger; no fresh direct
  Fighter page or complete Fighter class list was read.

## Excluded work and regression scope

**A-035 remains separate.** The existing Scourge first-training guidance,
“no maximum yet” and “5 for good” phrases are deliberately unchanged, despite
the source concerns recorded in the ledger. Their preservation is a scope
boundary, not an endorsement. This correction does not certify A-014, any
whole-life skill budget, exact cross-class totals, allocation feasibility or
the complete build. Misleading universal per-skill totals were removed without
substituting new totals. Selected allocations were not changed.

`tools/test_class_skill_costs.py` checks the visible rules, literal positive
source lists, repeated prices, non-exhaustive examples, source identity and
scope boundaries. Negative controls cover wrong prices/classes, unsupported
fall-through rules, hidden/inert content, changed targets/budgets and unrelated
Mechanic, bow, gear or script changes. Reversing exactly 14 reviewed price
replacements and the build stamp reconstructs the complete PR #39 index at
`594090c930222ea688e80ca8aec487fb0746cf45`; all 60 pre-existing snapshots have
retained hashes. Prior preservation checks apply their original hashes after
the same exact reversal. Software tests check source consistency and change
scope, not live game behavior.

Source credit: [DDO Wiki](https://ddowiki.com/), under
[CC BY-SA 2.5](https://creativecommons.org/licenses/by-sa/2.5/). Normal page URLs,
capture times and displayed revision metadata are preserved in the ledger.
