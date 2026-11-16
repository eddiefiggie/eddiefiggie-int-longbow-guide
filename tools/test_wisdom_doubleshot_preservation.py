"""Exact .2-to-.1 restoration and independently captured complete .1 results.

Current functional tests exercise the real new Doubleshot contract separately.
These checks keep the complete predecessor and the only approved result delta
reviewable; neither path certifies live-game totals or DPS.
"""
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
import wisdom_ability_preservation as abilities
import wisdom_doubleshot_preservation as preservation


ROOT = Path(__file__).resolve().parents[1]
LEDGER = 'tools/fixtures/endgame-stacking/ledger.json'
RESULTS = ROOT / 'tools/fixtures/wisdom-doubleshot/baseline-results.json'
RESULTS_SHA = '153b654bfa877a1a8e9578ae044f788d481a27c991a3c239b6181a767cb94dd2'
NEW_HISTORY = {
    'tools/wisdom_ability_proofs.py',
    'tools/fixtures/wisdom-abilities/scope.json',
    'tools/fixtures/wisdom-abilities/baseline-results.json',
    'evidence/wisdom-loadout/wisdom-con-sources-2026-11-16.json',
    'evidence/wisdom-loadout/wisdom-con-integration-2026-11-16.json',
    'versions/11-16-26.1.html',
}
EXPECTED_DOUBLESHOT = {
    'stat': 'Doubleshot', 'channel': 'gear', 'total': 35,
    'counted': ['goggles-ds', 'ring-ds', 'boots-ds', 'armor-ds', 'quickblade-ds'],
    'suppressed': [], 'excluded': [], 'missing_interactions': [],
    'proofs': [
        ['goggles-ds', 'ring-ds', 'doubleshot-selected-six-pairs'],
        ['goggles-ds', 'boots-ds', 'doubleshot-selected-six-pairs'],
        ['goggles-ds', 'armor-ds', 'doubleshot-selected-six-pairs'],
        ['goggles-ds', 'quickblade-ds', 'artifact-other-types'],
        ['ring-ds', 'boots-ds', 'doubleshot-selected-six-pairs'],
        ['ring-ds', 'armor-ds', 'doubleshot-selected-six-pairs'],
        ['ring-ds', 'quickblade-ds', 'artifact-other-types'],
        ['boots-ds', 'armor-ds', 'doubleshot-selected-six-pairs'],
        ['boots-ds', 'quickblade-ds', 'artifact-other-types'],
        ['armor-ds', 'quickblade-ds', 'artifact-other-types'],
    ],
    'complete': True,
}


class DoubleshotPreservationTests(unittest.TestCase):
    def test_scope_pins_actual_point_one_and_extends_literal_history(self):
        scope = preservation.load_scope()
        self.assertEqual(scope['baseline_commit'], 'dca599357207c5861d2819358f7d011bba5d6dd0')
        self.assertEqual(scope['baseline_tree'], '239b0303b28572df40cda9d9838d76cde2365d0c')
        self.assertEqual((scope['baseline_build'], scope['current_build']),
                         ('11-16-26.1', '11-16-26.2'))
        self.assertEqual(len(scope['files']), 8)
        kept = scope['preserved_files']
        previous = abilities.load_scope()['preserved_files']
        self.assertEqual(len(previous), 209)
        self.assertEqual(len(kept), 215)
        self.assertEqual(set(kept) - set(previous), NEW_HISTORY)
        self.assertEqual({path: kept[path] for path in previous}, previous)
        self.assertEqual({p: sum(k.startswith(p + '/') for k in kept)
                          for p in ('evidence', 'tools/fixtures', 'versions')},
                         {'evidence': 57, 'tools/fixtures': 77, 'versions': 76})
        self.assertNotIn('evidence/wisdom-loadout/README.md', kept)
        self.assertNotIn('evidence/wisdom-loadout/doubleshot-sources-2026-11-16.json', kept)
        self.assertNotIn('versions/11-16-26.2.html', kept)
        self.assertTrue(preservation.validate_full_reversal())

    def test_every_file_reverses_and_reconstructs_exactly(self):
        scope = preservation.load_scope()
        for path, expected in preservation.BASE_FILES.items():
            with self.subTest(path=path):
                raw = preservation.checkpoint_file_bytes(path)
                self.assertEqual((len(raw), preservation.sha(raw)), expected)
                self.assertNotEqual(raw, (ROOT / path).read_bytes())
                text = raw.decode()
                for change in scope['files'][path]['reviewed_replacements']:
                    self.assertTrue(change['before'])
                    self.assertEqual(text.count(change['before']), 1)
                    text = text.replace(change['before'], change['after'], 1)
                self.assertEqual(text, (ROOT / path).read_text())

    def test_stale_mixed_duplicate_and_unrelated_mutants_fail_closed(self):
        for path in preservation.REVIEWED_PATHS:
            scope = preservation.load_scope()
            current = (ROOT / path).read_text()
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
            current = (ROOT / path).read_text()
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

    def test_original_and_new_history_cannot_be_dropped_or_rehashed(self):
        for path in ('tools/fixtures/wisdom-chains-type/scope.json',
                     'tools/fixtures/wisdom-abilities/scope.json',
                     'evidence/wisdom-loadout/wisdom-con-sources-2026-11-16.json'):
            for operation in ('delete', 'rehash'):
                scope = copy.deepcopy(preservation.load_scope())
                if operation == 'delete':
                    del scope['preserved_files'][path]
                else:
                    scope['preserved_files'][path]['sha256'] = '0' * 64
                with patch.object(preservation, 'FIXTURE',
                                  SimpleNamespace(read_text=lambda: json.dumps(scope))):
                    with self.subTest(path=path, operation=operation), self.assertRaises(AssertionError):
                        preservation.load_scope()

    def test_changed_disk_bytes_and_literal_helpers_are_rechecked(self):
        original = Path.read_bytes
        for path in (LEDGER, 'tools/stacking_audit.py', 'tools/bowmodel.py',
                     *preservation.PROOF_DEPENDENCIES,
                     'evidence/wisdom-loadout/wisdom-con-sources-2026-11-16.json',
                     'evidence/wisdom-loadout/wisdom-con-integration-2026-11-16.json'):
            def changed(target):
                raw = original(target)
                return raw + b'\n' if target == ROOT / path else raw
            with self.subTest(path=path), patch.object(Path, 'read_bytes', changed):
                with self.assertRaises(AssertionError):
                    preservation.checkpoint_file_bytes(path)
                with self.assertRaises(AssertionError):
                    preservation.validate_full_reversal()

    def test_outer_view_feeds_the_unchanged_point_one_contract(self):
        self.assertTrue(abilities.validate_full_reversal())
        for path in abilities.REVIEWED_PATHS:
            self.assertEqual(abilities.restore_file(path, preservation.checkpoint_file_bytes(path)),
                             abilities.checkpoint_file_text(path))

    def test_isolated_point_one_renderers_and_snapshot_match_without_global_replacement(self):
        names = ('stacking_audit', 'wisdom_loadout', 'build_stacking_audit',
                 'recipe_proofs', 'fort_spot_proofs', 'chains_type_proofs',
                 'wisdom_ability_proofs')
        before = {name: sys.modules[name] for name in names}
        calculator = preservation.historical_calculator()
        recipe = preservation.historical_recipe_renderer()
        renderer = preservation.historical_audit_renderer()
        self.assertIsNot(calculator, audit)
        self.assertIsNot(recipe, wisdom_loadout)
        self.assertIsNot(renderer, build_stacking_audit)
        dependencies = dict(preservation.historical_proof_dependencies())
        for name, module in dependencies.items():
            self.assertIsNot(module, sys.modules[name])
        data = json.loads(preservation.checkpoint_file_text(LEDGER))
        self.assertEqual(calculator.load(), data)
        self.assertEqual(renderer.detail(data), preservation.checkpoint_file_text('endgame-stacking-audit.html'))
        html = preservation.checkpoint_file_text('index.html')
        self.assertTrue(renderer.validate_guide(html, data))
        for kind, render in (('recipe', recipe.render_recipe), ('priorities', recipe.render_priorities),
                             ('onepage', recipe.render_onepage_rows)):
            start, end = recipe.MARKERS[kind]
            self.assertEqual(html.split(start, 1)[1].split(end, 1)[0],
                             '\n' + render(recipe.load()) + '\n')
        self.assertEqual(snapshot_html(html), (ROOT / 'versions/11-16-26.1.html').read_text())
        self.assertEqual(before, {name: sys.modules[name] for name in names})

    def test_cached_access_rechecks_engine_and_all_four_literal_dependencies(self):
        original = Path.read_bytes
        for accessor in (preservation.historical_calculator,
                         preservation.historical_recipe_renderer,
                         preservation.historical_audit_renderer):
            accessor()
            for path in ('tools/stacking_audit.py', *preservation.PROOF_DEPENDENCIES):
                def changed(target):
                    raw = original(target)
                    return raw + b'\n' if target == ROOT / path else raw
                with self.subTest(accessor=accessor.__name__, path=path):
                    with patch.object(Path, 'read_bytes', changed), self.assertRaises(AssertionError):
                        accessor()


class CompletePointOneArithmeticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = RESULTS.read_bytes()
        assert preservation.sha(raw) == RESULTS_SHA
        cls.expected = json.loads(raw)
        assert cls.expected['schema'] == 'wisdom-doubleshot-preserved-results-v1'
        assert cls.expected['baseline_commit'] == preservation.BASE_COMMIT
        assert cls.expected['baseline_tree'] == preservation.BASE_TREE
        assert cls.expected['baseline_build'] == '11-16-26.1'

    def test_fixture_is_actual_point_one_not_the_preceding_point_nine(self):
        cases = {(case['stat'], case['channel']): case['result']
                 for case in self.expected['ledger_cases']
                 if case['level'] == 36 and not case['active']}
        self.assertEqual((cases['Wisdom', 'gear']['total'], cases['Wisdom', 'gear']['complete']),
                         (18, True))
        con = cases['Constitution', 'gear']
        self.assertEqual((con['total'], con['complete'], con['excluded']), (None, False, ['skull-con']))
        data = json.loads(preservation.checkpoint_file_text(LEDGER))
        self.assertEqual(sum(c['amount'] for c in data['components'] if c['id'] in con['counted']), 17)
        ds = cases['Doubleshot', 'gear']
        self.assertEqual((ds['total'], ds['complete'], ds['excluded']),
                         (None, False, ['quickblade-ds']))
        self.assertEqual(len(ds['missing_interactions']), 6)

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

    def test_actual_new_engine_preserves_all_152_complete_point_one_input_objects(self):
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

    def test_current_delta_is_only_two_level36_gear_doubleshot_objects(self):
        data = audit.load()
        self.assertTrue(audit.validate(data))
        before = json.dumps(data, sort_keys=True)
        changes = []
        for case in self.expected['ledger_cases']:
            result = audit.subtotal(data, case['stat'], channel=case['channel'],
                                    active=case['active'], level=case['level'])
            if result == case['result']:
                continue
            changes.append((case['level'], case['stat'], case['channel'], tuple(case['active'])))
            self.assertEqual((case['level'], case['stat'], case['channel']), (36, 'Doubleshot', 'gear'))
            self.assertEqual((case['result']['total'], case['result']['excluded']),
                             (None, ['quickblade-ds']))
            self.assertEqual(len(case['result']['missing_interactions']), 6)
            self.assertEqual(result, EXPECTED_DOUBLESHOT)
        self.assertEqual(set(changes), {(36, 'Doubleshot', 'gear', active)
                                       for active in ((), ('force',))})
        self.assertEqual(len(changes), 2)
        self.assertEqual(len(self.expected['ledger_cases']) - len(changes), 150)
        self.assertEqual(sum(case['level'] == 35 for case in self.expected['ledger_cases']), 76)
        self.assertEqual(json.dumps(data, sort_keys=True), before)


if __name__ == '__main__':
    unittest.main()

