# Optional Mechanic evidence (A-016)

The [optional Mechanic note](../../index.html#optional-mechanic) retains the
4-AP Arbalester/Mechanics package and corrects only its funding advice and the
separate 7-AP extension. It changes no selected class, enhancement purchase,
levelling schedule, gear, bow option or model output.

## Source receipt

[source-ledger.md](source-ledger.md) is the independent source reviewer's exact
ledger transmitted through the parent task on 8 November 2026. It records normal
cloud-browser reads of Mechanic enhancements at 19:35:21.705 UTC and Enhancements
at 19:36:21.571 UTC, plus observations of the published Guide. Displayed oldids
721681 and 704870 are metadata; no historical revision URLs were opened.
Anonymous Wiki caches were up to 9 and 4 hours old respectively.

The separate [Arcane Archer supplement](arcane-archer-supplement.md) records the
direct Awareness effect and rank metadata at 19:42:48.072 UTC, displayed oldid
722900, cache up to 5 hours old. It supplies mechanics evidence for the selected
Arcane Archer rank 3; the earlier Guide observation establishes selection only.
It makes no claim about another Arcane Archer ability or to-hit interaction.

The implementing executor read the transmitted ledger, not the separate raw
JSON receipt. Its own direct web-tool attempts to open both Wiki pages failed
with restricted-URL errors. The parent reports reading the raw receipt in its
environment; that file was not materialized or independently read here.
[receipt.json](receipt.json) distinguishes reported raw-packet metadata from
verified local ledger identity. The retained ledger has one final LF (5,129
bytes); adding one LF reproduces the original 5,130-byte SHA256 exactly.
This verifies the transmitted ledger rendition, not the separate raw JSON.
The supplement is also retained with one final LF (1,386 bytes); adding one LF
reproduces its reported original 1,387-byte SHA256. Its raw supplement receipt
was likewise reported read by the parent, not materialized or read here.

The older 2 November observation has no usable revision permalink here. This
receipt does not reconstruct it or claim a new live-game test.

## Narrow claim map

| Claim | Source and reasoning |
|---|---|
| Arbalester 1 AP, then Mechanics ranks 1–3 at 1 AP each | Mechanic core and Tier One definitions; 4 AP total is arithmetic; Rogue 1 and actual available AP are required |
| Awareness rank 1 costs 1 AP and prints +1 Listen, Search and Spot | Mechanic Awareness definition plus the explicit rank/cost explanation in Enhancements |
| Awareness brings the 4-AP package to 5 AP before Skill Boost | Derived purchase order; the tier-2 gate independently requires Rogue 2 and 5 AP already spent |
| Skill Boost has one rank, costs 2 AP and gives +6 to all skills for 20 seconds, cooldown 30 seconds | Direct Mechanic entry; 7 AP total is arithmetic; the normal Rogue-1 chassis cannot qualify by AP alone |
| Awareness 1 does not add to an owned higher Awareness | Explicit highest-Awareness-only rule in Enhancements plus the direct Arcane Archer Awareness effect/rank supplement; the selected Arcane Archer Awareness 3 remains unchanged |
| Early optional spending needs contemporaneous funding and valid gates | AP are earned during heroic levelling and prerequisites must be met before purchase; future omissions or later refunds are not earlier available AP |

No combined Search total or new alternate level-by-level allocation is derived.
No particular main-tree refund choice is revalidated. Skill Boost's listed
active effect is preserved separately; this source check does not establish
interactions with every other active boost.

## Regression scope

`tools/test_optional_mechanic.py` binds the visible note, source receipt and
purchase qualifications, with mutations for ranks, gates, order, funding,
hidden text and unrelated content. Reversing only this exact prose replacement
and build stamp reconstructs the complete PR #38 index at
`2512c0081c047f5a6c50fba23ca3aae3c0f451d4`.

The prior build and bow scope tests reverse the same exact replacement before
applying their original hashes. Their gear, Calamitous/Sinew, model and negative
controls remain intact. These are source-consistency and scope checks, not
independent authentication of the Wiki or live-game certification.
