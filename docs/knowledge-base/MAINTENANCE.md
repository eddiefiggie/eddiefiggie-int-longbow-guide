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
