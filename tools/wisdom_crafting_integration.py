"""Exact 11-15-26.3-to-fbb1 checkpoint views for crafting evidence integration.

This outer layer preserves the source-finding checkpoint and both older exact
reversal contracts. It never accepts an already-old file as a current file.
Checkpoint views are historical test inputs, not current recipe or mechanics
validation; current semantic tests must read the actual production artifacts.
"""
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tools/fixtures/wisdom-crafting-integration/scope.json'
BASE_COMMIT = 'fbb1c5ed9aca2c1c360147732ac3ba61c77c435e'
BASE_TREE = 'df677f8c9d2cd113b55d0418dd765729924895c6'
BASE_FILES = {
    'index.html': (392823, '281c8e4ce94f28d5d23c345f01d34bfcb0423f73ff90d871d82b7ecf8611f048'),
    'tools/fixtures/endgame-stacking/ledger.json': (367507, '381fe7e81573fdb727a103df020270c5b8e66b560325fc9b8825668878607560'),
    'evidence/endgame-stacking/source-excerpts.json': (276122, '0f13e0875c61c4fb0d5420b6825417f416cb3fa1c18677d24074e3bfd9a77c1f'),
    'endgame-stacking-audit.html': (374382, '0b51824f17b18bcb2533034b653254f411775f898b515d971e1e17e6fcf1e2d7'),
    'heroic-crafting-print.html': (4604, '87ae7532b16452d35dc20ba9419a1dfe2c40e88a76817d20ff6628cc6f7e12c6'),
    'tools/wisdom_loadout.py': (37528, '25a9bc502ae5afe8e9cdbbc48762c674fa2f62459c96b3a91fe9f3438a055d8c'),
    'tools/build_stacking_audit.py': (26317, '699bba973b9f08b2df57e2728534a341935e8390e8be641599b695c75ddee49f'),
}
REVIEWED_PATHS = tuple(BASE_FILES)
ORIGINAL_SCOPES = {
    'tools/fixtures/wisdom-loadout/scope.json': '3a3d34bc5cb2524bf611bfa2128605daf9f3dd554d458a50928f099d80933bd0',
    'tools/fixtures/wisdom-corrections/scope.json': '7a079fd078bf37bf9def7ddd4a67c647a2092206ef0a2ddbfb9823b3da3654ef',
}


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def load_scope():
    data = json.loads(FIXTURE.read_text())
    assert data['schema'] == 'wisdom-crafting-integration-exact-reversal-v1'
    assert data['repository'] == 'eddiefiggie/eddiefiggie-int-longbow-guide'
    assert data['baseline_commit'] == BASE_COMMIT
    assert data['baseline_tree'] == BASE_TREE
    assert data['approved_branch'] == 'feat/wisdom-loadout-priorities'
    assert (data['baseline_build'], data['current_build']) == ('11-15-26.2', '11-15-26.3')
    assert set(data['files']) == set(BASE_FILES)
    for path, digest in ORIGINAL_SCOPES.items():
        assert sha((ROOT / path).read_bytes()) == digest, (path, 'original scope preserved')
    for path, expected in BASE_FILES.items():
        row = data['files'][path]
        assert (row['baseline_bytes'], row['baseline_sha256']) == expected, path
        assert row['reviewed_replacements'], path
    return data


def restore_file(path, current, *, scope=None):
    """Reverse only approved unique contexts, then enforce the fixed checkpoint."""
    data = load_scope() if scope is None else scope
    assert path in BASE_FILES
    row = data['files'][path]
    raw = current if isinstance(current, bytes) else current.encode()
    assert len(raw) == row['current_bytes'] and sha(raw) == row['current_sha256'], path
    text = raw.decode()
    assert row['reviewed_replacements'], path
    for change in reversed(row['reviewed_replacements']):
        assert change['before'] != change['after']
        assert change['after'] and text.count(change['after']) == 1, (path, 'unique exact after-context')
        text = text.replace(change['after'], change['before'], 1)
    size, digest = BASE_FILES[path]
    assert len(text.encode()) == size and sha(text) == digest, (path, 'fixed fbb1 checkpoint')
    return text


def checkpoint_file_bytes(path):
    """Read unaffected files literally; strictly reverse every scoped current file."""
    raw = (ROOT / path).read_bytes()
    return restore_file(path, raw).encode() if path in REVIEWED_PATHS else raw


def checkpoint_file_text(path):
    return checkpoint_file_bytes(path).decode()


def validate_full_reversal():
    scope = load_scope()
    for path in REVIEWED_PATHS:
        restore_file(path, (ROOT / path).read_bytes(), scope=scope)
    return True
