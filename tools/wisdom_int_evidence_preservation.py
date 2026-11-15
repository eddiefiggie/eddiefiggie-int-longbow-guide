"""Exact .5-to-.4 views for the approved seven-input Intelligence integration.

Historical views reverse independently pinned current bytes before any older
contract runs. New source evidence and actual-current acceptance tests remain
separate: no historical view is a certificate for the selected game's totals.
"""
import builtins
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import types
import wisdom_int_stacking_preservation as int_stacking


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tools/fixtures/wisdom-int-evidence/scope.json'
BASE_COMMIT = 'd05e7865da76a47a92741cb79029a35fbd0f7712'
BASE_TREE = 'c1b236d5cafc7695af9ec77410d329c7a0b9cc44'
BASE_FILES = {
    'index.html': (396989, 'c38907cefa72151a10b30795860d9ef80c1dcb03dfb60435ff4a27987e1d5c70'),
    'tools/fixtures/endgame-stacking/ledger.json': (380535, 'f0f22a13abdec97d1faa571f37b9016d5d3da571f6759714f570baac7e051318'),
    'evidence/endgame-stacking/source-excerpts.json': (287361, 'd57c27ef815eccd2876a13f73ca3ebb27c027c86e699d9b58adb6170b3c18b05'),
    'endgame-stacking-audit.html': (388453, '0421053e5a8fbb0e732302ffdcd41bee5f18acaf9e32aaad7f96e2252ea2a746'),
    'heroic-crafting-print.html': (4604, '77b7310277058efc5d655a49f46b0191e6c02cf5a11209d9fc929184d1a9c6e8'),
    'tools/wisdom_loadout.py': (42925, 'efd8dc5e3c1da287c27f212ecc2fdf4f33159576510ae0c05b9485c3f9217394'),
    'tools/build_stacking_audit.py': (27062, '77cdeb37b969f0bceeea0e3cb4debe3d7c7dce1eafb6bbdc3a62c8a977b19956'),
}
REVIEWED_PATHS = tuple(BASE_FILES)
PRESERVED_COUNT = 61
PRESERVED_MANIFEST_SHA = '02d6c9e66c513a1e2bbbc409f7f1631bb7b123c09ce99b5dab61330dd96f8263'


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def load_scope():
    data = json.loads(FIXTURE.read_text())
    assert data['schema'] == 'wisdom-int-evidence-exact-reversal-v1'
    assert data['repository'] == 'eddiefiggie/eddiefiggie-int-longbow-guide'
    assert data['baseline_commit'] == BASE_COMMIT
    assert data['baseline_tree'] == BASE_TREE
    assert data['approved_branch'] == 'feat/wisdom-loadout-priorities'
    assert (data['baseline_build'], data['current_build']) == ('11-15-26.4', '11-15-26.5')
    assert set(data['files']) == set(BASE_FILES)
    for path, expected in BASE_FILES.items():
        row = data['files'][path]
        assert (row['baseline_bytes'], row['baseline_sha256']) == expected, path
        assert row['reviewed_replacements'], path
    preserved = data['preserved_files']
    assert len(preserved) == PRESERVED_COUNT
    canonical = json.dumps(preserved, sort_keys=True, separators=(',', ':'))
    assert sha(canonical) == PRESERVED_MANIFEST_SHA, 'independently pinned preserved inventory'
    assert not set(preserved) & set(REVIEWED_PATHS)
    return data


def restore_file(path, current, *, scope=None):
    """Require exact current bytes and unique hunks; never accept old/mixed input."""
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
    assert len(text.encode()) == size and sha(text) == digest, (path, 'fixed d05e786 checkpoint')
    return text


def checkpoint_file_bytes(path):
    """Return strict .4 bytes; protected unaffected paths must stay literal."""
    raw = int_stacking.checkpoint_file_bytes(path)
    if path in REVIEWED_PATHS:
        return restore_file(path, raw).encode()
    preserved = load_scope()['preserved_files']
    if path in preserved:
        expected = preserved[path]
        assert (len(raw), sha(raw)) == (expected['bytes'], expected['sha256']), path
    return raw


def checkpoint_file_text(path):
    return checkpoint_file_bytes(path).decode()


def validate_preserved_files():
    for path, expected in load_scope()['preserved_files'].items():
        raw = int_stacking.checkpoint_file_bytes(path)
        assert (len(raw), sha(raw)) == (expected['bytes'], expected['sha256']), path
    return True


def validate_full_reversal():
    scope = load_scope()
    for path in REVIEWED_PATHS:
        restore_file(path, int_stacking.checkpoint_file_bytes(path), scope=scope)
    return validate_preserved_files()


def _module(name, path, source, dependencies=None):
    """Bind explicit checkpoint dependencies without changing sys.modules."""
    imports = dependencies or {}
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / path)

    def import_checkpoint(name, globals=None, locals=None, fromlist=(), level=0):
        if level == 0 and name in imports:
            return imports[name]
        return builtins.__import__(name, globals, locals, fromlist, level)

    module.__dict__['__builtins__'] = {**vars(builtins), '__import__': import_checkpoint}
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    return module


@lru_cache(maxsize=1)
def _calculator(source):
    module = _module('_int_evidence_checkpoint_calculator', 'tools/stacking_audit.py', source)
    module.load = lambda: json.loads(checkpoint_file_text('tools/fixtures/endgame-stacking/ledger.json'))
    return module


def historical_calculator():
    # Always revalidate actual bytes even if the compiled checkpoint is cached.
    return _calculator(checkpoint_file_bytes('tools/stacking_audit.py'))


@lru_cache(maxsize=1)
def _recipe_renderer(source, calculator):
    return _module('_int_evidence_checkpoint_recipe', 'tools/wisdom_loadout.py', source,
                   {'stacking_audit': calculator})


def historical_recipe_renderer():
    return _recipe_renderer(checkpoint_file_bytes('tools/wisdom_loadout.py'), historical_calculator())


@lru_cache(maxsize=1)
def _audit_renderer(source, calculator, recipe):
    return _module('_int_evidence_checkpoint_audit', 'tools/build_stacking_audit.py', source,
                   {'stacking_audit': calculator, 'wisdom_loadout': recipe})


def historical_audit_renderer():
    return _audit_renderer(checkpoint_file_bytes('tools/build_stacking_audit.py'),
                           historical_calculator(), historical_recipe_renderer())
