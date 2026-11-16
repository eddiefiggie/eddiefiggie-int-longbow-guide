# Maintenance

1. Record current main, the candidate head and changed paths. Separate documentation, editorial consistency and mechanics changes.
2. Read the affected committed source and evidence. Preserve the [principles](PRINCIPLES.md), exact variant and uncertainty; identify any inference rather than presenting it as a quotation.
3. Sweep repeated instructions in summaries, tables and prose. Reconcile the entire affected claim without expanding the scope of its evidence.
4. Run the applicable checks below and review the final diff. Report passed, failed and unrun checks separately; software tests do not establish game truth.
5. Distinguish a local candidate, public PR, merged commit, successful deployment and observed live content. A result applies to the tested source identity, not automatically to later edits.

## Current checks

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools -p 'test_*.py' -v
```

The [Guide checks workflow](../../.github/workflows/guide-checks.yml) runs that discovery command on PRs, including drafts. Main contains tests for selected bow corrections, editorial consistency, model arithmetic, Guide integrity, roadmap accessibility markup, Sapphire evidence and Lamordia handling. The [model](../../tools/bowmodel.py) supplies the shipped scenarios; compare all complete output tuples when checking preservation. Do not substitute an old test count for running current discovery. There is no `tools/qc.py` entrypoint on the checkpointed main.

Integrity tests check the current snapshot, unique IDs, internal anchors and Guide-relative assets. They do not check all historical snapshots, external URLs, CSS URLs, srcset or actual rendering. For documentation, validate relative paths and fragments, review external targets against actual repository records, and scan for private information and unsupported status claims. Use browser checks for affected layout and interactions; an unavailable viewport is unverified, not a pass.

## Versions and deployment

For Guide content, follow [README updating rules](../../README.md#updating): update the build stamp and generate a matching new snapshot without overwriting history. Documentation-only work leaves `index.html`, its stamp and snapshot unchanged.

The [Pages workflow](../../.github/workflows/pages.yml) runs on main pushes and manual dispatch. A docs-only merge therefore still triggers deployment, although Guide runtime bytes should stay identical. Verify deployment separately; this workflow does not run the test suite. Before merging, check the exact head, current repository rules and unresolved reviews rather than assuming an earlier status still applies.

## Legendary Trick Shot retained-source guards (4 November 2026)

The [retained evidence and coverage notes](../../evidence/legendary-trick-shot/README.md)
bind the existing prerequisite cell and three selected schedules to Wiki revision
714089: character level at least 30 and an already-selected Trick Shot. The
separate classification check binds “Listed as a Legendary feat on the wiki” to
the actual page-category link. Both run under standard unittest discovery, with
negative controls for missing/later prerequisites, incorrect levels, corrupted
source/claim context and unsupported slot assertions. These predicates are
necessary-condition and retained-category checks only: slot eligibility, full
build legality, live-game behavior, bonuses and stacking remain unverified.
The exact capture hash, missing capture timestamp and logged-out cache limitation
are retained; a citation or agreement between repeated claims is not validation.
Revisit the tests and evidence together if the source or Guide representation
changes. This integration changes no player-facing content or runtime files.

## Score explanation structure guard

The score explanation check parses the actual paragraph in the bow-model section
before its table. Commented-out text, script text and uninstantiated templates do
not satisfy it. Negative cases cover those regressions, misplaced and duplicate
paragraphs; positive cases allow harmless inline markup and an obsolete commented
copy beside the real paragraph. The normalization and rounding checks still run
against the actual model script. This checks document structure and wording, not
CSS visibility, browser rendering or the validity of game assumptions.

## Lamordia checklist content guard

The Guide-side Lamordia check requires the reviewed checklist outside HTML
`hidden` and inert subtrees, including hidden ancestors and templates. Hiding
individual compatibility, ML34 or recovery list items cannot satisfy the exact
reviewed context. Visible wrappers and an inert obsolete copy beside the real
checklist remain acceptable. The retained crafting-source parser and its
revision, identity and claim checks are unchanged. This is a structural check,
not a browser/CSS visibility test or fresh verification of game mechanics.

## Selected endgame stacking ledger

`tools/fixtures/endgame-stacking/ledger.json` separates exact component definitions from positive pairwise interaction rules. An unknown/conflicting component cannot be activated into a subtotal, and a missing edge withholds the combined result. Do not replace explicit evidence with a generic “different types stack” assumption. `kit_min_level` is the full filled-kit applicability floor, not each source item's own minimum level.

After an evidence or classification change, run `PYTHONDONTWRITEBYTECODE=1 python3 tools/build_stacking_audit.py` to regenerate the selected-only source excerpt packet, detailed audit and current summary. For Guide edits, regenerate the print sheet and snapshot as usual, then run the full discovery command above. The new tests include arithmetic/provenance/context/qualification mutations and compare generated documents against their actual gated calculations. Existing tests still protect gear, purchases and historical model bytes. This repository currently configures no independent lint or static-type command; the documented Python/Node aggregate suite is required. Browser layout, disclosure navigation and small-viewport overflow remain separate checks.

Counting requires an exact source revision and a genuine observation date/time bound to the hashed record. Missing metadata, body text and receipt-creation timestamps cannot satisfy that gate. Unqualified rules remain visible but cannot establish a pairwise edge. Public renderer entrypoints validate source identity and fixed factual prerequisites; numeric clauses are bound separately even when a tooltip contains multiple bonuses in one sentence.

## A-074 selected-kit change

`tools/test_queen_basic.py` checks the complete historical A-074 recipe, explicit
empties, 33 sockets / 28 occupied, model-only deltas, evidence exclusions and exact scope.
Its reversible change contract restores the exact prior index before older
release contracts apply their unchanged hashes. Do not widen that contract to
allow unrelated choices. Queen relay/model inputs are not original captures and
cannot qualify for counting without the existing provenance and type gates.
Run `tools/build_stacking_audit.py`, `tools/build_crafting_sheet.py` and
`tools/build_snapshot.py` after current Guide/audit edits, then run full discovery.

## Wisdom artifact selection and generated priorities

`tools/fixtures/wisdom-loadout/selection.json` is the shared input for the current
recipe, ranked objectives and one-page summary. The exact query order is not
derived by sorting achieved values. The raw optimal result, practical manual
refinement and optional ring completion are separate records. Run builders in
this order: `tools/build_wisdom_loadout.py`, `tools/build_stacking_audit.py`,
`tools/build_crafting_sheet.py`, then `tools/build_snapshot.py`.

The current stacking ledger must contain every relevant selected input, including
unresolved additions, and exclude absent prior items/sets. A missing input must
not manufacture a complete subtotal. Source-quality labels in the optimizer
review do not replace the existing revision/observation/value/type and positive
interaction gates. The original Wisdom implementation left the calculator
unchanged; the separately approved .4 bounded proof dispatcher is described below.

The new exact outer preservation contract restores the approved predecessor
before historical tests apply their unchanged hashes and assertions; those tests
do not certify the new kit. Separate current tests must reject manifest/render
drift, priority reordering, a missing artifact, prohibited choices and promotion
of provisional values into certified totals. Preserve all published snapshots,
original captures, model bytes, and unrelated build choices. Browser checks of
the new tables on desktop and narrow viewports remain separate from the suite.

### Bounded correction layer

The 11-15-26.2 mechanics-text correction uses `tools/wisdom_corrections.py` and
its exact scope fixture to restore the PR47 draft before the original Wisdom
reversal runs. Do not rewrite the original scope, predecessor hashes or earlier
snapshots. Inner negative controls test the independently restored draft;
separate outer controls reject stale, mixed, duplicated and unrelated changes in
the actual current files. Current recipe and mechanics tests must still read
the production files. The loadout manifest, numeric ledger, source grades and
calculator outputs do not change. This layer is preservation evidence, not a
mechanics certificate or a substitute for the blocked browser release checks.

### Bounded crafting-integration layer

Build 11-15-26.3 adds `tools/wisdom_crafting_integration.py` as an exact outer
reversal to the fbb1 source-finding checkpoint. Its seven-file scope runs before
the unchanged correction and original Wisdom reversals. The original six-source
crafting packet and its 19-hash checkpoint remain historical evidence; tests of
that checkpoint read strictly restored bytes, not regraded current inputs.

The .3 checkpoint tests separately require the single Glabrezu Insight INT +7
source qualification, four withheld Chains inputs, unchanged selected/model
tuples and the complete expected calculator-result delta. The calculator's
single-source typed-numeric-clause and positive-interaction gates do not change.
Do not concatenate recipe/category passages into a fabricated finished tooltip,
reuse another item's Spot tooltip for Chains, or give an old source a new
observation date. These preservation layers did not grant permission for a
multi-source evidence contract; the later bounded design was separately approved.

### Bounded recipe-proof layer

Build 11-15-26.4 adds `tools/recipe_proofs.py` and a narrow dispatcher in the
existing calculator. The four fixed Chains IDs cannot escape this route by
deleting or emptying their proof. Every count attempt rereads the pinned selection
and real source records; an asserted success flag, fabricated joined quote,
unrelated direct source or unsupported category/type premise must fail closed.
The same-record header hierarchy, Legendary column, craft channel, category offer
and membership context are part of the reviewed proof, not optional annotations.

`tools/wisdom_recipe_proof_preservation.py` and its exact eight-file scope restore
the .3 checkpoint before older reversals or pinned calculator hashes are applied.
All 55 protected records and prior scopes stay literal. Historical renderers use
strictly restored .3 dependencies without changing global imports; they are not
substitutes for tests against the actual new engine. Do not weaken an old hash to
accept the new code or let a cached historical module bypass current-byte checks.

The real new engine must reproduce all 76 old-input result objects. After only
Combustion and Quality INT qualify, exactly four level36 records change and 72
stay identical; all 76 level35 records stay identical. Tests compare every field,
including the newly exposed missing Insight/Quality edge and seven remaining INT
exclusions. Current renderer tests distinguish direct from derived source support
and reject stale qualification labels. Keep the existing direct-path negative
tests running on the real new engine. All seven interaction rules, numerical
core semantics, selection, priorities, source grades and previous captures remain
unchanged. This contract does not certify the rest of the loadout or authorize
merge/publication; browser, accessibility and print checks remain separate.

### Seven-INT direct-source integration layer

Build 11-15-26.5 uses the existing direct-source gates for seven selected INT
definitions. The new [source packet](../../evidence/wisdom-loadout/int-evidence-sources-2026-11-15.json)
and [integration receipt](../../evidence/wisdom-loadout/int-evidence-integration-2026-11-15.json)
are additive records; old observations, claim grades and provenance gaps must
not be rewritten. New host/socket observations do not silently qualify every
effect on those hosts. Historical Slavers Spot evidence is recorded with its
older value, different host and continuity limit, not added to counted inputs.

`tools/wisdom_int_evidence_preservation.py` restores the exact .4 checkpoint
before the existing bounded-recipe and older preservation layers run. Its
seven-production-file scope contains 27 unique reversal hunks and 61 protected
records. Preserve the earlier scope fixtures, hashes and historical assertions.
Separate current-state
tests must exercise actual production data and the unchanged calculator,
rejecting source/provenance/value/type/host/level mutations and promotion of
unresolved Chains inputs. Compare complete result objects, not only totals.

Keep the existing same-type suppression and positive-interaction gates: newly
qualified inputs cannot manufacture a complete INT total. Test unchanged
selection/core tuples, rules and lower-level applicability separately from
changed evidence labels. Record actual suite, builder and diff results in the
receipt; these checks do not establish source freshness, live-game mechanics,
guide layout, accessibility, print pagination or release permission.

### Bounded INT-interaction layer

Build 11-15-26.6 adds exactly `int-selected-ten-pairs` and
`fort-enh-insight-observed`. Accept only the historical seven-rule profile or
the complete reviewed nine-rule profile; reject duplicate IDs, partial additions,
renamed rules, widened stats/types/channels and replacement member pairs.
Keep all seven legacy dictionaries and their source records literal, including
the old Fortification record's missing observation.

The positive Tip179 clause is bound to exactly five selected IDs and ten pairs.
The entire nine-definition INT family must also remain intact for completeness:
pin the direct and recipe bindings, core amounts/types/hosts, state/conditions,
level floor, suppressed inputs and exact membership. Recheck actual packet bytes
and original observation/revision contexts in public `proof`/`subtotal` routes;
calling `validate` first is not a prerequisite callers can be trusted to meet.
Unknown or conflicting input cannot be enabled by a force flag. A new component
or source binding requires review, not an edited hash or a broader type list.

`tools/wisdom_int_stacking_preservation.py` strictly restores the exact .5
checkpoint across eight reviewed production paths. The new scope independently
pins 187 unchanged evidence/fixture/snapshot/code files, excluding the mutable
current evidence README index. It precedes the existing .5-to-.4 and earlier
layers. Historical assertions run on their own exact restored code/inputs;
actual .6 acceptance runs separately on real production modules. Do not replace
global imports, relax old hashes or let cached accessors skip current-byte checks.

Compare all 152 complete old-input results at levels35/36 through the real new
engine. Current data may change only the two level36 INT records: total37,
seven counted, two suppressed, no excluded input, no missing pair, ten added
proof edges. The other 74 level36 and all 76 level35 objects remain identical.
Chains/Queen Fortification and Chains Spot remain excluded. Preserve selection,
priorities, recipes, claim grades, model outputs and prior snapshots. Build a
new path-rebased .6 snapshot and record actual suite/CI status separately from
browser QA, source freshness, in-game testing and release authorization.

### Bounded offensive-text integration layer

Build 11-15-26.7 corrects current explanations and generated applicability labels,
with a separate source/claim inventory. The source summaries are transcribed
observations and paraphrases, not new raw-capture records for ledger counting.
Keep the selection manifest, ledger, calculator, recipe proof engine, bow model,
old evidence and previous snapshots literal. Compare complete results, not only
the INT headline, when verifying this presentation-only integration.

`tools/wisdom_offense_preservation.py` restores the exact .6 checkpoint before
the existing .6-to-.5 and earlier contracts. Keep their fixed baselines and
negative controls intact; current .7 assertions must read actual production
files separately. Distinguish level 30's 4d6/2d6 named imbue subtotal from the
equipped Emerald's 5d6/3d6, and preserve archived experiment sections exactly.
Use all four documented builders and a new path-rebased snapshot. Report actual
aggregate/CI results in the integration receipt; browser rendering, keyboard
behavior, print pagination and live-game validation remain separate checks.

### Bounded Fortification/Spot integration layer

Build 11-15-26.8 adds only the three reviewed definitions and the exact
`heroism-spot` / `luck-spot` pair. Retain the
[source register](../../evidence/wisdom-loadout/fort-spot-sources-2026-11-15.json)
as the frozen investigation bytes: its read-only scope and no-promotion field
describe that earlier stage, while the separate integration receipt records
the later implementation. Do not silently update an old observation, join
Queen's label and description into a synthetic quote, or replace the explicit
Skill/Spot membership evidence with a generic keyword mapping.

Recheck actual source bytes and exact identity, amount, type, selected host,
socket, level, state and proof bindings through public calculation/proof routes;
prior fixture validation is not a trusted prerequisite. Preserve all nine prior
rules and the original direct-source and bounded Chains contracts. The new pair
must not admit other IDs, stats, channels or type combinations. Both fixed Chains
IDs must remain unresolved even if a caller attaches another proof or a direct
source label.

Fortification completeness requires exactly `chains-fortification` and
`queen-fortification`. Spot requires exactly `chains-spot`, `heroism-spot` and
`luck-spot`. Test deletion, renaming, duplication, altered bindings and wrong
source context against these families, retaining the existing INT guard. The
current level-36 complete results must remain `null`, with supported subsets
84 and 7 and the appropriate Chains exclusion. Compare complete result objects,
including counted/excluded inputs and interaction details, rather than checking
only those two numbers. Lower-level applicability and all unaffected results
need their own preservation comparison.

Use an exact outer .8-to-.7 restoration before the existing historical layers;
keep prior scope files, fixed hashes and negative controls intact. Separate
current-state tests must exercise actual .8 production code and inputs. Preserve
all selected data, complete historical bow tuples/results, old evidence and
snapshots. Run the four documented builders and generate a new path-rebased .8
snapshot. Record actual builder, aggregate and draft-update results in the
[receipt](../../evidence/wisdom-loadout/fort-spot-integration-2026-11-15.json);
do not reuse the preceding build's test count or treat source review as browser,
accessibility, print, live-game or release verification.
