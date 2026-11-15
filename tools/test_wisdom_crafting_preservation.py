"""Exact .3-to-checkpoint preservation, not live crafting or mechanics proof.

The original source-finding checkpoint and older correction contracts remain
historical inputs. Actual-current source qualification is exercised separately
by test_wisdom_recipe_integration; actual-current recipe and renderer checks
remain in test_wisdom_loadout and the existing integrity suites. The later .4
layer is reversed before this unchanged historical contract is exercised.
"""
import copy
from pathlib import Path
import unittest

import wisdom_crafting_integration as integration
import wisdom_corrections as corrections
import wisdom_preservation as preservation
import wisdom_recipe_proof_preservation as recipe_proofs


ROOT = Path(__file__).resolve().parents[1]
IMMUTABLE = {
    'tools/fixtures/wisdom-loadout/scope.json': (568103, '3a3d34bc5cb2524bf611bfa2128605daf9f3dd554d458a50928f099d80933bd0'),
    'tools/fixtures/wisdom-corrections/scope.json': (27015, '7a079fd078bf37bf9def7ddd4a67c647a2092206ef0a2ddbfb9823b3da3654ef'),
    'evidence/wisdom-loadout/crafting-browser-2026-11-15.json': (26984, '4394f8f408d6d448a99f473ece71ce26248d3710e8e9243a0d98d532cbd77d01'),
    'tools/stacking_audit.py': (11763, '97432b1a37543645986a343ec0c6d3c8d58b77c4089e03307dfdf2840d3c606d'),
    'versions/11-15-26.1.html': (390376, '9dcc34e46b405d9917a713d14fb3b63f4b5b10c72284a9d516a95486df4cd17f'),
    'versions/11-15-26.2.html': (392943, '48e66b9bb02bc32c991545f6d660e66ea53fa7a4dbb1a5d44535e9bf7200cd67'),
}


class WisdomCraftingPreservationTests(unittest.TestCase):
    def test_scope_binds_exact_approved_checkpoint_and_seven_files(self):
        scope = integration.load_scope()
        self.assertEqual(scope['baseline_commit'], 'fbb1c5ed9aca2c1c360147732ac3ba61c77c435e')
        self.assertEqual(scope['baseline_tree'], 'df677f8c9d2cd113b55d0418dd765729924895c6')
        self.assertEqual(scope['approved_branch'], 'feat/wisdom-loadout-priorities')
        self.assertEqual((scope['baseline_build'], scope['current_build']),
                         ('11-15-26.2', '11-15-26.3'))
        self.assertEqual(len(integration.REVIEWED_PATHS), 7)
        self.assertEqual(set(scope['files']), set(integration.BASE_FILES))
        for path, expected in integration.BASE_FILES.items():
            row = scope['files'][path]
            with self.subTest(path=path):
                self.assertEqual((row['baseline_bytes'], row['baseline_sha256']), expected)
                self.assertTrue(row['reviewed_replacements'])
                self.assertNotEqual(row['current_sha256'], row['baseline_sha256'])

    def test_all_seven_restored_point_three_files_reverse_to_fixed_checkpoint_bytes(self):
        self.assertTrue(integration.validate_full_reversal())
        for path, expected in integration.BASE_FILES.items():
            raw = integration.checkpoint_file_bytes(path)
            with self.subTest(path=path):
                self.assertEqual((len(raw), integration.sha(raw)), expected)
                self.assertEqual(raw.decode(), integration.checkpoint_file_text(path))
                self.assertNotEqual(raw, recipe_proofs.checkpoint_file_bytes(path))

    def test_exact_hunks_also_reconstruct_current_files_in_forward_order(self):
        scope = integration.load_scope()
        for path in integration.REVIEWED_PATHS:
            text = integration.checkpoint_file_text(path)
            for change in scope['files'][path]['reviewed_replacements']:
                self.assertNotEqual(change['before'], change['after'])
                self.assertTrue(change['before'])
                self.assertEqual(text.count(change['before']), 1, path)
                text = text.replace(change['before'], change['after'], 1)
            with self.subTest(path=path):
                self.assertEqual(text, recipe_proofs.checkpoint_file_text(path))

    def test_original_correction_and_wisdom_layers_still_pass_independently(self):
        self.assertTrue(corrections.validate_full_reversal())
        self.assertTrue(preservation.validate_full_reversal())
        for path in preservation.REVIEWED_PATHS:
            checkpoint = integration.checkpoint_file_text(path)
            original = (corrections.restore_file(path, checkpoint)
                        if path in corrections.REVIEWED_PATHS else checkpoint)
            with self.subTest(path=path):
                self.assertEqual(preservation.restore_wisdom_file(path, original),
                                 preservation.predecessor_file_text(path))

    def test_stale_mixed_duplicated_and_unrelated_current_files_are_rejected(self):
        scope = integration.load_scope()
        for path in integration.REVIEWED_PATHS:
            current = recipe_proofs.checkpoint_file_text(path)
            change = scope['files'][path]['reviewed_replacements'][0]
            mutants = {
                'already-old': integration.checkpoint_file_text(path),
                'unrelated': current + '\n',
                'mixed': current.replace(change['after'], change['before'], 1),
                'duplicated': current.replace(change['after'], change['after'] * 2, 1),
            }
            for label, mutant in mutants.items():
                with self.subTest(path=path, mutation=label):
                    self.assertNotEqual(mutant, current)
                    with self.assertRaises(AssertionError):
                        integration.restore_file(path, mutant)

    def test_fixed_checkpoint_rejects_rehashed_unrelated_edits_for_every_file(self):
        for path in integration.REVIEWED_PATHS:
            mutant = recipe_proofs.checkpoint_file_text(path) + '\n'
            scope = copy.deepcopy(integration.load_scope())
            row = scope['files'][path]
            row['current_bytes'] = len(mutant.encode())
            row['current_sha256'] = integration.sha(mutant)
            with self.subTest(path=path), self.assertRaises(AssertionError):
                integration.restore_file(path, mutant, scope=scope)

    def test_exact_context_guards_reject_rehashed_missing_and_duplicate_hunks(self):
        for path in integration.REVIEWED_PATHS:
            current = recipe_proofs.checkpoint_file_text(path)
            original_scope = integration.load_scope()
            change = original_scope['files'][path]['reviewed_replacements'][0]
            for label, replacement in (('missing', change['before']),
                                       ('duplicated', change['after'] * 2)):
                mutant = current.replace(change['after'], replacement, 1)
                scope = copy.deepcopy(original_scope)
                scope['files'][path]['current_bytes'] = len(mutant.encode())
                scope['files'][path]['current_sha256'] = integration.sha(mutant)
                with self.subTest(path=path, mutation=label), self.assertRaises(AssertionError):
                    integration.restore_file(path, mutant, scope=scope)

    def test_forged_scope_baseline_cannot_replace_independently_fixed_checkpoint(self):
        path = 'index.html'
        mutant = recipe_proofs.checkpoint_file_text(path) + '\n'
        forged_checkpoint = integration.checkpoint_file_text(path) + '\n'
        scope = copy.deepcopy(integration.load_scope())
        row = scope['files'][path]
        row['current_bytes'], row['current_sha256'] = len(mutant.encode()), integration.sha(mutant)
        row['baseline_bytes'] = len(forged_checkpoint.encode())
        row['baseline_sha256'] = integration.sha(forged_checkpoint)
        with self.assertRaises(AssertionError):
            integration.restore_file(path, mutant, scope=scope)

    def test_capture_scopes_calculator_and_snapshots_keep_exact_checkpoint_bytes(self):
        for path, expected in IMMUTABLE.items():
            # Captures/scopes/snapshots remain literal; the newly extended
            # calculator must reverse to its unchanged .3 byte/hash assertion.
            raw = recipe_proofs.checkpoint_file_bytes(path)
            with self.subTest(path=path):
                self.assertNotIn(path, integration.REVIEWED_PATHS)
                self.assertEqual((len(raw), integration.sha(raw)), expected)
                self.assertEqual(integration.checkpoint_file_bytes(path), raw)

    def test_new_and_prior_snapshots_each_match_their_exact_source_build(self):
        import build_snapshot
        current = recipe_proofs.checkpoint_file_text('index.html')
        checkpoint = integration.checkpoint_file_text('index.html')
        self.assertEqual(build_snapshot.current_build(current), '11-15-26.3')
        self.assertEqual(build_snapshot.current_build(checkpoint), '11-15-26.2')
        self.assertEqual((ROOT / 'versions/11-15-26.3.html').read_text(),
                         build_snapshot.snapshot_html(current))
        self.assertEqual((ROOT / 'versions/11-15-26.2.html').read_text(),
                         build_snapshot.snapshot_html(checkpoint))


if __name__ == '__main__':
    unittest.main()
