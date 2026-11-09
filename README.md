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
| `tools/bowmodel.py` | The per-shot bow damage model behind the "Bow damage model" section (`python3 bowmodel.py`) |

## Related

- [DDO Loadout Optimizer](https://eddiefiggie.github.io/ddo-loadout-optimizer/) — the gear solver the kits were run on (bundle *INT Longbow R10 v3*)
- [ddo-gear-planner](https://github.com/eddiefiggie/ddo-gear-planner) — item and crafting data

## Updating

Edit `index.html` and set its displayed build to `MM-DD-YY.x` (x = iteration that day). Run `python3 tools/build_snapshot.py` to generate the matching file in `versions/`, with relative image and print links rebased for that directory. Do not byte-copy the index: that breaks snapshot asset paths. Regenerate the print reference with `python3 tools/build_crafting_sheet.py` when its source or build stamp changes. Run the checks before committing. GitHub Pages serves `main` from the repo root.

## Testing

From the repository root, run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools -p 'test_*.py' -v` (Python standard library; Node.js is also required for the purchase-checkoff JavaScript execution tests).

The [Guide checks workflow](.github/workflows/guide-checks.yml) runs that same discovery command on pull requests, including drafts. It automates the existing internal regression and structural checks; passing them does not certify game mechanics. The workflow uses read-only repository access and does not persist checkout credentials. Pages deployment and branch-protection settings are unchanged.

`tools/test_guide_integrity.py` checks that the current snapshot exactly matches the deterministic builder output, IDs are unique, same-page anchors resolve, and local `href`/`src` files exist. `tools/test_snapshot_paths.py` also resolves the current snapshot's assets and fragment links from its own directory and rejects path/content regressions. These checks ignore external URLs and validate neither older snapshots nor game mechanics. A `<base>` element needs an explicit resolver update. CSS URLs, `srcset`, and browser rendering are outside these checks. Run them locally before committing; the Pages deployment workflow does not run tests.

## Audits

Every section is checked line by line against the DDO wiki; see [AUDITS.md](AUDITS.md) for dates, scope and corrections, and open an issue if a number does not match its page.

## Project maintenance

See the [knowledge base](docs/knowledge-base/README.md) for build principles, evidence limits, open decisions, maintenance checks and a dated release checkpoint.

## Crafting print reference

`heroic-crafting-print.html` is generated from the three complete heroic crafting blocks in `index.html`, preserving their markup and pinned citations. After changing the Guide or its build stamp, run `python3 tools/build_crafting_sheet.py`; the full suite rejects a stale sheet. It excludes the session-only purchase checkoff. Actual print pagination must be reviewed separately from structural tests.
