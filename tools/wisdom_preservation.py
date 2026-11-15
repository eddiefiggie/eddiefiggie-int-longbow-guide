"""Exact predecessor views for the explicitly approved Wisdom loadout release.

These views do not make the old Queen BASIC recipe current.  They prove that
the new, separately tested release reverses to the immutable pre-Wisdom source
before the older contracts and their unchanged hashes are evaluated.  No test
may use a frozen predecessor without first validating the current file's exact
reviewed reversal.
"""
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import types
import wisdom_corrections as corrections
import wisdom_crafting_integration as crafting
import wisdom_recipe_proof_preservation as recipe_proofs
import wisdom_int_evidence_preservation as int_evidence


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tools/fixtures/wisdom-loadout'
BASE_COMMIT = '5ded199eadbade29dcdb0c1eccfad4758a65c328'
BASE_INDEX_SHA = 'b3e62101b7902f32e10c8beceff7efbcc3557729c9622ea529706a64c886f016'
BASE_LEDGER_SHA = 'e59f05eb7ca3b5f23c8f5c68a3b1e32cdd877589c5d7cf82fd025f7fb76a286e'
BASE_GENERATOR_SHA = '196c14c2be802bc12445629f030cec7dad0871921dfc552ee72fadb7e3cb370f'
BASE_EXCERPTS_SHA = 'ccbcd4b80992f9469820b639c2543e75c58aafed8a9ea2b2146e249e39902bc5'
BASE_SNAPSHOT_SHA = '5f693e7cce129f8dd42219ec8b0025f2e39b8ae3b82bf77955911ff7b0d2b5ba'
BASE_MODEL_SHA = '7d9e0843939310214d73b00e7e936ca4e842bf7bf0fc3f8da1b849e8c8faf236'
BASE_CALCULATOR_SHA = '97432b1a37543645986a343ec0c6d3c8d58b77c4089e03307dfdf2840d3c606d'
REVIEWED_PATHS = (
    'index.html',
    'tools/fixtures/endgame-stacking/ledger.json',
    'tools/build_stacking_audit.py',
    'evidence/endgame-stacking/source-excerpts.json',
    'endgame-stacking-audit.html',
)


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def load_scope():
    data = json.loads((FIXTURE / 'scope.json').read_text())
    assert data['schema'] == 'wisdom-release-exact-reversal-v1'
    assert data['baseline_commit'] == BASE_COMMIT
    assert data['approved_branch'] == 'feat/wisdom-loadout-priorities'
    assert set(data['files']) == set(REVIEWED_PATHS)
    expected = {
        'index.html': BASE_INDEX_SHA,
        'tools/fixtures/endgame-stacking/ledger.json': BASE_LEDGER_SHA,
        'tools/build_stacking_audit.py': BASE_GENERATOR_SHA,
        'evidence/endgame-stacking/source-excerpts.json': BASE_EXCERPTS_SHA,
    }
    for path, digest in expected.items():
        assert data['files'][path]['baseline_sha256'] == digest, path
    return data


def frozen_index():
    """Recover the exact source of the already-published immutable snapshot.

    This bounded inverse is valid only for these pinned bytes, not arbitrary
    snapshots.  Both snapshot and recovered source hashes are fixed independently
    of the new release fixture; historical files are never rewritten.
    """
    raw = (ROOT / 'versions/11-09-26.5.html').read_bytes()
    assert len(raw) == 353085 and sha(raw) == BASE_SNAPSHOT_SHA
    value = raw.decode().replace('href="../', 'href="').replace('src="../', 'src="')
    assert len(value.encode()) == 353010 and sha(value) == BASE_INDEX_SHA
    return value


def frozen_ledger_bytes():
    raw = (FIXTURE / 'predecessor-ledger.json').read_bytes()
    assert len(raw) == 344992 and sha(raw) == BASE_LEDGER_SHA
    return raw


def frozen_generator_bytes():
    raw = (FIXTURE / 'predecessor-generator.py').read_bytes()
    assert len(raw) == 20931 and sha(raw) == BASE_GENERATOR_SHA
    return raw


def restore_file(path, current, *, scope=None):
    """Restore INT, recipe-proof, crafting, correction and original layers."""
    if path in int_evidence.REVIEWED_PATHS:
        current = int_evidence.restore_file(path, current)
    if path in recipe_proofs.REVIEWED_PATHS:
        current = recipe_proofs.restore_file(path, current)
    if path in crafting.REVIEWED_PATHS:
        current = crafting.restore_file(path, current)
    if path in corrections.REVIEWED_PATHS:
        current = corrections.restore_file(path, current)
    return restore_wisdom_file(path, current, scope=scope)


def restore_wisdom_file(path, current, *, scope=None):
    """Reverse each approved exact hunk, then enforce the old complete-file hash.

    This inner operation accepts only the exact PR47 Wisdom predecessor.
    The required current hash rejects mixed releases, extra edits, dropped or
    duplicated changes.  Counts prevent an accidental replacement elsewhere.
    There is deliberately no fallback accepting an already-old file.
    """
    data = load_scope() if scope is None else scope
    assert path in REVIEWED_PATHS
    rule = data['files'][path]
    raw = current if isinstance(current, bytes) else current.encode()
    assert len(raw) == rule['current_bytes'] and sha(raw) == rule['current_sha256'], path
    text = raw.decode()
    for change in reversed(rule['reviewed_replacements']):
        assert change['before'] != change['after']
        assert change['after'] and text.count(change['after']) == 1, (path, 'exact reviewed after-context')
        text = text.replace(change['after'], change['before'], 1)
    restored = text.encode()
    assert len(restored) == rule['baseline_bytes'], path
    assert sha(restored) == rule['baseline_sha256'], path
    return text


def predecessor_file_text(path):
    return restore_file(path, (ROOT / path).read_bytes())


def predecessor_index():
    restored = predecessor_file_text('index.html')
    assert restored == frozen_index()
    return restored


def predecessor_ledger():
    restored = predecessor_file_text('tools/fixtures/endgame-stacking/ledger.json').encode()
    assert restored == frozen_ledger_bytes()
    return json.loads(restored)


def predecessor_file_bytes(path):
    """Only scoped current artifacts are reversed; unaffected files stay literal."""
    if path in REVIEWED_PATHS:
        return predecessor_file_text(path).encode()
    return recipe_proofs.checkpoint_file_bytes(path)


@lru_cache(maxsize=1)
def historical_renderer():
    """Execute the pinned predecessor renderer against the pinned calculator.

    Older semantic/mutation tests use this renderer and the restored predecessor
    ledger.  Dedicated current-release tests exercise the production renderer
    and production ledger, so neither current correctness nor old evidence
    guards is delegated to a frozen artifact alone.
    """
    current_restored = predecessor_file_text('tools/build_stacking_audit.py').encode()
    assert current_restored == frozen_generator_bytes()
    module = types.ModuleType('_wisdom_predecessor_stacking_renderer')
    module.__file__ = str(FIXTURE / 'predecessor-generator.py')
    exec(compile(current_restored, module.__file__, 'exec'), module.__dict__)
    calculator = recipe_proofs.historical_calculator()
    for name in ('ROOT', 'validate', 'subtotal', 'source_provenance'):
        setattr(module, name, getattr(calculator, name))
    module.load = predecessor_ledger
    return module


def validate_full_reversal():
    scope = load_scope()
    restored = {path: restore_file(path, (ROOT / path).read_bytes(), scope=scope)
                for path in REVIEWED_PATHS}
    assert restored['index.html'] == frozen_index()
    assert restored['tools/fixtures/endgame-stacking/ledger.json'].encode() == frozen_ledger_bytes()
    assert restored['tools/build_stacking_audit.py'].encode() == frozen_generator_bytes()
    data = json.loads(frozen_ledger_bytes())
    excerpts = json.dumps({
        'scope': 'Selected source contexts only; exact excerpts with origin file hashes/pointers. Original mixed capture files are not linked as audit payload.',
        'sources': data['sources'],
    }, ensure_ascii=False, indent=2) + '\n'
    assert restored['evidence/endgame-stacking/source-excerpts.json'] == excerpts
    assert sha(excerpts) == BASE_EXCERPTS_SHA
    assert restored['endgame-stacking-audit.html'] == historical_renderer().detail(data)
    assert sha((ROOT / 'tools/bowmodel.py').read_bytes()) == BASE_MODEL_SHA
    assert sha(recipe_proofs.checkpoint_file_bytes('tools/stacking_audit.py')) == BASE_CALCULATOR_SHA
    return True
