"""Actual-current exact reversal guards, separate from historic mechanics tests."""
import copy
import json
import re
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import selected_recipe_preservation as p


class SelectedRecipePreservationTests(unittest.TestCase):
    def test_current_files_reverse_exactly_and_roundtrip(self):
        scope = p.load_scope()
        self.assertEqual(scope['baseline_commit'], '96e937aa57171be6a211136d50e01050b19cb744')
        for path, expected in p.BASE_FILES.items():
            raw = (p.ROOT / path).read_bytes()
            old = p.restore_file(path, raw)
            self.assertEqual((len(old.encode()), p.sha(old)), expected)
            for change in scope['files'][path]['reviewed_replacements']:
                self.assertEqual(old.count(change['before']), 1)
                old = old.replace(change['before'], change['after'], 1)
            self.assertEqual(old.encode(), raw)
        self.assertTrue(p.validate_preserved_files())

    def test_stale_extra_and_rehashed_mutants_fail(self):
        for path in p.BASE_FILES:
            current = (p.ROOT / path).read_text()
            scope = p.load_scope()
            changes = scope['files'][path]['reviewed_replacements']
            if not changes:
                continue
            change = changes[0]
            mutants = [current + '\n', p.checkpoint_file_text(path),
                       current.replace(change['after'], change['after'] * 2, 1)]
            for mutant in mutants:
                with self.subTest(path=path):
                    self.assertNotEqual(mutant, current)
                    with self.assertRaises(AssertionError):
                        p.restore_file(path, mutant)
                    forged = copy.deepcopy(scope)
                    forged['files'][path]['current_bytes'] = len(mutant.encode())
                    forged['files'][path]['current_sha256'] = p.sha(mutant)
                    with self.assertRaises(AssertionError):
                        p.restore_file(path, mutant, scope=forged)

    def test_historical_imports_do_not_replace_production(self):
        import wisdom_loadout
        import stacking_audit
        original = {n: sys.modules[n] for n in ('wisdom_loadout', 'stacking_audit')}
        historic = p.historical_recipe_renderer()
        self.assertIsNot(historic, wisdom_loadout)
        self.assertEqual(historic.__checkpoint_sha256__, p.BASE_FILES['tools/wisdom_loadout.py'][1])
        self.assertEqual(original, {n: sys.modules[n] for n in original})
        self.assertNotEqual(wisdom_loadout.load()['schema'], historic.load()['schema'])

    def test_actual_early_xp_block_is_unchanged_and_new_bands_omit_gift(self):
        actual = (p.ROOT / 'index.html').read_text()
        previous = p.checkpoint_file_text('index.html')
        pattern = r'<aside id="early-xp-options".*?</aside>'
        # The exact preserved source block may use a section rather than aside.
        pattern = r'<(section|aside|div) id="early-xp-options".*?</\1>'
        old = re.search(pattern, previous, re.S)
        self.assertIsNotNone(old)
        self.assertEqual(re.search(pattern, actual, re.S)[0], old[0])
        new_bands = actual[actual.index('id="gear-band-15-19"'):actual.index('id="critical-profile"')]
        self.assertNotIn("Master's Gift", new_bands)

    def test_cached_module_access_rechecks_reviewed_source_bytes(self):
        p.historical_recipe_renderer()
        original = Path.read_bytes
        target = p.ROOT / 'tools/wisdom_loadout.py'
        def changed(path):
            raw = original(path)
            return raw + b'\n' if path == target else raw
        with patch.object(Path, 'read_bytes', changed), self.assertRaises(AssertionError):
            p.historical_recipe_renderer()

    def test_cached_reversal_rereads_scope_bytes_after_success(self):
        current = (p.ROOT / 'index.html').read_bytes()
        expected = p.restore_file('index.html', current)
        scope = p.load_scope()
        scope['files']['index.html']['current_bytes'] += 1
        changed_scope = json.dumps(scope).encode()
        original = Path.read_bytes
        def changed(path):
            return changed_scope if path == p.FIXTURE else original(path)
        with patch.object(Path, 'read_bytes', changed), self.assertRaises(AssertionError):
            p.restore_file('index.html', current)
        self.assertEqual(p.restore_file('index.html', current), expected)
