"""Exact .7-to-.6 views for the bounded offensive-mechanics text correction.

Current production claims have separate tests. This outer adapter only recovers
the independently pinned .6 inputs for unchanged historical contracts; it does
not turn those historical statements or model scores into current game rules.
"""
import builtins
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import types
import wisdom_fort_spot_preservation as fort_spot


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tools/fixtures/wisdom-offense/scope.json'
BASE_COMMIT = 'cdb39fe7cdfbcbb2d2143c49c88979b008158c28'
BASE_TREE = '11b6e905e2174ea9bcae0ad77c7aaf224e999701'
BASE_FILES = {
    'index.html': (400179, 'b0aa72c322dd01f8505c24d2b8f93a5d784c8463aee562592734f871ebec4d90'),
    'endgame-stacking-audit.html': (408537, '3d805c276c5b7643776b7942899150352d034a58dbf5f13f7ae5b92c6da95cd5'),
    'heroic-crafting-print.html': (4604, 'ba0f84736f259657d44bee13450c5ccea8204a8632a00909ada439f62ed87966'),
    'tools/wisdom_loadout.py': (46507, '315878c9d09c736f87e0ddb3f818f0cacaa9848293f668bffbb111216cc81458'),
    'tools/build_stacking_audit.py': (28086, 'fabd8575dbc8416f31173c432e4895893906f2e06088517ed164382634c3e167'),
}
REVIEWED_PATHS = tuple(BASE_FILES)
PRESERVED_COUNT = 194
PRESERVED_MANIFEST_SHA = 'd0b84a9daadf48cc8494038365c4d5293c26d5f534494c3c4e8ab443545d0e2c'


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def load_scope():
    data = json.loads(FIXTURE.read_text())
    assert data['schema'] == 'wisdom-offense-exact-reversal-v1'
    assert data['repository'] == 'eddiefiggie/eddiefiggie-int-longbow-guide'
    assert data['baseline_commit'] == BASE_COMMIT
    assert data['baseline_tree'] == BASE_TREE
    assert data['approved_branch'] == 'feat/wisdom-loadout-priorities'
    assert (data['baseline_build'], data['current_build']) == ('11-15-26.6', '11-15-26.7')
    assert set(data['files']) == set(BASE_FILES)
    for path, expected in BASE_FILES.items():
        row = data['files'][path]
        assert (row['baseline_bytes'], row['baseline_sha256']) == expected, path
        assert row['reviewed_replacements'], path
    preserved = data['preserved_files']
    assert len(preserved) == PRESERVED_COUNT
    canonical = json.dumps(preserved, sort_keys=True, separators=(',', ':'))
    assert sha(canonical) == PRESERVED_MANIFEST_SHA, 'independently pinned .6 inventory'
    assert not set(preserved) & set(REVIEWED_PATHS)
    return data


def restore_file(path, current, *, scope=None):
    """Accept only exact .7 bytes and reverse unique contexts to fixed .6 bytes."""
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
    assert (len(text.encode()), sha(text)) == (size, digest), (path, 'fixed cdb39fe checkpoint')
    return text


def checkpoint_file_bytes(path):
    """Return exact .6 bytes while checking literal preserved inputs on disk."""
    raw = fort_spot.checkpoint_file_bytes(path)
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
        raw = fort_spot.checkpoint_file_bytes(path)
        assert (len(raw), sha(raw)) == (expected['bytes'], expected['sha256']), path
    return True


def validate_full_reversal():
    scope = load_scope()
    for path in REVIEWED_PATHS:
        restore_file(path, fort_spot.checkpoint_file_bytes(path), scope=scope)
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
def _calculator(source):
    module = _module('_offense_checkpoint_calculator', 'tools/stacking_audit.py', source)
    module.load = lambda: json.loads(checkpoint_file_text('tools/fixtures/endgame-stacking/ledger.json'))
    return module


def historical_calculator():
    # Validate literal dependencies before every access, including cache hits.
    checkpoint_file_bytes('tools/recipe_proofs.py')
    return _calculator(checkpoint_file_bytes('tools/stacking_audit.py'))


@lru_cache(maxsize=1)
def _recipe_renderer(source, calculator):
    return _module('_offense_checkpoint_recipe', 'tools/wisdom_loadout.py', source,
                   {'stacking_audit': calculator})


def historical_recipe_renderer():
    return _recipe_renderer(checkpoint_file_bytes('tools/wisdom_loadout.py'), historical_calculator())


@lru_cache(maxsize=1)
def _audit_renderer(source, calculator, recipe):
    return _module('_offense_checkpoint_audit', 'tools/build_stacking_audit.py', source,
                   {'stacking_audit': calculator, 'wisdom_loadout': recipe})


def historical_audit_renderer():
    return _audit_renderer(checkpoint_file_bytes('tools/build_stacking_audit.py'),
                           historical_calculator(), historical_recipe_renderer())
