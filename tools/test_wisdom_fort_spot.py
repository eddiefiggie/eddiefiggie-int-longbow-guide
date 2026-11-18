"""Exact restored .8 routes: three definitions, one pair, incomplete families.

The .9 outer contract restores the .8 engine, proof helpers and input bytes.
All original .8 negative controls run against those matching dependencies and
temporary source copies; separate Chains tests exercise actual .9 production.
Passing these checks is not a live-game or complete-character certificate.
"""
from contextlib import contextmanager
# Historical assertions run against the exact authenticated checkpoint.
import selected_recipe_preservation as selected_history

import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import wisdom_fort_spot_preservation as preservation
import wisdom_chains_type_preservation as chains_type


audit = selected_history.checkpoint_module(chains_type, 'stacking_audit')
definitions = selected_history.checkpoint_module(chains_type, 'fort_spot_proofs')


ROOT = selected_history.HistoricalPath(__file__).resolve().parents[1]
LEDGER = 'tools/fixtures/endgame-stacking/ledger.json'
MANIFEST = 'tools/fixtures/wisdom-loadout/selection.json'
PACKET = 'evidence/wisdom-loadout/fort-spot-sources-2026-11-15.json'
PACKET_SHA = 'a9b2ef77eb3ca10dc77ab93e22a201517920a709615c0905e3e21d77a1cc3456'
MANIFEST_SHA = '8223bd8e25ed9dc4ad9454439ead42dfb693cc008d18d0ddfeb270d33863c37d'
OLD_LEDGER_SHA = 'cb71531a07b73697b0af1bccf6fe330e10e0db900a7f194f79036ce3ccf2da0a'
RESULTS = 'tools/fixtures/wisdom-fort-spot/baseline-results.json'
RESULTS_SHA = 'ed85fe5c80a8e708d1866707020352556c136283b0601fadc0776fefd9bfee8a'
RULE = 'spot-heroism-luck'
QUALIFIED = {'queen-fortification', 'heroism-spot', 'luck-spot'}
FAMILIES = {'Fortification': ('queen-fortification', 'chains-fortification'),
            'Spot': ('chains-spot', 'heroism-spot', 'luck-spot')}
FAMILY_IDS = set().union(*map(set, FAMILIES.values()))
LEGACY_RULES = {'same-type-best', 'artifact-other-types', 'exceptional-other-types',
                'prr-combination', 'mrr-combination', 'vitality-combination',
                'fort-enh-insight'}
INT_RULES = LEGACY_RULES | {'int-selected-ten-pairs', 'fort-enh-insight-observed'}
EXPECTED_RULE = {
    'id': RULE, 'source': 'fort-spot-tip179-20261115',
    'quote': 'Different types of bonuses stack', 'kind': 'selected_pairs',
    'types': ['Morale', 'Luck'], 'stats': ['Spot'], 'channel': 'gear',
    'component_pairs': [['heroism-spot', 'luck-spot']],
}
EXPECTED_RESULTS = {
    'Fortification': {
        'stat': 'Fortification', 'channel': 'gear', 'total': None,
        'counted': ['queen-fortification'], 'suppressed': [],
        'excluded': ['chains-fortification'], 'missing_interactions': [],
        'proofs': [], 'complete': False,
    },
    'Spot': {
        'stat': 'Spot', 'channel': 'gear', 'total': None,
        'counted': ['heroism-spot', 'luck-spot'], 'suppressed': [],
        'excluded': ['chains-spot'], 'missing_interactions': [],
        'proofs': [['heroism-spot', 'luck-spot', RULE]], 'complete': False,
    },
}
# Each role is tied to its original observation, not a date reconstructed from
# the new packet's filename or an independently unobserved revision endpoint.
SOURCE_BINDINGS = {
    'fort-spot-queen-20261115': (0, ['exact_dom_markup'], '715898', '2026-11-16T01:05:25.602Z'),
    'fort-spot-heroism-20261115': (4, ['exact_item_text'], '709967', '2026-11-16T01:09:07.734Z'),
    'fort-spot-luck-20261115': (5, ['exact_item_text'], '718411', '2026-11-16T01:09:37.578Z'),
    'fort-spot-skill-20261115': (6, ['exact_spot_row'], '701579', '2026-11-16T01:09:56.532Z'),
    'fort-spot-spot-20261115': (7, ['exact_excerpts', 1], '674283', '2026-11-16T01:11:01.629Z'),
    'fort-spot-luck-type-20261115': (8, ['exact_excerpts', 0], '606272', '2026-11-16T01:11:11.360Z'),
    'fort-spot-morale-20261115': (9, ['exact_excerpts', 0], '256257', '2026-11-16T01:11:29.079Z'),
    'fort-spot-tip179-20261115': (11, ['exact_excerpts', 0], '514316', '2026-11-16T01:12:43.234Z'),
    'fort-spot-pendant-host-20261115': (14, ['exact_excerpts', 2], '707320', '2026-11-16T01:14:26.094Z'),
    'fort-spot-pendant-level-20261115': (14, ['exact_excerpts', 1], '707320', '2026-11-16T01:14:26.094Z'),
    'fort-spot-artifact-host-20261115': (15, ['exact_excerpts', 2], '700306', '2026-11-16T01:15:14.309Z'),
    'fort-spot-artifact-level-20261115': (15, ['exact_excerpts', 1], '700306', '2026-11-16T01:15:14.309Z'),
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def component(data, cid):
    matches = [row for row in data['components'] if row['id'] == cid]
    assert len(matches) == 1, cid
    return matches[0]


def rule(data, rid=RULE):
    matches = [row for row in data['rules'] if row['id'] == rid]
    assert len(matches) == 1, rid
    return matches[0]


def core(row):
    return {key: value for key, value in row.items() if key != 'note'}


def result_for(engine, data, case):
    return engine.subtotal(data, case['stat'], channel=case['channel'],
                           level=case['level'], active=case['active'])


class HistoricalPointEightFortSpotTests(unittest.TestCase):
    def setUp(self):
        self.assertIs(audit, selected_history.checkpoint_module(chains_type, 'stacking_audit'))
        self.data = audit.load()

    def assert_invalid(self, data):
        with self.assertRaises((AssertionError, KeyError, TypeError, ValueError, IndexError)):
            audit.validate(data)

    def assert_incomplete(self, data, stats=FAMILIES):
        # The active flags cannot elevate an unknown or malformed definition.
        for stat in stats:
            for active in ((), ('force', 'equipped', 'enabled')):
                result = audit.subtotal(data, stat, active=active)
                self.assertIsNone(result['total'], (stat, result))
                self.assertFalse(result['complete'], (stat, result))

    def assert_pair_rejected(self, data, left=None, right=None, stat='Spot'):
        left = component(data, 'heroism-spot') if left is None else left
        right = component(data, 'luck-spot') if right is None else right
        self.assertIsNone(audit.proof(data, stat, left, right))
        self.assertIsNone(audit.proof(data, stat, right, left))

    @contextmanager
    def isolated_sources(self):
        """Real copied bytes, with real public routes redirected to that root."""
        with tempfile.TemporaryDirectory(prefix='fort-spot-functional-') as directory:
            root = Path(directory)
            paths = {MANIFEST} | {source['path'] for source in self.data['sources'].values()}
            for relative in paths:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            with patch.object(audit, 'ROOT', root):
                self.assertTrue(audit.validate(self.data, root=root))
                self.assertEqual(audit.subtotal(self.data, 'Spot'), EXPECTED_RESULTS['Spot'])
                self.assertEqual(audit.proof(self.data, 'Spot', component(self.data, 'heroism-spot'),
                                            component(self.data, 'luck-spot')), RULE)
                yield root

    def test_exact_point_eight_engine_packet_and_fixed_selected_definitions(self):
        self.assertEqual(Path(audit.__file__).resolve(), ROOT / 'tools/stacking_audit.py')
        self.assertTrue(audit.validate(self.data))
        self.assertEqual(digest((ROOT / PACKET).read_bytes()), PACKET_SHA)
        self.assertEqual(digest((ROOT / MANIFEST).read_bytes()), MANIFEST_SHA)
        self.assertEqual(set(definitions.DEFINITION_IDS), QUALIFIED)
        self.assertEqual(set(definitions.FAMILY_IDS), FAMILY_IDS)
        self.assertEqual(definitions.FAMILIES, FAMILIES)
        self.assertEqual(set(definitions.SOURCE_SHA256), set(SOURCE_BINDINGS))
        self.assertEqual(rule(self.data), EXPECTED_RULE)
        for cid, expected in {
            'queen-fortification': ('Fortification', 84, 'Insight', 'Cloak'),
            'heroism-spot': ('Spot', 4, 'Morale', 'Legendary Glabrezu Claw Pendant / Green'),
            'luck-spot': ('Spot', 3, 'Luck', 'Yeenoghu’s Reign / Blue'),
        }.items():
            row = component(self.data, cid)
            with self.subTest(component=cid):
                self.assertEqual(tuple(row[key] for key in ('stat', 'amount', 'bonus_type', 'host')), expected)
                self.assertEqual((row['state'], row['channel'], row['kit_min_level'], row['requires']),
                                 ('verified', 'gear', 36, []))
                self.assertTrue(definitions.validate_component(self.data, row, ROOT))
                self.assertTrue(all(row[key] == '' for key in ('source', 'value_pattern', 'type_evidence')))

    def test_source_bindings_keep_original_revision_observation_and_fragment_roles(self):
        packet = json.loads((ROOT / PACKET).read_text())
        self.assertEqual(len(packet['observations']), 16)
        self.assertFalse(packet['method']['formal_ledger_promotion'])
        self.assertFalse(packet['method']['live_game_test'])
        self.assertIn('not a complete raw DOM/HTTP archive', packet['method']['retention'])
        self.assertIn('not independently reopened', packet['method']['revision'])
        for sid, (index, suffix, oldid, observed) in SOURCE_BINDINGS.items():
            source = self.data['sources'][sid]
            record = packet['observations'][index]
            with self.subTest(source=sid):
                self.assertEqual((source['path'], source['sha256']), (PACKET, PACKET_SHA))
                self.assertEqual(source['record_pointer'], ['observations', index])
                self.assertEqual(source['pointer'], ['observations', index] + suffix)
                self.assertEqual(source['quote'], audit.resolve(record, suffix))
                self.assertEqual(source['url'], record['url'])
                self.assertEqual(source['revision'], record['revision_link'])
                self.assertTrue(source['revision'].endswith('oldid=' + oldid))
                self.assertEqual(source['observed_pointer'], ['observed_utc'])
                self.assertEqual(source['observed'], observed)
                self.assertEqual(record['observed_utc'], observed)
                self.assertFalse(record['revision_endpoint_independently_reopened'])
                self.assertTrue(audit.source_provenance(source))
        self.assertIn('2022', packet['observations'][11]['page_modified_display'])
        self.assertIn('same family', packet['observations'][12]['exact_excerpts'][0])
        self.assertIsNone(packet['observations'][6]['cache_notice'])
        self.assertIn('not proof no page or evidence exists', packet['bounded_search']['limit'])

    def test_supported_inputs_and_pair_do_not_become_complete_84_or_7_totals(self):
        for active in ((), ('force',), ('force', 'equipped', 'enabled')):
            for stat, expected in EXPECTED_RESULTS.items():
                with self.subTest(stat=stat, active=active):
                    self.assertEqual(audit.subtotal(self.data, stat, active=active), expected)
        self.assertEqual(sum(component(self.data, cid)['amount'] for cid in EXPECTED_RESULTS['Spot']['counted']), 7)
        self.assertEqual(audit.subtotal(self.data, 'Intelligence')['total'], 37)
        self.assertEqual(len(audit.subtotal(self.data, 'Intelligence')['proofs']), 23)

    def test_full_level_floor_applies_to_all_five_inputs_in_both_active_cases(self):
        for stat, ids in FAMILIES.items():
            for active in ((), ('force',)):
                result = audit.subtotal(self.data, stat, level=35, active=active)
                with self.subTest(stat=stat, active=active):
                    self.assertEqual(result['counted'], [])
                    self.assertEqual(result['excluded'], list(ids))
                    self.assertEqual(result['proofs'], [])
                    self.assertFalse(result['complete'])
                    self.assertIsNone(result['total'])

    def test_only_exact_named_pair_is_available_in_either_orientation(self):
        heroism, luck = (component(self.data, cid) for cid in ('heroism-spot', 'luck-spot'))
        self.assertEqual(audit.proof(self.data, 'Spot', heroism, luck), RULE)
        self.assertEqual(audit.proof(self.data, 'Spot', luck, heroism), RULE)
        self.assert_pair_rejected(self.data, heroism, heroism)
        for stat in ('Listen', 'Wisdom', 'Fortification', 'Intelligence'):
            self.assert_pair_rejected(self.data, heroism, luck, stat)
        self.assert_pair_rejected(self.data, component(self.data, 'chains-spot'), heroism)
        self.assert_pair_rejected(self.data, component(self.data, 'chains-spot'), luck)
        self.assert_pair_rejected(self.data, component(self.data, 'chains-fortification'),
                                  component(self.data, 'queen-fortification'), 'Fortification')

    def test_detached_pair_arguments_cannot_borrow_selected_names_or_types(self):
        heroism, luck = (component(self.data, cid) for cid in ('heroism-spot', 'luck-spot'))
        for key, value in [('id', 'another-morale-item'), ('stat', 'Listen'), ('channel', 'build'),
                           ('amount', 40), ('bonus_type', 'Luck'), ('host', 'Other host'),
                           ('kit_min_level', 28), ('requires', ['force']), ('state', 'conditional')]:
            with self.subTest(field=key):
                self.assert_pair_rejected(self.data, dict(heroism, **{key: value}), luck)
        self.assert_pair_rejected(self.data, dict(heroism, id='unselected-morale'),
                                  dict(luck, id='unselected-luck'))

    def test_missing_duplicate_renamed_extra_and_moved_family_members_fail_closed(self):
        for stat, ids in FAMILIES.items():
            for cid in ids:
                for operation in ('remove', 'duplicate', 'rename', 'move-stat', 'move-channel'):
                    changed = copy.deepcopy(self.data)
                    row = component(changed, cid)
                    original = copy.deepcopy(row)
                    if operation == 'remove':
                        changed['components'].remove(row)
                    elif operation == 'duplicate':
                        changed['components'].append(copy.deepcopy(row))
                    elif operation == 'rename':
                        row['id'] = 'substitute-' + cid
                    elif operation == 'move-stat':
                        row['stat'] = 'Listen'
                    else:
                        row['channel'] = 'build'
                    with self.subTest(stat=stat, member=cid, operation=operation):
                        self.assertFalse(definitions.family_valid(changed, stat, root=ROOT))
                        self.assert_invalid(changed)
                        self.assert_incomplete(changed, [stat])
                        if stat == 'Spot':
                            left = original if cid == 'heroism-spot' else component(changed, 'heroism-spot')
                            right = original if cid == 'luck-spot' else component(changed, 'luck-spot')
                            self.assert_pair_rejected(changed, left, right)
            changed = copy.deepcopy(self.data)
            changed['components'].append(dict(component(changed, ids[0]), id='extra-family-member'))
            self.assert_invalid(changed)
            self.assert_incomplete(changed, [stat])

    def test_all_five_selected_cores_reject_amount_type_host_state_and_level_changes(self):
        edits = [('amount', 999), ('bonus_type', 'Untyped'), ('host', 'Unselected host'),
                 ('kit_min_level', 35), ('requires', ['force']), ('state', 'conditional')]
        for stat, ids in FAMILIES.items():
            for cid in ids:
                for field, value in edits:
                    changed = copy.deepcopy(self.data)
                    component(changed, cid)[field] = value
                    with self.subTest(component=cid, field=field):
                        self.assert_invalid(changed)
                        self.assert_incomplete(changed, [stat])
                        self.assertFalse(definitions.family_valid(changed, stat, root=ROOT))

    def test_chains_cannot_be_promoted_by_state_flag_direct_source_or_recipe_proof(self):
        for cid in ('chains-fortification', 'chains-spot'):
            for operation in ('state', 'direct-source', 'recipe-proof', 'definition-proof'):
                changed = copy.deepcopy(self.data)
                row = component(changed, cid)
                row['state'] = 'verified'
                if operation == 'direct-source':
                    row.update(source='fort-spot-heroism-20261115', value_pattern=r'(?P<value>4)',
                               type_evidence='Morale Bonus')
                elif operation == 'recipe-proof':
                    row['recipe_proof'] = copy.deepcopy(component(changed, 'chains-quality-int')['recipe_proof'])
                elif operation == 'definition-proof':
                    row['definition_proof'] = copy.deepcopy(component(changed, 'heroism-spot')['definition_proof'])
                with self.subTest(component=cid, operation=operation):
                    self.assert_invalid(changed)
                    self.assert_incomplete(changed, [row['stat']])

    def test_definition_proof_removal_hybrid_and_swapped_roles_do_not_fall_back(self):
        for cid in sorted(QUALIFIED):
            original = component(self.data, cid)
            operations = ['remove', 'empty', 'contract', 'method', 'hybrid', 'missing-role', 'wrong-role']
            for operation in operations:
                changed = copy.deepcopy(self.data)
                row = component(changed, cid)
                if operation == 'remove':
                    row.pop('definition_proof')
                elif operation == 'empty':
                    row['definition_proof'] = {}
                elif operation in ('contract', 'method'):
                    row['definition_proof'][operation] = 'unreviewed'
                elif operation == 'hybrid':
                    row.update(source=original['definition_proof']['sources']['item'],
                               value_pattern=r'(?P<value>84)', type_evidence='Insight')
                elif operation == 'missing-role':
                    del row['definition_proof']['sources']['item']
                else:
                    row['definition_proof']['sources']['item'] = 'fort-spot-tip179-20261115'
                with self.subTest(component=cid, operation=operation):
                    self.assertFalse(definitions.validate_component(changed, row, ROOT))
                    self.assertFalse(audit.component_provenance(changed, row))
                    self.assert_invalid(changed)
                    self.assert_incomplete(changed, [original['stat']])

    def test_new_pinned_sources_cannot_be_borrowed_by_unreviewed_direct_components(self):
        # A valid new observation is not a general source gate for arbitrary rows.
        # This explicitly exercises subtotal without first calling validate().
        for aliased in (False, True):
            for channel in ('gear', 'build'):
                changed = copy.deepcopy(self.data)
                sid = 'fort-spot-heroism-20261115'
                if aliased:
                    changed['sources']['renamed-source'] = copy.deepcopy(changed['sources'][sid])
                    sid = 'renamed-source'
                row = copy.deepcopy(component(changed, 'heroism-spot'))
                row.update(id='outside-bounded-definition', stat='Unreviewed skill', channel=channel,
                           source=sid, value_pattern=r'(?P<value>4)', type_evidence='Morale Bonus')
                row.pop('definition_proof')
                changed['components'].append(row)
                with self.subTest(alias=aliased, channel=channel):
                    self.assertFalse(audit.component_provenance(changed, row))
                    result = audit.subtotal(changed, row['stat'], channel=channel)
                    self.assertNotIn(row['id'], result['counted'])
                    self.assertFalse(result['complete'])
                    self.assertIsNone(result['total'])
                    self.assert_invalid(changed)

    def test_observed_utc_is_not_a_generic_legacy_observation_pointer(self):
        self.assertNotIn(('observed_utc',), audit.OBSERVATION_POINTERS)
        for sid in ('heroism', 'good-luck', 'fortification-rule'):
            old = self.data['sources'][sid]
            self.assertFalse(audit.source_provenance(old))
            changed = dict(old, observed='2026-11-16T01:09:07.734Z',
                           observed_pointer=['observed_utc'],
                           revision='https://ddowiki.com/index.php?title=Skill&oldid=701579',
                           revision_pointer=['revision_link'])
            self.assertFalse(audit.observation_context(changed))
            self.assertFalse(audit.source_provenance(changed))
        self.assertNotIn('Spot', audit.STAT_WORDS)
        self.assertNotIn('Fortification', audit.STAT_WORDS)

    def test_bounded_source_cannot_enable_an_unreviewed_effect_or_generic_pair(self):
        for aliased in (False, True):
            changed = copy.deepcopy(self.data)
            sid = 'fort-spot-heroism-20261115'
            if aliased:
                changed['sources']['another-source-name'] = copy.deepcopy(changed['sources'][sid])
                sid = 'another-source-name'
            effect = next(row for row in changed['non_total_effects'] if row['id'] == 'heroism-other-skills')
            effect.update(state='verified', sources=[sid])
            with self.subTest(alias=aliased):
                self.assert_invalid(changed)
                borrowed = copy.deepcopy(component(self.data, 'heroism-spot'))
                borrowed.pop('definition_proof')
                borrowed.update(id='borrowed-source-prr', stat='PRR', source=sid)
                # PRR has an existing affirmative general combination rule; it
                # must not legitimize an unreviewed use of this bounded source.
                partner = next(row for row in changed['components']
                               if row['stat'] == 'PRR' and row['bonus_type'] != borrowed['bonus_type'])
                self.assertIsNone(audit.proof(changed, 'PRR', borrowed, partner))
                self.assertIsNone(audit.proof(changed, 'PRR', partner, borrowed))

    def test_new_source_metadata_changes_cannot_requalify_the_named_pair(self):
        sid = 'fort-spot-heroism-20261115'
        edits = [('observed', '2026-11-16T01:09:08.734Z'), ('observed', None),
                 ('observed_pointer', ['created_at']), ('revision', None),
                 ('revision_pointer', None), ('url', 'https://ddowiki.com/page/Skill'),
                 ('path', 'evidence/wisdom-loadout/sources.json'), ('sha256', '0' * 64),
                 ('record_pointer', ['observations', 5]),
                 ('pointer', ['observations', 5, 'exact_item_text']), ('quote', '+4 Morale bonus to Spot.')]
        for key, value in edits:
            changed = copy.deepcopy(self.data)
            changed['sources'][sid][key] = value
            with self.subTest(field=key, value=value):
                self.assertFalse(definitions.observation_context(changed['sources'][sid]))
                self.assert_invalid(changed)
                self.assert_incomplete(changed, ['Spot'])
                self.assert_pair_rejected(changed)

    def test_every_definition_role_and_rule_source_is_a_required_live_binding(self):
        uses = {cid: set(component(self.data, cid)['definition_proof']['sources'].values())
                for cid in QUALIFIED}
        for cid, sids in uses.items():
            for sid in sids:
                changed = copy.deepcopy(self.data)
                del changed['sources'][sid]
                with self.subTest(component=cid, source=sid):
                    self.assertFalse(definitions.validate_component(changed, component(changed, cid), ROOT))
                    self.assert_incomplete(changed, [component(changed, cid)['stat']])
                    self.assert_invalid(changed)
        for sid in ('fort-spot-tip179-20261115', 'fort-spot-luck-type-20261115', 'fort-spot-morale-20261115'):
            changed = copy.deepcopy(self.data)
            del changed['sources'][sid]
            with self.subTest(rule_source=sid):
                self.assertFalse(definitions.validate_rule_source(changed, ROOT))
                self.assert_pair_rejected(changed)
                self.assert_invalid(changed)
                self.assert_incomplete(changed, ['Spot'])

    def test_rule_widening_missing_duplicate_and_partial_profiles_fail_closed(self):
        edits = [('id', 'renamed-spot-rule'), ('kind', 'different_types'),
                 ('types', ['*']), ('types', ['Morale', 'Luck', 'Competence']),
                 ('stats', ['*']), ('stats', ['Listen']), ('channel', 'build'),
                 ('source', 'stack'), ('quote', 'Bonuses of the same type do not stack:'),
                 ('component_pairs', []),
                 ('component_pairs', [['heroism-spot', 'luck-spot'], ['chains-spot', 'heroism-spot']])]
        for key, value in edits:
            changed = copy.deepcopy(self.data)
            rule(changed)[key] = value
            with self.subTest(field=key):
                self.assert_invalid(changed)
                self.assert_incomplete(changed)
                self.assert_pair_rejected(changed)
        for operation in ('remove-new-rule', 'duplicate-new-rule', 'remove-legacy-rule',
                           'remove-int-additions', 'remove-new-sources', 'strip-all-new-markers'):
            changed = copy.deepcopy(self.data)
            if operation == 'remove-new-rule':
                changed['rules'].remove(rule(changed))
            elif operation == 'duplicate-new-rule':
                changed['rules'].append(copy.deepcopy(rule(changed)))
            elif operation == 'remove-legacy-rule':
                changed['rules'].remove(rule(changed, 'same-type-best'))
            elif operation == 'remove-int-additions':
                changed['rules'] = [r for r in changed['rules'] if r['id'] not in INT_RULES - LEGACY_RULES]
            else:
                changed['sources'] = {sid: s for sid, s in changed['sources'].items() if sid not in SOURCE_BINDINGS}
                if operation == 'strip-all-new-markers':
                    changed['rules'].remove(rule(changed))
                    for cid in QUALIFIED:
                        component(changed, cid).pop('definition_proof')
            with self.subTest(operation=operation):
                self.assertTrue(definitions.uses_contract(changed))
                self.assert_invalid(changed)
                self.assert_incomplete(changed)
                self.assert_pair_rejected(changed)

    def test_actual_packet_bytes_and_rehashed_caller_metadata_fail_independent_pin(self):
        with self.isolated_sources() as root:
            path = root / PACKET
            path.write_bytes(path.read_bytes() + b' ')
            for forge_hash in (False, True):
                changed = copy.deepcopy(self.data)
                if forge_hash:
                    for source in changed['sources'].values():
                        if source['path'] == PACKET:
                            source['sha256'] = digest(path.read_bytes())
                with self.subTest(caller_rehashed=forge_hash):
                    with self.assertRaises((AssertionError, KeyError, TypeError, ValueError)):
                        audit.validate(changed, root=root)
                    self.assert_incomplete(changed)
                    self.assert_pair_rejected(changed)
                    for cid in QUALIFIED:
                        self.assertFalse(definitions.validate_component(changed, component(changed, cid), root))

    def test_actual_selected_manifest_bytes_are_rechecked_after_prior_success(self):
        with self.isolated_sources() as root:
            path = root / MANIFEST
            selected = json.loads(path.read_text())
            selected['selection']['full_kit_ml'] = 35
            path.write_text(json.dumps(selected))
            self.assert_incomplete(self.data)
            self.assert_pair_rejected(self.data)
            for cid in QUALIFIED:
                self.assertFalse(definitions.validate_component(self.data, component(self.data, cid), root))
            with self.assertRaises((AssertionError, KeyError, TypeError, ValueError)):
                audit.validate(self.data, root=root)

    def test_semantic_popup_mutants_fail_even_when_byte_gate_is_bypassed_for_this_control(self):
        packet = json.loads((ROOT / PACKET).read_text())
        original = packet['observations'][0]
        definitions._queen(original)
        edits = [('/page/Fortification', '/page/Armor-Piercing'),
                 ('Insightful Fortification  +84%', 'Insightful Fortification  +85%'),
                 ('/page/Insight_bonus', '/page/Quality_bonus'),
                 ('+84% <a href="/page/Insight_bonus"', '+83% <a href="/page/Insight_bonus"'),
                 ('popup has_tooltip with-icon basic', 'popup unrelated with-icon basic'),
                 ('popup tooltip wide left below', 'popup unrelated wide left below')]
        for old, new in edits:
            changed = copy.deepcopy(original)
            self.assertIn(old, changed['exact_dom_markup'])
            changed['exact_dom_markup'] = changed['exact_dom_markup'].replace(old, new)
            with self.subTest(old=old), self.assertRaises(AssertionError):
                definitions._queen(changed)
        # Equal text in two sibling fields is not the same-item popup association.
        changed = dict(original, exact_dom_markup='<div>' + original['exact_dom_markup'] + '</div>')
        with self.assertRaises(AssertionError):
            definitions._queen(changed)

    def test_semantic_membership_and_host_mutants_fail_without_relying_on_packet_hash(self):
        # Bypass only the low-level byte/metadata read in this deliberate control;
        # real validate_component still checks the selected row and interpretation.
        actual_source = definitions._source_record
        edits = [
            ('fort-spot-heroism-20261115', 'exact_item_text', '+4 Morale Bonus', '+4 Luck Bonus'),
            ('fort-spot-heroism-20261115', 'exact_item_text', 'Skill Checks', 'Saving Throws'),
            ('fort-spot-heroism-20261115', 'exact_item_text', 'Minimum Level\t28\t', 'Minimum Level\t30\t'),
            ('fort-spot-heroism-20261115', 'exact_item_text', 'Blue, Green, or Purple', 'Blue or Purple'),
            ('fort-spot-skill-20261115', 'exact_spot_row', '\tSpot\t', '\tListen\t'),
            ('fort-spot-spot-20261115', ('exact_excerpts', 1), 'The Spot skill', 'The Listen skill'),
            ('fort-spot-spot-20261115', ('exact_excerpts', 2), 'Spot check', 'Listen check'),
            ('fort-spot-pendant-host-20261115', ('exact_excerpts', 2), 'Green', 'Yellow'),
            ('fort-spot-pendant-level-20261115', ('exact_excerpts', 1), '35', '34'),
        ]
        for sid, field, old, new in edits:
            def altered(data, requested, root, sid=sid, field=field, old=old, new=new):
                record = copy.deepcopy(actual_source(data, requested, root))
                if requested == sid:
                    if isinstance(field, tuple):
                        key, index = field
                        self.assertIn(old, record[key][index])
                        record[key][index] = record[key][index].replace(old, new)
                    else:
                        self.assertIn(old, record[field])
                        record[field] = record[field].replace(old, new)
                return record
            with self.subTest(source=sid, field=field), patch.object(definitions, '_source_record', altered):
                self.assertFalse(definitions.validate_component(self.data, component(self.data, 'heroism-spot'), ROOT))

    def test_semantic_rule_control_requires_positive_statement_and_overlap_limits(self):
        actual_source = definitions._source_record
        for sid, old in [('fort-spot-tip179-20261115', 'Different types of bonuses stack'),
                         ('fort-spot-luck-type-20261115', 'Only the highest luck bonus applies.'),
                         ('fort-spot-morale-20261115', 'Only the highest morale bonus applies.')]:
            def altered(data, requested, root, sid=sid, old=old):
                record = copy.deepcopy(actual_source(data, requested, root))
                if requested == sid:
                    self.assertIn(old, record['exact_excerpts'][0])
                    record['exact_excerpts'][0] = record['exact_excerpts'][0].replace(old, '[REMOVED]')
                return record
            with self.subTest(source=sid), patch.object(definitions, '_source_record', altered):
                self.assertFalse(definitions.validate_rule_source(self.data, ROOT))
                self.assert_pair_rejected(self.data)


class FortSpotBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = preservation.checkpoint_file_bytes(LEDGER)
        assert digest(raw) == OLD_LEDGER_SHA
        cls.previous = json.loads(raw)
        raw = (ROOT / RESULTS).read_bytes()
        assert digest(raw) == RESULTS_SHA
        cls.results = json.loads(raw)

    def setUp(self):
        self.assertIs(audit, selected_history.checkpoint_module(chains_type, 'stacking_audit'))
        self.data = audit.load()

    def test_exact_seven_nine_and_ten_rule_profiles_remain_distinct(self):
        seven = copy.deepcopy(self.previous)
        seven['rules'] = [r for r in seven['rules'] if r['id'] in LEGACY_RULES]
        for sid in ('tip179-live-20261115', 'fort-rule-live-20261115'):
            del seven['sources'][sid]
            del seven['source_roles'][sid]
        for data, expected in ((seven, LEGACY_RULES), (self.previous, INT_RULES),
                               (self.data, INT_RULES | {RULE})):
            with self.subTest(profile_size=len(expected)):
                self.assertEqual(audit.rule_profile(data), frozenset(expected))
                self.assertTrue(audit.validate(data))
        old_engine = selected_history.checkpoint_module(preservation, 'stacking_audit')
        for case in self.results['ledger_cases']:
            with self.subTest(seven_rule_case=(case['level'], case['stat'], case['active'])):
                self.assertEqual(result_for(audit, seven, case), result_for(old_engine, seven, case))

    def test_all_152_old_input_result_objects_survive_through_exact_point_eight_engine(self):
        self.assertEqual(self.results['baseline_commit'], '72db151c4f881c08844d273caee2914ddc736641')
        self.assertEqual(self.results['baseline_tree'], '573c0b26ac30dce65a3d4fcf6107a38dc5c8058d')
        self.assertEqual(len(self.results['ledger_cases']), 152)
        self.assertTrue(audit.validate(self.previous))
        for case in self.results['ledger_cases']:
            with self.subTest(level=case['level'], stat=case['stat'], active=case['active']):
                self.assertEqual(result_for(audit, self.previous, case), case['result'])

    def test_point_eight_changes_exactly_four_complete_objects_without_new_total(self):
        changed = []
        for case in self.results['ledger_cases']:
            actual = result_for(audit, self.data, case)
            if actual != case['result']:
                changed.append((case['level'], case['stat'], tuple(case['active'])))
                self.assertEqual(case['level'], 36)
                self.assertIn(case['stat'], EXPECTED_RESULTS)
                self.assertEqual(actual, EXPECTED_RESULTS[case['stat']])
            else:
                self.assertEqual(actual, case['result'])
        self.assertEqual(set(changed), {(36, stat, active) for stat in FAMILIES for active in ((), ('force',))})
        self.assertEqual(len(changed), 4)

    def test_prior_sources_rules_selection_and_unrelated_definitions_stay_literal(self):
        self.assertEqual(set(self.data['sources']), set(self.previous['sources']) | set(SOURCE_BINDINGS))
        for sid, original in self.previous['sources'].items():
            with self.subTest(source=sid):
                self.assertEqual(self.data['sources'][sid], original)
                self.assertEqual(self.data['source_roles'][sid], self.previous['source_roles'][sid])
        self.assertEqual(self.data['rules'], self.previous['rules'] + [EXPECTED_RULE])
        self.assertEqual([c['id'] for c in self.data['components']], [c['id'] for c in self.previous['components']])
        for before, after in zip(self.previous['components'], self.data['components']):
            if before['id'] not in QUALIFIED:
                self.assertEqual(core(after), core(before), before['id'])
        for cid in ('chains-fortification', 'chains-spot'):
            self.assertEqual(component(self.data, cid), component(self.previous, cid))
        self.assertEqual(digest((ROOT / MANIFEST).read_bytes()), MANIFEST_SHA)
        self.assertEqual(digest(chains_type.checkpoint_file_bytes('tools/recipe_proofs.py')),
                         'b4c2b4fd95a0a9de4b5f8155245ba8934a8f1ae89c3e2f1d7e8eac545bb627ec')


if __name__ == '__main__':
    unittest.main()
