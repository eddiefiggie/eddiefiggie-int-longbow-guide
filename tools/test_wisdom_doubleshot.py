"""Actual-current, bounded selected-gear Doubleshot acceptance and rejection tests.

Expected results and prior inputs are independent of the new helper's constants.
Temporary source mutations exercise real file reads; semantic mutations follow
an authenticated read and separately check the interpretation of its clauses.
"""
from contextlib import contextmanager
from copy import deepcopy
from hashlib import sha256
import itertools
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import stacking_audit as audit
import wisdom_doubleshot_proofs as definitions
import wisdom_doubleshot_preservation as preservation


ROOT = Path(__file__).resolve().parents[1]
LEDGER = 'tools/fixtures/endgame-stacking/ledger.json'
MANIFEST = 'tools/fixtures/wisdom-loadout/selection.json'
LOADOUT = 'evidence/wisdom-loadout/loadout.json'
PACKET = 'evidence/wisdom-loadout/doubleshot-sources-2026-11-16.json'
PACKET_SHA = '49798b85597ad45f027d52754388336325cde0441484bbee5de90c0bf4d59ed5'
BASELINE_RESULTS = 'tools/fixtures/wisdom-doubleshot/baseline-results.json'
BASELINE_SHA = '153b654bfa877a1a8e9578ae044f788d481a27c991a3c239b6181a767cb94dd2'
CONTRACT = 'selected-gear-doubleshot-v1'
RULE_ID = 'doubleshot-selected-six-pairs'
FAMILY = ('goggles-ds', 'ring-ds', 'boots-ds', 'armor-ds', 'quickblade-ds')
NATIVE_PAIRS = (
    ('goggles-ds', 'ring-ds'), ('goggles-ds', 'boots-ds'),
    ('goggles-ds', 'armor-ds'), ('ring-ds', 'boots-ds'),
    ('ring-ds', 'armor-ds'), ('boots-ds', 'armor-ds'),
)
NEW_SOURCES = {
    'ds-augment-system-20261116', 'ds-quickblade-20261116',
    'ds-set-table-20261116', 'ds-set-rules-20261116',
    'ds-goggles-host-20261116', 'ds-chains-host-20261116',
    'ds-yeenoghu-host-20261116', 'ds-green-recipe-20261116',
}
EXPECTED_RULE = {
    'id': RULE_ID, 'source': 'tip179-live-20261115',
    'quote': 'Different types of bonuses stack', 'kind': 'selected_pairs',
    'types': ['Enhancement', 'Quality', 'Insight', 'Profane'],
    'stats': ['Doubleshot'], 'channel': 'gear',
    'component_pairs': [list(pair) for pair in NATIVE_PAIRS],
}
EXPECTED_RESULT = {
    'stat': 'Doubleshot', 'channel': 'gear', 'total': 35,
    'counted': list(FAMILY), 'suppressed': [], 'excluded': [],
    'missing_interactions': [],
    'proofs': [
        ['goggles-ds', 'ring-ds', RULE_ID],
        ['goggles-ds', 'boots-ds', RULE_ID],
        ['goggles-ds', 'armor-ds', RULE_ID],
        ['goggles-ds', 'quickblade-ds', 'artifact-other-types'],
        ['ring-ds', 'boots-ds', RULE_ID],
        ['ring-ds', 'armor-ds', RULE_ID],
        ['ring-ds', 'quickblade-ds', 'artifact-other-types'],
        ['boots-ds', 'armor-ds', RULE_ID],
        ['boots-ds', 'quickblade-ds', 'artifact-other-types'],
        ['armor-ds', 'quickblade-ds', 'artifact-other-types'],
    ],
    'complete': True,
}


def component(data, cid):
    found = [row for row in data['components'] if row['id'] == cid]
    assert len(found) == 1, cid
    return found[0]


def set_path(record, path, value):
    for part in path[:-1]:
        record = record[part]
    record[path[-1]] = value


class CurrentDoubleshotTests(unittest.TestCase):
    def setUp(self):
        self.data = audit.load()

    def assert_family_rejected(self, data):
        self.assertFalse(definitions.family_valid(data, root=ROOT))
        result = audit.subtotal(data, 'Doubleshot', active=('force', 'all', 'quickblade'))
        self.assertEqual((result['total'], result['complete'], result['counted']),
                         (None, False, []))
        for partner in ('ring-ds', 'quickblade-ds'):
            self.assertIsNone(audit.proof(data, 'Doubleshot',
                component(self.data, 'goggles-ds'), component(self.data, partner)))

    def assert_edges_withheld(self, data, missing_kind):
        result = audit.subtotal(data, 'Doubleshot')
        self.assertEqual(result['counted'], list(FAMILY))
        self.assertEqual(result['excluded'], [])
        self.assertEqual((result['total'], result['complete']), (None, False))
        expected = [row for row in EXPECTED_RESULT['proofs'] if row[2] != missing_kind]
        gaps = [row[:2] for row in EXPECTED_RESULT['proofs'] if row[2] == missing_kind]
        self.assertEqual(result['proofs'], expected)
        self.assertEqual(result['missing_interactions'], gaps)
        for a, b in gaps:
            self.assertIsNone(audit.proof(data, 'Doubleshot', component(data, a), component(data, b)))

    @contextmanager
    def isolated_sources(self):
        with tempfile.TemporaryDirectory(prefix='doubleshot-functional-') as directory:
            root = Path(directory)
            paths = {MANIFEST, LOADOUT, PACKET} | {s['path'] for s in self.data['sources'].values()}
            for path in paths:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, target)
            with patch.object(audit, 'ROOT', root):
                self.assertEqual(audit.subtotal(self.data, 'Doubleshot'), EXPECTED_RESULT)
                yield root

    def test_actual_current_module_and_exact_definition_inventory(self):
        self.assertIs(audit, sys.modules['stacking_audit'])
        self.assertEqual(Path(audit.__file__).resolve(), ROOT / 'tools/stacking_audit.py')
        self.assertTrue(audit.validate(self.data))
        self.assertEqual(definitions.CONTRACT, CONTRACT)
        self.assertEqual(set(definitions.COMPONENT_IDS), {'quickblade-ds'})
        self.assertEqual(definitions.FAMILY_IDS, FAMILY)
        self.assertEqual(set(definitions.NEW_SOURCES), NEW_SOURCES)
        self.assertEqual(sha256((ROOT / PACKET).read_bytes()).hexdigest(), PACKET_SHA)
        self.assertEqual(sha256((ROOT / MANIFEST).read_bytes()).hexdigest(),
                         '8223bd8e25ed9dc4ad9454439ead42dfb693cc008d18d0ddfeb270d33863c37d')
        self.assertEqual(sha256((ROOT / LOADOUT).read_bytes()).hexdigest(),
                         '20f5bca4573d803a196695aa999f4acc07e71db077e3b66fde51a560b6da0843')
        expected = [(9, 'Enhancement'), (3, 'Quality'), (5, 'Insight'), (3, 'Profane'), (15, 'Artifact')]
        for cid, values in zip(FAMILY, expected):
            row = component(self.data, cid)
            self.assertEqual((row['amount'], row['bonus_type']), values)
            self.assertEqual((row['stat'], row['channel'], row['state'], row['kit_min_level'], row['requires']),
                             ('Doubleshot', 'gear', 'verified', 36, []))
            self.assertTrue(definitions.validate_component(self.data, row, ROOT))

    def test_complete_result_and_flags_match_whole_independent_expectation(self):
        for active in ((), ('force',), ('all', 'quickblade', 'force')):
            self.assertEqual(audit.subtotal(self.data, 'Doubleshot', active=active), EXPECTED_RESULT)

    def test_level35_withholds_every_selected_component_even_with_flags(self):
        expected = dict(EXPECTED_RESULT, total=None, counted=[], excluded=list(FAMILY), proofs=[], complete=False)
        for active in ((), ('all', 'quickblade', 'force')):
            self.assertEqual(audit.subtotal(self.data, 'Doubleshot', level=35, active=active), expected)

    def test_exact_six_pairs_and_four_unchanged_artifact_edges_both_directions(self):
        rules = [rule for rule in self.data['rules'] if rule['id'] == RULE_ID]
        self.assertEqual(rules, [EXPECTED_RULE])
        self.assertEqual(len(self.data['rules']), 17)
        for left, right, rid in EXPECTED_RESULT['proofs']:
            a, b = component(self.data, left), component(self.data, right)
            with self.subTest(pair=(left, right)):
                self.assertEqual(audit.proof(self.data, 'Doubleshot', a, b), rid)
                self.assertEqual(audit.proof(self.data, 'Doubleshot', b, a), rid)

    def test_current_successor_preserves_prior_totals_and_every_skull_pair_rejection(self):
        for stat, total in {'Intelligence': 37, 'Fortification': 226, 'Spot': 27, 'Wisdom': 18}.items():
            result = audit.subtotal(self.data, stat)
            self.assertEqual(result['total'], total)
            self.assertTrue(result['complete'])
        con = audit.subtotal(self.data, 'Constitution')
        self.assertEqual((con['total'], con['complete'], con['excluded']), (None, False, ['skull-con']))
        self.assertEqual(sum(component(self.data, cid)['amount'] for cid in con['counted']), 17)
        skull = component(self.data, 'skull-con')
        for row in self.data['components']:
            if row['stat'] == 'Constitution' and row['id'] != 'skull-con':
                self.assertIsNone(audit.proof(self.data, 'Constitution', skull, row))
                self.assertIsNone(audit.proof(self.data, 'Constitution', row, skull))

    def test_all_prior_sources_rules_and_other_components_are_literal(self):
        old = json.loads(preservation.checkpoint_file_text(LEDGER))
        self.assertEqual(self.data['rules'][:-1], old['rules'])
        self.assertEqual(set(self.data['sources']) - set(old['sources']), NEW_SOURCES)
        for sid, source in old['sources'].items():
            self.assertEqual(self.data['sources'][sid], source, sid)
        self.assertEqual(len(old['components']), len(self.data['components']))
        for row in old['components']:
            now = component(self.data, row['id'])
            if row['id'] != 'quickblade-ds':
                self.assertEqual(now, row, row['id'])
            else:
                self.assertEqual(row['state'], 'unknown')
                unchanged = set(row) - {'state', 'note'}
                self.assertEqual({k: now[k] for k in unchanged}, {k: row[k] for k in unchanged})
                self.assertEqual(set(now) - set(row), {'definition_proof'})
        for key in old.keys() - {'sources', 'rules', 'components', 'source_roles'}:
            self.assertEqual(self.data[key], old[key], key)
        for sid, role in old['source_roles'].items():
            if sid != 'tip179-live-20261115':
                self.assertEqual(self.data['source_roles'][sid], role, sid)

    def test_only_two_of_152_complete_current_result_objects_change(self):
        raw = (ROOT / BASELINE_RESULTS).read_bytes()
        self.assertEqual(sha256(raw).hexdigest(), BASELINE_SHA)
        baseline = json.loads(raw)
        self.assertEqual(len(baseline['ledger_cases']), 152)
        changed = []
        for case in baseline['ledger_cases']:
            actual = audit.subtotal(self.data, case['stat'], channel=case['channel'],
                                    active=case['active'], level=case['level'])
            if actual != case['result']:
                changed.append((case['level'], case['stat'], case['channel'], tuple(case['active'])))
                self.assertEqual(actual, EXPECTED_RESULT)
        self.assertEqual(changed, [(36, 'Doubleshot', 'gear', ()), (36, 'Doubleshot', 'gear', ('force',))])

    def test_missing_duplicate_renamed_moved_substituted_and_extra_members_fail_closed(self):
        for cid in FAMILY:
            for operation in ('missing', 'duplicate', 'rename', 'other-stat', 'other-channel'):
                data = deepcopy(self.data)
                row = component(data, cid)
                if operation == 'missing':
                    data['components'].remove(row)
                elif operation == 'duplicate':
                    data['components'].append(deepcopy(row))
                elif operation == 'rename':
                    row['id'] = 'replacement-' + cid
                elif operation == 'other-stat':
                    row['stat'] = 'Doublestrike'
                else:
                    row['channel'] = 'build'
                with self.subTest(cid=cid, operation=operation):
                    self.assert_family_rejected(data)
        data = deepcopy(self.data)
        extra = deepcopy(component(data, 'quickblade-ds'))
        extra['id'] = 'extra-artifact-ds'
        data['components'].append(extra)
        self.assert_family_rejected(data)
        data = deepcopy(self.data)
        replacement = deepcopy(component(data, 'solar-con'))
        replacement.update(id='quickblade-ds', stat='Doubleshot')
        data['components'][data['components'].index(component(data, 'quickblade-ds'))] = replacement
        self.assert_family_rejected(data)

    def test_component_core_changes_cannot_be_activated_by_caller_flags(self):
        changes = {'amount': 45, 'bonus_type': 'Untyped', 'host': 'unselected host',
                   'kit_min_level': 1, 'state': 'conditional', 'requires': ['force']}
        for cid in FAMILY:
            for field, value in changes.items():
                data = deepcopy(self.data)
                component(data, cid)[field] = value
                with self.subTest(cid=cid, field=field):
                    self.assert_family_rejected(data)
        data = deepcopy(self.data)
        component(data, 'quickblade-ds')['state'] = 'unknown'
        self.assert_family_rejected(data)

    def test_direct_proof_rejects_detached_self_wrong_stat_channel_and_missing_keys(self):
        a, b = component(self.data, 'goggles-ds'), component(self.data, 'quickblade-ds')
        self.assertIsNone(audit.proof(self.data, 'Doubleshot', a, a))
        self.assertIsNone(audit.proof(self.data, 'Dexterity', a, b))
        for key, value in (('amount', 999), ('host', 'wrong'), ('channel', 'build'),
                           ('stat', 'Dexterity'), ('id', 'unknown-ds')):
            wrong = deepcopy(a)
            wrong[key] = value
            self.assertIsNone(audit.proof(self.data, 'Doubleshot', wrong, b))
        for key in ('channel', 'id', 'stat', 'bonus_type', 'amount', 'source'):
            wrong = deepcopy(a)
            del wrong[key]
            self.assertIsNone(audit.proof(self.data, 'Doubleshot', wrong, b))
            self.assertIsNone(audit.proof(self.data, 'Doubleshot', b, wrong))
        for wrong in (None, [], False, True, 0, 5, 'invalid'):
            self.assertIsNone(audit.proof(self.data, 'Doubleshot', wrong, b))
            self.assertIsNone(audit.proof(self.data, 'Doubleshot', b, wrong))

    def test_malformed_definition_shapes_and_damaged_upgrade_cannot_escape_to_old_profile(self):
        for value in (None, [], False, True, 0, 17, 'invalid', {}, {'contract': CONTRACT}):
            for partial in (False, True):
                data = deepcopy(self.data)
                component(data, 'quickblade-ds')['definition_proof'] = value
                if partial:
                    data['rules'] = [rule for rule in data['rules'] if rule['id'] != RULE_ID]
                    for sid in NEW_SOURCES:
                        del data['sources'][sid]
                with self.subTest(value=value, partial=partial):
                    self.assertTrue(definitions.uses_contract(data))
                    self.assert_family_rejected(data)
        data = deepcopy(self.data)
        row = component(data, 'quickblade-ds')
        row['source'] = 'ds-quickblade-20261116'
        row['value_pattern'] = r'\+(?P<value>15)% Artifact'
        row['type_evidence'] = 'Artifact'
        self.assert_family_rejected(data)

    def test_old_rule_profiles_do_not_authorize_the_new_selected_family(self):
        profiles = (audit.LEGACY_RULE_IDS, audit.INT_RULE_IDS, audit.FORT_SPOT_RULE_IDS,
                    audit.CHAINS_TYPE_RULE_IDS, audit.ABILITY_RULE_IDS)
        self.assertEqual([len(ids) for ids in profiles], [7, 9, 10, 12, 16])
        for ids in profiles:
            data = deepcopy(self.data)
            data['rules'] = [rule for rule in data['rules'] if rule['id'] in ids]
            self.assertEqual(audit.rule_profile(data), ids)
            self.assertFalse(audit.current_rule_profile(data))
            result = audit.subtotal(data, 'Doubleshot')
            self.assertEqual((result['total'], result['complete'], result['counted']), (None, False, []))
            self.assertIsNone(audit.proof(data, 'Doubleshot', component(data, 'goggles-ds'),
                                         component(data, 'quickblade-ds')))

    def test_new_rule_cannot_expand_to_wildcards_unlisted_pairs_or_partial_profiles(self):
        mutations = {'types': ['*'], 'stats': ['*'], 'channel': 'build', 'kind': 'different_types',
                     'source': 'artifact', 'quote': 'Different types always stack',
                     'component_pairs': [['goggles-ds', 'quickblade-ds']]}
        for key, value in mutations.items():
            data = deepcopy(self.data)
            next(rule for rule in data['rules'] if rule['id'] == RULE_ID)[key] = value
            self.assertIsNone(audit.rule_profile(data))
            result = audit.subtotal(data, 'Doubleshot')
            self.assertEqual((result['total'], result['counted']), (None, []))
        data = deepcopy(self.data)
        data['rules'].append(deepcopy(data['rules'][-1]))
        self.assertIsNone(audit.rule_profile(data))
        self.assertIsNone(audit.proof(data, 'Doubleshot', component(data, 'goggles-ds'),
                                     component(data, 'quickblade-ds')))

    def test_exact_new_source_metadata_and_observation_whitelist(self):
        mutations = {'quote': 'different text', 'url': 'https://ddowiki.com/page/Other',
                     'revision': 'https://ddowiki.com/index.php?title=Other&oldid=1',
                     'observed': '2026-11-16T05:00:00.000Z', 'observed_pointer': ['created_at'],
                     'pointer': ['observations', 7, 'exact_doubleshot_clause'],
                     'record_pointer': ['observations', 7], 'sha256': '0' * 64,
                     'source_contract': 'unbounded'}
        for sid in sorted(NEW_SOURCES):
            self.assertTrue(definitions.validate_source(self.data, sid, ROOT))
            self.assertTrue(audit.source_provenance(self.data['sources'][sid]))
            for key, value in mutations.items():
                data = deepcopy(self.data)
                data['sources'][sid][key] = value
                with self.subTest(sid=sid, key=key):
                    self.assertFalse(definitions.validate_source(data, sid, ROOT))
            data = deepcopy(self.data)
            del data['sources'][sid]
            self.assert_family_rejected(data)
        arbitrary = {'observed_pointer': ['started_at_utc'], 'observed': '2026-11-16T05:04:12.273Z'}
        self.assertFalse(audit.observation_context(arbitrary))
        self.assertNotIn(('started_at_utc',), audit.OBSERVATION_POINTERS)
        wrong = deepcopy(self.data['sources']['ds-quickblade-20261116'])
        wrong['quote'] += ' changed'
        self.assertFalse(audit.observation_context(wrong))

    def test_new_source_aliases_cannot_define_foreign_numeric_or_non_total_effects(self):
        data = deepcopy(self.data)
        data['sources']['alias-quickblade'] = deepcopy(data['sources']['ds-quickblade-20261116'])
        foreign = deepcopy(component(data, 'quickblade-ds'))
        foreign.pop('definition_proof')
        foreign.update(id='foreign-dex', stat='Dexterity', source='alias-quickblade',
                       value_pattern=r'\+(?P<value>15)% Artifact', type_evidence='Artifact')
        data['components'].append(foreign)
        self.assertTrue(audit.bounded_source(data['sources']['alias-quickblade'], 'alias-quickblade'))
        self.assertFalse(audit.component_provenance(data, foreign))
        self.assertIn('foreign-dex', audit.subtotal(data, 'Dexterity')['excluded'])
        with self.assertRaises(AssertionError):
            audit.validate(data)
        data = deepcopy(self.data)
        data['non_total_effects'].append({'id': 'foreign-effect', 'state': 'verified',
                                        'sources': ['ds-quickblade-20261116'], 'note': 'Unsupported adoption'})
        with self.assertRaises(AssertionError):
            audit.validate(data)

    def test_lost_interaction_metadata_keeps_independent_definitions_but_withholds_edges(self):
        for sid, rid in (('tip179-live-20261115', RULE_ID), ('stack', RULE_ID),
                         ('artifact', 'artifact-other-types')):
            for change in ('missing', 'quote', 'observed'):
                data = deepcopy(self.data)
                if change == 'missing':
                    del data['sources'][sid]
                else:
                    data['sources'][sid][change] = 'not the observed premise'
                with self.subTest(source=sid, change=change):
                    self.assert_edges_withheld(data, rid)

    def test_actual_bytes_are_rechecked_without_accepting_caller_rehash(self):
        cases = [
            (PACKET, None), (MANIFEST, None), (LOADOUT, None),
            (self.data['sources']['goggles-ds']['path'], None),
            (self.data['sources']['tip179-live-20261115']['path'], RULE_ID),
            (self.data['sources']['stack']['path'], RULE_ID),
            (self.data['sources']['artifact']['path'], 'artifact-other-types'),
        ]
        with self.isolated_sources() as root:
            for path, lost_rule in cases:
                target = root / path
                original = target.read_bytes()
                try:
                    target.write_bytes(original + b'\n')
                    data = deepcopy(self.data)
                    for source in data['sources'].values():
                        if source['path'] == path:
                            source['sha256'] = sha256(target.read_bytes()).hexdigest()
                    with self.subTest(path=path):
                        if lost_rule:
                            self.assert_edges_withheld(data, lost_rule)
                        else:
                            result = audit.subtotal(data, 'Doubleshot')
                            self.assertEqual((result['total'], result['complete'], result['counted']),
                                             (None, False, []))
                            self.assertIsNone(audit.proof(data, 'Doubleshot', component(data, 'goggles-ds'),
                                                         component(data, 'quickblade-ds')))
                finally:
                    target.write_bytes(original)
            self.assertEqual(audit.subtotal(self.data, 'Doubleshot'), EXPECTED_RESULT)

    def test_missing_native_definition_source_never_counts_the_remaining_subset(self):
        for cid in FAMILY[:-1]:
            for change in ('missing', 'quote', 'observed', 'revision'):
                data = deepcopy(self.data)
                if change == 'missing':
                    del data['sources'][cid]
                else:
                    data['sources'][cid][change] = 'changed source identity'
                with self.subTest(cid=cid, change=change):
                    self.assert_family_rejected(data)

    def test_semantic_quickblade_threshold_type_level_and_once_only_conditions(self):
        cases = [
            ('ds-quickblade-20261116', ('exact_item_fields', 'Minimum Level'), '20'),
            ('ds-quickblade-20261116', ('exact_item_fields', 'Augment Type'), 'Sun'),
            ('ds-quickblade-20261116', ('exact_item_fields', 'Description'), '3 pieces equipped: +45% Artifact bonus to Doublestrike and Doubleshot'),
            ('ds-quickblade-20261116', ('exact_item_fields', 'Description'), '3 pieces equipped: +15% Equipment bonus to Doublestrike and Doubleshot'),
            ('ds-quickblade-20261116', ('exact_item_fields', 'Description'), '2 pieces equipped: +15% Artifact bonus to Doublestrike and Doubleshot'),
            ('ds-set-table-20261116', ('observed_row_display',), 'none'),
            ('ds-set-table-20261116', ('headers',), ['Color', 'ML', 'Set Augment']),
            ('ds-set-rules-20261116', ('exact_excerpts', 'activation'), 'Inventory is sufficient'),
            ('ds-set-rules-20261116', ('exact_excerpts', 'deactivation'), 'Permanent after slotting'),
            ('ds-set-rules-20261116', ('exact_excerpts', 'no_extra_reward'), 'Every copy adds the reward'),
            ('ds-set-rules-20261116', ('exact_excerpts', 'augment_sets'), 'Three sockets in one item suffice'),
            ('ds-augment-system-20261116', ('exact_excerpts', 'ordinary_colorless'), 'Only Colorless sockets'),
            ('ds-augment-system-20261116', ('exact_excerpts', 'minimum_level'), 'Minimum level never changes'),
        ]
        original = definitions._source_record
        for target, path, value in cases:
            def reader(data, sid, root):
                record = deepcopy(original(data, sid, root))
                if sid == target:
                    set_path(record, path, value)
                return record
            with self.subTest(target=target, path=path, value=value), patch.object(definitions, '_source_record', reader):
                self.assertFalse(definitions.validate_component(self.data, component(self.data, 'quickblade-ds'), ROOT))
                self.assertIsNone(audit.proof(self.data, 'Doubleshot', component(self.data, 'goggles-ds'),
                                             component(self.data, 'quickblade-ds')))

    def test_semantic_host_slot_level_and_legendary_green_recipe_columns(self):
        cases = [
            ('ds-goggles-host-20261116', ('exact_item_fields', 'Slot'), 'Wrist'),
            ('ds-goggles-host-20261116', ('exact_item_fields', 'Minimum level'), '32'),
            ('ds-goggles-host-20261116', ('observed_slot_labels',), ['Sun Augment Slot']),
            ('ds-chains-host-20261116', ('exact_excerpts', 'equip_choice'), 'Neck slot only'),
            ('ds-chains-host-20261116', ('exact_item_fields', 'Minimum level'), '8'),
            ('ds-yeenoghu-host-20261116', ('exact_item_fields', 'Slot'), 'Eye'),
            ('ds-yeenoghu-host-20261116', ('exact_green_tooltip',), 'Blue, Green, Yellow'),
            ('ds-yeenoghu-host-20261116', ('exact_item_fields', 'Minimum level'), '30'),
            ('ds-green-recipe-20261116', ('headers',), ['Group', 'Heroic', 'Legendary']),
            ('ds-green-recipe-20261116', ('derived_legendary_recipe',), {'Staff Splinters': 30}),
        ]
        original = definitions._source_record
        recipe = original(self.data, 'ds-green-recipe-20261116', ROOT)
        row = recipe['exact_excerpts']['green_recipe_row']
        cases.append(('ds-green-recipe-20261116', ('exact_excerpts', 'green_recipe_row'),
                      row.replace('100   Legendary Staff Splinters', '30   Legendary Staff Splinters')))
        for target, path, value in cases:
            def reader(data, sid, root):
                record = deepcopy(original(data, sid, root))
                if sid == target:
                    set_path(record, path, value)
                return record
            with self.subTest(target=target, path=path), patch.object(definitions, '_source_record', reader):
                self.assertFalse(definitions.validate_component(self.data, component(self.data, 'quickblade-ds'), ROOT))

    def test_semantic_selected_occupancy_and_crafting_prerequisites_are_not_snapshot_authority(self):
        original = definitions._selection
        # Each mutation occurs after the actual manifest bytes have been read.
        cases = [
            (('selection', 'full_kit_ml'), 35),
            (('query', 'race'), 'Warforged'),
            (('items', 2, 'sockets', 2, 'color'), 'Sun'),
            (('items', 2, 'sockets', 2, 'fill', 'ml'), 20),
            (('items', 2, 'sockets', 2, 'fill', 'id'), 'Different set'),
            (('items', 6, 'slot'), 'Bracers'),
            (('items', 6, 'sockets', 0, 'index'), 1),
            (('items', 6, 'crafts'), []),
            (('items', 11, 'minor_artifact'), False),
            (('items', 11, 'filled_ml'), 35),
            (('augment_sets', 2, 'threshold'), 2),
            (('augment_sets', 2, 'effects', 0, 'value'), 45),
            (('augment_sets', 2, 'placements', 1, 'host'), 'Legendary Goggles of the Archer'),
            (('construction_prerequisites',), []),
        ]
        for path, value in cases:
            def reader(root):
                selection = deepcopy(original(root))
                set_path(selection, path, value)
                return selection
            with self.subTest(path=path), patch.object(definitions, '_selection', reader):
                self.assert_family_rejected(self.data)

    def test_competing_set_and_extra_copy_do_not_become_extra_reward_or_suppressed_native_affix(self):
        original = definitions._selection
        for change in ('competing-set', 'extra-copy', 'extra-green-slot', 'native-ds-deleted'):
            def reader(root):
                selection = deepcopy(original(root))
                if change == 'competing-set':
                    selection['augment_sets'][0]['placements'][0]['host'] = 'Legendary Goggles of the Archer'
                elif change == 'extra-copy':
                    selection['items'][2]['sockets'][0]['fill'] = deepcopy(selection['items'][2]['sockets'][2]['fill'])
                elif change == 'extra-green-slot':
                    selection['items'][6]['sockets'].append(deepcopy(selection['items'][6]['sockets'][0]))
                else:
                    selection['items'][2]['native_affixes'] = [a for a in selection['items'][2]['native_affixes']
                                                             if a['stat'] != 'Doubleshot']
                return selection
            with self.subTest(change=change), patch.object(definitions, '_selection', reader):
                self.assert_family_rejected(self.data)
        self.assertIn('goggles-ds', audit.subtotal(self.data, 'Doubleshot')['counted'])

    def test_supplement_timestamps_are_separate_and_cannot_borrow_primary_revision(self):
        packet = json.loads((ROOT / PACKET).read_text())
        self.assertEqual(len(packet['observations']), 12)
        primary, supplement = packet['observations'][10:]
        self.assertLess(primary['ended_at_utc'], supplement['started_at_utc'])
        self.assertNotIn('displayed_permalink', supplement)
        self.assertFalse(packet['audit_interpretation']['implementation_authorized'])
        self.assertTrue(packet['integration_provenance']['implementation_authorized'])
        original = definitions._packet
        for key, value in (('started_at_utc', primary['started_at_utc']),
                           ('displayed_permalink', primary['displayed_permalink']),
                           ('exact_green_slot_tooltip', 'Blue, Green, Yellow')):
            def reader(root):
                data = deepcopy(original(root))
                data['observations'][11][key] = value
                return data
            with self.subTest(key=key), patch.object(definitions, '_packet', reader):
                self.assertFalse(definitions.validate_component(self.data, component(self.data, 'quickblade-ds'), ROOT))

    def test_same_family_caveat_and_original_artifact_limit_are_required(self):
        original = definitions._existing_record
        for sid in ('stack', 'artifact'):
            def reader(data, source_id, root):
                record = deepcopy(original(data, source_id, root))
                if source_id == sid:
                    if sid == 'stack':
                        record['text'] = record['text'].replace(
                            'Benefits from the same family, like Fortification or False Life, do not stack.', '')
                    else:
                        record['exact_source_sections'][1]['paragraph'] = 'Artifact stacks with itself'
                return record
            with self.subTest(sid=sid), patch.object(definitions, '_existing_record', reader):
                self.assert_edges_withheld(self.data, RULE_ID if sid == 'stack' else 'artifact-other-types')


if __name__ == '__main__':
    unittest.main()
