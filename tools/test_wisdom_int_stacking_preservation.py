# Historical .2 contract: exact approved-checkpoint bytes/modules are explicit.
# New selected-recipe tests exercise production separately; no global imports patched.
"""Strict .6 reversal, literal history and real-engine legacy compatibility.

Historical renderers are isolated checkpoint modules. The current calculator
is imported normally and is exercised independently on unchanged .5 inputs.
New .6 sources and interaction semantics have their own production-input tests.
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
import wisdom_int_stacking_preservation as preservation
import wisdom_int_evidence_preservation as int_evidence
import wisdom_recipe_proof_preservation as recipes
recipes = selected_history.historical_preservation_module('wisdom_recipe_proof_preservation')
import wisdom_crafting_integration as crafting
import wisdom_corrections as corrections
import wisdom_preservation as wisdom
import wisdom_offense_preservation as offense
import wisdom_chains_type_preservation as chains_type


ROOT = selected_history.HistoricalPath(__file__).resolve().parents[1]
LEDGER = 'tools/fixtures/endgame-stacking/ledger.json'
CALCULATOR = 'tools/stacking_audit.py'
DIRECT_INT_BINDINGS = {
    'boots-int': 'melancholic-int-live-20261115',
    'solar-int': 'solar-int-live-20261115',
    'lunar-int': 'lunar-int-live-20261115',
    'festive-int': 'festive-int-live-20261115',
    'dimlight-int': 'dimlight-int-live-20261115',
    'globe-intelligence': 'globe-int-live-20261115',
    'celestial-profane-intelligence': 'celestial-profane-int-live-20261115',
}


class IntelligenceStackingPreservationTests(unittest.TestCase):
    def test_scope_binds_independent_b83_checkpoint_and_complete_old_inventory(self):
        scope = preservation.load_scope()
        self.assertEqual(scope['baseline_commit'], 'b83e6a9251d743ecae39d0301d177a08de54f93c')
        self.assertEqual(scope['baseline_tree'], 'b1b39ce3a38017c67ffd4ea39a9965175c88a243')
        self.assertEqual(scope['approved_branch'], 'feat/wisdom-loadout-priorities')
        self.assertEqual((scope['baseline_build'], scope['current_build']),
                         ('11-15-26.5', '11-15-26.6'))
        self.assertEqual(len(scope['files']), 8)
        self.assertEqual(len(scope['preserved_files']), 187)
        self.assertTrue(preservation.validate_full_reversal())

    def test_protected_inventory_includes_all_baseline_sources_snapshots_and_scopes(self):
        preserved = preservation.load_scope()['preserved_files']
        self.assertEqual({prefix: sum(p.startswith(prefix + '/') for p in preserved)
                          for prefix in ('evidence', 'tools/fixtures', 'versions')},
                         {'evidence': 46, 'tools/fixtures': 68, 'versions': 71})
        for path in (
                'tools/fixtures/wisdom-loadout/selection.json',
                'tools/fixtures/wisdom-loadout/scope.json',
                'tools/fixtures/wisdom-corrections/scope.json',
                'tools/fixtures/wisdom-crafting-integration/scope.json',
                'tools/fixtures/wisdom-recipe-proofs/scope.json',
                'tools/fixtures/wisdom-int-evidence/scope.json',
                'evidence/wisdom-loadout/int-evidence-sources-2026-11-15.json',
                'evidence/wisdom-loadout/int-evidence-integration-2026-11-15.json',
                'versions/11-15-26.5.html', 'tools/bowmodel.py', 'tools/recipe_proofs.py'):
            with self.subTest(path=path):
                self.assertIn(path, preserved)
                self.assertEqual(preservation.checkpoint_file_bytes(path),
                                 chains_type.checkpoint_file_bytes(path))
        self.assertNotIn('evidence/wisdom-loadout/int-stacking-sources-2026-11-15.json', preserved)
        self.assertNotIn('versions/11-15-26.6.html', preserved)
        # The live evidence index is documentation, not an immutable receipt.
        self.assertNotIn('evidence/wisdom-loadout/README.md', preserved)

    def test_all_reviewed_files_reverse_and_reconstruct_in_both_directions(self):
        scope = preservation.load_scope()
        for path, expected in preservation.BASE_FILES.items():
            raw = preservation.checkpoint_file_bytes(path)
            with self.subTest(path=path):
                self.assertEqual((len(raw), preservation.sha(raw)), expected)
                self.assertNotEqual(raw, offense.checkpoint_file_bytes(path))
                text = raw.decode()
                for change in scope['files'][path]['reviewed_replacements']:
                    self.assertTrue(change['before'])
                    self.assertNotEqual(change['before'], change['after'])
                    self.assertEqual(text.count(change['before']), 1)
                    text = text.replace(change['before'], change['after'], 1)
                self.assertEqual(text, offense.checkpoint_file_text(path))

    def test_stale_mixed_duplicate_and_unrelated_current_bytes_fail_closed(self):
        scope = preservation.load_scope()
        for path in preservation.REVIEWED_PATHS:
            current = offense.checkpoint_file_text(path)
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
            mutant = offense.checkpoint_file_text(path) + '\n'
            scope = copy.deepcopy(preservation.load_scope())
            row = scope['files'][path]
            row['current_bytes'], row['current_sha256'] = len(mutant.encode()), preservation.sha(mutant)
            with self.subTest(path=path), self.assertRaises(AssertionError):
                preservation.restore_file(path, mutant, scope=scope)

    def test_unique_hunks_reject_rehashed_missing_and_duplicate_context(self):
        for path in preservation.REVIEWED_PATHS:
            current = offense.checkpoint_file_text(path)
            original = preservation.load_scope()
            change = original['files'][path]['reviewed_replacements'][0]
            for label, replacement in (('missing', change['before']), ('duplicate', change['after'] * 2)):
                mutant = current.replace(change['after'], replacement, 1)
                scope = copy.deepcopy(original)
                row = scope['files'][path]
                row['current_bytes'], row['current_sha256'] = len(mutant.encode()), preservation.sha(mutant)
                with self.subTest(path=path, mutation=label), self.assertRaises(AssertionError):
                    preservation.restore_file(path, mutant, scope=scope)

    def test_forged_scope_cannot_replace_independently_fixed_baseline(self):
        for path in preservation.REVIEWED_PATHS:
            mutant = offense.checkpoint_file_text(path) + '\n'
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
            path = 'tools/fixtures/wisdom-int-evidence/scope.json'
            if mutation == 'omit':
                del changed['preserved_files'][path]
            else:
                changed['preserved_files'][path]['sha256'] = '0' * 64
            fixture = SimpleNamespace(read_text=lambda: json.dumps(changed))
            with self.subTest(mutation=mutation), patch.object(preservation, 'FIXTURE', fixture):
                with self.assertRaises(AssertionError):
                    preservation.load_scope()

    def test_mutated_protected_source_is_rejected_without_changing_a_disk_file(self):
        path = 'evidence/wisdom-loadout/int-evidence-sources-2026-11-15.json'
        original = Path.read_bytes

        def changed_bytes(target):
            raw = original(target)
            return raw + b'\n' if target == ROOT / path else raw

        with patch.object(Path, 'read_bytes', changed_bytes):
            with self.assertRaises(AssertionError):
                preservation.checkpoint_file_bytes(path)
            with self.assertRaises(AssertionError):
                preservation.validate_preserved_files()

    def test_all_older_reversals_keep_their_original_contracts(self):
        for layer in (int_evidence, recipes, crafting, corrections, wisdom):
            with self.subTest(layer=layer.__name__):
                self.assertTrue(layer.validate_full_reversal())
        for path in int_evidence.REVIEWED_PATHS:
            with self.subTest(path=path):
                self.assertEqual(int_evidence.restore_file(path, preservation.checkpoint_file_bytes(path)),
                                 int_evidence.checkpoint_file_text(path))

    def test_current_and_predecessor_snapshots_match_their_own_exact_sources(self):
        import build_snapshot
        current = offense.checkpoint_file_text('index.html')
        old = preservation.checkpoint_file_text('index.html')
        self.assertEqual(build_snapshot.current_build(current), '11-15-26.6')
        self.assertEqual(build_snapshot.current_build(old), '11-15-26.5')
        self.assertEqual((ROOT / 'versions/11-15-26.6.html').read_text(), build_snapshot.snapshot_html(current))
        self.assertEqual((ROOT / 'versions/11-15-26.5.html').read_text(), build_snapshot.snapshot_html(old))

    def test_historical_renderers_bind_exact_point_five_without_global_substitution(self):
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


class RealNewEnginePointFiveCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(preservation.checkpoint_file_text(LEDGER))
        self.old = selected_history.checkpoint_module(preservation, 'stacking_audit')

    def test_real_new_engine_matches_all_76_complete_old_results_at_both_levels(self):
        self.assertEqual(Path(audit.__file__).resolve(), ROOT / CALCULATOR)
        self.assertEqual(audit.__checkpoint_sha256__, selected_history.sha(selected_history.checkpoint_file_bytes('tools/stacking_audit.py')))
        self.assertIsNot(audit.validate, self.old.validate)
        self.assertNotEqual(preservation.sha((ROOT / CALCULATOR).read_bytes()),
                            preservation.BASE_FILES[CALCULATOR][1])
        self.assertTrue(audit.validate(self.data))
        self.assertTrue(self.old.validate(self.data))
        families = sorted({(row['stat'], row['channel']) for row in self.data['components']})
        self.assertEqual(len(families), 38)
        before = json.dumps(self.data, sort_keys=True)
        for level in (35, 36):
            count = 0
            for stat, channel in families:
                for active in ((), ('force',)):
                    with self.subTest(level=level, stat=stat, channel=channel, active=active):
                        self.assertEqual(audit.subtotal(self.data, stat, channel=channel, active=active, level=level),
                                         self.old.subtotal(self.data, stat, channel=channel, active=active, level=level))
                    count += 1
            self.assertEqual(count, 76)
        self.assertEqual(json.dumps(self.data, sort_keys=True), before)

    def test_real_new_engine_keeps_seven_direct_source_missing_metadata_guards(self):
        for cid, sid in DIRECT_INT_BINDINGS.items():
            for field, pointer in (('observed', 'observed_pointer'), ('revision', 'revision_pointer')):
                changed = copy.deepcopy(self.data)
                changed['sources'][sid][field] = None
                changed['sources'][sid][pointer] = None
                with self.subTest(component=cid, missing=field):
                    with self.assertRaises(AssertionError):
                        audit.validate(changed)
                    self.assertIn(cid, audit.subtotal(changed, 'Intelligence')['excluded'])

    def test_real_new_engine_keeps_seven_direct_source_forgery_guards(self):
        mutations = (
            ('url', 'https://ddowiki.com/page/Fortification'),
            ('revision', 'https://ddowiki.com/index.php?title=Intelligence&oldid=1'),
            ('observed', '2099-01-01T00:00:00Z'),
            ('pointer', ['captures', 'missing', 'effect_visible_text']),
            ('record_pointer', ['captures', 'missing']),
            ('quote', '+999 Artifact Bonus to Intelligence'), ('sha256', '0' * 64),
        )
        for cid, sid in DIRECT_INT_BINDINGS.items():
            for field, value in mutations:
                changed = copy.deepcopy(self.data)
                changed['sources'][sid][field] = value
                with self.subTest(component=cid, field=field), self.assertRaises((AssertionError, KeyError)):
                    audit.validate(changed)

    def test_real_new_engine_keeps_seven_direct_clause_guards(self):
        for cid in DIRECT_INT_BINDINGS:
            original = next(row for row in self.data['components'] if row['id'] == cid)
            for field, value in (
                    ('amount', original['amount'] + 1), ('bonus_type', 'Untyped'),
                    ('stat', 'Ranged Power'), ('channel', 'build'),
                    ('value_pattern', r'(?P<value>999)'),
                    ('type_evidence', 'Invented typed Intelligence claim')):
                changed = copy.deepcopy(self.data)
                next(row for row in changed['components'] if row['id'] == cid)[field] = value
                with self.subTest(component=cid, field=field), self.assertRaises(AssertionError):
                    audit.validate(changed)


if __name__ == '__main__':
    unittest.main()
