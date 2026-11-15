"""Render only the three explicit Wisdom selection blocks in index.html."""
import argparse
from pathlib import Path
from wisdom_loadout import ROOT, load, replace_blocks, validate


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check freshness without writing any file')
    args = parser.parse_args(argv)
    data = load()
    result = validate(data)
    path = ROOT / 'index.html'
    old = path.read_text(encoding='utf-8')
    new = replace_blocks(old, data)
    if args.check:
        if old != new:
            print('Wisdom loadout blocks are stale; no file was changed.')
            return 1
        print('Wisdom loadout blocks are current; model-only validation passed.')
        return 0
    if old != new:
        path.write_text(new, encoding='utf-8')
    print(f"Rendered Wisdom loadout blocks: {result['items']} items, {result['artifacts']} artifact, {result['sockets']} sockets. No mechanics certification implied.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
