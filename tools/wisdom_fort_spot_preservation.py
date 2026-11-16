"""Exact .8-to-.7 views for the bounded Fortification/Spot qualification.

Current production behavior has separate tests. This outer adapter only recovers
the independently pinned .7 inputs for unchanged historical contracts. Complete
old-input results and archived model tuples are preserved, not newly certified
as live-game behavior or complete current character totals.
"""
import builtins
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import types
import wisdom_chains_type_preservation as chains_type


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tools/fixtures/wisdom-fort-spot/scope.json'
BASE_COMMIT = '72db151c4f881c08844d273caee2914ddc736641'
BASE_TREE = '573c0b26ac30dce65a3d4fcf6107a38dc5c8058d'
BASE_FILES = {
    'index.html': (409084, 'c093cc88d07e53b4b17469515b9e3e820b703152767dccfa4febd73b4bda97df'),
    'tools/fixtures/endgame-stacking/ledger.json': (397408, 'cb71531a07b73697b0af1bccf6fe330e10e0db900a7f194f79036ce3ccf2da0a'),
    'evidence/endgame-stacking/source-excerpts.json': (300997, '8d889810c18796d108ede267699c65efa84b16fecf07ddadb120640b5ab1a70d'),
    'endgame-stacking-audit.html': (409338, '52e383ac1e9f5b30a33c588dff0027cbe29d864026afe0f1578bdf8e9093d1be'),
    'heroic-crafting-print.html': (4604, '503b3831d44001bde975338e9124d2aa08cb8aa98324b07a40c2ce6dff339058'),
    'tools/wisdom_loadout.py': (47024, '11e5620f5a8f2065a18e13045573c1e323519329645aa3a95af4a85659c7b39e'),
    'tools/build_stacking_audit.py': (28518, '4009b6b4fce269af1bffb9c1be9f95556b062c032b62af1c690fb96560be8841'),
    'tools/stacking_audit.py': (23316, '92a32e9d4d2fd78e55640ec16834b3c7ec97d8501e4daa03adbf28f81c7e1998'),
}
REVIEWED_PATHS = tuple(BASE_FILES)
PRESERVED_COUNT = 197
PRESERVED_MANIFEST_SHA = 'c87c50446facf1770026b4eab2a7d53c64bffc91756021c515c0644a21b46da1'


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def load_scope():
    data = json.loads(FIXTURE.read_text())
    assert data['schema'] == 'wisdom-fort-spot-exact-reversal-v1'
    assert data['repository'] == 'eddiefiggie/eddiefiggie-int-longbow-guide'
    assert data['baseline_commit'] == BASE_COMMIT
    assert data['baseline_tree'] == BASE_TREE
    assert data['approved_branch'] == 'feat/wisdom-loadout-priorities'
    assert (data['baseline_build'], data['current_build']) == ('11-15-26.7', '11-15-26.8')
    assert set(data['files']) == set(BASE_FILES)
    for path, expected in BASE_FILES.items():
        row = data['files'][path]
        assert (row['baseline_bytes'], row['baseline_sha256']) == expected, path
        assert row['reviewed_replacements'], path
    preserved = data['preserved_files']
    assert len(preserved) == PRESERVED_COUNT
    canonical = json.dumps(preserved, sort_keys=True, separators=(',', ':'))
    assert sha(canonical) == PRESERVED_MANIFEST_SHA, 'independently pinned .7 inventory'
    assert not set(preserved) & set(REVIEWED_PATHS)
    return data


def restore_file(path, current, *, scope=None):
    """Accept only exact .8 bytes and reverse unique contexts to fixed .7 bytes."""
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
    assert (len(text.encode()), sha(text)) == (size, digest), (path, 'fixed 72db151 checkpoint')
    return text


def checkpoint_file_bytes(path):
    """Return exact .7 bytes while checking literal preserved inputs on disk."""
    raw = chains_type.checkpoint_file_bytes(path)
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
        raw = chains_type.checkpoint_file_bytes(path)
        assert (len(raw), sha(raw)) == (expected['bytes'], expected['sha256']), path
    return True


def validate_full_reversal():
    scope = load_scope()
    for path in REVIEWED_PATHS:
        restore_file(path, chains_type.checkpoint_file_bytes(path), scope=scope)
    return validate_preserved_files()


def _module(name, path, source, dependencies=None):
    """Bind only this restored module's imports; do not replace sys.modules."""
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
def _calculator(source, recipes):
    module = _module('_fort_spot_checkpoint_calculator', 'tools/stacking_audit.py', source,
                     {'recipe_proofs': recipes})
    module.load = lambda: json.loads(checkpoint_file_text('tools/fixtures/endgame-stacking/ledger.json'))
    return module


def historical_calculator():
    # Validate exact historical dependencies before every access, including cache hits.
    checkpoint_file_bytes('tools/recipe_proofs.py')
    return _calculator(checkpoint_file_bytes('tools/stacking_audit.py'),
                       chains_type.historical_recipe_proofs())


@lru_cache(maxsize=1)
def _recipe_renderer(source, calculator):
    return _module('_fort_spot_checkpoint_recipe', 'tools/wisdom_loadout.py', source,
                   {'stacking_audit': calculator})


def historical_recipe_renderer():
    return _recipe_renderer(checkpoint_file_bytes('tools/wisdom_loadout.py'), historical_calculator())


@lru_cache(maxsize=1)
def _audit_renderer(source, calculator, recipe):
    return _module('_fort_spot_checkpoint_audit', 'tools/build_stacking_audit.py', source,
                   {'stacking_audit': calculator, 'wisdom_loadout': recipe})


def historical_audit_renderer():
    return _audit_renderer(checkpoint_file_bytes('tools/build_stacking_audit.py'),
                           historical_calculator(), historical_recipe_renderer())
