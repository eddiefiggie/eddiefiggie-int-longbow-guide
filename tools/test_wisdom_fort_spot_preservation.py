# Historical .2 contract: exact approved-checkpoint bytes/modules are explicit.
# New selected-recipe tests exercise production separately; no global imports patched.
"""Exact .8 reversal and complete .7 arithmetic preservation.

The production engine remains a normal import and receives explicit old input
for the full-result comparison. Isolated predecessor renderers never replace
global production imports or certify current live-game behavior.
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
from build_snapshot import snapshot_html
import stacking_audit as audit
audit = selected_history.historical_module('stacking_audit')
import wisdom_loadout
wisdom_loadout = selected_history.historical_module('wisdom_loadout')
import wisdom_offense_preservation as offense
import wisdom_fort_spot_preservation as preservation
import wisdom_chains_type_preservation as chains_type


ROOT = selected_history.HistoricalPath(__file__).resolve().parents[1]
LEDGER = 'tools/fixtures/endgame-stacking/ledger.json'
RESULTS = ROOT / 'tools/fixtures/wisdom-fort-spot/baseline-results.json'
RESULTS_SHA = 'ed85fe5c80a8e708d1866707020352556c136283b0601fadc0776fefd9bfee8a'


class FortSpotPreservationTests(unittest.TestCase):
    def test_scope_pins_approved_point_seven_and_literal_history(self):
        scope = preservation.load_scope()
        self.assertEqual(scope['baseline_commit'], '72db151c4f881c08844d273caee2914ddc736641')
        self.assertEqual(scope['baseline_tree'], '573c0b26ac30dce65a3d4fcf6107a38dc5c8058d')
        self.assertEqual((scope['baseline_build'], scope['current_build']),
                         ('11-15-26.7', '11-15-26.8'))
        self.assertEqual(len(scope['files']), 8)
        preserved = scope['preserved_files']
        self.assertEqual(len(preserved), 197)
        self.assertEqual({prefix: sum(p.startswith(prefix + '/') for p in preserved)
                          for prefix in ('evidence', 'tools/fixtures', 'versions')},
                         {'evidence': 51, 'tools/fixtures': 71, 'versions': 73})
        for path in (
                'tools/fixtures/wisdom-loadout/selection.json',
                'tools/fixtures/wisdom-loadout/scope.json',
                'tools/fixtures/wisdom-corrections/scope.json',
                'tools/fixtures/wisdom-crafting-integration/scope.json',
                'tools/fixtures/wisdom-recipe-proofs/scope.json',
                'tools/fixtures/wisdom-int-evidence/scope.json',
                'tools/fixtures/wisdom-int-stacking/scope.json',
                'tools/fixtures/wisdom-offense/scope.json',
                'tools/fixtures/wisdom-offense/baseline-results.json',
                'evidence/wisdom-loadout/offensive-sources-2026-11-15.json',
                'evidence/wisdom-loadout/offensive-mechanics-2026-11-15.json',
                'evidence/wisdom-loadout/offensive-integration-2026-11-15.json',
                'tools/bowmodel.py', 'tools/recipe_proofs.py',
                'versions/11-15-26.7.html'):
            self.assertIn(path, preserved)
        self.assertNotIn('evidence/wisdom-loadout/README.md', preserved)
        self.assertNotIn('versions/11-15-26.8.html', preserved)
        self.assertTrue(preservation.validate_full_reversal())

    def test_every_reviewed_file_reverses_and_reconstructs_exactly(self):
        scope = preservation.load_scope()
        for path, expected in preservation.BASE_FILES.items():
            with self.subTest(path=path):
                old = preservation.checkpoint_file_bytes(path)
                self.assertEqual((len(old), preservation.sha(old)), expected)
                self.assertNotEqual(old, chains_type.checkpoint_file_bytes(path))
                text = old.decode()
                for change in scope['files'][path]['reviewed_replacements']:
                    self.assertTrue(change['before'])
                    self.assertEqual(text.count(change['before']), 1)
                    text = text.replace(change['before'], change['after'], 1)
                self.assertEqual(text, chains_type.checkpoint_file_text(path))

    def test_stale_mixed_duplicate_and_unrelated_bytes_fail_closed(self):
        scope = preservation.load_scope()
        for path in preservation.REVIEWED_PATHS:
            current = chains_type.checkpoint_file_text(path)
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

    def test_rehashed_mutants_cannot_redefine_contexts_or_fixed_baselines(self):
        for path in preservation.REVIEWED_PATHS:
            current = chains_type.checkpoint_file_text(path)
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
                forged_old = preservation.checkpoint_file_text(path) + '\n'
                row['baseline_bytes'], row['baseline_sha256'] = len(forged_old.encode()), preservation.sha(forged_old)
                with self.subTest(path=path, mutation=label), self.assertRaises(AssertionError):
                    preservation.restore_file(path, mutant, scope=scope)

    def test_protected_inventory_cannot_be_removed_or_rehashed(self):
        original = preservation.load_scope()
        for mutation in ('omit', 'rehash'):
            changed = copy.deepcopy(original)
            path = 'tools/fixtures/wisdom-offense/scope.json'
            if mutation == 'omit':
                del changed['preserved_files'][path]
            else:
                changed['preserved_files'][path]['sha256'] = '0' * 64
            fixture = SimpleNamespace(read_text=lambda: json.dumps(changed))
            with self.subTest(mutation=mutation), patch.object(preservation, 'FIXTURE', fixture):
                with self.assertRaises(AssertionError):
                    preservation.load_scope()

    def test_changed_production_and_preserved_bytes_are_rechecked(self):
        original = Path.read_bytes
        for path in (LEDGER, 'evidence/endgame-stacking/source-excerpts.json',
                     'tools/stacking_audit.py', 'tools/bowmodel.py',
                     'evidence/wisdom-loadout/offensive-sources-2026-11-15.json'):
            def changed_bytes(target):
                raw = original(target)
                return raw + b'\n' if target == ROOT / path else raw

            with self.subTest(path=path), patch.object(Path, 'read_bytes', changed_bytes):
                with self.assertRaises(AssertionError):
                    preservation.checkpoint_file_bytes(path)
                with self.assertRaises(AssertionError):
                    preservation.validate_full_reversal()

    def test_outer_view_feeds_unchanged_offense_contract(self):
        self.assertTrue(offense.validate_full_reversal())
        for path in offense.REVIEWED_PATHS:
            with self.subTest(path=path):
                self.assertEqual(offense.restore_file(path, preservation.checkpoint_file_bytes(path)),
                                 offense.checkpoint_file_text(path))

    def test_isolated_point_seven_renderers_and_snapshot_match(self):
        names = ('stacking_audit', 'wisdom_loadout', 'build_stacking_audit')
        before = {name: sys.modules[name] for name in names}
        calculator = selected_history.checkpoint_module(preservation, 'stacking_audit')
        recipe = selected_history.checkpoint_module(preservation, 'wisdom_loadout')
        renderer = selected_history.checkpoint_module(preservation, 'build_stacking_audit')
        self.assertIsNot(calculator, audit)
        self.assertIsNot(recipe, wisdom_loadout)
        self.assertIsNot(renderer, build_stacking_audit)
        self.assertEqual(calculator.load(), json.loads(preservation.checkpoint_file_text(LEDGER)))
        self.assertEqual(renderer.detail(calculator.load()),
                         preservation.checkpoint_file_text('endgame-stacking-audit.html'))
        html = preservation.checkpoint_file_text('index.html')
        self.assertTrue(renderer.validate_guide(html, calculator.load()))
        selected = recipe.load()
        for kind, render in (('recipe', recipe.render_recipe), ('priorities', recipe.render_priorities),
                             ('onepage', recipe.render_onepage_rows)):
            start, end = recipe.MARKERS[kind]
            self.assertEqual(html.split(start, 1)[1].split(end, 1)[0], '\n' + render(selected) + '\n')
        self.assertEqual((ROOT / 'versions/11-15-26.7.html').read_text(), snapshot_html(html))
        self.assertEqual(before, {name: sys.modules[name] for name in names})

    def test_cached_predecessors_revalidate_current_files_on_every_access(self):
        for accessor in (preservation.historical_calculator, preservation.historical_recipe_renderer,
                         preservation.historical_audit_renderer):
            accessor()
            with self.subTest(accessor=accessor.__name__):
                with patch.object(preservation, 'checkpoint_file_bytes', side_effect=AssertionError('changed bytes')):
                    with self.assertRaises(AssertionError):
                        accessor()


class CompletePointSevenArithmeticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = RESULTS.read_bytes()
        assert preservation.sha(raw) == RESULTS_SHA
        cls.expected = json.loads(raw)
        assert cls.expected['schema'] == 'wisdom-fort-spot-preserved-results-v1'
        assert cls.expected['baseline_commit'] == preservation.BASE_COMMIT
        assert cls.expected['baseline_tree'] == preservation.BASE_TREE
        assert cls.expected['baseline_build'] == '11-15-26.7'

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

    def test_actual_engine_preserves_all_152_old_input_complete_results(self):
        self.assertEqual(Path(audit.__file__).resolve(), ROOT / 'tools/stacking_audit.py')
        self.assertEqual(audit.__checkpoint_sha256__, selected_history.sha(selected_history.checkpoint_file_bytes('tools/stacking_audit.py')))
        data = json.loads(preservation.checkpoint_file_text(LEDGER))
        self.assertTrue(audit.validate(data))
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
