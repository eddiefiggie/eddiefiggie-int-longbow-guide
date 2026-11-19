"""Exact 11-16-26.2-to-.1 views for selected gear Doubleshot qualification.

Complete historical outputs and independent .1 hashes remain fixed. Historical
modules use restored inputs and literal, hash-checked .1 proof dependencies;
separate functional tests exercise the actual new engine and its narrow scope.
No restoration or software check authenticates live-game Doubleshot or DPS.
"""
import builtins
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import types
import selected_recipe_preservation as selected_recipes


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tools/fixtures/wisdom-doubleshot/scope.json'
BASE_COMMIT = 'dca599357207c5861d2819358f7d011bba5d6dd0'
BASE_TREE = '239b0303b28572df40cda9d9838d76cde2365d0c'
BASE_FILES = {
    'index.html': (416984, '6fe441c549172da4b04b404bf3bccdb6af805e5352335eec8c55d114628f9224'),
    'tools/fixtures/endgame-stacking/ledger.json': (440672, '305528c8ab2d5434ef7a95c285d4ad2b1911ff46881c62c91ca64094886ca1ec'),
    'evidence/endgame-stacking/source-excerpts.json': (335580, '860f35dcd3bc3e1dc4122feefbde559e297e2b993ad05198c37dcc95d3213c7b'),
    'endgame-stacking-audit.html': (459900, '3c3268d5fdbdc35ccefb34eda91fe1288341334d7ed47e24394824d38301e057'),
    'heroic-crafting-print.html': (4604, 'db96495ac5793f5b971ee9f1a9c788972b02b8c71d8165462240ffc98ddfc42e'),
    'tools/wisdom_loadout.py': (54122, '404ad0bde93b1c87a8e5895bc91dfbc30fbfca6358d77f5393f5a47636f8c123'),
    'tools/build_stacking_audit.py': (33543, 'db2cc0fb878038b9f973f741adc5c0bcfd9857a0fdc134b781d43ed90f0a2468'),
    'tools/stacking_audit.py': (31644, '534baf523787469c4ca320ea64e9bebe8e43139daaae21a71465d603ab611a9b'),
}
REVIEWED_PATHS = tuple(BASE_FILES)
PRESERVED_COUNT = 215
PRESERVED_MANIFEST_SHA = 'f5fbec7f8490243fc0c70823903f982db494e4392ad452381044c122292f3c39'
PROOF_DEPENDENCIES = ('tools/recipe_proofs.py', 'tools/fort_spot_proofs.py',
                      'tools/chains_type_proofs.py', 'tools/wisdom_ability_proofs.py')


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def load_scope():
    data = json.loads(FIXTURE.read_text())
    assert data['schema'] == 'wisdom-doubleshot-exact-reversal-v1'
    assert data['repository'] == 'eddiefiggie/eddiefiggie-int-longbow-guide'
    assert data['baseline_commit'] == BASE_COMMIT
    assert data['baseline_tree'] == BASE_TREE
    assert data['approved_branch'] == 'feat/wisdom-loadout-priorities'
    assert (data['baseline_build'], data['current_build']) == ('11-16-26.1', '11-16-26.2')
    assert set(data['files']) == set(BASE_FILES)
    for path, expected in BASE_FILES.items():
        row = data['files'][path]
        assert (row['baseline_bytes'], row['baseline_sha256']) == expected, path
        assert row['reviewed_replacements'], path
    preserved = data['preserved_files']
    assert len(preserved) == PRESERVED_COUNT
    canonical = json.dumps(preserved, sort_keys=True, separators=(',', ':'))
    assert sha(canonical) == PRESERVED_MANIFEST_SHA, 'independently pinned .1 inventory'
    assert not set(preserved) & set(REVIEWED_PATHS)
    return data


def restore_file(path, current, *, scope=None):
    """Accept exact new bytes and reverse unique contexts to fixed .1 bytes."""
    data = load_scope() if scope is None else scope
    assert path in BASE_FILES
    row = data['files'][path]
    raw = current if isinstance(current, bytes) else current.encode()
    if (len(raw), sha(raw)) != (row['current_bytes'], row['current_sha256']):
        # An explicit caller may supply the new outer release instead of .2.
        # Only its exact independently pinned reversal may enter this old layer.
        raw = selected_recipes.restore_file(path, raw).encode()
    assert len(raw) == row['current_bytes'] and sha(raw) == row['current_sha256'], path
    text = raw.decode()
    assert row['reviewed_replacements'], path
    for change in reversed(row['reviewed_replacements']):
        assert change['before'] != change['after']
        assert change['after'] and text.count(change['after']) == 1, (path, 'unique exact after-context')
        text = text.replace(change['after'], change['before'], 1)
    size, digest = BASE_FILES[path]
    assert (len(text.encode()), sha(text)) == (size, digest), (path, 'fixed dca5993 checkpoint')
    return text


def checkpoint_file_bytes(path):
    """Return exact .1 bytes while rechecking unchanged historical inputs."""
    raw = selected_recipes.checkpoint_file_bytes(path)
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
        raw = selected_recipes.checkpoint_file_bytes(path)
        assert (len(raw), sha(raw)) == (expected['bytes'], expected['sha256']), path
    return True


def validate_full_reversal():
    scope = load_scope()
    for path in REVIEWED_PATHS:
        restore_file(path, selected_recipes.checkpoint_file_bytes(path), scope=scope)
    return validate_preserved_files()


def _module(name, path, source, dependencies=None):
    """Bind restored local imports without changing global production modules."""
    imports = dependencies or {}
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / path)

    def import_checkpoint(name, globals=None, locals=None, fromlist=(), level=0):
        if level == 0 and name == 'pathlib':
            return types.SimpleNamespace(Path=selected_recipes.HistoricalPath)
        if level == 0 and name in imports:
            return imports[name]
        if level == 0 and name in selected_recipes.PROOF_MODULES:
            return selected_recipes.historical_proof_module(name)
        return builtins.__import__(name, globals, locals, fromlist, level)

    module.__dict__['__builtins__'] = {**vars(builtins), '__import__': import_checkpoint}
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    return module


@lru_cache(maxsize=None)
def _proof_dependency(name, path, source):
    return _module('_doubleshot_checkpoint_' + name, path, source)


def historical_proof_dependencies():
    # Each access rereads and verifies all four literal .1 helpers before any
    # cached module is reused. Only this isolated engine's imports are bound.
    return tuple((Path(path).stem, _proof_dependency(Path(path).stem, path,
                                                   checkpoint_file_bytes(path)))
                 for path in PROOF_DEPENDENCIES)


@lru_cache(maxsize=1)
def _calculator(source, dependencies):
    module = _module('_doubleshot_checkpoint_calculator', 'tools/stacking_audit.py',
                     source, dict(dependencies))
    module.load = lambda: json.loads(checkpoint_file_text('tools/fixtures/endgame-stacking/ledger.json'))
    return module


def historical_calculator():
    return _calculator(checkpoint_file_bytes('tools/stacking_audit.py'),
                       historical_proof_dependencies())


@lru_cache(maxsize=1)
def _recipe_renderer(source, calculator):
    return _module('_doubleshot_checkpoint_recipe', 'tools/wisdom_loadout.py', source,
                   {'stacking_audit': calculator})


def historical_recipe_renderer():
    return _recipe_renderer(checkpoint_file_bytes('tools/wisdom_loadout.py'), historical_calculator())


@lru_cache(maxsize=1)
def _audit_renderer(source, calculator, recipe, dependencies):
    return _module('_doubleshot_checkpoint_audit', 'tools/build_stacking_audit.py', source,
                   {**dict(dependencies), 'stacking_audit': calculator, 'wisdom_loadout': recipe})


def historical_audit_renderer():
    return _audit_renderer(checkpoint_file_bytes('tools/build_stacking_audit.py'),
                           historical_calculator(), historical_recipe_renderer(),
                           historical_proof_dependencies())
