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
| `tools/bowmodel.py` | The preserved historical per-shot bow model; not a DPS simulation of the current Wisdom loadout |
| `tools/fixtures/wisdom-loadout/selection.json` | Shared current endgame recipe, exact optimizer priorities/constraints and model-only achieved values |
| `tools/build_wisdom_loadout.py` | Generates the current recipe, priority table and one-page rows from that record |

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

## Project maintenance

See the [knowledge base](docs/knowledge-base/README.md) for build principles, evidence limits, open decisions, maintenance checks and a dated release checkpoint.

## Crafting print reference

`heroic-crafting-print.html` is generated from the three complete heroic crafting blocks in `index.html`, preserving their markup and pinned citations. After changing the Guide or its build stamp, run `python3 tools/build_crafting_sheet.py`; the full suite rejects a stale sheet. It excludes the session-only purchase checkoff. Actual print pagination must be reviewed separately from structural tests.
