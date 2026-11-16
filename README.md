# INT Longbow Guide

A complete plan for one Dungeons & Dragons Online character: an Intelligence-based longbow archer, levels 1-36 and Reaper 10, built as a reincarnation platform (Rogue 1 / Ranger 9 / ten levels of the past-life class).

**Read it:** https://eddiefiggie.github.io/eddiefiggie-int-longbow-guide/

Source-backed claims name their [DDO wiki](https://ddowiki.com) pages; model-only arithmetic, relayed observations and missing evidence are distinguished in the Guide and audit. Judgment calls are labelled *build decision*. Written for Update 82.0.1.

## Layout

| Path | What |
|---|---|
| `index.html` | The current guide (self-contained page; images in `img/`) |
| `versions/` | Every published build, one file each, named by build number (`10-29-26.8.html`; earlier ones `v32.html` … `v44.html`) |
| `img/` | Cover art and the six enhancement/destiny tree images (rendered on DDO BuildHub) |
| `tools/bowmodel.py` | The preserved historical speed-adjusted bow comparison model; not calibrated DPS or a simulation of the current Wisdom loadout |
| `tools/fixtures/wisdom-loadout/selection.json` | Shared current endgame recipe, exact optimizer priorities/constraints and model-only achieved values |
| `tools/build_wisdom_loadout.py` | Generates the current recipe, priority table and one-page rows from that record |
| `tools/recipe_proofs.py` | Bounded, source-supported recipe proofs for the four selected Chains IDs; not a general inference or stacking engine |
| `tools/chains_type_proofs.py` | Exact Wiki/Nexus recipe bindings for the two selected Chains type definitions, preserving missing numeric fields and source limits |
| `tools/wisdom_ability_proofs.py` | Eight exact WIS/CON definition bindings, four named pairs and complete-family safeguards that retain the conflicting Skull |
| `tools/wisdom_doubleshot_proofs.py` | One selected Quickblade definition, six exact native Doubleshot pairs and five-member family/applicability safeguards |
| `tools/stacking_audit.py` | Source-gated selected-gear arithmetic with exact definition, family and positive-interaction checks; not a universal stacking default or DPS simulator |

## Related

- [DDO Loadout Optimizer](https://eddiefiggie.github.io/ddo-loadout-optimizer/) — the gear solver; the current exact query and practical manual refinements are retained in the [Wisdom loadout record](docs/knowledge-base/WISDOM-ARTIFACT-LOADOUT.md), separate from historical bundles
- [ddo-gear-planner](https://github.com/eddiefiggie/ddo-gear-planner) — item and crafting data

## Updating

Edit `index.html` and set its displayed build to `MM-DD-YY.x` (x = iteration that day). The current Wisdom recipe, priorities and one-page summary are generated: update their shared selection record and provenance deliberately, then run `python3 tools/build_wisdom_loadout.py`; do not hand-edit those marker blocks. Reconcile the selected evidence ledger without upgrading unsupported claims, then run `python3 tools/build_stacking_audit.py`. Regenerate the print reference with `python3 tools/build_crafting_sheet.py`, then run `python3 tools/build_snapshot.py` to create the matching new file in `versions/`, with relative image, evidence and print links rebased. Do not byte-copy the index or overwrite an existing published snapshot. Run the checks before committing. GitHub Pages serves `main` from the repo root; a local update or PR is not a deployment.

## Testing

From the repository root, run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools -p 'test_*.py' -v` (Python standard library; Node.js is also required for the purchase-checkoff JavaScript execution tests).

The [Guide checks workflow](.github/workflows/guide-checks.yml) runs that same discovery command on pull requests, including drafts. It automates the existing internal regression and structural checks; passing them does not certify game mechanics. The workflow uses read-only repository access and does not persist checkout credentials. Pages deployment and branch-protection settings are unchanged.

`tools/test_guide_integrity.py` checks that the current snapshot exactly matches the deterministic builder output, IDs are unique, same-page anchors resolve, and local `href`/`src` files exist. `tools/test_snapshot_paths.py` also resolves the current snapshot's assets and fragment links from its own directory and rejects path/content regressions. These checks ignore external URLs and validate neither older snapshots nor game mechanics. A `<base>` element needs an explicit resolver update. CSS URLs, `srcset`, and browser rendering are outside these checks. Run them locally before committing; the Pages deployment workflow does not run tests.

## Audits

See [AUDITS.md](AUDITS.md) for dated Wiki checks, source scope, corrections and unresolved claims. Internal regression tests and optimizer arithmetic are not blanket mechanics certification; open an issue if a number does not match its stated source.

The [scoped offensive-mechanics inventory](evidence/wisdom-loadout/offensive-mechanics-2026-11-15.json)
records the current ability-modifier, imbue, critical-progression, alacrity and
Doubleshot corrections separately from preserved historical experiments. Its
source register contains transcribed browser observations and paraphrases, not
an exported raw DOM packet or new calculator-qualified component records.

### Current draft: selected-gear Doubleshot evidence

Build **11-16-26.2** qualifies one **Quickblade 15 Artifact Doubleshot**
contribution and adds exactly six named interactions among the four native
bonuses. Four existing Artifact-rule relationships complete the five-member
family: **9 Enhancement + 3 Quality + 5 Insight + 3 Profane + 15 Artifact =
35 percentage points** of selected-gear Doubleshot at the unchanged kit floor
of **level 36**. Level-35 full-kit results remain withheld. This is the same
gear contribution with improved evidence, not a new 35-point character gain.

Quickblade requires three distinct equipped hosts: the goggles' ordinary
Colorless socket, Chains' separately crafted Green socket, and Yeenoghu's
Green socket. Each augment is ML30; other selected fills make the whole kit
ML36. One three-piece set gives one reward. The selected configuration credits
no native named-set bonus on those hosts that Quickblade would suppress; this
does not establish an owned item's upgrade state. See the
[placement record](docs/knowledge-base/WISDOM-ARTIFACT-LOADOUT.md#current-selected-gear-doubleshot-integration--build-11-16-262).

The [source packet](evidence/wisdom-loadout/doubleshot-sources-2026-11-16.json)
keeps actual Wiki observations, reused-source identities and the Stack caveat.
The closed 17-rule profile is not a universal stacking default or a client test.
INT 37, WIS 18, CON subset 17/full `null`, Fortification 226 and direct Spot 27
remain unchanged. The [integration receipt](evidence/wisdom-loadout/doubleshot-integration-2026-11-16.json)
records actual precommit verification; [draft PR #47](https://github.com/eddiefiggie/eddiefiggie-int-longbow-guide/pull/47)
records the delivered commit and its CI outcome. A draft is not a published release.

### Historical .1 checkpoint: bounded Wisdom and Constitution evidence

Build **11-16-26.1** integrates eight standing-gear definitions and four exact
positive pairs. At the unchanged level-36 kit floor, selected-gear **Wisdom is
18** (`15 + 2 + 1`), while **Constitution has a supported subset of 17**
(`7 + 3 + 4 + 2 + 1`) and a complete result of `null`. The conflicting Skull
remains present and excluded, including from every public pair proof. Its
modeled 32 and own-page 33 Constitution cases remain separate and unchanged.

Exact three-member Wisdom and six-member Constitution guards prevent an omitted
or changed input from manufacturing completeness. Existing **INT 37,
Fortification 226% and direct Spot 27** remain unchanged; level-35 full-kit
results stay incomplete. These are existing gear contributions, not new ability
points, whole-character scores or HP/Spot/Will/DPS results.

The [source register](evidence/wisdom-loadout/wisdom-con-sources-2026-11-16.json)
preserves the completed audit's original observations, reused-source references,
Skull conflict and Stack caveat. The
[integration receipt](evidence/wisdom-loadout/wisdom-con-integration-2026-11-16.json)
records this later authorized change and actual verification/draft status.

### Historical .9 checkpoint: completed selected Fortification and Spot families

Build **11-15-26.9** qualifies the existing Chains **142 Enhancement
Fortification** and **20 Competence Spot** recipe contributions, using retained
Wiki values/host evidence and two exact Legendary recipe type definitions from
DDO Nexus. It adds only the Chains/Heroism and Chains/Luck Spot interactions.
At the unchanged level-36 kit floor, the derived selected-gear totals are
**226% Fortification** (`142 + 84`) and **+27 direct Spot** (`20 + 4 + 3`);
**+37 selected-gear INT** is unchanged. The level-35 full-kit results remain
incomplete. These are the existing gear sums, not additional character gains.

The [Chains type register](evidence/wisdom-loadout/chains-type-sources-2026-11-15.json)
retains the exact Nexus URLs, Spot Extra variant, observed markup and absent
numeric/client-version fields. Nexus is an unaffiliated beta reference; this is
a bounded multi-source derivation, not a primary client test or a universal
stacking rule. Whole-character scores and other mechanics gaps remain separate.
See the [integration receipt](evidence/wisdom-loadout/chains-type-integration-2026-11-15.json)
for actual verification and draft status.

### Historical .8 checkpoint: bounded Fortification and Spot evidence

Build **11-15-26.8** binds three selected definitions: Queen's 84 Insight
Fortification, Greater Heroism's 4 Morale Spot and Good Luck's 3 Luck Spot.
One named Heroism/Luck Spot interaction supports their combined **7**. At the
selected kit's level-36 applicability floor, **84 Fortification and 7 direct
Spot are supported subsets**; both complete selected-gear totals remain
`null` because the Chains inputs remain unknown and excluded. These are
existing contributions with improved evidence, not additional character bonuses.

The [new source register](evidence/wisdom-loadout/fort-spot-sources-2026-11-15.json)
retains the fresh review's 16 scoped browser observations, including separate
tooltip labels, exact fragments, category membership and provenance limits.
The [integration receipt](evidence/wisdom-loadout/fort-spot-integration-2026-11-15.json)
records verification and draft-update status separately. The existing closed INT
rule and family safeguards remain; this adds one exact Spot pair and bounded
Fortification/Spot completeness guards, not a general stacking default.

## Project maintenance

See the [knowledge base](docs/knowledge-base/README.md) for build principles, evidence limits, open decisions, maintenance checks and a dated release checkpoint.

## Crafting print reference

`heroic-crafting-print.html` is generated from the three complete heroic crafting blocks in `index.html`, preserving their markup and pinned citations. After changing the Guide or its build stamp, run `python3 tools/build_crafting_sheet.py`; the full suite rejects a stale sheet. It excludes the session-only purchase checkoff. Actual print pagination must be reviewed separately from structural tests.
