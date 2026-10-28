# INT Longbow Guide

A complete plan for one Dungeons & Dragons Online character: an Intelligence-based longbow archer, levels 1-36 and Reaper 10, built as a reincarnation platform (Rogue 1 / Ranger 9 / ten levels of the past-life class).

**Read it:** https://eddiefiggie.github.io/eddiefiggie-int-longbow-guide/

Every number comes from the [DDO wiki](https://ddowiki.com) page named in the guide's Sources; judgment calls are labelled *build decision*. Written for Update 82.0.1.

## Layout

| Path | What |
|---|---|
| `index.html` | The current guide (self-contained page; images in `img/`) |
| `versions/` | Every published version, one file each (`v32.html`, …) |
| `img/` | Cover art and the six enhancement/destiny tree images (rendered on DDO BuildHub) |
| `tools/bowmodel.py` | The per-shot bow damage model behind the "Bow damage model" section (`python3 bowmodel.py`) |

## Related

- [DDO Loadout Optimizer](https://eddiefiggie.github.io/ddo-loadout-optimizer/) — the gear solver the kits were run on (bundle *INT Longbow R10 v3*)
- [ddo-gear-planner](https://github.com/eddiefiggie/ddo-gear-planner) — item and crafting data

## Updating

Edit `index.html`, copy it to `versions/vNN.html`, bump the version in the `<h1>`, commit. GitHub Pages serves `main` from the repo root.
