# Historical .2 contract: exact approved-checkpoint bytes/modules are explicit.
# New selected-recipe tests exercise production separately; no global imports patched.
"""Exact .7 reversal and complete retained arithmetic, not DPS certification.

Current text and source boundaries are tested separately on real production
files. The predecessor modules below never replace normal production imports.
"""
import selected_recipe_preservation as selected_history
import copy
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import bowmodel
import build_stacking_audit
build_stacking_audit = selected_history.historical_module('build_stacking_audit')
import stacking_audit as audit
audit = selected_history.historical_module('stacking_audit')
import wisdom_loadout
wisdom_loadout = selected_history.historical_module('wisdom_loadout')
import wisdom_int_stacking_preservation as int_stacking
import wisdom_offense_preservation as preservation
import wisdom_fort_spot_preservation as fort_spot


ROOT = selected_history.HistoricalPath(__file__).resolve().parents[1]
RESULTS = ROOT / 'tools/fixtures/wisdom-offense/baseline-results.json'
RESULTS_SHA = 'e41e7e7dcac3a128d7a6822c7fc802c3e48218c3718b69abe33dee85b8c009e1'
LEDGER = 'tools/fixtures/endgame-stacking/ledger.json'


class OffensivePreservationTests(unittest.TestCase):
    def test_scope_binds_approved_point_six_and_all_literal_history(self):
        scope = preservation.load_scope()
        self.assertEqual(scope['baseline_commit'], 'cdb39fe7cdfbcbb2d2143c49c88979b008158c28')
        self.assertEqual(scope['baseline_tree'], '11b6e905e2174ea9bcae0ad77c7aaf224e999701')
        self.assertEqual((scope['baseline_build'], scope['current_build']),
                         ('11-15-26.6', '11-15-26.7'))
        self.assertEqual(len(scope['files']), 5)
        preserved = scope['preserved_files']
        self.assertEqual(len(preserved), 194)
        self.assertEqual({prefix: sum(p.startswith(prefix + '/') for p in preserved)
                          for prefix in ('evidence', 'tools/fixtures', 'versions')},
                         {'evidence': 49, 'tools/fixtures': 70, 'versions': 72})
        for path in (
                LEDGER, 'evidence/endgame-stacking/source-excerpts.json',
                'tools/fixtures/wisdom-loadout/selection.json',
                'tools/fixtures/wisdom-loadout/scope.json',
                'tools/fixtures/wisdom-corrections/scope.json',
                'tools/fixtures/wisdom-crafting-integration/scope.json',
                'tools/fixtures/wisdom-recipe-proofs/scope.json',
                'tools/fixtures/wisdom-int-evidence/scope.json',
                'tools/fixtures/wisdom-int-stacking/scope.json',
                'evidence/wisdom-loadout/int-stacking-sources-2026-11-15.json',
                'evidence/wisdom-loadout/int-stacking-integration-2026-11-15.json',
                'tools/bowmodel.py', 'tools/stacking_audit.py', 'tools/recipe_proofs.py',
                'versions/11-15-26.6.html'):
            self.assertIn(path, preserved)
        self.assertNotIn('versions/11-15-26.7.html', preserved)
        self.assertNotIn('evidence/wisdom-loadout/README.md', preserved)
        self.assertTrue(preservation.validate_full_reversal())

    def test_every_reviewed_file_reverses_and_reconstructs_exactly(self):
        scope = preservation.load_scope()
        for path, expected in preservation.BASE_FILES.items():
            raw = preservation.checkpoint_file_bytes(path)
            with self.subTest(path=path):
                self.assertEqual((len(raw), preservation.sha(raw)), expected)
                self.assertNotEqual(raw, fort_spot.checkpoint_file_bytes(path))
                text = raw.decode()
                for change in scope['files'][path]['reviewed_replacements']:
                    self.assertTrue(change['before'])
                    self.assertEqual(text.count(change['before']), 1)
                    text = text.replace(change['before'], change['after'], 1)
                self.assertEqual(text, fort_spot.checkpoint_file_text(path))

    def test_stale_mixed_duplicate_and_unrelated_bytes_fail_closed(self):
        scope = preservation.load_scope()
        for path in preservation.REVIEWED_PATHS:
            current = fort_spot.checkpoint_file_text(path)
            change = scope['files'][path]['reviewed_replacements'][0]
            mutants = {
                'stale': preservation.checkpoint_file_text(path),
                'extra': current + '\n',
                'mixed': current.replace(change['after'], change['before'], 1),
                'duplicate': current.replace(change['after'], change['after'] * 2, 1),
            }
            for label, mutant in mutants.items():
                with self.subTest(path=path, mutation=label):
                    self.assertNotEqual(mutant, current)
                    with self.assertRaises(AssertionError):
                        preservation.restore_file(path, mutant)

    def test_rehashed_mutants_cannot_evade_unique_contexts_or_fixed_baselines(self):
        for path in preservation.REVIEWED_PATHS:
            current = fort_spot.checkpoint_file_text(path)
            original = preservation.load_scope()
            change = original['files'][path]['reviewed_replacements'][0]
            mutants = {
                'unrelated': current + '\n',
                'missing context': current.replace(change['after'], change['before'], 1),
                'duplicate context': current.replace(change['after'], change['after'] * 2, 1),
            }
            for label, mutant in mutants.items():
                scope = copy.deepcopy(original)
                row = scope['files'][path]
                row['current_bytes'], row['current_sha256'] = len(mutant.encode()), preservation.sha(mutant)
                # Even a fixture author supplying a new claimed old hash may
                # not redefine the independently fixed checkpoint.
                forged_old = preservation.checkpoint_file_text(path) + '\n'
                row['baseline_bytes'], row['baseline_sha256'] = len(forged_old.encode()), preservation.sha(forged_old)
                with self.subTest(path=path, mutation=label), self.assertRaises(AssertionError):
                    preservation.restore_file(path, mutant, scope=scope)

    def test_protected_inventory_cannot_be_removed_or_rehashed(self):
        original = preservation.load_scope()
        for mutation in ('omit', 'rehash'):
            changed = copy.deepcopy(original)
            path = 'tools/fixtures/wisdom-int-stacking/scope.json'
            if mutation == 'omit':
                del changed['preserved_files'][path]
            else:
                changed['preserved_files'][path]['sha256'] = '0' * 64
            fixture = SimpleNamespace(read_text=lambda: json.dumps(changed))
            with self.subTest(mutation=mutation), patch.object(preservation, 'FIXTURE', fixture):
                with self.assertRaises(AssertionError):
                    preservation.load_scope()

    def test_real_preserved_ledger_sources_and_engine_are_rechecked(self):
        original = Path.read_bytes
        for path in (LEDGER, 'evidence/endgame-stacking/source-excerpts.json',
                     'tools/bowmodel.py', 'tools/stacking_audit.py'):
            def changed_bytes(target):
                raw = original(target)
                return raw + b'\n' if target == ROOT / path else raw

            with self.subTest(path=path), patch.object(Path, 'read_bytes', changed_bytes):
                with self.assertRaises(AssertionError):
                    preservation.checkpoint_file_bytes(path)
                with self.assertRaises(AssertionError):
                    preservation.validate_preserved_files()

    def test_new_outer_view_feeds_the_unchanged_inner_contract(self):
        self.assertTrue(int_stacking.validate_full_reversal())
        for path in int_stacking.REVIEWED_PATHS:
            with self.subTest(path=path):
                self.assertEqual(int_stacking.restore_file(path, preservation.checkpoint_file_bytes(path)),
                                 int_stacking.checkpoint_file_text(path))

    def test_isolated_point_six_renderers_match_without_global_substitution(self):
        names = ('stacking_audit', 'wisdom_loadout', 'build_stacking_audit')
        before = {name: sys.modules[name] for name in names}
        calculator = selected_history.checkpoint_module(preservation, 'stacking_audit')
        recipe = selected_history.checkpoint_module(preservation, 'wisdom_loadout')
        renderer = selected_history.checkpoint_module(preservation, 'build_stacking_audit')
        self.assertIsNot(calculator, audit)
        self.assertIsNot(recipe, wisdom_loadout)
        self.assertIsNot(renderer, build_stacking_audit)
        self.assertEqual(calculator.load(), json.loads(fort_spot.checkpoint_file_text(LEDGER)))
        self.assertEqual(renderer.detail(calculator.load()),
                         preservation.checkpoint_file_text('endgame-stacking-audit.html'))
        html = preservation.checkpoint_file_text('index.html')
        selected = recipe.load()
        for kind, render in (('recipe', recipe.render_recipe), ('priorities', recipe.render_priorities),
                             ('onepage', recipe.render_onepage_rows)):
            start, end = recipe.MARKERS[kind]
            self.assertEqual(html.split(start, 1)[1].split(end, 1)[0], '\n' + render(selected) + '\n')
        self.assertEqual(before, {name: sys.modules[name] for name in names})

    def test_cached_historical_modules_still_validate_current_files(self):
        for accessor in (preservation.historical_calculator, preservation.historical_recipe_renderer,
                         preservation.historical_audit_renderer):
            accessor()
            with self.subTest(accessor=accessor.__name__):
                with patch.object(preservation, 'checkpoint_file_bytes', side_effect=AssertionError('changed bytes')):
                    with self.assertRaises(AssertionError):
                        accessor()


class CompleteRetainedArithmeticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = RESULTS.read_bytes()
        assert preservation.sha(raw) == RESULTS_SHA
        cls.expected = json.loads(raw)
        assert cls.expected['schema'] == 'wisdom-offense-preserved-results-v1'
        assert cls.expected['baseline_commit'] == preservation.BASE_COMMIT
        assert cls.expected['baseline_tree'] == preservation.BASE_TREE

    def test_actual_model_preserves_all_39_inputs_layers_and_complete_results(self):
        self.assertEqual(Path(bowmodel.__file__).resolve(), ROOT / 'tools/bowmodel.py')
        self.assertEqual(preservation.checkpoint_file_bytes('tools/bowmodel.py'),
                         (ROOT / 'tools/bowmodel.py').read_bytes())
        actual = []
        for level, bows in bowmodel.BANDS.items():
            values = [bowmodel.dmg(bow, level) for _, bow in bows]
            top = max(result[0] for result in values)
            for (name, bow), value in zip(bows, values):
                actual.append({'level': level, 'name': name, 'input': list(bow),
                               'layers': list(bowmodel.layers(level)), 'flat': bowmodel.FLAT[level],
                               'doubleshot_pool': bowmodel.DSPOOL[level], 'result': list(value),
                               'normalized_percent': value[0] / top * 100})
        self.assertEqual(len(actual), 39)
        self.assertEqual(actual, self.expected['bow_model_cases'])

    def test_actual_engine_preserves_all_152_complete_ledger_results(self):
        self.assertEqual(Path(audit.__file__).resolve(), ROOT / 'tools/stacking_audit.py')
        self.assertEqual(audit.__checkpoint_sha256__, selected_history.sha(selected_history.checkpoint_file_bytes('tools/stacking_audit.py')))
        self.assertEqual(preservation.checkpoint_file_bytes(LEDGER), fort_spot.checkpoint_file_bytes(LEDGER))
        data = json.loads(fort_spot.checkpoint_file_text(LEDGER))
        before = json.dumps(data, sort_keys=True)
        families = sorted({(row['stat'], row['channel']) for row in data['components']})
        self.assertEqual(len(families), 38)
        actual = [{'level': level, 'stat': stat, 'channel': channel, 'active': list(active),
                   'result': audit.subtotal(data, stat, channel=channel, active=active, level=level)}
                  for level in (35, 36) for stat, channel in families for active in ((), ('force',))]
        self.assertEqual(len(actual), 152)
        self.assertEqual(actual, self.expected['ledger_cases'])
        self.assertEqual(json.dumps(data, sort_keys=True), before)


if __name__ == '__main__':
    unittest.main()
