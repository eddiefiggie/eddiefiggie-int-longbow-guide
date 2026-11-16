"""Exact 11-16-26.1-to-.9 views for the bounded WIS/CON qualification.

Complete historical outputs and independent .9 hashes remain fixed. Historical
modules use restored inputs and literal, hash-checked .9 proof dependencies;
separate functional tests exercise the actual new engine and its narrow scope.
No restoration or software check authenticates a live-game ability score.
"""
import builtins
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import types
import wisdom_doubleshot_preservation as doubleshot


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tools/fixtures/wisdom-abilities/scope.json'
BASE_COMMIT = '834b8c4cc648f9263ea19ac4203eedd872888f06'
BASE_TREE = '0b6263ca9bb201b5267774d6f8af198fe013d35e'
BASE_FILES = {
    'index.html': (412646, 'e6e1a3b914b839408a49bc615dab0462000f6daaef30ae0b5772d04a8655e47c'),
    'tools/fixtures/endgame-stacking/ledger.json': (424507, '5be6934a289390637bde9c1af3256e82bff5bc00db7227b488cb7868d0bb392f'),
    'evidence/endgame-stacking/source-excerpts.json': (323412, '5f4c10a668968f6519215b50aec37aece4dc2f803cc8d1e7e1cb035b8bc1955b'),
    'endgame-stacking-audit.html': (439562, '208ca68ae88d982508d80ffd6a256d3a5379b0b78dbad6ffe474086d8159e0bf'),
    'heroic-crafting-print.html': (4604, '9f78e67cc28e08cd1fa676ea1db0786c3321e86a7bd91ac6d2f39d7deff797c9'),
    'tools/wisdom_loadout.py': (50061, '250a8ac4ea129db2de9364b51cdbe38fa7d1ad62af411284caf49089f8a6674a'),
    'tools/build_stacking_audit.py': (31207, '762cfb13e683bd21354f90801b0135f22168e873a87a6a7fef57703dc3b6cbda'),
    'tools/stacking_audit.py': (28079, '052f717d129c2523d7b3b9b5026a4b0be19d36f81683e260e2be3ea0af4f9d81'),
}
REVIEWED_PATHS = tuple(BASE_FILES)
PRESERVED_COUNT = 209
PRESERVED_MANIFEST_SHA = '27cf2e80d81cabeafd6a010541cc0ec8b4c41c60d12e93eb3cd04d3321414bec'
PROOF_DEPENDENCIES = ('tools/recipe_proofs.py', 'tools/fort_spot_proofs.py',
                      'tools/chains_type_proofs.py')


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def load_scope():
    data = json.loads(FIXTURE.read_text())
    assert data['schema'] == 'wisdom-ability-exact-reversal-v1'
    assert data['repository'] == 'eddiefiggie/eddiefiggie-int-longbow-guide'
    assert data['baseline_commit'] == BASE_COMMIT
    assert data['baseline_tree'] == BASE_TREE
    assert data['approved_branch'] == 'feat/wisdom-loadout-priorities'
    assert (data['baseline_build'], data['current_build']) == ('11-15-26.9', '11-16-26.1')
    assert set(data['files']) == set(BASE_FILES)
    for path, expected in BASE_FILES.items():
        row = data['files'][path]
        assert (row['baseline_bytes'], row['baseline_sha256']) == expected, path
        assert row['reviewed_replacements'], path
    preserved = data['preserved_files']
    assert len(preserved) == PRESERVED_COUNT
    canonical = json.dumps(preserved, sort_keys=True, separators=(',', ':'))
    assert sha(canonical) == PRESERVED_MANIFEST_SHA, 'independently pinned .9 inventory'
    assert not set(preserved) & set(REVIEWED_PATHS)
    return data


def restore_file(path, current, *, scope=None):
    """Accept exact new bytes and reverse unique contexts to fixed .9 bytes."""
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
    assert (len(text.encode()), sha(text)) == (size, digest), (path, 'fixed 834b8c4 checkpoint')
    return text


def checkpoint_file_bytes(path):
    """Return exact .9 bytes while rechecking unchanged historical inputs."""
    raw = doubleshot.checkpoint_file_bytes(path)
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
        raw = doubleshot.checkpoint_file_bytes(path)
        assert (len(raw), sha(raw)) == (expected['bytes'], expected['sha256']), path
    return True


def validate_full_reversal():
    scope = load_scope()
    for path in REVIEWED_PATHS:
        restore_file(path, doubleshot.checkpoint_file_bytes(path), scope=scope)
    return validate_preserved_files()


def _module(name, path, source, dependencies=None):
    """Bind restored local imports without changing global production modules."""
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
    module = _module('_ability_checkpoint_calculator', 'tools/stacking_audit.py', source)
    module.load = lambda: json.loads(checkpoint_file_text('tools/fixtures/endgame-stacking/ledger.json'))
    return module


def historical_calculator():
    # The unchanged .9 helpers stay literal. Recheck them even on cache hits.
    for path in PROOF_DEPENDENCIES:
        checkpoint_file_bytes(path)
    return _calculator(checkpoint_file_bytes('tools/stacking_audit.py'))


@lru_cache(maxsize=1)
def _recipe_renderer(source, calculator):
    return _module('_ability_checkpoint_recipe', 'tools/wisdom_loadout.py', source,
                   {'stacking_audit': calculator})


def historical_recipe_renderer():
    return _recipe_renderer(checkpoint_file_bytes('tools/wisdom_loadout.py'), historical_calculator())


@lru_cache(maxsize=1)
def _audit_renderer(source, calculator, recipe):
    return _module('_ability_checkpoint_audit', 'tools/build_stacking_audit.py', source,
                   {'stacking_audit': calculator, 'wisdom_loadout': recipe})


def historical_audit_renderer():
    return _audit_renderer(checkpoint_file_bytes('tools/build_stacking_audit.py'),
                           historical_calculator(), historical_recipe_renderer())
