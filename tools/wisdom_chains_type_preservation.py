"""Exact .9-to-.8 views for the two bounded Chains type qualifications.

The independent .8 hashes and complete-result fixture are historical contracts.
These adapters restore inputs and their matching proof dependencies before old
assertions run; separate tests exercise actual .9 production behavior. Neither
kind of software check authenticates source observations or live-game behavior.
"""
import builtins
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import types


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tools/fixtures/wisdom-chains-type/scope.json'
BASE_COMMIT = '30ce02c4e823ae92a1cd2dde4db99fa60ad825d9'
BASE_TREE = '21b6dcfe104cf357877e8e5c8a4335d9547f99c7'
BASE_FILES = {
    'index.html': (412084, 'ceb70a07fac6fd4e84e0d7f9c0f54156dd4b4366b1c38d0baf60ed6356f75a2c'),
    'tools/fixtures/endgame-stacking/ledger.json': (417507, '05c50d3c87c4e2ce88a30aa5820bc19d72b0151ab2c53bc9950f3fb48ccd43c5'),
    'evidence/endgame-stacking/source-excerpts.json': (318800, '10446af3dfe8f7bea6d0706f80fd091693d847049b8c126c0071cce63de35177'),
    'endgame-stacking-audit.html': (431087, '298d3302898d366e0dab0b452aa2fd99832e53d33f925f082b6d7c3414c042f1'),
    'heroic-crafting-print.html': (4604, 'ea138fd845fc7e6a32a03ac2a5951c77360a50a373f0a44cc994d3f1eab27cd0'),
    'tools/wisdom_loadout.py': (49477, 'ca3b27ec91b329ea65ba28858936024afee54888aaa6035bb9b56841a288a21c'),
    'tools/build_stacking_audit.py': (29812, '1f2e100ff4bba98a88bbabb1daed588b1a4cb6e6061d4473d273e4c9c6629ec9'),
    'tools/stacking_audit.py': (26643, '4ef3706d84ec45d0a8cd5ab01abe886067f17682a672938ef824375702308994'),
    'tools/recipe_proofs.py': (16152, 'b4c2b4fd95a0a9de4b5f8155245ba8934a8f1ae89c3e2f1d7e8eac545bb627ec'),
    'tools/fort_spot_proofs.py': (17997, 'd5a4bc9b9fdde6e7ab6fba0af1692f3b935671d8f7add89160b7f1fcf911711d'),
}
REVIEWED_PATHS = tuple(BASE_FILES)
PRESERVED_COUNT = 201
PRESERVED_MANIFEST_SHA = '3bb2ab96e7d7fb09ae08bcf4d90f93bd787c216a4fd84ba54b1f2e459444edbf'


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def load_scope():
    data = json.loads(FIXTURE.read_text())
    assert data['schema'] == 'wisdom-chains-type-exact-reversal-v1'
    assert data['repository'] == 'eddiefiggie/eddiefiggie-int-longbow-guide'
    assert data['baseline_commit'] == BASE_COMMIT
    assert data['baseline_tree'] == BASE_TREE
    assert data['approved_branch'] == 'feat/wisdom-loadout-priorities'
    assert (data['baseline_build'], data['current_build']) == ('11-15-26.8', '11-15-26.9')
    assert set(data['files']) == set(BASE_FILES)
    for path, expected in BASE_FILES.items():
        row = data['files'][path]
        assert (row['baseline_bytes'], row['baseline_sha256']) == expected, path
        assert row['reviewed_replacements'], path
    preserved = data['preserved_files']
    assert len(preserved) == PRESERVED_COUNT
    canonical = json.dumps(preserved, sort_keys=True, separators=(',', ':'))
    assert sha(canonical) == PRESERVED_MANIFEST_SHA, 'independently pinned .8 inventory'
    assert not set(preserved) & set(REVIEWED_PATHS)
    return data


def restore_file(path, current, *, scope=None):
    """Accept only exact .9 bytes and reverse unique contexts to fixed .8 bytes."""
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
    assert (len(text.encode()), sha(text)) == (size, digest), (path, 'fixed 30ce02c checkpoint')
    return text


def checkpoint_file_bytes(path):
    """Return exact .8 bytes, rechecking literal historical files on disk."""
    raw = (ROOT / path).read_bytes()
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
        raw = (ROOT / path).read_bytes()
        assert (len(raw), sha(raw)) == (expected['bytes'], expected['sha256']), path
    return True


def validate_full_reversal():
    scope = load_scope()
    for path in REVIEWED_PATHS:
        restore_file(path, (ROOT / path).read_bytes(), scope=scope)
    return validate_preserved_files()


def _module(name, path, source, dependencies=None):
    """Bind this restored module's imports without replacing global modules."""
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
def _recipe_proofs(source):
    return _module('_chains_type_checkpoint_recipe_proofs', 'tools/recipe_proofs.py', source)


def historical_recipe_proofs():
    return _recipe_proofs(checkpoint_file_bytes('tools/recipe_proofs.py'))


@lru_cache(maxsize=1)
def _fort_spot_proofs(source):
    return _module('_chains_type_checkpoint_fort_spot_proofs', 'tools/fort_spot_proofs.py', source)


def historical_fort_spot_proofs():
    return _fort_spot_proofs(checkpoint_file_bytes('tools/fort_spot_proofs.py'))


@lru_cache(maxsize=1)
def _calculator(source, recipes, definitions):
    module = _module('_chains_type_checkpoint_calculator', 'tools/stacking_audit.py', source,
                     {'recipe_proofs': recipes, 'fort_spot_proofs': definitions})
    module.load = lambda: json.loads(checkpoint_file_text('tools/fixtures/endgame-stacking/ledger.json'))
    return module


def historical_calculator():
    # Revalidate the engine and both changed proof dependencies on every access.
    return _calculator(checkpoint_file_bytes('tools/stacking_audit.py'),
                       historical_recipe_proofs(), historical_fort_spot_proofs())


@lru_cache(maxsize=1)
def _recipe_renderer(source, calculator):
    return _module('_chains_type_checkpoint_recipe', 'tools/wisdom_loadout.py', source,
                   {'stacking_audit': calculator})


def historical_recipe_renderer():
    return _recipe_renderer(checkpoint_file_bytes('tools/wisdom_loadout.py'), historical_calculator())


@lru_cache(maxsize=1)
def _audit_renderer(source, calculator, recipe):
    return _module('_chains_type_checkpoint_audit', 'tools/build_stacking_audit.py', source,
                   {'stacking_audit': calculator, 'wisdom_loadout': recipe})


def historical_audit_renderer():
    return _audit_renderer(checkpoint_file_bytes('tools/build_stacking_audit.py'),
                           historical_calculator(), historical_recipe_renderer())
