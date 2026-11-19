# Historical .2 contract: exact approved-checkpoint bytes/modules are explicit.
# New selected-recipe tests exercise production separately; no global imports patched.
"""Adversarial checks of the real bounded recipe path and direct entrypoints.

Fixtures below are in-memory candidate bindings, not rewritten Wiki receipts.
The production integration and unchanged-engine comparisons have separate tests.
"""
import selected_recipe_preservation as selected_history
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import recipe_proofs as proofs
proofs = selected_history.historical_module('recipe_proofs')
import stacking_audit as audit
audit = selected_history.historical_module('stacking_audit')
import wisdom_int_evidence_preservation as int_evidence
import wisdom_chains_type_preservation as chains_type


ROOT = selected_history.HistoricalPath(__file__).resolve().parents[1]
SUPPORTED = ('chains-combustion', 'chains-quality-int')
ROLES = ('host', 'recipe', 'membership')


def component(data, cid):
    return next(row for row in data['components'] if row['id'] == cid)


def raw_record(binding):
    packet, name, _, _ = proofs.SOURCE_BINDINGS[binding]
    path, _ = proofs.PACKETS[packet]
    return json.loads((ROOT / path).read_text())['captures'][name]


def ready_ledger():
    """Exercise the real engine with fixed .4 data and test-only source IDs."""
    data = json.loads(int_evidence.checkpoint_file_text('tools/fixtures/endgame-stacking/ledger.json'))
    for binding in ('host', 'recipe', 'combustion', 'intelligence'):
        packet, name, field, _ = proofs.SOURCE_BINDINGS[binding]
        path, digest = proofs.PACKETS[packet]
        record = raw_record(binding)
        data['sources']['test-proof-' + binding] = {
            'path': path, 'sha256': digest, 'pointer': ['captures', name, field],
            'quote': record[field], 'url': record['source_url'],
            'revision': record['revision_link'],
            'observed': record['body_observation']['started_at_utc'],
            'freshness_limit': 'Scoped retained DOM and actual observation window; not a live-game test.',
            'record_pointer': ['captures', name], 'url_key': 'source_url',
            'revision_pointer': ['revision_link'],
            'observed_pointer': ['body_observation', 'started_at_utc'],
        }
    for cid, membership in zip(SUPPORTED, ('combustion', 'intelligence')):
        row = component(data, cid)
        row.update(state='verified', source='', value_pattern='', type_evidence='',
                   recipe_proof={'contract': 'slave-lords-selected-v1', 'sources': {
                       'host': 'test-proof-host', 'recipe': 'test-proof-recipe',
                       'membership': 'test-proof-' + membership}})
    return data


class BoundedRecipeProofTests(unittest.TestCase):
    def setUp(self):
        self.data = ready_ledger()

    def reject_at_all_entrypoints(self, changed, cid):
        row = component(changed, cid)
        with self.assertRaises(AssertionError):
            proofs.validate_component(changed, row)
        with self.assertRaises((AssertionError, KeyError)):
            audit.validate(changed)
        # No validate() call supplies a cached success token to this separate
        # entrypoint. Exercise conditions/level so the malformed row is reached.
        with self.assertRaises(AssertionError):
            audit.subtotal(changed, row['stat'], channel=row['channel'],
                           active=row['requires'], level=99)

    def test_two_reviewed_proofs_validate_without_direct_tooltip_bindings(self):
        self.assertTrue(audit.validate(self.data))
        for cid in SUPPORTED:
            row = component(self.data, cid)
            with self.subTest(component=cid):
                self.assertTrue(proofs.validate_component(self.data, row))
                self.assertTrue(audit.component_provenance(self.data, row))
                self.assertEqual((row['source'], row['value_pattern'], row['type_evidence']), ('', '', ''))
        self.assertEqual(audit.subtotal(self.data, 'Combustion'), {
            'stat': 'Combustion', 'channel': 'gear', 'total': 142,
            'counted': ['chains-combustion'], 'suppressed': [], 'excluded': [],
            'missing_interactions': [], 'proofs': [], 'complete': True})
        intelligence = audit.subtotal(self.data, 'Intelligence')
        self.assertIsNone(intelligence['total'])
        self.assertFalse(intelligence['complete'])
        self.assertEqual(intelligence['counted'], ['glabrezu-insight-int', 'chains-quality-int'])
        self.assertEqual(intelligence['missing_interactions'],
                         [['glabrezu-insight-int', 'chains-quality-int']])
        self.assertEqual(intelligence['proofs'], [])
        self.assertEqual(len(intelligence['excluded']), 7)

    def test_point_eight_ledger_keeps_two_complete_recipe_proofs_through_current_engine(self):
        # Restore only the input; audit and proofs remain actual production imports.
        current = json.loads(chains_type.checkpoint_file_text('tools/fixtures/endgame-stacking/ledger.json'))
        bound = [c['id'] for c in current['components'] if 'recipe_proof' in c]
        self.assertEqual(bound, list(SUPPORTED))
        self.assertTrue(audit.validate(current))
        for cid in SUPPORTED:
            self.assertTrue(proofs.validate_component(current, component(current, cid)))
        for cid in ('chains-fortification', 'chains-spot'):
            row = component(current, cid)
            self.assertEqual((row['state'], row['source']), ('unknown', ''))
            self.assertIn(cid, audit.subtotal(current, row['stat'], active=('force',))['excluded'])

    def test_source_aliases_do_not_supply_authority_but_correct_contexts_still_work(self):
        changed = copy.deepcopy(self.data)
        row = component(changed, 'chains-combustion')
        for role in ROLES:
            previous = row['recipe_proof']['sources'][role]
            alias = 'arbitrary-id-for-' + role
            changed['sources'][alias] = copy.deepcopy(changed['sources'][previous])
            row['recipe_proof']['sources'][role] = alias
        self.assertTrue(proofs.validate_component(changed, row))
        row['recipe_proof']['sources']['membership'] = 'test-proof-host'
        self.reject_at_all_entrypoints(changed, row['id'])

    def test_missing_null_empty_unknown_and_assertion_only_proofs_do_not_fall_back(self):
        for cid in proofs.BOUNDED_COMPONENT_IDS:
            for payload in ('missing', None, {}, False, [],
                            {'contract': 'unknown', 'sources': {}},
                            {'contract': proofs.CONTRACT, 'sources': {}, 'verified': True}):
                changed = copy.deepcopy(self.data)
                row = component(changed, cid)
                row.update(state='verified', source='glabrezu-insight-int-live-20261115')
                if payload == 'missing':
                    row.pop('recipe_proof', None)
                else:
                    row['recipe_proof'] = copy.deepcopy(payload)
                with self.subTest(component=cid, proof=payload):
                    self.reject_at_all_entrypoints(changed, cid)

    def test_dual_direct_binding_is_rejected_even_with_a_valid_proof(self):
        for cid in SUPPORTED:
            for field, value in (('source', 'glabrezu-insight-int-live-20261115'),
                                 ('value_pattern', r'(?P<value>142)'),
                                 ('type_evidence', 'Equipment')):
                changed = copy.deepcopy(self.data)
                component(changed, cid)[field] = value
                with self.subTest(component=cid, field=field):
                    self.reject_at_all_entrypoints(changed, cid)

    def test_unapproved_component_and_duplicate_component_cannot_use_the_route(self):
        changed = copy.deepcopy(self.data)
        component(changed, 'chains-combustion')['id'] = 'invented-combustion'
        self.reject_at_all_entrypoints(changed, 'invented-combustion')
        for cid in SUPPORTED:
            changed = copy.deepcopy(self.data)
            changed['components'].append(copy.deepcopy(component(changed, cid)))
            with self.subTest(duplicate=cid):
                self.reject_at_all_entrypoints(changed, cid)

    def test_selected_amount_stat_type_host_channel_level_and_conditions_are_bound(self):
        mutations = (
            ('amount', 70), ('amount', 142.0), ('stat', 'Fire weapon damage'),
            ('bonus_type', 'Alchemical'), ('host', 'Legendary Chains / Prefix'),
            ('channel', 'build'), ('kit_min_level', 28), ('kit_min_level', 37),
            ('requires', ['force']), ('state', 'conditional'))
        for field, value in mutations:
            changed = copy.deepcopy(self.data)
            row = component(changed, 'chains-combustion')
            row[field] = value
            if field == 'state':
                row['requires'] = ['force']
            with self.subTest(field=field, value=value):
                self.reject_at_all_entrypoints(changed, row['id'])

    def test_missing_swapped_duplicate_or_extra_proof_legs_are_rejected(self):
        for cid in SUPPORTED:
            for mode in ('missing-host', 'missing-recipe', 'missing-membership', 'swapped', 'duplicate', 'extra'):
                changed = copy.deepcopy(self.data)
                sources = component(changed, cid)['recipe_proof']['sources']
                if mode.startswith('missing-'):
                    del sources[mode.removeprefix('missing-')]
                elif mode == 'swapped':
                    sources['host'], sources['recipe'] = sources['recipe'], sources['host']
                elif mode == 'duplicate':
                    sources['membership'] = sources['host']
                else:
                    sources['type'] = 'test-proof-intelligence'
                with self.subTest(component=cid, mode=mode):
                    self.reject_at_all_entrypoints(changed, cid)

    def test_every_leaf_rejects_missing_or_wrong_provenance_context_and_quote(self):
        for cid in SUPPORTED:
            for role in ROLES:
                original = self.data['sources'][component(self.data, cid)['recipe_proof']['sources'][role]]
                mutations = (
                    {'observed': None, 'observed_pointer': None},
                    {'observed': '2026-11-15T00:00:00Z'},
                    {'observed_pointer': ['page_modified_display']},
                    {'observed_pointer': ['body_observation', 'ended_at_utc']},
                    {'revision': None, 'revision_pointer': None},
                    {'revision': 'https://ddowiki.com/index.php?title=Ability&oldid=1'},
                    {'record_pointer': ['captures', 'glabrezu']},
                    {'pointer': ['captures', 'glabrezu', 'selected_option_html']},
                    {'sha256': '0' * 64},
                    {'path': 'evidence/wisdom-loadout/sources.json'},
                    {'url': 'https://ddowiki.com/page/Item:Legendary_Keylock_Ring'},
                    {'quote': original['quote'][:25]},
                    {'quote': 'Invented +142 Equipment Combustion on Legendary Chains.'},
                    {'freshness_limit': ''},
                )
                for fields in mutations:
                    changed = copy.deepcopy(self.data)
                    sid = component(changed, cid)['recipe_proof']['sources'][role]
                    changed['sources'][sid].update(fields)
                    with self.subTest(component=cid, role=role, fields=tuple(fields)):
                        self.reject_at_all_entrypoints(changed, cid)
                changed = copy.deepcopy(self.data)
                del changed['sources'][component(changed, cid)['recipe_proof']['sources'][role]]
                with self.subTest(component=cid, role=role, removed=True):
                    self.reject_at_all_entrypoints(changed, cid)

    def test_source_file_and_selected_manifest_are_reread_without_cached_success(self):
        self.assertTrue(proofs.validate_component(self.data, component(self.data, 'chains-combustion')))
        read_bytes = Path.read_bytes
        for relative in (proofs.MANIFEST_PATH, proofs.PACKETS['crafting'][0]):
            target = ROOT / relative

            def changed_bytes(path):
                raw = read_bytes(path)
                return raw + b'\n' if path == target else raw

            with self.subTest(path=relative), patch.object(Path, 'read_bytes', changed_bytes):
                self.reject_at_all_entrypoints(self.data, 'chains-combustion')
        changed = copy.deepcopy(self.data)
        changed['sources']['test-proof-recipe']['sha256'] = '0' * 64
        self.reject_at_all_entrypoints(changed, 'chains-combustion')

    def test_semantic_host_and_header_guards_reject_wrong_slots_tiers_and_columns(self):
        host, recipe = raw_record('host'), raw_record('recipe')
        self.assertTrue(proofs._host_and_recipe(host, recipe, 'Suffix'))
        for old, new in (('Minimum level\t28', 'Minimum level\t8'),
                         ("\nLegendary Slaver's Suffix Slot\n", "\nHeroic Slaver's Suffix Slot\n"),
                         ('or the Waist slot', 'but not the Waist slot')):
            changed = copy.deepcopy(host)
            changed['item_table_visible_text'] = changed['item_table_visible_text'].replace(old, new)
            with self.subTest(host_mutation=old), self.assertRaises(AssertionError):
                proofs._host_and_recipe(changed, recipe, 'Suffix')
        changed = copy.deepcopy(host)
        changed['slot_tooltip_text']["Legendary Slaver's Suffix Slot"] = 'Apply a different shard.'
        with self.assertRaises(AssertionError):
            proofs._host_and_recipe(changed, recipe, 'Suffix')
        for mode in ('swapped-columns', 'wrong-span', 'missing-offer', 'missing-group', 'duplicate-group'):
            changed = copy.deepcopy(recipe)
            if mode == 'swapped-columns':
                header = changed['recipe_table_headers'][1]
                header[0], header[1] = header[1], header[0]
            elif mode == 'wrong-span':
                changed['recipe_table_headers'][0][2]['column_span'] = 1
            elif mode == 'missing-offer':
                changed['gem_slot_rule_visible_text'] = 'Some effects exist.'
            elif mode == 'missing-group':
                changed['recipe_table_visible_text'] = changed['recipe_table_visible_text'].replace('\nSuffix\n', '\nOther\n')
            else:
                changed['recipe_table_visible_text'] += '\nSuffix\n'
            with self.subTest(recipe_mutation=mode), self.assertRaises(AssertionError):
                proofs._host_and_recipe(host, changed, 'Suffix')

    def test_semantic_recipe_guards_bind_group_row_value_unit_and_not_nearby_numbers(self):
        host, recipe, member = raw_record('host'), raw_record('recipe'), raw_record('combustion')
        group = proofs._host_and_recipe(host, recipe, 'Suffix')
        proofs._combustion(recipe, group, member)
        for old, new in (('+142', '+70'), ('+142', '+142%'), ('+142', '+143'),
                         ('/page/Spell_Power', '/page/Spell_Lore'),
                         ('Equipment Bonus', 'Alchemical Bonus')):
            changed = copy.deepcopy(recipe)
            changed['spell_power_row_html'] = changed['spell_power_row_html'].replace(old, new)
            with self.subTest(row_mutation=(old, new)), self.assertRaises(AssertionError):
                proofs._combustion(changed, group, member)
        for wrong_group in ('Spell Power\t+142', group.replace('Spell Power (single type)', 'Spell Lore (single type)'), group + '\n' + group):
            with self.subTest(group=wrong_group[:45]), self.assertRaises(AssertionError):
                proofs._combustion(recipe, wrong_group, member)
        changed = copy.deepcopy(recipe)
        changed['spell_power_row_html'] *= 2
        with self.assertRaises(AssertionError):
            proofs._combustion(changed, group, member)

    def test_semantic_membership_guards_do_not_transfer_other_effects_or_types(self):
        host, recipe, member = raw_record('host'), raw_record('recipe'), raw_record('combustion')
        group = proofs._host_and_recipe(host, recipe, 'Suffix')
        for field, old, new in (
                ('headers_visible_text', 'Equipment bonus', 'Alchemical bonus'),
                ('selected_row_html', '/page/Combustion', '/page/Corrosion'),
                ('selected_row_html', 'Fire Spells', 'Fire weapon damage'),
                ('selected_row_visible_text', 'Combustion', 'Inferno'),
                ('weapon_limit_visible_text', 'does not affect', 'always affects')):
            changed = copy.deepcopy(member)
            changed[field] = changed[field].replace(old, new)
            with self.subTest(field=field), self.assertRaises(AssertionError):
                proofs._combustion(recipe, group, changed)

    def test_quality_attribute_requires_exact_category_membership_and_synonym(self):
        host, recipe, member = raw_record('host'), raw_record('recipe'), raw_record('intelligence')
        group = proofs._host_and_recipe(host, recipe, 'Bonus')
        proofs._quality_intelligence(recipe, group, member)
        for field, value in (
                ('requested_url', 'https://ddowiki.com/page/Nearly_Complete'),
                ('ability_members_visible_text', member['ability_members_visible_text'].replace('Intelligence (INT), ', '')),
                ('attribute_synonym_visible_text', 'Abilities and attributes are different categories.')):
            changed = copy.deepcopy(member)
            changed[field] = value
            with self.subTest(field=field), self.assertRaises(AssertionError):
                proofs._quality_intelligence(recipe, group, changed)
        for old, new in (('\t+1\t+3\t', '\t+3\t+1\t'), ('Quality Attributes', 'Insightful Attributes')):
            changed = copy.deepcopy(recipe)
            changed['quality_attributes_row_visible_text'] = changed['quality_attributes_row_visible_text'].replace(old, new)
            with self.subTest(row_mutation=old), self.assertRaises(AssertionError):
                proofs._quality_intelligence(changed, group, member)
        with self.assertRaises(AssertionError):
            proofs._quality_intelligence(recipe, 'Quality Attributes +3', member)

    def test_unresolved_fortification_and_spot_cannot_be_promoted_by_borrowing_proofs(self):
        for cid in ('chains-fortification', 'chains-spot'):
            changed = copy.deepcopy(self.data)
            row = component(changed, cid)
            row.update(state='verified', recipe_proof=copy.deepcopy(
                component(changed, 'chains-combustion')['recipe_proof']))
            with self.subTest(component=cid):
                self.reject_at_all_entrypoints(changed, cid)
        self.assertEqual(set(proofs.BOUNDED_COMPONENT_IDS), {
            'chains-combustion', 'chains-quality-int', 'chains-fortification', 'chains-spot'})
        self.assertEqual(set(proofs.UNRESOLVED), {'chains-fortification', 'chains-spot'})

    def test_component_qualification_creates_no_new_stacking_edge_or_lower_level_permission(self):
        left = component(self.data, 'glabrezu-insight-int')
        right = component(self.data, 'chains-quality-int')
        self.assertIsNone(audit.proof(self.data, 'Intelligence', left, right))
        self.assertEqual(len(self.data['rules']), 7)
        for cid in SUPPORTED:
            row = component(self.data, cid)
            for active in ((), ('force',)):
                with self.subTest(component=cid, active=active):
                    at35 = audit.subtotal(self.data, row['stat'], level=35, active=active)
                    self.assertIn(cid, at35['excluded'])
                    self.assertNotIn(cid, at35['counted'])
                    self.assertIsNone(at35['total'])
                    self.assertIn(cid, audit.subtotal(self.data, row['stat'], level=36, active=active)['counted'])

    def test_existing_direct_clause_mutations_still_use_real_unchanged_validation(self):
        for field, value in (('amount', 8), ('stat', 'Wisdom'),
                             ('bonus_type', 'Enhancement'), ('type_evidence', 'Enhancement bonus')):
            changed = copy.deepcopy(self.data)
            component(changed, 'glabrezu-insight-int')[field] = value
            with self.subTest(field=field), self.assertRaises(AssertionError):
                audit.validate(changed)


if __name__ == '__main__':
    unittest.main()
