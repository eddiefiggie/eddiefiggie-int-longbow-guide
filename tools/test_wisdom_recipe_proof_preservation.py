"""Exact .4 preservation plus real-new-engine backward-compatibility checks.

Historical rendering is isolated, not substituted for current qualification.
The actual new calculator is exercised on all 76 unchanged .3 result objects
and direct-source negative controls. These are regression checks, not DDO proof.
"""
import ast
import copy
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import stacking_audit as audit
import wisdom_corrections as corrections
import wisdom_crafting_integration as crafting
import wisdom_preservation as wisdom
import wisdom_recipe_proof_preservation as preservation
import wisdom_int_evidence_preservation as int_evidence
import wisdom_int_stacking_preservation as int_stacking
import wisdom_fort_spot_preservation as fort_spot


ROOT = Path(__file__).resolve().parents[1]
LEDGER = 'tools/fixtures/endgame-stacking/ledger.json'
CALCULATOR = 'tools/stacking_audit.py'
GLABREZU = 'glabrezu-insight-int'
GLABREZU_SOURCE = 'glabrezu-insight-int-live-20261115'


def checkpoint_ledger():
    return json.loads(preservation.checkpoint_file_text(LEDGER))


def component(data, cid):
    return next(row for row in data['components'] if row['id'] == cid)


class RecipeProofPreservationTests(unittest.TestCase):
    def test_exact_approved_checkpoint_eight_paths_and_fifty_five_preserved_records(self):
        scope = preservation.load_scope()
        self.assertEqual(scope['baseline_commit'], '6d978f48fc3eeb807f4560e75ac27e6639af35f4')
        self.assertEqual(scope['baseline_tree'], 'b636b6463a2978410ed4dca75ee5c8fc18c763a1')
        self.assertEqual(scope['approved_branch'], 'feat/wisdom-loadout-priorities')
        self.assertEqual((scope['baseline_build'], scope['current_build']),
                         ('11-15-26.3', '11-15-26.4'))
        self.assertEqual(len(scope['files']), 8)
        self.assertEqual(set(scope['files']), set(preservation.BASE_FILES))
        self.assertEqual(len(scope['preserved_files']), 55)
        self.assertTrue(preservation.validate_full_reversal())

    def test_every_actual_file_reverses_and_reconstructs_in_both_directions(self):
        scope = preservation.load_scope()
        for path, expected in preservation.BASE_FILES.items():
            raw = preservation.checkpoint_file_bytes(path)
            with self.subTest(path=path):
                self.assertEqual((len(raw), preservation.sha(raw)), expected)
                self.assertNotEqual(raw, int_evidence.checkpoint_file_bytes(path))
                text = raw.decode()
                for change in scope['files'][path]['reviewed_replacements']:
                    self.assertTrue(change['before'])
                    self.assertNotEqual(change['before'], change['after'])
                    self.assertEqual(text.count(change['before']), 1)
                    text = text.replace(change['before'], change['after'], 1)
                self.assertEqual(text, int_evidence.checkpoint_file_text(path))

    def test_old_mixed_duplicate_and_unrelated_files_have_no_fallback(self):
        scope = preservation.load_scope()
        for path in preservation.REVIEWED_PATHS:
            current = int_evidence.checkpoint_file_text(path)
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
            mutant = int_evidence.checkpoint_file_text(path) + '\n'
            scope = copy.deepcopy(preservation.load_scope())
            row = scope['files'][path]
            row['current_bytes'], row['current_sha256'] = len(mutant.encode()), preservation.sha(mutant)
            with self.subTest(path=path), self.assertRaises(AssertionError):
                preservation.restore_file(path, mutant, scope=scope)

    def test_unique_context_guards_reject_rehashed_missing_or_duplicated_hunks(self):
        for path in preservation.REVIEWED_PATHS:
            current = int_evidence.checkpoint_file_text(path)
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

    def test_mutable_scope_cannot_replace_the_independent_calculator_baseline(self):
        mutant = int_evidence.checkpoint_file_text(CALCULATOR) + '\n'
        forged_old = preservation.checkpoint_file_text(CALCULATOR) + '\n'
        scope = copy.deepcopy(preservation.load_scope())
        row = scope['files'][CALCULATOR]
        row['current_bytes'], row['current_sha256'] = len(mutant.encode()), preservation.sha(mutant)
        row['baseline_bytes'], row['baseline_sha256'] = len(forged_old.encode()), preservation.sha(forged_old)
        with self.assertRaises(AssertionError):
            preservation.restore_file(CALCULATOR, mutant, scope=scope)

    def test_original_records_are_literal_and_their_inventory_cannot_be_rewritten(self):
        self.assertTrue(preservation.validate_preserved_files())
        original = preservation.load_scope()
        for mutation in ('omit', 'rehash'):
            changed = copy.deepcopy(original)
            path = 'evidence/wisdom-loadout/crafting-browser-2026-11-15.json'
            if mutation == 'omit':
                del changed['preserved_files'][path]
            else:
                changed['preserved_files'][path]['sha256'] = '0' * 64
            fixture = SimpleNamespace(read_text=lambda: json.dumps(changed))
            with self.subTest(mutation=mutation), patch.object(preservation, 'FIXTURE', fixture):
                with self.assertRaises(AssertionError):
                    preservation.load_scope()

    def test_all_older_exact_contracts_remain_independently_valid(self):
        self.assertTrue(crafting.validate_full_reversal())
        self.assertTrue(corrections.validate_full_reversal())
        self.assertTrue(wisdom.validate_full_reversal())
        for path in crafting.REVIEWED_PATHS:
            checkpoint = preservation.checkpoint_file_text(path)
            with self.subTest(path=path):
                self.assertEqual(crafting.restore_file(path, checkpoint),
                                 crafting.checkpoint_file_text(path))

    def test_current_and_prior_snapshots_match_their_own_exact_sources(self):
        import build_snapshot
        current = int_evidence.checkpoint_file_text('index.html')
        old = preservation.checkpoint_file_text('index.html')
        self.assertEqual(build_snapshot.current_build(current), '11-15-26.4')
        self.assertEqual(build_snapshot.current_build(old), '11-15-26.3')
        self.assertEqual((ROOT / 'versions/11-15-26.4.html').read_text(), build_snapshot.snapshot_html(current))
        self.assertEqual((ROOT / 'versions/11-15-26.3.html').read_text(), build_snapshot.snapshot_html(old))

    def test_frozen_renderers_use_exact_data_without_replacing_live_modules(self):
        names = ('stacking_audit', 'wisdom_loadout', 'build_stacking_audit')
        before = {name: sys.modules.get(name) for name in names}
        old = checkpoint_ledger()
        calculator = preservation.historical_calculator()
        recipe = preservation.historical_recipe_renderer()
        renderer = preservation.historical_audit_renderer()
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

    def test_cached_historical_modules_still_revalidate_current_source_bytes(self):
        for accessor in (preservation.historical_calculator,
                         preservation.historical_recipe_renderer,
                         preservation.historical_audit_renderer):
            accessor()
            with self.subTest(accessor=accessor.__name__):
                with patch.object(preservation, 'checkpoint_file_bytes', side_effect=AssertionError('changed current bytes')):
                    with self.assertRaises(AssertionError):
                        accessor()


class RealNewEngineCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.data = checkpoint_ledger()
        self.old = preservation.historical_calculator()

    def test_real_new_engine_matches_all_76_complete_point_three_result_objects(self):
        self.assertEqual(Path(audit.__file__).resolve(), ROOT / CALCULATOR)
        self.assertIsNot(audit.validate, self.old.validate)
        self.assertNotEqual(preservation.sha((ROOT / CALCULATOR).read_bytes()),
                            preservation.BASE_FILES[CALCULATOR][1])
        self.assertTrue(audit.validate(self.data))
        self.assertTrue(self.old.validate(self.data))
        self.assertTrue(all('recipe_proof' not in row for row in self.data['components']))
        families = sorted({(row['stat'], row['channel']) for row in self.data['components']})
        self.assertEqual(len(families), 38)
        before = json.dumps(self.data, sort_keys=True)
        count = 0
        for stat, channel in families:
            for active in ((), ('force',)):
                with self.subTest(stat=stat, channel=channel, active=active):
                    self.assertEqual(audit.subtotal(self.data, stat, channel=channel, active=active),
                                     self.old.subtotal(self.data, stat, channel=channel, active=active))
                count += 1
        self.assertEqual(count, 76)
        self.assertEqual(json.dumps(self.data, sort_keys=True), before)

    def test_existing_contracts_and_historical_positive_rules_are_unchanged(self):
        point_five = int_stacking.historical_calculator()
        # Preserve the original .5-to-.3 equality, including the seven-rule
        # registry. The historical .6/.7 registry adds only its two approved
        # rules; current .8 additions have separate exact-profile tests.
        for name in ('STATES', 'OBSERVATION_POINTERS', 'RULE_CONTRACTS', 'STAT_WORDS'):
            with self.subTest(contract=name):
                self.assertEqual(getattr(point_five, name), getattr(self.old, name))
        for name in ('STATES', 'OBSERVATION_POINTERS', 'STAT_WORDS'):
            with self.subTest(current_contract=name):
                self.assertEqual(getattr(audit, name), getattr(self.old, name))
        point_seven = fort_spot.historical_calculator()
        self.assertEqual(set(point_seven.RULE_CONTRACTS), set(self.old.RULE_CONTRACTS) | {
            'int-selected-ten-pairs', 'fort-enh-insight-observed'})
        for rid, contract in self.old.RULE_CONTRACTS.items():
            with self.subTest(current_legacy_rule=rid):
                self.assertEqual(audit.RULE_CONTRACTS[rid], contract)
        for sid, source in self.data['sources'].items():
            with self.subTest(source=sid):
                self.assertEqual(audit.source_provenance(source), self.old.source_provenance(source))
                self.assertEqual(audit.observation_context(source), self.old.observation_context(source))

    def test_numeric_core_and_historical_interaction_proof_ast_remain_unchanged(self):
        current = ast.parse((ROOT / CALCULATOR).read_text())
        point_five = ast.parse(int_stacking.checkpoint_file_text(CALCULATOR))
        old = ast.parse(preservation.checkpoint_file_text(CALCULATOR))

        def functions(module):
            return {node.name: node for node in module.body if isinstance(node, ast.FunctionDef)}

        a, b, prior = functions(current), functions(old), functions(point_five)
        for name in ('applies', 'proof', 'doubleshot_effective'):
            with self.subTest(historical_function=name):
                self.assertEqual(ast.dump(prior[name], include_attributes=False),
                                 ast.dump(b[name], include_attributes=False))
        # .6 intentionally changes proof dispatch, but applicability,
        # doubleshot arithmetic and the numeric subtotal core stay live checks.
        for name in ('applies', 'doubleshot_effective'):
            with self.subTest(current_function=name):
                self.assertEqual(ast.dump(a[name], include_attributes=False),
                                 ast.dump(b[name], include_attributes=False))

        def arithmetic_tail(function):
            start = next(i for i, node in enumerate(function.body)
                         if isinstance(node, ast.Assign)
                         and any(isinstance(target, ast.Name) and target.id == 'groups'
                                 for target in node.targets))
            return [ast.dump(node, include_attributes=False) for node in function.body[start:]]

        self.assertEqual(arithmetic_tail(a['subtotal']), arithmetic_tail(b['subtotal']))

    def test_real_direct_source_path_still_rejects_forged_source_and_component_inputs(self):
        source_mutations = (
            {'observed': None, 'observed_pointer': None},
            {'observed': '2099-01-01T00:00:00Z'},
            {'revision': None, 'revision_pointer': None},
            {'revision': 'https://ddowiki.com/index.php?title=Item:Legendary_Glabrezu_Claw_Pendant&oldid=1'},
            {'sha256': '0' * 64},
            {'url': 'https://ddowiki.com/page/Item:Legendary_Chains'},
            {'pointer': ['captures', 'chains', 'item_table_visible_text']},
            {'quote': 'Invented +8 Insight bonus to Intelligence.'},
        )
        for fields in source_mutations:
            changed = copy.deepcopy(self.data)
            changed['sources'][GLABREZU_SOURCE].update(fields)
            with self.subTest(source_fields=fields):
                with self.assertRaises((AssertionError, KeyError, IndexError)):
                    audit.validate(changed)
                with self.assertRaises((AssertionError, KeyError, IndexError)):
                    self.old.validate(changed)
        for field, value in (('amount', 8), ('bonus_type', 'Equipment'), ('stat', 'Wisdom'),
                             ('channel', 'build'), ('type_evidence', ''), ('value_pattern', ''),
                             ('source', 'claws-wisdom')):
            changed = copy.deepcopy(self.data)
            component(changed, GLABREZU)[field] = value
            with self.subTest(component_field=field):
                with self.assertRaises((AssertionError, KeyError, IndexError)):
                    audit.validate(changed)
                with self.assertRaises((AssertionError, KeyError, IndexError)):
                    self.old.validate(changed)

    def test_missing_direct_provenance_and_positive_edges_remain_fail_closed(self):
        changed = copy.deepcopy(self.data)
        changed['sources'][GLABREZU_SOURCE].update(observed=None, observed_pointer=None)
        for active in ((), ('force',)):
            result = audit.subtotal(changed, 'Intelligence', active=active)
            with self.subTest(active=active):
                self.assertIn(GLABREZU, result['excluded'])
                self.assertFalse(result['complete'])
                self.assertEqual(result, self.old.subtotal(changed, 'Intelligence', active=active))
        self.assertEqual(audit.subtotal(self.data, 'HP')['total'], 108)
        changed = copy.deepcopy(self.data)
        changed['rules'] = [rule for rule in changed['rules'] if rule['id'] != 'vitality-combination']
        result = audit.subtotal(changed, 'HP')
        self.assertIsNone(result['total'])
        self.assertTrue(result['missing_interactions'])
        self.assertEqual(result, self.old.subtotal(changed, 'HP'))


if __name__ == '__main__':
    unittest.main()
