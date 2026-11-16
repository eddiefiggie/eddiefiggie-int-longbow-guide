"""Exact bounded correction-to-PR47 reversal; not a mechanics certificate.

The original Wisdom scope and its old hashes remain immutable. Historical
consumers first restore these reviewed corrections, then apply that old scope.
Current recipe/mechanics tests must still use the actual production files.
"""
import hashlib
import json
from pathlib import Path
import wisdom_crafting_integration as crafting


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tools/fixtures/wisdom-corrections/scope.json'
BASE_COMMIT = '564d5259f715962851fd1a4fcbc62820785f4d56'
BASE_TREE = '91be55a45a88d76e80122a3fdaaf7d6d7bd565ab'
BASE_FILES = {
    'index.html': (390256, 'ac66f2ca703abdc6ddb820ae05d0f30e5b9dc337837c509c5c9771108947cf0d'),
    'tools/fixtures/endgame-stacking/ledger.json': (366635, 'e9a2864f23e8fb033fbada0e3813a9f77bd09c6bf9da05b9b60cf3113009c533'),
    'endgame-stacking-audit.html': (373553, 'fd8ed376175c465122d4ca37df7d1aad01ae0973ffd4b2cf760bebf4fa80b13c'),
    'tools/wisdom_loadout.py': (36879, '71268b7b401865652074a006e6b8208d5b7a05620dd8df167a39f9761e3a79c6'),
    'heroic-crafting-print.html': (4604, 'c913ad13fc3f44437adf42cb4faff75a3f7224c6054a27e65f546b5ca175969d'),
}
REVIEWED_PATHS = tuple(BASE_FILES)
ORIGINAL_SCOPE_SHA = '3a3d34bc5cb2524bf611bfa2128605daf9f3dd554d458a50928f099d80933bd0'


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def load_scope():
    scope = json.loads(FIXTURE.read_text())
    assert scope['schema'] == 'wisdom-corrections-exact-reversal-v1'
    assert scope['baseline_commit'] == BASE_COMMIT
    assert scope['baseline_tree'] == BASE_TREE
    assert scope['approved_branch'] == 'feat/wisdom-loadout-priorities'
    assert set(scope['files']) == set(BASE_FILES)
    assert sha((ROOT / 'tools/fixtures/wisdom-loadout/scope.json').read_bytes()) == ORIGINAL_SCOPE_SHA
    for path, (size, digest) in BASE_FILES.items():
        row = scope['files'][path]
        assert (row['baseline_bytes'], row['baseline_sha256']) == (size, digest), path
    return scope


def restore_file(path, current, *, scope=None):
    """Reject old, mixed and extra edits; reverse only unique exact contexts."""
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
    assert len(text.encode()) == size and sha(text) == digest, (path, 'fixed PR47 predecessor')
    return text


def original_file_text(path):
    return restore_file(path, crafting.checkpoint_file_bytes(path))


def validate_full_reversal():
    scope = load_scope()
    for path in REVIEWED_PATHS:
        restore_file(path, crafting.checkpoint_file_bytes(path), scope=scope)
    return True
