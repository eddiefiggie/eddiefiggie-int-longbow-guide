# Historical .2 contract: exact approved-checkpoint bytes/modules are explicit.
# New selected-recipe tests exercise production separately; no global imports patched.
"""Historical .4 recipe qualification and full-result change boundary.

These tests run the real current engine on .4 inputs and strictly restored .4
renderers. Exact .3 bytes provide the comparison. Actual .6 acceptance lives
separately in test_wisdom_int_stacking; historical rendering cannot certify
its new inputs.
Neither source qualification nor a passing suite certifies live-game DPS.
"""
import selected_recipe_preservation as selected_history
import copy
from hashlib import sha256
import json
from pathlib import Path
import unittest

import stacking_audit as audit
audit = selected_history.historical_module('stacking_audit')
import wisdom_recipe_proof_preservation as preservation
import wisdom_int_evidence_preservation as int_evidence
from test_lamordia_handling import Document, norm


ROOT = selected_history.HistoricalPath(__file__).resolve().parents[1]
LEDGER = 'tools/fixtures/endgame-stacking/ledger.json'
PACKET = 'evidence/wisdom-loadout/recipe-proof-sources-2026-11-15.json'
PACKET_SHA = '32b74bbce3d952f71dae94f22845e8ea414fcc821932e915bd9821f950ac3830'
RECORD = 'evidence/wisdom-loadout/recipe-proof-integration-2026-11-15.json'
QUALIFIED = ('chains-combustion', 'chains-quality-int')
WITHHELD = ('chains-fortification', 'chains-spot')
SOURCE_IDS = {
    'chains-host-recipe-20261115', 'chains-legendary-recipe-20261115',
    'chains-combustion-membership-20261115', 'chains-intelligence-membership-20261115',
}


def components(data):
    return {row['id']: row for row in data['components']}


def current_scope_contract(current, previous):
    """Only the two approved component proofs and documented notes may change."""
    audit.validate(current)
    assert set(current) == set(previous)
    edited = {'sources', 'source_roles', 'components', 'non_total_effects'}
    for key in set(current) - edited:
        assert current[key] == previous[key], key
    assert set(current['sources']) == set(previous['sources']) | SOURCE_IDS
    for sid, source in previous['sources'].items():
        assert current['sources'][sid] == source, sid
        assert current['source_roles'][sid] == previous['source_roles'][sid], sid
    assert set(current['source_roles']) == set(current['sources'])
    assert all(current['source_roles'][sid].startswith('recipe proof: ') for sid in SOURCE_IDS)
    assert [c['id'] for c in current['components']] == [c['id'] for c in previous['components']]
    for row, old in zip(current['components'], previous['components']):
        cid = row['id']
        allowed = ({'state', 'recipe_proof', 'note'} if cid in QUALIFIED else
                   {'note'} if cid == 'chains-fortification' else set())
        assert {k: v for k, v in row.items() if k not in allowed} == {
            k: v for k, v in old.items() if k not in allowed}, cid
        if allowed:
            assert row['note'] and row['note'] != old['note'], cid
        if cid in QUALIFIED:
            assert old['state'] == 'unknown' and row['state'] == 'verified'
            assert set(row) == set(old) | {'recipe_proof'}
            assert row['source'] == row['value_pattern'] == row['type_evidence'] == ''
        else:
            assert set(row) == set(old), cid
    assert [e['id'] for e in current['non_total_effects']] == [e['id'] for e in previous['non_total_effects']]
    for row, old in zip(current['non_total_effects'], previous['non_total_effects']):
        if row['id'] == 'chains-construction':
            assert set(row) == set(old)
            assert {k: v for k, v in row.items() if k != 'note'} == {
                k: v for k, v in old.items() if k != 'note'}
            assert row['note'] != old['note']
        else:
            assert row == old, row['id']
    return True


class CurrentRecipeIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous = json.loads(preservation.checkpoint_file_text(LEDGER))
        cls.old_engine = selected_history.checkpoint_module(preservation, 'stacking_audit')

    def setUp(self):
        self.data = json.loads(int_evidence.checkpoint_file_text(LEDGER))
        self.recipe = selected_history.checkpoint_module(int_evidence, 'wisdom_loadout')
        self.page = selected_history.checkpoint_module(int_evidence, 'build_stacking_audit')

    def test_only_reviewed_two_proofs_and_notes_change(self):
        self.assertTrue(current_scope_contract(self.data, self.previous))
        self.assertEqual(len(self.data['components']), 104)
        self.assertEqual(len(self.data['rules']), 7)

    def test_source_legs_are_actual_full_fields_not_composed_tooltips(self):
        self.assertEqual(sha256((ROOT / PACKET).read_bytes()).hexdigest(), PACKET_SHA)
        for sid in SOURCE_IDS:
            source = self.data['sources'][sid]
            captured = json.loads((ROOT / source['path']).read_text())
            context = audit.resolve(captured, source['pointer'])
            record = audit.resolve(captured, source['record_pointer'])
            self.assertEqual(source['quote'], context)
            self.assertEqual(source['observed'], record['body_observation']['started_at_utc'])
            self.assertEqual(source['revision'], record['revision_link'])
            self.assertEqual(source['url'], record['source_url'])
            self.assertEqual(sha256((ROOT / source['path']).read_bytes()).hexdigest(), source['sha256'])
        packet = json.loads((ROOT / PACKET).read_text())
        member = packet['captures']['ability']
        self.assertIn('Intelligence (INT)', member['ability_members_visible_text'])
        self.assertIn('Abilities are also sometimes named attributes or stats.',
                      member['attribute_synonym_visible_text'])
        self.assertIn('href="/page/Attributes"',
                      packet['captures']['slave_lords_category_link']['quality_attributes_cell_html'])

    def test_all_76_full_results_change_only_as_explicitly_approved(self):
        pairs = sorted({(c['stat'], c['channel']) for c in self.data['components']})
        self.assertEqual(len(pairs), 38)
        changed, unchanged = [], 0
        for stat, channel in pairs:
            for active in ((), ('force',)):
                before = self.old_engine.subtotal(self.previous, stat, channel=channel, active=active)
                after = audit.subtotal(self.data, stat, channel=channel, active=active)
                expected = copy.deepcopy(before)
                if (stat, channel) == ('Combustion', 'gear'):
                    expected.update(total=142, counted=['chains-combustion'], excluded=[], complete=True)
                elif (stat, channel) == ('Intelligence', 'gear'):
                    expected['counted'].append('chains-quality-int')
                    expected['excluded'].remove('chains-quality-int')
                    expected['missing_interactions'] = [['glabrezu-insight-int', 'chains-quality-int']]
                    self.assertIsNone(expected['total'])
                    self.assertFalse(expected['complete'])
                    self.assertEqual(len(expected['excluded']), 7)
                with self.subTest(stat=stat, channel=channel, active=active):
                    self.assertEqual(after, expected)
                if before != after:
                    changed.append((stat, channel, active))
                else:
                    unchanged += 1
        self.assertEqual(changed, [('Combustion', 'gear', ()), ('Combustion', 'gear', ('force',)),
                                   ('Intelligence', 'gear', ()), ('Intelligence', 'gear', ('force',))])
        self.assertEqual(unchanged, 72)

    def test_all_level_35_results_remain_identical_and_floor_36_is_preserved(self):
        for stat, channel in sorted({(c['stat'], c['channel']) for c in self.data['components']}):
            for active in ((), ('force',)):
                self.assertEqual(audit.subtotal(self.data, stat, channel=channel, active=active, level=35),
                                 self.old_engine.subtotal(self.previous, stat, channel=channel,
                                                          active=active, level=35))
        chosen = self.recipe.load()
        self.assertEqual(chosen['selection']['full_kit_ml'], 36)
        self.assertEqual([i['id'] for i in chosen['items'] if i['minor_artifact']], ["Yeenoghu's Reign"])
        self.assertFalse(chosen['optional']['ring_dexterity_13']['selected'])

    def test_unsupported_types_remain_unknown_without_inherited_other_item_binding(self):
        for cid in WITHHELD:
            row = components(self.data)[cid]
            self.assertEqual((row['state'], row['source'], row['value_pattern'], row['type_evidence']),
                             ('unknown', '', '', ''))
            self.assertNotIn('recipe_proof', row)
            self.assertIn(cid, audit.subtotal(self.data, row['stat'])['excluded'])
        self.assertEqual(self.data['rules'], self.previous['rules'])

    def test_current_renderer_and_generated_pages_explicitly_label_proof_kind(self):
        compact = self.recipe.render_crafting_qualification(self.data, compact=True)
        full = self.recipe.render_crafting_qualification(self.data)
        self.assertIn('data-crafting-qualification="bounded-recipe-proof"', compact)
        self.assertEqual(full.count('<strong>SOURCE-SUPPORTED RECIPE DERIVATION</strong>'), 2)
        self.assertEqual(full.count('<strong>RECIPE SUPPORTED · INPUT WITHHELD</strong>'), 2)
        self.assertIn('DIRECT SOURCE-QUALIFIED INPUT', full)
        for limit in ('not weapon damage', 'seven other inputs', 'Insight–Chains Quality',
                      'Fortification and Spot remain excluded', 'not invented finished-item tooltips'):
            self.assertIn(limit, compact)
        html = int_evidence.checkpoint_file_text('index.html')
        self.assertIn(full, html)
        self.assertEqual(html.count(compact), 2)
        self.assertNotIn('data-crafting-qualification="glabrezu-only"', html)
        self.assertIn('build 11-15-26.4', html)
        self.assertTrue(self.page.validate_guide(html, self.data))
        self.assertEqual(int_evidence.checkpoint_file_text('endgame-stacking-audit.html'), self.page.detail(self.data))

    def test_audit_rows_link_all_proof_legs_without_false_missing_source_labels(self):
        document = Document(self.page.detail(self.data))
        for cid in QUALIFIED:
            rows = [n for n in document.root.nodes('tr') if n.attrs.get('id') == 'component-' + cid]
            self.assertEqual(len(rows), 1)
            row = rows[0]
            self.assertIn('verified · source-supported recipe derivation', norm(row.text()))
            self.assertNotIn('source missing', norm(row.text()))
            expected = ['#source-' + sid for sid in components(self.data)[cid]['recipe_proof']['sources'].values()]
            self.assertEqual([n.attrs['href'] for n in row.nodes('a')], expected)

    def test_current_renderer_rejects_stale_or_forged_qualification(self):
        mutations = [('missing proof', lambda d: components(d)['chains-combustion'].pop('recipe_proof')),
                     ('withdrawn state', lambda d: components(d)['chains-quality-int'].update(state='unknown')),
                     ('wrong category', lambda d: components(d)['chains-quality-int']['recipe_proof']['sources'].update(
                         membership='chains-combustion-membership-20261115')),
                     ('unapproved Fortification', lambda d: components(d)['chains-fortification'].update(state='verified')),
                     ('unapproved Spot', lambda d: components(d)['chains-spot'].update(state='verified'))]
        for label, mutate in mutations:
            data = copy.deepcopy(self.data)
            mutate(data)
            with self.subTest(label=label), self.assertRaises(AssertionError):
                self.recipe.render_crafting_qualification(data)

    def test_current_scope_rejects_model_and_semantic_drift(self):
        for field, value in [('amount', 143), ('bonus_type', 'Insight'), ('host', 'Another host'),
                             ('kit_min_level', 28), ('channel', 'build'), ('requires', ['force'])]:
            data = copy.deepcopy(self.data)
            components(data)['chains-combustion'][field] = value
            with self.subTest(field=field), self.assertRaises(AssertionError):
                current_scope_contract(data, self.previous)
        data = copy.deepcopy(self.data)
        components(data)['chains-spot']['note'] += ' Unreviewed change.'
        with self.assertRaises(AssertionError):
            current_scope_contract(data, self.previous)

    def test_generated_source_index_is_literal_current_ledger_projection(self):
        excerpts = json.loads(int_evidence.checkpoint_file_text('evidence/endgame-stacking/source-excerpts.json'))
        self.assertEqual(excerpts['sources'], self.data['sources'])
        self.assertEqual(excerpts['source_roles'], self.data['source_roles'])

    def test_integration_receipt_records_actual_scope_without_publication_claim(self):
        record = json.loads((ROOT / RECORD).read_text())
        self.assertEqual(record['build'], '11-15-26.4')
        self.assertEqual(record['baseline']['remote_head'], '6d978f48fc3eeb807f4560e75ac27e6639af35f4')
        self.assertEqual(record['baseline']['remote_and_initial_staged_tree'], 'b636b6463a2978410ed4dca75ee5c8fc18c763a1')
        self.assertEqual(record['scope']['qualified_component_ids'], list(QUALIFIED))
        self.assertEqual(record['scope']['unqualified_component_ids'], list(WITHHELD))
        self.assertTrue(record['scope']['bounded_proof_engine_added'])
        for field in ('selection_changed', 'priorities_changed', 'positive_interaction_rules_changed',
                      'historical_claim_inventory_regraded', 'new_optimizer_run', 'live_game_test',
                      'new_acquisition_or_event_exception', 'merge_or_publication'):
            self.assertFalse(record['scope'][field], field)
        self.assertEqual(record['result_delta']['changed_level36_records'], 4)
        self.assertEqual(record['result_delta']['unchanged_level36_records'], 72)
        self.assertEqual(record['result_delta']['unchanged_level35_records'], 76)


if __name__ == '__main__':
    unittest.main()
