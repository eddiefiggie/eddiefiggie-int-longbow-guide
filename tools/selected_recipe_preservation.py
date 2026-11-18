"""Exact 18 November draft -> approved 16 November checkpoint views.

Historical readers are explicit isolated modules and paths. Production imports
and current recipe tests never use this overlay. Old hashes and assertions are
retained; this is file preservation evidence, not mechanics certification.
"""
import builtins
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import types

ROOT = Path(__file__).resolve().parents[1]
BASE_COMMIT = '96e937aa57171be6a211136d50e01050b19cb744'
FIXTURE = ROOT / 'tools/fixtures/selected-recipes-preservation/scope.json'
BASE_FILES = {
 'index.html': (420449, '62c1e09dfbf9c24feb2b10838c6e534cc4408a661ad81a5de25530a197f822e4'),
 'heroic-crafting-print.html': (4604, '3ae44d0e778ba356feda7db2248178693afcb446eae18bdf081e73230b704344'),
 'endgame-stacking-audit.html': (478299, '8302e980a1adc999b481268f45b28eb9315761aa85d4fd928d2b9d7ed521db71'),
 'tools/wisdom_loadout.py': (57452, '3e97270cddc4345b6a3b1106fe6c7b916d1232658d670a399f428e46ea928741'),
 'tools/build_stacking_audit.py': (35035, 'bab1dfa6c6566eda9bfd694166bea16bc4b2b416d9421ab7a6edaa7300ddfddb'),
 'tools/fixtures/wisdom-loadout/selection.json': (170414, '8223bd8e25ed9dc4ad9454439ead42dfb693cc008d18d0ddfeb270d33863c37d'),
}
REVIEWED_PATHS = tuple(BASE_FILES)
PRESERVED_COUNT = 225
PRESERVED_SHA = 'dd265e0a2f38b0e50147ca94f0f5fcfa899e40ba737b979861cd06a7608a3625'
PROOF_MODULES = ('recipe_proofs', 'fort_spot_proofs', 'chains_type_proofs',
                 'wisdom_ability_proofs', 'wisdom_doubleshot_proofs')


def sha(raw):
    return sha256(raw if isinstance(raw, bytes) else raw.encode()).hexdigest()


def load_scope():
    return _validate_scope(json.loads(FIXTURE.read_bytes()))


def _validate_scope(data):
    assert data['baseline_commit'] == BASE_COMMIT
    assert data['schema'] == 'selected-recipes-exact-reversal-v1'
    assert set(data['files']) == set(BASE_FILES)
    for path, fixed in BASE_FILES.items():
        row = data['files'][path]
        assert (row['baseline_bytes'], row['baseline_sha256']) == fixed, path
    return data


def preserved_files():
    data = json.loads((FIXTURE.parent / 'preserved.json').read_text())
    assert len(data) == PRESERVED_COUNT
    assert sha(json.dumps(data, sort_keys=True, separators=(',', ':'))) == PRESERVED_SHA
    return data


def validate_preserved_files():
    for path, expected in preserved_files().items():
        raw = (ROOT / path).read_bytes()
        assert (len(raw), sha(raw)) == (expected['bytes'], expected['sha256']), path
    return True


@lru_cache(maxsize=16)
def _restore_exact_inputs(path, raw, scope_raw):
    # Memoize only pure computation over exact bytes, never filesystem success.
    # Callers reread both files before every lookup; any mutation is a new key.
    return restore_file(path, raw, scope=_validate_scope(json.loads(scope_raw)))


def restore_file(path, raw, *, scope=None):
    raw = raw if isinstance(raw, bytes) else raw.encode()
    if scope is None:
        return _restore_exact_inputs(path, raw, FIXTURE.read_bytes())
    data = scope
    assert path in BASE_FILES
    raw = raw if isinstance(raw, bytes) else raw.encode()
    row = data['files'][path]
    assert (len(raw), sha(raw)) == (row['current_bytes'], row['current_sha256']), path
    text = raw.decode()
    for change in reversed(row['reviewed_replacements']):
        assert change['after'] and change['before'] != change['after']
        assert text.count(change['after']) == 1, (path, 'unique after-context')
        text = text.replace(change['after'], change['before'], 1)
    assert (len(text.encode()), sha(text)) == BASE_FILES[path], (path, 'fixed approved checkpoint')
    return text


def checkpoint_file_bytes(path):
    raw = (ROOT / path).read_bytes()
    if path in BASE_FILES:
        return restore_file(path, raw).encode()
    return raw


def checkpoint_file_text(path):
    return checkpoint_file_bytes(path).decode()


class HistoricalPath(type(Path())):
    """Only reads of exact reviewed repository paths use the .2 overlay."""
    def read_bytes(self):
        try:
            relative = str(self.relative_to(ROOT))
        except ValueError:
            return super().read_bytes()
        return checkpoint_file_bytes(relative)

    def read_text(self, encoding=None, errors=None):
        return self.read_bytes().decode(encoding or 'utf-8', errors or 'strict')


def _module(name, dependencies=None):
    path = 'tools/' + name + '.py'
    source = checkpoint_file_bytes(path)
    if path not in BASE_FILES:
        expected = preserved_files()[path]
        assert (len(source), sha(source)) == (expected['bytes'], expected['sha256']), path
    deps = dependencies if dependencies is not None else {}
    module = types.ModuleType('_selected_recipes_checkpoint_' + name)
    module.__file__ = str(ROOT / path)
    module.__checkpoint_sha256__ = sha(source)
    pathlib = types.SimpleNamespace(Path=HistoricalPath)
    def historical_import(import_name, globals=None, locals=None, fromlist=(), level=0):
        if level == 0 and import_name == 'pathlib':
            return pathlib
        if level == 0 and import_name in deps:
            return deps[import_name]
        return builtins.__import__(import_name, globals, locals, fromlist, level)
    module.__dict__['__builtins__'] = {**vars(builtins), '__import__': historical_import}
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    return module


@lru_cache(maxsize=1)
def _historical_modules():
    deps = {}
    for name in PROOF_MODULES:
        deps[name] = _module(name, deps)
    deps['stacking_audit'] = _module('stacking_audit', deps)
    deps['wisdom_loadout'] = _module('wisdom_loadout', deps)
    deps['build_stacking_audit'] = _module('build_stacking_audit', deps)
    return deps


def historical_module(name):
    # Reread exact reviewed files before returning a cached historical module.
    for path in BASE_FILES:
        checkpoint_file_bytes(path)
    for module_name in (*PROOF_MODULES, 'stacking_audit'):
        path = 'tools/' + module_name + '.py'
        expected = preserved_files()[path]
        raw = (ROOT / path).read_bytes()
        assert (len(raw), sha(raw)) == (expected['bytes'], expected['sha256']), path
    return _historical_modules()[name]


def historical_calculator():
    return historical_module('stacking_audit')


def historical_recipe_renderer():
    return historical_module('wisdom_loadout')


def historical_audit_renderer():
    return historical_module('build_stacking_audit')


def historical_proof_module(name):
    assert name in PROOF_MODULES
    path = 'tools/' + name + '.py'
    raw = (ROOT / path).read_bytes()
    expected = preserved_files()[path]
    assert (len(raw), sha(raw)) == (expected['bytes'], expected['sha256']), path
    return _historical_modules()[name]


def checkpoint_module(layer, name):
    """Compile a prior layer's authenticated code with explicit historic reads.

    The layer still performs all of its original fixed-hash restoration. Only
    module-local Path/import bindings differ; production modules are untouched.
    """
    names = (*PROOF_MODULES, 'stacking_audit', 'wisdom_loadout', 'build_stacking_audit')
    sources = tuple((n, layer.checkpoint_file_bytes('tools/' + n + '.py')) for n in names)
    ledger = layer.checkpoint_file_bytes('tools/fixtures/endgame-stacking/ledger.json')
    return _checkpoint_modules(sources, ledger)[name]


@lru_cache(maxsize=16)
def _checkpoint_modules(sources, ledger):
    deps = {}
    for name, source in sources:
        module = types.ModuleType('_selected_recipes_prior_' + name)
        module.__file__ = str(ROOT / 'tools' / (name + '.py'))
        module.__checkpoint_sha256__ = sha(source)
        def checkpoint_import(import_name, globals=None, locals=None, fromlist=(), level=0):
            if level == 0 and import_name == 'pathlib':
                return types.SimpleNamespace(Path=HistoricalPath)
            if level == 0 and import_name in deps:
                return deps[import_name]
            return builtins.__import__(import_name, globals, locals, fromlist, level)
        module.__dict__['__builtins__'] = {**vars(builtins), '__import__': checkpoint_import}
        exec(compile(source, module.__file__, 'exec'), module.__dict__)
        deps[name] = module
        if name == 'stacking_audit':
            module.load = lambda: json.loads(ledger)
    return deps


def historical_preservation_module(name):
    assert name == 'wisdom_recipe_proof_preservation'
    # The original preserved inventory must read the exact approved checkpoint.
    return _module(name)
