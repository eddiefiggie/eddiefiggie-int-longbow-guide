# Historical .2 contract: exact approved-checkpoint bytes/modules are explicit.
# New selected-recipe tests exercise production separately; no global imports patched.
"""Strict .5 checkpoint reversal and literal history, not DDO certification.

Actual-current source, semantic, renderer and whole-result checks are separate
in test_wisdom_int_stacking. The .5 tests in test_wisdom_int_evidence explicitly
use historical inputs; no historical module replaces current entrypoints.
"""
import selected_recipe_preservation as selected_history
import copy
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import stacking_audit as audit
audit = selected_history.historical_module('stacking_audit')
import wisdom_int_evidence_preservation as preservation
import wisdom_int_stacking_preservation as int_stacking
import wisdom_recipe_proof_preservation as recipes
recipes = selected_history.historical_preservation_module('wisdom_recipe_proof_preservation')
import wisdom_crafting_integration as crafting
import wisdom_corrections as corrections
import wisdom_preservation as wisdom


ROOT = selected_history.HistoricalPath(__file__).resolve().parents[1]
LEDGER = 'tools/fixtures/endgame-stacking/ledger.json'


class IntelligenceEvidencePreservationTests(unittest.TestCase):
    def test_scope_binds_independent_d05_checkpoint_and_fixed_preserved_inventory(self):
        scope = preservation.load_scope()
        self.assertEqual(scope['baseline_commit'], 'd05e7865da76a47a92741cb79029a35fbd0f7712')
        self.assertEqual(scope['baseline_tree'], 'c1b236d5cafc7695af9ec77410d329c7a0b9cc44')
        self.assertEqual(scope['approved_branch'], 'feat/wisdom-loadout-priorities')
        self.assertEqual((scope['baseline_build'], scope['current_build']),
                         ('11-15-26.4', '11-15-26.5'))
        self.assertEqual(len(scope['files']), 7)
        self.assertEqual(len(scope['preserved_files']), 61)
        self.assertTrue(preservation.validate_full_reversal())

    def test_all_reviewed_files_reverse_and_reconstruct_in_both_directions(self):
        scope = preservation.load_scope()
        for path, expected in preservation.BASE_FILES.items():
            raw = preservation.checkpoint_file_bytes(path)
            with self.subTest(path=path):
                self.assertEqual((len(raw), preservation.sha(raw)), expected)
                self.assertNotEqual(raw, int_stacking.checkpoint_file_bytes(path))
                text = raw.decode()
                for change in scope['files'][path]['reviewed_replacements']:
                    self.assertTrue(change['before'])
                    self.assertNotEqual(change['before'], change['after'])
                    self.assertEqual(text.count(change['before']), 1)
                    text = text.replace(change['before'], change['after'], 1)
                self.assertEqual(text, int_stacking.checkpoint_file_text(path))

    def test_stale_mixed_duplicate_and_unrelated_current_bytes_fail_closed(self):
        scope = preservation.load_scope()
        for path in preservation.REVIEWED_PATHS:
            current = int_stacking.checkpoint_file_text(path)
            change = scope['files'][path]['reviewed_replacements'][0]
            mutants = {
                'old': preservation.checkpoint_file_text(path),
                'extra': current + '\n',
                'mixed': current.replace(change['after'], change['before'], 1),
                'duplicate': current.replace(change['after'], change['after'] * 2, 1),
            }
            for label, mutant in mutants.items():
                with self.subTest(path=path, mutation=label):
                    self.assertNotEqual(mutant, current)
                    with self.assertRaises(AssertionError):
                        preservation.restore_file(path, mutant)

    def test_fixed_baselines_reject_rehashed_unrelated_changes(self):
        for path in preservation.REVIEWED_PATHS:
            mutant = int_stacking.checkpoint_file_text(path) + '\n'
            scope = copy.deepcopy(preservation.load_scope())
            row = scope['files'][path]
            row['current_bytes'], row['current_sha256'] = len(mutant.encode()), preservation.sha(mutant)
            with self.subTest(path=path), self.assertRaises(AssertionError):
                preservation.restore_file(path, mutant, scope=scope)

    def test_unique_hunks_reject_rehashed_missing_and_duplicate_context(self):
        for path in preservation.REVIEWED_PATHS:
            current = int_stacking.checkpoint_file_text(path)
            original = preservation.load_scope()
            change = original['files'][path]['reviewed_replacements'][0]
            for label, replacement in (('missing', change['before']),
                                       ('duplicate', change['after'] * 2)):
                mutant = current.replace(change['after'], replacement, 1)
                scope = copy.deepcopy(original)
                row = scope['files'][path]
                row['current_bytes'], row['current_sha256'] = len(mutant.encode()), preservation.sha(mutant)
                with self.subTest(path=path, mutation=label), self.assertRaises(AssertionError):
                    preservation.restore_file(path, mutant, scope=scope)

    def test_forged_scope_cannot_replace_independently_fixed_baseline(self):
        for path in preservation.REVIEWED_PATHS:
            mutant = int_stacking.checkpoint_file_text(path) + '\n'
            forged_old = preservation.checkpoint_file_text(path) + '\n'
            scope = copy.deepcopy(preservation.load_scope())
            row = scope['files'][path]
            row['current_bytes'], row['current_sha256'] = len(mutant.encode()), preservation.sha(mutant)
            row['baseline_bytes'], row['baseline_sha256'] = len(forged_old.encode()), preservation.sha(forged_old)
            with self.subTest(path=path), self.assertRaises(AssertionError):
                preservation.restore_file(path, mutant, scope=scope)

    def test_preserved_inventory_cannot_be_omitted_or_rehashed(self):
        original = preservation.load_scope()
        self.assertTrue(preservation.validate_preserved_files())
        for mutation in ('omit', 'rehash'):
            changed = copy.deepcopy(original)
            path = 'evidence/wisdom-loadout/recipe-proof-sources-2026-11-15.json'
            if mutation == 'omit':
                del changed['preserved_files'][path]
            else:
                changed['preserved_files'][path]['sha256'] = '0' * 64
            fixture = SimpleNamespace(read_text=lambda: json.dumps(changed))
            with self.subTest(mutation=mutation), patch.object(preservation, 'FIXTURE', fixture):
                with self.assertRaises(AssertionError):
                    preservation.load_scope()

    def test_all_older_reversals_keep_their_original_contracts(self):
        self.assertTrue(recipes.validate_full_reversal())
        self.assertTrue(crafting.validate_full_reversal())
        self.assertTrue(corrections.validate_full_reversal())
        self.assertTrue(wisdom.validate_full_reversal())
        for path in recipes.REVIEWED_PATHS:
            with self.subTest(path=path):
                self.assertEqual(recipes.restore_file(path, preservation.checkpoint_file_bytes(path)),
                                 recipes.checkpoint_file_text(path))

    def test_point_five_and_predecessor_snapshots_match_their_own_exact_sources(self):
        import build_snapshot
        current = int_stacking.checkpoint_file_text('index.html')
        old = preservation.checkpoint_file_text('index.html')
        self.assertEqual(build_snapshot.current_build(current), '11-15-26.5')
        self.assertEqual(build_snapshot.current_build(old), '11-15-26.4')
        self.assertEqual((ROOT / 'versions/11-15-26.5.html').read_text(), build_snapshot.snapshot_html(current))
        self.assertEqual((ROOT / 'versions/11-15-26.4.html').read_text(), build_snapshot.snapshot_html(old))

    def test_historical_renderers_bind_exact_point_four_without_global_substitution(self):
        names = ('stacking_audit', 'wisdom_loadout', 'build_stacking_audit')
        before = {name: sys.modules.get(name) for name in names}
        old = json.loads(preservation.checkpoint_file_text(LEDGER))
        calculator = selected_history.checkpoint_module(preservation, 'stacking_audit')
        recipe = selected_history.checkpoint_module(preservation, 'wisdom_loadout')
        renderer = selected_history.checkpoint_module(preservation, 'build_stacking_audit')
        self.assertIsNot(calculator, audit)
        self.assertEqual(calculator.load(), old)
        self.assertEqual(renderer.detail(old), preservation.checkpoint_file_text('endgame-stacking-audit.html'))
        selected = recipe.load()
        html = preservation.checkpoint_file_text('index.html')
        for kind, render in (('recipe', recipe.render_recipe), ('priorities', recipe.render_priorities),
                             ('onepage', recipe.render_onepage_rows)):
            start, end = recipe.MARKERS[kind]
            body = html.split(start, 1)[1].split(end, 1)[0]
            with self.subTest(block=kind):
                self.assertEqual(body, '\n' + render(selected) + '\n')
        self.assertEqual(before, {name: sys.modules.get(name) for name in names})

    def test_cached_modules_still_check_actual_bytes_on_every_access(self):
        for accessor in (preservation.historical_calculator,
                         preservation.historical_recipe_renderer,
                         preservation.historical_audit_renderer):
            accessor()
            with self.subTest(accessor=accessor.__name__):
                with patch.object(preservation, 'checkpoint_file_bytes', side_effect=AssertionError('changed current bytes')):
                    with self.assertRaises(AssertionError):
                        accessor()

    def test_point_five_engine_and_bounded_proof_code_stay_byte_identical(self):
        preserved = preservation.load_scope()['preserved_files']
        for path in ('tools/stacking_audit.py', 'tools/recipe_proofs.py'):
            raw = int_stacking.checkpoint_file_bytes(path)
            with self.subTest(path=path):
                self.assertEqual((len(raw), preservation.sha(raw)),
                                 (preserved[path]['bytes'], preserved[path]['sha256']))
                self.assertEqual(raw, preservation.checkpoint_file_bytes(path))

    def test_actual_engine_preserves_all_seventy_six_complete_old_input_results(self):
        old = json.loads(preservation.checkpoint_file_text(LEDGER))
        frozen = selected_history.checkpoint_module(preservation, 'stacking_audit')
        self.assertEqual(Path(audit.__file__).resolve(), ROOT / 'tools/stacking_audit.py')
        self.assertIsNot(audit.validate, frozen.validate)
        self.assertTrue(audit.validate(old))
        self.assertTrue(frozen.validate(old))
        families = sorted({(row['stat'], row['channel']) for row in old['components']})
        self.assertEqual(len(families), 38)
        before = json.dumps(old, sort_keys=True)
        for stat, channel in families:
            for active in ((), ('force',)):
                with self.subTest(stat=stat, channel=channel, active=active):
                    self.assertEqual(audit.subtotal(old, stat, channel=channel, active=active),
                                     frozen.subtotal(old, stat, channel=channel, active=active))
        self.assertEqual(json.dumps(old, sort_keys=True), before)


if __name__ == '__main__':
    unittest.main()
