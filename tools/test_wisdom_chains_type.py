"""Exact .9 acceptance and misuse controls for the two Legendary types.

The ability layer restores the matching .9 calculator, inputs and renderers;
unchanged proof helper bytes are independently checked before historical access.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import chains_type_proofs as types
import fort_spot_proofs as fort_spot
import recipe_proofs as recipes
import wisdom_ability_preservation as abilities

audit = abilities.historical_calculator()
loadout = abilities.historical_recipe_renderer()
renderer = abilities.historical_audit_renderer()


class ChainsTypeIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.assertIs(audit, abilities.historical_calculator())
        self.data = audit.load()

    def row(self, cid, data=None):
        return next(row for row in (self.data if data is None else data)['components']
                    if row['id'] == cid)

    def assert_rejected(self, data, stat):
        with self.assertRaises((AssertionError, KeyError, TypeError, ValueError)):
            audit.validate(data)
        for active in ((), ('force', 'all', 'rage', 'bloodrage', 'rams-might')):
            result = audit.subtotal(data, stat, active=active)
            self.assertIsNone(result['total'])
            self.assertFalse(result['complete'])

    def test_exact_current_results_and_unchanged_intelligence(self):
        self.assertTrue(audit.validate(self.data))
        self.assertEqual([row['id'] for row in self.data['components'] if 'recipe_proof' in row],
                         ['chains-fortification', 'chains-combustion',
                          'chains-quality-int', 'chains-spot'])
        self.assertEqual(audit.subtotal(self.data, 'Fortification'), {
            'stat': 'Fortification', 'channel': 'gear', 'total': 226,
            'counted': ['queen-fortification', 'chains-fortification'],
            'suppressed': [], 'excluded': [], 'missing_interactions': [],
            'proofs': [['queen-fortification', 'chains-fortification', 'fort-enh-insight-observed']],
            'complete': True})
        self.assertEqual(audit.subtotal(self.data, 'Spot'), {
            'stat': 'Spot', 'channel': 'gear', 'total': 27,
            'counted': ['chains-spot', 'heroism-spot', 'luck-spot'],
            'suppressed': [], 'excluded': [], 'missing_interactions': [],
            'proofs': [['chains-spot', 'heroism-spot', 'spot-chains-heroism'],
                       ['chains-spot', 'luck-spot', 'spot-chains-luck'],
                       ['heroism-spot', 'luck-spot', 'spot-heroism-luck']],
            'complete': True})
        intelligence = audit.subtotal(self.data, 'Intelligence')
        self.assertTrue(intelligence['complete'])
        self.assertEqual(intelligence['total'], 37)
        self.assertEqual(intelligence['suppressed'],
                         ['celestial-profane-intelligence', 'globe-intelligence'])

    def test_full_kit_level_gate_still_withholds_all_three_families(self):
        for stat in ('Fortification', 'Spot', 'Intelligence'):
            for active in ((), ('force', 'all')):
                with self.subTest(stat=stat, active=active):
                    result = audit.subtotal(self.data, stat, level=35, active=active)
                    self.assertIsNone(result['total'])
                    self.assertFalse(result['complete'])
                    self.assertEqual(result['counted'], [])

    def test_exact_source_types_keep_missing_parameters_and_provenance(self):
        packet = json.loads((audit.ROOT / types.PACKET_PATH).read_text())
        self.assertEqual(sha256((audit.ROOT / types.PACKET_PATH).read_bytes()).hexdigest(),
                         'a949c385294d81804e6770632fdcb0277c4307bfefc6c1f5396eade2c3946c96')
        self.assertEqual(packet['scope'],
                         'Read-only investigation. No repository, calculator, ledger, or PR changes.')
        for sid in types.SOURCE_SHA256:
            self.assertTrue(types.validate_source(self.data, sid))
        for index, sid in [(2, 'chains-types-fortification-20261115'),
                           (3, 'chains-types-spot-20261115')]:
            source = self.data['sources'][sid]
            self.assertIsNone(source['revision'])
            self.assertIsNone(source['revision_pointer'])
            self.assertFalse(audit.source_provenance(source))
            self.assertIsNone(packet['sources'][index]['numeric_parameter_observed'])
            self.assertIsNone(packet['sources'][index]['source_version_observed'])
            self.assertEqual(source['quote'],
                             packet['sources'][index]['application']['added_effect_markup_exact'])
            self.assertNotIn('+142%', source['quote'])
            self.assertNotIn('+20', source['quote'])
        self.assertEqual(packet['sources'][3]['variant'], '0x7002C66B')

    def test_each_source_binding_is_required_and_cannot_be_relabelled(self):
        mutations = {
            'url': 'https://ddonexus.com/Item/Legendary_Slavers_Spot/2C640',
            'quote': '<li title="+20 Competence bonus to Spot.">Spot +20</li>',
            'observed': '2026-11-16T04:00:00.000Z',
            'observed_pointer': ['prepared_at_utc'],
            'revision': 'https://ddowiki.com/index.php?title=Spot&oldid=1',
            'revision_pointer': ['permalink_href'],
            'record_pointer': ['sources', 1],
            'pointer': ['sources', 3, 'variant'],
            'sha256': '0' * 64,
            'source_contract': 'unreviewed-types-v2',
        }
        for key, value in mutations.items():
            data = deepcopy(self.data)
            data['sources']['chains-types-spot-20261115'][key] = value
            with self.subTest(key=key):
                self.assertFalse(types.validate_source(data, 'chains-types-spot-20261115'))
                self.assert_rejected(data, 'Spot')
        for sid in types.SOURCE_SHA256:
            data = deepcopy(self.data)
            del data['sources'][sid]
            with self.subTest(missing=sid):
                self.assert_rejected(data, 'Fortification' if 'spot-' not in sid else 'Spot')

    def test_each_proof_leg_and_fixed_id_cannot_escape_to_a_direct_source(self):
        for cid in types.COMPONENT_IDS:
            for leg in types.PROOFS[cid]['sources']:
                data = deepcopy(self.data)
                del self.row(cid, data)['recipe_proof']['sources'][leg]
                with self.subTest(cid=cid, missing=leg):
                    self.assert_rejected(data, self.row(cid)['stat'])
            data = deepcopy(self.data)
            row = self.row(cid, data)
            del row['recipe_proof']
            row.update(source='fort-spot-queen-20261115', value_pattern=r'(?P<value>84)',
                       type_evidence='Insight', state='verified')
            with self.subTest(cid=cid, direct_escape=True):
                self.assert_rejected(data, self.row(cid)['stat'])

    def test_complete_families_reject_omission_duplication_and_foreign_members(self):
        for stat, ids in fort_spot.FAMILIES.items():
            for cid in ids:
                for change in ('delete', 'duplicate', 'rename', 'move'):
                    data = deepcopy(self.data)
                    row = self.row(cid, data)
                    if change == 'delete':
                        data['components'].remove(row)
                    elif change == 'duplicate':
                        data['components'].append(deepcopy(row))
                    elif change == 'rename':
                        row['id'] = cid + '-replacement'
                    else:
                        row['channel'] = 'build'
                    with self.subTest(stat=stat, cid=cid, change=change):
                        self.assert_rejected(data, stat)
            data = deepcopy(self.data)
            added = deepcopy(self.row(ids[0], data))
            added.update(id='extra-family-member', amount=999)
            data['components'].append(added)
            with self.subTest(stat=stat, extra=True):
                self.assert_rejected(data, stat)

    def test_selected_definition_core_fields_are_not_caller_options(self):
        for cid in types.COMPONENT_IDS:
            for key, value in [('amount', 999), ('bonus_type', 'Quality'),
                               ('host', 'Legendary Five Rings / Extra'),
                               ('kit_min_level', 28), ('requires', ['force']),
                               ('state', 'conditional'), ('stat', 'Listen')]:
                data = deepcopy(self.data)
                self.row(cid, data)[key] = value
                with self.subTest(cid=cid, key=key):
                    self.assert_rejected(data, self.row(cid)['stat'])

    def test_both_new_edges_are_exact_and_mandatory(self):
        for rid in types.RULE_IDS:
            for change in ('delete', 'duplicate', 'rename', 'types', 'stats', 'pair', 'channel'):
                data = deepcopy(self.data)
                rule = next(r for r in data['rules'] if r['id'] == rid)
                if change == 'delete':
                    data['rules'].remove(rule)
                elif change == 'duplicate':
                    data['rules'].append(deepcopy(rule))
                elif change == 'rename':
                    rule['id'] += '-alias'
                elif change == 'types':
                    rule['types'] = ['*']
                elif change == 'stats':
                    rule['stats'] = ['*']
                elif change == 'pair':
                    rule['component_pairs'] = [['heroism-spot', 'luck-spot']]
                else:
                    rule['channel'] = 'build'
                with self.subTest(rid=rid, change=change):
                    self.assert_rejected(data, 'Spot')
                    self.assertIsNone(audit.proof(data, 'Spot', self.row('chains-spot', data),
                                                self.row('heroism-spot', data)))

    def test_pair_entrypoint_checks_both_orders_and_rejects_detached_arguments(self):
        pairs = [('chains-fortification', 'queen-fortification', 'Fortification',
                  'fort-enh-insight-observed'),
                 ('chains-spot', 'heroism-spot', 'Spot', 'spot-chains-heroism'),
                 ('chains-spot', 'luck-spot', 'Spot', 'spot-chains-luck'),
                 ('heroism-spot', 'luck-spot', 'Spot', 'spot-heroism-luck')]
        for first, second, stat, expected in pairs:
            for a, b in ((self.row(first), self.row(second)), (self.row(second), self.row(first))):
                with self.subTest(first=a['id'], second=b['id']):
                    self.assertEqual(audit.proof(self.data, stat, a, b), expected)
                    detached = deepcopy(a)
                    detached['amount'] += 1
                    self.assertIsNone(audit.proof(self.data, stat, detached, b))
                    self.assertIsNone(audit.proof(self.data, 'Listen', a, b))

    def test_nexus_aliases_cannot_borrow_legacy_provenance(self):
        for host in ('ddonexus.com', 'DDONEXUS.COM', 'www.ddonexus.com',
                     'ddonexus.com.', 'www.ddonexus.com.', 'api.ddonexus.com'):
            data = deepcopy(self.data)
            source = deepcopy(data['sources']['chains-types-fortification-20261115'])
            source.pop('source_contract')
            source.update(path='unreviewed.json', sha256='0' * 64,
                          url='https://' + host + '/Item/Legendary_Slaver_Fortification',
                          revision='https://ddowiki.com/index.php?title=Fortification&oldid=1',
                          revision_pointer=['revision_link'], observed_pointer=['observed'])
            data['sources']['altered-alias'] = source
            row = deepcopy(self.row('chains-fortification'))
            row.pop('recipe_proof')
            row.update(id='foreign-probe', stat='Foreign probe', source='altered-alias',
                       value_pattern=r'(?P<value>142)', type_evidence='Enhancement')
            data['components'].append(row)
            with self.subTest(host=host):
                self.assertTrue(audit.source_provenance(source))
                self.assertTrue(types.bounded_source(source, 'altered-alias'))
                self.assertFalse(audit.component_provenance(data, row))
                self.assertIsNone(audit.subtotal(data, 'Foreign probe')['total'])
                self.assertFalse(audit.subtotal(data, 'Foreign probe')['complete'])
                self.assertIsNone(audit.proof(data, 'Foreign probe', row, deepcopy(row)))

    def test_bounded_sources_cannot_qualify_non_total_effects_or_generic_rules(self):
        for sid in types.SOURCE_SHA256:
            data = deepcopy(self.data)
            data['non_total_effects'].append({'id': 'borrowed-effect', 'state': 'verified',
                'sources': [sid], 'note': 'Deliberately invalid probe', 'host': 'Foreign', 'claim': 'Probe'})
            with self.subTest(sid=sid):
                with self.assertRaises(AssertionError):
                    audit.validate(data)
        data = deepcopy(self.data)
        rule = next(r for r in data['rules'] if r['id'] == 'same-type-best')
        rule['source'] = 'chains-types-fortification-20261115'
        self.assert_rejected(data, 'Fortification')

    def test_actual_file_tampering_cannot_be_authorized_by_updating_the_ledger_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for path in {source['path'] for source in self.data['sources'].values()} | {recipes.MANIFEST_PATH}:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((audit.ROOT / path).read_bytes())
            target = root / types.PACKET_PATH
            packet = json.loads(target.read_text())
            packet['sources'][3]['variant'] = '0x7002C640'
            packet['sources'][3]['application']['removed_slot_exact'] = "Legendary Slaver's Bonus Slot"
            target.write_text(json.dumps(packet))
            data = deepcopy(self.data)
            for sid in types.SOURCE_SHA256:
                data['sources'][sid]['sha256'] = sha256(target.read_bytes()).hexdigest()
            with patch.object(audit, 'ROOT', root):
                self.assertFalse(types.validate_component(data, self.row('chains-spot', data), root))
                self.assertIsNone(audit.subtotal(data, 'Spot')['total'])
            # Restore the source, then change selected applicability on disk.
            target.write_bytes((audit.ROOT / types.PACKET_PATH).read_bytes())
            manifest = root / recipes.MANIFEST_PATH
            selection = json.loads(manifest.read_text())
            selection['selection']['full_kit_ml'] = 28
            manifest.write_text(json.dumps(selection))
            with patch.object(audit, 'ROOT', root):
                self.assertIsNone(audit.subtotal(self.data, 'Fortification')['total'])
                self.assertIsNone(audit.subtotal(self.data, 'Spot')['total'])

    def test_rendered_outputs_describe_actual_totals_and_source_limits(self):
        self.assertTrue(renderer.validate_guide(abilities.checkpoint_file_text('index.html'), self.data))
        paragraph = loadout.render_crafting_qualification(self.data)
        for text in ('226% Fortification', '+27 direct Spot', '+37 at level 36',
                     'numeric parameters are empty', 'data is marked beta',
                     'not an authenticated game-client observation'):
            self.assertIn(text, paragraph)
        self.assertNotIn('INPUT WITHHELD', paragraph)
        self.assertNotIn('Both complete selected totals remain withheld', paragraph)
        detail = renderer.detail(self.data)
        self.assertEqual(detail, abilities.checkpoint_file_text('endgame-stacking-audit.html'))
        self.assertIn('no available revision or client version', detail)
        self.assertIn('Source page', detail)
        self.assertIn('0x7002C66B', detail)

    def test_renderers_refuse_partial_evidence(self):
        data = deepcopy(self.data)
        del data['sources']['chains-types-spot-20261115']
        for render in (renderer.summary, renderer.detail, loadout.render_crafting_qualification):
            with self.subTest(render=render.__name__):
                with self.assertRaises((AssertionError, KeyError)):
                    render(data)


if __name__ == '__main__':
    unittest.main()
