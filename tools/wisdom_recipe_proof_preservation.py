"""Exact .4-to-.3 views for the approved bounded recipe-proof integration.

Every historical view first reverses the actual current file to independently
pinned predecessor bytes. Existing scopes, captures and snapshots are not
rewritten. Frozen modules serve historical rendering/differential tests only;
the real new engine also runs against unchanged .3 data and direct-path mutants.
"""
import builtins
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import types


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tools/fixtures/wisdom-recipe-proofs/scope.json'
BASE_COMMIT = '6d978f48fc3eeb807f4560e75ac27e6639af35f4'
BASE_TREE = 'b636b6463a2978410ed4dca75ee5c8fc18c763a1'
BASE_FILES = {
    'index.html': (396014, 'b3fb5d8f3b41980fa51cb2ba79efd004da58bc870a8a2cb6b36173aca23ef121'),
    'tools/fixtures/endgame-stacking/ledger.json': (369741, '1bdd704625d8790b475429cd81fa48636a42ceedb677c0e2d5ff1bae46f330c3'),
    'evidence/endgame-stacking/source-excerpts.json': (277576, '11b40559d7e78d3000008d80f0294ac7f555ebce767aa5975acc832e6779f3e7'),
    'endgame-stacking-audit.html': (377250, 'fffadb76e7ff2cf2f24c1b320591027a72297bf681910044246f5b6ffa44b78f'),
    'heroic-crafting-print.html': (4604, '23a12a9bbfbe8f528f9aa8f5cdbc1de0b50e4d4b21a1122e7854f4dfc4342578'),
    'tools/wisdom_loadout.py': (41607, '1cd1668d54d995c1da6b1fda1868a5f85dba42c2df513f034b6b32ee2ab3e501'),
    'tools/build_stacking_audit.py': (26573, '0580e2ead8977ffb86b8f743acd332dc0e7a23c0dd005936d471ae5f5425ecdb'),
    'tools/stacking_audit.py': (11763, '97432b1a37543645986a343ec0c6d3c8d58b77c4089e03307dfdf2840d3c606d'),
}
REVIEWED_PATHS = tuple(BASE_FILES)
ORIGINAL_SCOPES = {
    'tools/fixtures/wisdom-loadout/scope.json': '3a3d34bc5cb2524bf611bfa2128605daf9f3dd554d458a50928f099d80933bd0',
    'tools/fixtures/wisdom-corrections/scope.json': '7a079fd078bf37bf9def7ddd4a67c647a2092206ef0a2ddbfb9823b3da3654ef',
    'tools/fixtures/wisdom-crafting-integration/scope.json': '3f10236d292373e4951fc249c69f6858ab59bb3537c54c416f147eb76b4ad996',
}
PRESERVED_COUNT = 55
PRESERVED_MANIFEST_SHA = 'c76d5575f605ee5754494b59d9afc75b1643b2b15e2438f652f6065629f6ac54'


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def load_scope():
    data = json.loads(FIXTURE.read_text())
    assert data['schema'] == 'wisdom-recipe-proof-exact-reversal-v1'
    assert data['repository'] == 'eddiefiggie/eddiefiggie-int-longbow-guide'
    assert data['baseline_commit'] == BASE_COMMIT
    assert data['baseline_tree'] == BASE_TREE
    assert data['approved_branch'] == 'feat/wisdom-loadout-priorities'
    assert (data['baseline_build'], data['current_build']) == ('11-15-26.3', '11-15-26.4')
    assert set(data['files']) == set(BASE_FILES)
    for path, digest in ORIGINAL_SCOPES.items():
        assert sha((ROOT / path).read_bytes()) == digest, (path, 'original scope preserved')
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
    """Require exact current bytes and unique hunks; reject old/mixed fallbacks."""
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
    assert len(text.encode()) == size and sha(text) == digest, (path, 'fixed 6d978f48 checkpoint')
    return text


def checkpoint_file_bytes(path):
    """Return exact .3 bytes for reviewed files; unaffected paths stay literal."""
    raw = (ROOT / path).read_bytes()
    return restore_file(path, raw).encode() if path in REVIEWED_PATHS else raw


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
    """Bind only explicit historical dependencies, without changing sys.modules."""
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
    module = _module('_recipe_proof_checkpoint_calculator', 'tools/stacking_audit.py', source)
    # Historical renderers' default load must see exact .3 data, not the live .4
    # ledger. validate/subtotal and all other functions are the pinned old code.
    module.load = lambda: json.loads(checkpoint_file_text('tools/fixtures/endgame-stacking/ledger.json'))
    return module


def historical_calculator():
    # Revalidate current bytes even when the compiled predecessor is cached.
    return _calculator(checkpoint_file_bytes('tools/stacking_audit.py'))


@lru_cache(maxsize=1)
def _recipe_renderer(source, calculator):
    return _module('_recipe_proof_checkpoint_recipe', 'tools/wisdom_loadout.py', source,
                   {'stacking_audit': calculator})


def historical_recipe_renderer():
    return _recipe_renderer(checkpoint_file_bytes('tools/wisdom_loadout.py'), historical_calculator())


@lru_cache(maxsize=1)
def _audit_renderer(source, calculator, recipe):
    return _module('_recipe_proof_checkpoint_audit', 'tools/build_stacking_audit.py', source,
                   {'stacking_audit': calculator, 'wisdom_loadout': recipe})


def historical_audit_renderer():
    return _audit_renderer(checkpoint_file_bytes('tools/build_stacking_audit.py'),
                           historical_calculator(), historical_recipe_renderer())
