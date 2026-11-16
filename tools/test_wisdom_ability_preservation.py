"""Exact outer restoration and complete independently captured .9 outputs."""
import copy
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import bowmodel
import build_stacking_audit
from build_snapshot import snapshot_html
import stacking_audit as audit
import wisdom_loadout
import wisdom_chains_type_preservation as chains_type
import wisdom_ability_preservation as preservation
import wisdom_doubleshot_preservation as doubleshot


ROOT = Path(__file__).resolve().parents[1]
LEDGER = 'tools/fixtures/endgame-stacking/ledger.json'
RESULTS = ROOT / 'tools/fixtures/wisdom-abilities/baseline-results.json'
RESULTS_SHA = 'e96e8c4b561b69eec2d3a70eb5647ce01c7bf7f523d1db1de422a1728a70f16d'


class AbilityPreservationTests(unittest.TestCase):
    def test_scope_pins_approved_point_nine_and_literal_history(self):
        scope = preservation.load_scope()
        self.assertEqual(scope['baseline_commit'], '834b8c4cc648f9263ea19ac4203eedd872888f06')
        self.assertEqual(scope['baseline_tree'], '0b6263ca9bb201b5267774d6f8af198fe013d35e')
        self.assertEqual((scope['baseline_build'], scope['current_build']), ('11-15-26.9', '11-16-26.1'))
        self.assertEqual(len(scope['files']), 8)
        kept = scope['preserved_files']
        self.assertEqual(len(kept), 209)
        self.assertEqual({p: sum(k.startswith(p + '/') for k in kept)
                          for p in ('evidence', 'tools/fixtures', 'versions')},
                         {'evidence': 55, 'tools/fixtures': 75, 'versions': 75})
        for directory in ('wisdom-loadout', 'wisdom-corrections', 'wisdom-crafting-integration',
                          'wisdom-recipe-proofs', 'wisdom-int-evidence', 'wisdom-int-stacking',
                          'wisdom-offense', 'wisdom-fort-spot', 'wisdom-chains-type'):
            self.assertIn('tools/fixtures/' + directory + '/scope.json', kept)
        for path in ('tools/fixtures/wisdom-loadout/selection.json',
                     'tools/fixtures/wisdom-chains-type/baseline-results.json',
                     'evidence/wisdom-loadout/chains-type-sources-2026-11-15.json',
                     'evidence/wisdom-loadout/chains-type-integration-2026-11-15.json',
                     'tools/bowmodel.py', 'tools/recipe_proofs.py',
                     'tools/fort_spot_proofs.py', 'tools/chains_type_proofs.py',
                     'versions/11-15-26.9.html'):
            self.assertIn(path, kept)
        self.assertNotIn('evidence/wisdom-loadout/README.md', kept)
        self.assertNotIn('versions/11-16-26.1.html', kept)
        self.assertTrue(preservation.validate_full_reversal())

    def test_every_file_reverses_and_reconstructs_exactly(self):
        scope = preservation.load_scope()
        for path, expected in preservation.BASE_FILES.items():
            with self.subTest(path=path):
                raw = preservation.checkpoint_file_bytes(path)
                self.assertEqual((len(raw), preservation.sha(raw)), expected)
                self.assertNotEqual(raw, doubleshot.checkpoint_file_bytes(path))
                text = raw.decode()
                for change in scope['files'][path]['reviewed_replacements']:
                    self.assertTrue(change['before'])
                    self.assertEqual(text.count(change['before']), 1)
                    text = text.replace(change['before'], change['after'], 1)
                self.assertEqual(text, doubleshot.checkpoint_file_text(path))

    def test_stale_mixed_duplicate_and_unrelated_mutants_fail_closed(self):
        for path in preservation.REVIEWED_PATHS:
            scope = preservation.load_scope()
            current = doubleshot.checkpoint_file_text(path)
            change = scope['files'][path]['reviewed_replacements'][0]
            mutants = (preservation.checkpoint_file_text(path), current + '\n',
                       current.replace(change['after'], change['before'], 1),
                       current.replace(change['after'], change['after'] * 2, 1))
            for index, mutant in enumerate(mutants):
                with self.subTest(path=path, mutation=index):
                    self.assertNotEqual(mutant, current)
                    with self.assertRaises(AssertionError):
                        preservation.restore_file(path, mutant)

    def test_rehashed_mutants_cannot_redefine_contexts_or_fixed_baselines(self):
        for path in preservation.REVIEWED_PATHS:
            current = doubleshot.checkpoint_file_text(path)
            original = preservation.load_scope()
            change = original['files'][path]['reviewed_replacements'][0]
            for mutant in (current + '\n', current.replace(change['after'], change['before'], 1),
                           current.replace(change['after'], change['after'] * 2, 1)):
                scope = copy.deepcopy(original)
                row = scope['files'][path]
                row['current_bytes'], row['current_sha256'] = len(mutant.encode()), preservation.sha(mutant)
                forged = preservation.checkpoint_file_text(path) + '\n'
                row['baseline_bytes'], row['baseline_sha256'] = len(forged.encode()), preservation.sha(forged)
                with self.subTest(path=path), self.assertRaises(AssertionError):
                    preservation.restore_file(path, mutant, scope=scope)

    def test_literal_inventory_cannot_be_dropped_or_rehashed(self):
        for operation in ('delete', 'rehash'):
            scope = copy.deepcopy(preservation.load_scope())
            path = 'tools/fixtures/wisdom-chains-type/scope.json'
            if operation == 'delete':
                del scope['preserved_files'][path]
            else:
                scope['preserved_files'][path]['sha256'] = '0' * 64
            with patch.object(preservation, 'FIXTURE', SimpleNamespace(read_text=lambda: json.dumps(scope))):
                with self.subTest(operation=operation), self.assertRaises(AssertionError):
                    preservation.load_scope()

    def test_changed_disk_bytes_and_literal_helpers_are_rechecked(self):
        original = Path.read_bytes
        for path in (LEDGER, 'tools/stacking_audit.py', 'tools/bowmodel.py',
                     'tools/recipe_proofs.py', 'tools/fort_spot_proofs.py', 'tools/chains_type_proofs.py',
                     'evidence/wisdom-loadout/chains-type-sources-2026-11-15.json'):
            def changed(target):
                raw = original(target)
                return raw + b'\n' if target == ROOT / path else raw
            with self.subTest(path=path), patch.object(Path, 'read_bytes', changed):
                with self.assertRaises(AssertionError):
                    preservation.checkpoint_file_bytes(path)
                with self.assertRaises(AssertionError):
                    preservation.validate_full_reversal()

    def test_outer_view_feeds_unchanged_chains_contract(self):
        self.assertTrue(chains_type.validate_full_reversal())
        for path in chains_type.REVIEWED_PATHS:
            self.assertEqual(chains_type.restore_file(path, preservation.checkpoint_file_bytes(path)),
                             chains_type.checkpoint_file_text(path))

    def test_isolated_point_nine_renderers_and_snapshot_match_without_global_replacement(self):
        names = ('stacking_audit', 'wisdom_loadout', 'build_stacking_audit',
                 'recipe_proofs', 'fort_spot_proofs', 'chains_type_proofs')
        before = {name: sys.modules[name] for name in names}
        calculator = preservation.historical_calculator()
        recipe = preservation.historical_recipe_renderer()
        renderer = preservation.historical_audit_renderer()
        self.assertIsNot(calculator, audit)
        self.assertIsNot(recipe, wisdom_loadout)
        self.assertIsNot(renderer, build_stacking_audit)
        data = json.loads(preservation.checkpoint_file_text(LEDGER))
        self.assertEqual(calculator.load(), data)
        self.assertEqual(renderer.detail(data), preservation.checkpoint_file_text('endgame-stacking-audit.html'))
        html = preservation.checkpoint_file_text('index.html')
        self.assertTrue(renderer.validate_guide(html, data))
        for kind, render in (('recipe', recipe.render_recipe), ('priorities', recipe.render_priorities),
                             ('onepage', recipe.render_onepage_rows)):
            start, end = recipe.MARKERS[kind]
            self.assertEqual(html.split(start, 1)[1].split(end, 1)[0], '\n' + render(recipe.load()) + '\n')
        self.assertEqual(snapshot_html(html), (ROOT / 'versions/11-15-26.9.html').read_text())
        self.assertEqual(before, {name: sys.modules[name] for name in names})

    def test_cached_access_rechecks_engine_and_every_proof_dependency(self):
        original = Path.read_bytes
        for accessor in (preservation.historical_calculator, preservation.historical_recipe_renderer,
                         preservation.historical_audit_renderer):
            accessor()
            for path in ('tools/stacking_audit.py', *preservation.PROOF_DEPENDENCIES):
                def changed(target):
                    raw = original(target)
                    return raw + b'\n' if target == ROOT / path else raw
                with self.subTest(accessor=accessor.__name__, path=path):
                    with patch.object(Path, 'read_bytes', changed), self.assertRaises(AssertionError):
                        accessor()


class CompletePointNineArithmeticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = RESULTS.read_bytes()
        assert preservation.sha(raw) == RESULTS_SHA
        cls.expected = json.loads(raw)
        assert cls.expected['schema'] == 'wisdom-ability-preserved-results-v1'
        assert cls.expected['baseline_commit'] == preservation.BASE_COMMIT
        assert cls.expected['baseline_tree'] == preservation.BASE_TREE
        assert cls.expected['baseline_build'] == '11-15-26.9'

    def test_all_39_actual_bow_inputs_layers_and_full_results_are_preserved(self):
        actual = []
        self.assertEqual(preservation.checkpoint_file_bytes('tools/bowmodel.py'),
                         (ROOT / 'tools/bowmodel.py').read_bytes())
        for level, bows in bowmodel.BANDS.items():
            values = [bowmodel.dmg(bow, level) for _, bow in bows]
            top = max(value[0] for value in values)
            for (name, bow), value in zip(bows, values):
                actual.append({'level': level, 'name': name, 'input': list(bow),
                               'layers': list(bowmodel.layers(level)), 'flat': bowmodel.FLAT[level],
                               'doubleshot_pool': bowmodel.DSPOOL[level], 'result': list(value),
                               'normalized_percent': value[0] / top * 100})
        self.assertEqual(len(actual), 39)
        self.assertEqual(actual, self.expected['bow_model_cases'])

    def test_actual_new_engine_preserves_all_152_complete_old_input_objects(self):
        self.assertIs(audit, sys.modules['stacking_audit'])
        self.assertEqual(Path(audit.__file__).resolve(), ROOT / 'tools/stacking_audit.py')
        data = json.loads(preservation.checkpoint_file_text(LEDGER))
        self.assertTrue(audit.validate(data))
        before = json.dumps(data, sort_keys=True)
        self.assertEqual(len(self.expected['ledger_cases']), 152)
        for case in self.expected['ledger_cases']:
            with self.subTest(level=case['level'], stat=case['stat'], active=case['active']):
                self.assertEqual(audit.subtotal(data, case['stat'], channel=case['channel'],
                                               active=case['active'], level=case['level']), case['result'])
        self.assertEqual(json.dumps(data, sort_keys=True), before)

    def test_point_one_input_delta_is_only_four_level36_wisdom_constitution_objects(self):
        data = json.loads(doubleshot.checkpoint_file_text(LEDGER))
        self.assertTrue(audit.validate(data))
        before = json.dumps(data, sort_keys=True)
        changes = []
        for case in self.expected['ledger_cases']:
            result = audit.subtotal(data, case['stat'], channel=case['channel'],
                                    active=case['active'], level=case['level'])
            if result == case['result']:
                continue
            changes.append((case['level'], case['stat'], tuple(case['active'])))
            self.assertEqual(case['level'], 36)
            self.assertIn(case['stat'], ('Wisdom', 'Constitution'))
            self.assertEqual(case['result']['counted'], [])
            self.assertEqual(result['missing_interactions'], [])
            if case['stat'] == 'Wisdom':
                self.assertEqual((result['total'], result['complete'], result['excluded']), (18, True, []))
            else:
                self.assertEqual((result['total'], result['complete'], result['excluded']),
                                 (None, False, ['skull-con']))
                self.assertEqual(sum(c['amount'] for c in data['components'] if c['id'] in result['counted']), 17)
        self.assertEqual(set(changes), {(36, stat, active)
                                       for stat in ('Wisdom', 'Constitution') for active in ((), ('force',))})
        self.assertEqual(len(changes), 4)
        self.assertEqual(sum(case['level'] == 35 for case in self.expected['ledger_cases']), 76)
        self.assertEqual(json.dumps(data, sort_keys=True), before)


if __name__ == '__main__':
    unittest.main()
