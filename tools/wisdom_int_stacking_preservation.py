"""Exact .6-to-.5 checkpoint views for the scoped Intelligence interaction rule.

Only the independently pinned .5 bytes may reach historical tests. Actual .6
mechanics and source-negative checks live separately; a restored historical
module is never a substitute for testing the current production engine.
"""
import builtins
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import types
import wisdom_offense_preservation as offense
import wisdom_chains_type_preservation as chains_type


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tools/fixtures/wisdom-int-stacking/scope.json'
BASE_COMMIT = 'b83e6a9251d743ecae39d0301d177a08de54f93c'
BASE_TREE = 'b1b39ce3a38017c67ffd4ea39a9965175c88a243'
BASE_FILES = {
    'index.html': (398279, '335c4ec217ed0585a3bb82447ea2cbae2650aaa423e32e6015b0963cc7a32c3e'),
    'tools/fixtures/endgame-stacking/ledger.json': (391674, '5447ec7baafd3f91f7db47290a5fec022625561ffff8cd3a1d38eaa9863b24bf'),
    'evidence/endgame-stacking/source-excerpts.json': (297468, '97cc5f6708ac4102de2f53f5d4a63f8465478001c46c276d91034eb9b129eebd'),
    'endgame-stacking-audit.html': (401005, '378e4b0b49babdebdaba9936cae698a9d3b7e26f5e330d7eeef39a7a9711fc21'),
    'heroic-crafting-print.html': (4604, 'ecc1d8b185b3fd40100fd5f61dca85fe432bb0bdb0f6bb5a0d26d5937de99f17'),
    'tools/wisdom_loadout.py': (44717, '4b65c2f883c20fff4383b9cdaa2f86786e34064b491cff2e85cf0260a53bf000'),
    'tools/build_stacking_audit.py': (27078, '53fada9f8ba6ec4f8d75bd26270fb9432492d8ac0998312c1a37a1f93a52fec3'),
    'tools/stacking_audit.py': (12585, 'cd87217a2a49435f2caf2e84c9fa785a6d5462f43d829dca0212103861279d98'),
}
REVIEWED_PATHS = tuple(BASE_FILES)
PRESERVED_COUNT = 187
PRESERVED_MANIFEST_SHA = 'd341ef5ad2f3f864692220f8dea687b8ad27a6a3f1738d11171da8bf7a2d67c5'


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def load_scope():
    data = json.loads(FIXTURE.read_text())
    assert data['schema'] == 'wisdom-int-stacking-exact-reversal-v1'
    assert data['repository'] == 'eddiefiggie/eddiefiggie-int-longbow-guide'
    assert data['baseline_commit'] == BASE_COMMIT
    assert data['baseline_tree'] == BASE_TREE
    assert data['approved_branch'] == 'feat/wisdom-loadout-priorities'
    assert (data['baseline_build'], data['current_build']) == ('11-15-26.5', '11-15-26.6')
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
    """Require exact .6 bytes and unique contexts before returning fixed .5 bytes."""
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
    assert len(text.encode()) == size and sha(text) == digest, (path, 'fixed b83e6a9 checkpoint')
    return text


def checkpoint_file_bytes(path):
    """Return strict .5 bytes; unchanged evidence and history remain literal."""
    raw = offense.checkpoint_file_bytes(path)
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
        raw = offense.checkpoint_file_bytes(path)
        assert (len(raw), sha(raw)) == (expected['bytes'], expected['sha256']), path
    return True


def validate_full_reversal():
    scope = load_scope()
    for path in REVIEWED_PATHS:
        restore_file(path, offense.checkpoint_file_bytes(path), scope=scope)
    return validate_preserved_files()


def _module(name, path, source, dependencies=None):
    """Bind checkpoint dependencies locally without replacing sys.modules."""
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
    module = _module('_int_stacking_checkpoint_calculator', 'tools/stacking_audit.py', source,
                     {'recipe_proofs': recipes})
    module.load = lambda: json.loads(checkpoint_file_text('tools/fixtures/endgame-stacking/ledger.json'))
    return module


def historical_calculator():
    # Revalidate real files before every cached access, including the strictly
    # restored recipe helper whose bytes are unchanged between .5 and .8.
    checkpoint_file_bytes('tools/recipe_proofs.py')
    return _calculator(checkpoint_file_bytes('tools/stacking_audit.py'),
                       chains_type.historical_recipe_proofs())


@lru_cache(maxsize=1)
def _recipe_renderer(source, calculator):
    return _module('_int_stacking_checkpoint_recipe', 'tools/wisdom_loadout.py', source,
                   {'stacking_audit': calculator})


def historical_recipe_renderer():
    return _recipe_renderer(checkpoint_file_bytes('tools/wisdom_loadout.py'), historical_calculator())


@lru_cache(maxsize=1)
def _audit_renderer(source, calculator, recipe):
    return _module('_int_stacking_checkpoint_audit', 'tools/build_stacking_audit.py', source,
                   {'stacking_audit': calculator, 'wisdom_loadout': recipe})


def historical_audit_renderer():
    return _audit_renderer(checkpoint_file_bytes('tools/build_stacking_audit.py'),
                           historical_calculator(), historical_recipe_renderer())
