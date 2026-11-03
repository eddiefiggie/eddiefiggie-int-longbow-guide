# INT Longbow Guide

A complete plan for one Dungeons & Dragons Online character: an Intelligence-based longbow archer, levels 1-36 and Reaper 10, built as a reincarnation platform (Rogue 1 / Ranger 9 / ten levels of the past-life class).

**Read it:** https://eddiefiggie.github.io/eddiefiggie-int-longbow-guide/

Every number comes from the [DDO wiki](https://ddowiki.com) page named in the guide's Sources; judgment calls are labelled *build decision*. Written for Update 82.0.1.

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

Edit `index.html`, copy it to `versions/MM-DD-YY.x.html` (x = iteration that day), set the same build number in the line under the `<h1>`, commit. GitHub Pages serves `main` from the repo root.

## Testing

From the repository root, run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools -p 'test_*.py' -v` (Python standard library only).

The [Guide checks workflow](.github/workflows/guide-checks.yml) runs that same discovery command on pull requests, including drafts. It automates the existing internal regression and structural checks; passing them does not certify game mechanics. The workflow uses read-only repository access and does not persist checkout credentials. Pages deployment and branch-protection settings are unchanged.

`tools/test_guide_integrity.py` checks that the current guide matches the snapshot named by its displayed build, IDs are unique, same-page anchors resolve, and guide-relative `href`/`src` files exist. It ignores external URLs and checks neither older snapshots nor game mechanics. Local URLs are resolved from the guide's directory; a `<base>` element needs an explicit resolver update. CSS URLs, `srcset`, and browser rendering are outside these checks. Run them locally before committing; the Pages workflow does not run tests.

## Audits

Every section is checked line by line against the DDO wiki; see [AUDITS.md](AUDITS.md) for dates, scope and corrections, and open an issue if a number does not match its page.
