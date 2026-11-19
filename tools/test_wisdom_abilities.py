# Historical .2 contract: exact approved-checkpoint bytes/modules are explicit.
# New selected-recipe tests exercise production separately; no global imports patched.
"""Real current WIS/CON routes, bounded interactions and adversarial controls.

Expected values/members come from the reviewed source inventory; complete .9
results were captured independently before implementation. Passing tests does
not establish full-character scores or settle Skull's conflicting source value.
"""
import selected_recipe_preservation as selected_history
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
audit = selected_history.historical_module('stacking_audit')
import wisdom_ability_proofs as definitions
definitions = selected_history.historical_module('wisdom_ability_proofs')
import wisdom_ability_preservation as preservation
import wisdom_doubleshot_preservation as doubleshot


ROOT = selected_history.HistoricalPath(__file__).resolve().parents[1]
LEDGER = 'tools/fixtures/endgame-stacking/ledger.json'
MANIFEST = 'tools/fixtures/wisdom-loadout/selection.json'
MANIFEST_SHA = '8223bd8e25ed9dc4ad9454439ead42dfb693cc008d18d0ddfeb270d33863c37d'
PACKET = 'evidence/wisdom-loadout/wisdom-con-sources-2026-11-16.json'
PACKET_SHA = 'fae2de021955cdc4112c0f78f6ab3cbb77045375923d92f1c9f5a8cb95060d9d'
CONTRACT = 'selected-wisdom-constitution-v1'
FAMILIES = {
    'Wisdom': ('claws-wisdom', 'celestial-profane-wisdom', 'globe-wisdom'),
    'Constitution': ('skull-con', 'queen-insight-con', 'boots-quality-con', 'solar-con',
                     'celestial-profane-constitution', 'globe-constitution'),
}
FAMILY_IDS = set().union(*map(set, FAMILIES.values()))
QUALIFIED = FAMILY_IDS - {'skull-con'}
EXPECTED_DEFINITIONS = {
    'claws-wisdom': ('Wisdom', 15, 'Enhancement', 'Legendary Burrowing Claws / Nearly Complete'),
    'celestial-profane-wisdom': ('Wisdom', 2, 'Profane', 'Legendary Celestial Sapphire Ring'),
    'globe-wisdom': ('Wisdom', 1, 'Exceptional', 'Legendary Calamitous Longbow / Purple'),
    'queen-insight-con': ('Constitution', 7, 'Insight', 'Cloak Nearly Complete'),
    'boots-quality-con': ('Constitution', 3, 'Quality', 'Legendary Coldlight Runners / Dolorous'),
    'solar-con': ('Constitution', 4, 'Artifact', 'Light Armor of the Warblade’s Reflection / Sun'),
    'celestial-profane-constitution': ('Constitution', 2, 'Profane', 'Legendary Celestial Sapphire Ring'),
    'globe-constitution': ('Constitution', 1, 'Exceptional', 'Legendary Calamitous Longbow / Purple'),
}
PAIR_RULES = {
    ('claws-wisdom', 'celestial-profane-wisdom'): 'wisdom-claws-celestial',
    ('queen-insight-con', 'boots-quality-con'): 'constitution-queen-boots',
    ('queen-insight-con', 'celestial-profane-constitution'): 'constitution-queen-celestial',
    ('boots-quality-con', 'celestial-profane-constitution'): 'constitution-boots-celestial',
}
NEW_SOURCES = {
    'wiscon-nearly-complete-20261116', 'wiscon-claws-20261116', 'wiscon-queen-20261116',
    'wiscon-solar-20261116', 'wiscon-dolorous-20261116', 'wiscon-coldlight-host-20261116',
    'wiscon-reflection-host-20261116', 'wiscon-sun-system-20261116',
}
EXPECTED_REUSE_ROLES = {
    'tip179-live-20261115': 'current positive premise for exactly ten selected INT pairs and four separately named Wisdom/Constitution pairs; original observation and Stack caveat preserved; no generic different-type default',
    'globe-int-live-20261115': 'current selected Globe INT definition and bounded Wisdom/Constitution reuse; original observed all-ability clause and historical INT-only adoption scope preserved',
    'celestial-profane-int-live-20261115': 'current selected native Celestial INT definition and bounded Wisdom/Constitution membership derivations; optional Nearly Finished remains unselected and original capture/adoption scope is preserved',
    'chains-intelligence-membership-20261115': 'current selected Chains INT category premise and bounded native Celestial Wisdom/Constitution membership reuse; original observed ability list and historical INT recipe interpretation preserved',
}
EXPECTED_RESULTS = {
    'Wisdom': {
        'stat': 'Wisdom', 'channel': 'gear', 'total': 18,
        'counted': ['claws-wisdom', 'celestial-profane-wisdom', 'globe-wisdom'],
        'suppressed': [], 'excluded': [], 'missing_interactions': [],
        'proofs': [['claws-wisdom', 'celestial-profane-wisdom', 'wisdom-claws-celestial'],
                   ['claws-wisdom', 'globe-wisdom', 'exceptional-other-types'],
                   ['celestial-profane-wisdom', 'globe-wisdom', 'exceptional-other-types']],
        'complete': True,
    },
    'Constitution': {
        'stat': 'Constitution', 'channel': 'gear', 'total': None,
        'counted': ['globe-constitution', 'queen-insight-con', 'boots-quality-con',
                    'solar-con', 'celestial-profane-constitution'],
        'suppressed': [], 'excluded': ['skull-con'], 'missing_interactions': [],
        'proofs': [['globe-constitution', 'queen-insight-con', 'exceptional-other-types'],
                   ['globe-constitution', 'boots-quality-con', 'exceptional-other-types'],
                   ['globe-constitution', 'solar-con', 'artifact-other-types'],
                   ['globe-constitution', 'celestial-profane-constitution', 'exceptional-other-types'],
                   ['queen-insight-con', 'boots-quality-con', 'constitution-queen-boots'],
                   ['queen-insight-con', 'solar-con', 'artifact-other-types'],
                   ['queen-insight-con', 'celestial-profane-constitution', 'constitution-queen-celestial'],
                   ['boots-quality-con', 'solar-con', 'artifact-other-types'],
                   ['boots-quality-con', 'celestial-profane-constitution', 'constitution-boots-celestial'],
                   ['solar-con', 'celestial-profane-constitution', 'artifact-other-types']],
        'complete': False,
    },
}


def component(data, cid):
    rows = [row for row in data['components'] if row['id'] == cid]
    assert len(rows) == 1, cid
    return rows[0]


def core(row):
    return {k: v for k, v in row.items() if k != 'note'}


class CurrentAbilityTests(unittest.TestCase):
    def setUp(self):
        self.data = audit.load()

    def assert_invalid(self, data):
        with self.assertRaises((AssertionError, KeyError, TypeError, ValueError, IndexError)):
            audit.validate(data)

    def assert_family_rejected(self, data, stat):
        self.assert_invalid(data)
        result = audit.subtotal(data, stat, active=('force', 'all', 'bloodrage'))
        self.assertIsNone(result['total'])
        self.assertFalse(result['complete'])
        self.assertEqual(result['counted'], [])

    @contextmanager
    def isolated_sources(self):
        with tempfile.TemporaryDirectory(prefix='wiscon-functional-') as directory:
            root = Path(directory)
            packet = json.loads((ROOT / PACKET).read_text())
            paths = {MANIFEST, PACKET, 'evidence/wisdom-loadout/loadout.json'} | {
                s['path'] for s in self.data['sources'].values()}
            paths |= {s['path'] for s in packet['reused_sources']}
            for path in paths:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / path).read_bytes())
            with patch.object(audit, 'ROOT', root):
                self.assertTrue(audit.validate(self.data, root=root))
                self.assertEqual(audit.subtotal(self.data, 'Wisdom'), EXPECTED_RESULTS['Wisdom'])
                self.assertEqual(audit.subtotal(self.data, 'Constitution'), EXPECTED_RESULTS['Constitution'])
                yield root

    def test_actual_current_engine_and_exact_eight_definitions(self):
        self.assertEqual(audit.__checkpoint_sha256__, selected_history.sha(selected_history.checkpoint_file_bytes('tools/stacking_audit.py')))
        self.assertEqual(Path(audit.__file__).resolve(), ROOT / 'tools/stacking_audit.py')
        self.assertTrue(audit.validate(self.data))
        self.assertEqual(set(definitions.COMPONENT_IDS), QUALIFIED)
        self.assertEqual(set(definitions.FAMILY_IDS), FAMILY_IDS)
        self.assertEqual(definitions.FAMILIES, FAMILIES)
        for cid, expected in EXPECTED_DEFINITIONS.items():
            row = component(self.data, cid)
            with self.subTest(cid=cid):
                self.assertEqual(tuple(row[k] for k in ('stat', 'amount', 'bonus_type', 'host')), expected)
                self.assertEqual((row['state'], row['channel'], row['kit_min_level'], row['requires']),
                                 ('verified', 'gear', 36, []))
                self.assertEqual((row['source'], row['value_pattern'], row['type_evidence']), ('', '', ''))
                self.assertEqual(row['definition_proof']['contract'], CONTRACT)
                self.assertTrue(definitions.validate_component(self.data, row, ROOT))
        self.assertEqual(sha256((ROOT / PACKET).read_bytes()).hexdigest(), PACKET_SHA)
        self.assertEqual(sha256((ROOT / MANIFEST).read_bytes()).hexdigest(), MANIFEST_SHA)

    def test_complete_wisdom_and_incomplete_constitution_match_whole_expected_objects(self):
        for active in ((), ('force',), ('force', 'bloodrage', 'use_skull_16')):
            for stat, expected in EXPECTED_RESULTS.items():
                with self.subTest(stat=stat, active=active):
                    self.assertEqual(audit.subtotal(self.data, stat, active=active), expected)
        con = EXPECTED_RESULTS['Constitution']
        self.assertEqual(sum(component(self.data, cid)['amount'] for cid in con['counted']), 17)
        self.assertEqual(component(self.data, 'skull-con')['state'], 'conflicting')
        self.assertEqual(component(self.data, 'skull-con')['amount'], 16)

    def test_level35_does_not_count_the_level36_selected_kit(self):
        for stat, members in FAMILIES.items():
            for active in ((), ('force', 'bloodrage')):
                result = audit.subtotal(self.data, stat, level=35, active=active)
                self.assertEqual((result['total'], result['complete'], result['counted'], result['proofs']),
                                 (None, False, [], []))
                self.assertEqual(set(result['excluded']), set(members))

    def test_exact_four_rules_and_all_thirteen_supported_pair_relationships(self):
        found = {r['id']: r for r in self.data['rules'] if r['id'] in PAIR_RULES.values()}
        self.assertEqual(len(found), 4)
        self.assertEqual(set(definitions.RULE_IDS), set(PAIR_RULES.values()))
        for pair, rid in PAIR_RULES.items():
            a, b = (component(self.data, cid) for cid in pair)
            expected = {'id': rid, 'source': 'tip179-live-20261115',
                        'quote': 'Different types of bonuses stack', 'kind': 'selected_pairs',
                        'types': [a['bonus_type'], b['bonus_type']], 'stats': [a['stat']],
                        'channel': 'gear', 'component_pairs': [list(pair)]}
            self.assertEqual(found[rid], expected)
        total = 0
        for stat, result in EXPECTED_RESULTS.items():
            for left, right, rid in result['proofs']:
                a, b = component(self.data, left), component(self.data, right)
                self.assertEqual(audit.proof(self.data, stat, a, b), rid)
                self.assertEqual(audit.proof(self.data, stat, b, a), rid)
                total += 1
        self.assertEqual(total, 13)

    def test_every_skull_proof_is_rejected_including_artifact_and_exceptional_routes(self):
        skull = component(self.data, 'skull-con')
        for cid in FAMILY_IDS:
            other = component(self.data, cid)
            for stat in ('Constitution', 'Wisdom', 'Intelligence'):
                with self.subTest(partner=cid, stat=stat):
                    self.assertIsNone(audit.proof(self.data, stat, skull, other))
                    self.assertIsNone(audit.proof(self.data, stat, other, skull))

    def test_missing_duplicate_renamed_moved_and_substituted_members_cannot_complete_subset(self):
        for stat, members in FAMILIES.items():
            for cid in members:
                for mutation in ('missing', 'duplicate', 'renamed', 'other-stat', 'other-channel'):
                    changed = deepcopy(self.data)
                    row = component(changed, cid)
                    if mutation == 'missing':
                        changed['components'].remove(row)
                    elif mutation == 'duplicate':
                        changed['components'].append(deepcopy(row))
                    elif mutation == 'renamed':
                        row['id'] = 'substituted-' + cid
                    elif mutation == 'other-stat':
                        row['stat'] = 'Dexterity'
                    else:
                        row['channel'] = 'build'
                    with self.subTest(stat=stat, cid=cid, mutation=mutation):
                        self.assert_family_rejected(changed, stat)
                        self.assertFalse(definitions.family_valid(changed, stat, root=ROOT))
        for stat in FAMILIES:
            changed = deepcopy(self.data)
            row = deepcopy(component(changed, FAMILIES[stat][-1]))
            row['id'] = 'extra-family-member'
            changed['components'].append(row)
            self.assert_family_rejected(changed, stat)

    def test_amount_type_host_level_state_and_prerequisite_changes_fail_public_routes(self):
        changes = {'amount': 999, 'bonus_type': 'Untyped', 'host': 'unselected host',
                   'kit_min_level': 1, 'state': 'conditional', 'requires': ['force']}
        for cid in QUALIFIED:
            for field, value in changes.items():
                data = deepcopy(self.data)
                row = component(data, cid)
                row[field] = value
                with self.subTest(cid=cid, field=field):
                    self.assertFalse(definitions.validate_component(data, row, ROOT))
                    self.assert_family_rejected(data, EXPECTED_DEFINITIONS[cid][0])

    def test_skull_numeric_state_source_and_conflict_mutants_cannot_override_exclusion(self):
        for field, value in (('amount', 15), ('state', 'verified'), ('state', 'conditional'),
                             ('source', 'wiscon-queen-20261116'), ('related_sources', []),
                             ('requires', ['force']), ('kit_min_level', 1)):
            data = deepcopy(self.data)
            row = component(data, 'skull-con')
            row[field] = value
            with self.subTest(field=field, value=value):
                self.assert_family_rejected(data, 'Constitution')
                for partner in ('solar-con', 'globe-constitution'):
                    self.assertIsNone(audit.proof(data, 'Constitution', row, component(data, partner)))

    def test_detached_arguments_wrong_stats_channels_and_self_pairs_cannot_borrow_ids(self):
        for pair, _ in PAIR_RULES.items():
            a, b = (component(self.data, cid) for cid in pair)
            self.assertIsNone(audit.proof(self.data, a['stat'], a, a))
            self.assertIsNone(audit.proof(self.data, 'Dexterity', a, b))
            for field, value in (('amount', 999), ('host', 'wrong'), ('channel', 'build'),
                                 ('stat', 'Dexterity'), ('id', 'foreign')):
                altered = deepcopy(a)
                altered[field] = value
                with self.subTest(pair=pair, field=field):
                    self.assertIsNone(audit.proof(self.data, a['stat'], altered, b))
                    self.assertIsNone(audit.proof(self.data, a['stat'], b, altered))

    def test_definition_proof_removal_wrong_contract_and_hybrid_direct_fields_are_rejected(self):
        for cid in QUALIFIED:
            for operation in ('missing', 'empty', 'null', 'list', 'false', 'contract', 'wrong-role', 'direct'):
                data = deepcopy(self.data)
                row = component(data, cid)
                if operation == 'missing':
                    del row['definition_proof']
                elif operation == 'empty':
                    row['definition_proof'] = {}
                elif operation in ('null', 'list', 'false'):
                    row['definition_proof'] = {'null': None, 'list': [], 'false': False}[operation]
                elif operation == 'contract':
                    row['definition_proof']['contract'] = 'other'
                elif operation == 'wrong-role':
                    role = next(iter(row['definition_proof']['sources']))
                    row['definition_proof']['sources'][role] = 'globe-int-live-20261115'
                    if cid.startswith('globe-'):
                        row['definition_proof']['sources'][role] = 'wiscon-claws-20261116'
                else:
                    row['source'] = 'wiscon-claws-20261116'
                with self.subTest(cid=cid, operation=operation):
                    self.assert_family_rejected(data, EXPECTED_DEFINITIONS[cid][0])

    def test_malformed_proof_shapes_reject_current_and_partial_profiles_without_crashing(self):
        for value in (None, [], False, 'invalid'):
            for profile in ('current', 'partial'):
                data = deepcopy(self.data)
                if profile == 'partial':
                    for sid in NEW_SOURCES:
                        del data['sources'][sid]
                    data['rules'] = [r for r in data['rules'] if r['id'] not in PAIR_RULES.values()]
                for cid in QUALIFIED:
                    component(data, cid)['definition_proof'] = deepcopy(value)
                with self.subTest(proof=value, profile=profile):
                    # Verified fixed IDs must still detect a damaged upgrade
                    # after every other new-contract marker was removed.
                    self.assertTrue(definitions.uses_contract(data))
                    for stat in FAMILIES:
                        self.assert_family_rejected(data, stat)
                        left, right = (component(data, cid) for cid in FAMILIES[stat][-2:])
                        self.assertIsNone(audit.proof(data, stat, left, right))
            foreign = deepcopy(component(self.data, 'globe-dexterity'))
            foreign.update(id='foreign-malformed-proof', state='verified', definition_proof=deepcopy(value))
            data = deepcopy(self.data)
            data['components'].append(foreign)
            with self.subTest(proof=value, profile='foreign'):
                self.assert_invalid(data)
                self.assertFalse(audit.component_provenance(data, foreign))
                self.assertIn(foreign['id'], audit.subtotal(data, 'Dexterity')['excluded'])

    def test_each_proof_source_role_is_required_and_not_a_generic_all_ability_alias(self):
        for cid in QUALIFIED:
            original = component(self.data, cid)
            for role in original['definition_proof']['sources']:
                data = deepcopy(self.data)
                row = component(data, cid)
                del row['definition_proof']['sources'][role]
                with self.subTest(cid=cid, role=role):
                    self.assertFalse(definitions.validate_component(data, row, ROOT))
                    self.assert_family_rejected(data, original['stat'])
        for cid in ('globe-wisdom', 'celestial-profane-wisdom'):
            row = deepcopy(component(self.data, cid))
            row.update(id='foreign-dexterity', stat='Dexterity')
            self.assertFalse(definitions.validate_component(self.data, row, ROOT))

    def test_new_source_metadata_mutations_do_not_requalify_the_family(self):
        source_id = 'wiscon-claws-20261116'
        mutations = {'sha256': '0' * 64, 'url': 'https://ddowiki.com/page/Item:Other',
                     'revision': 'https://ddowiki.com/index.php?title=Item:Other&oldid=1',
                     'observed': '2026-11-16T00:00:00Z', 'quote': 'granting +999 Enhancement Wisdom.',
                     'pointer': ['observations', 3, 'exact_fragments', 0],
                     'record_pointer': ['observations', 3], 'observed_pointer': ['review_date_utc']}
        for field, value in mutations.items():
            data = deepcopy(self.data)
            data['sources'][source_id][field] = value
            with self.subTest(field=field):
                self.assertFalse(definitions.validate_source(data, source_id, ROOT))
                self.assert_family_rejected(data, 'Wisdom')

    def test_every_fresh_source_and_reused_premise_remains_a_required_live_binding(self):
        self.assertEqual(set(definitions.NEW_SOURCES), NEW_SOURCES)
        affected = {sid: ('Constitution',) for sid in NEW_SOURCES}
        affected['wiscon-claws-20261116'] = ('Wisdom',)
        affected['wiscon-nearly-complete-20261116'] = tuple(FAMILIES)
        affected.update({sid: tuple(FAMILIES) for sid in (
            'globe-int-live-20261115', 'celestial-profane-int-live-20261115',
            'chains-intelligence-membership-20261115', 'tip179-live-20261115', 'exceptional')})
        affected.update({sid: ('Constitution',) for sid in ('artifact', 'skull-con', 'nearly-complete')})
        for sid, stats in affected.items():
            data = deepcopy(self.data)
            del data['sources'][sid]
            with self.subTest(source=sid):
                self.assert_invalid(data)
                for stat in stats:
                    result = audit.subtotal(data, stat)
                    self.assertIsNone(result['total'])
                    self.assertFalse(result['complete'])
                if sid == 'artifact':
                    self.assertEqual(audit.subtotal(data, 'Wisdom'), EXPECTED_RESULTS['Wisdom'])
                if sid in {'artifact', 'exceptional'}:
                    result = audit.subtotal(data, 'Constitution')
                    self.assertEqual(result['counted'], EXPECTED_RESULTS['Constitution']['counted'])
                    missing = {
                        'artifact': [
                            ['queen-insight-con', 'solar-con'],
                            ['boots-quality-con', 'solar-con'],
                            ['solar-con', 'celestial-profane-constitution'],
                        ],
                        'exceptional': [
                            ['globe-constitution', 'queen-insight-con'],
                            ['globe-constitution', 'boots-quality-con'],
                            ['globe-constitution', 'celestial-profane-constitution'],
                        ],
                    }[sid]
                    self.assertEqual(result['missing_interactions'], missing)
                    self.assertTrue(all(edge[2] != sid + '-other-types' for edge in result['proofs']))
                    # This pair has two independently supported alternatives;
                    # deleting one premise must not disable the other rule.
                    remaining = 'exceptional' if sid == 'artifact' else 'artifact'
                    self.assertIn(['globe-constitution', 'solar-con', remaining + '-other-types'], result['proofs'])
                    for left, right in missing:
                        self.assertIsNone(audit.proof(data, 'Constitution',
                                                     component(data, left), component(data, right)))

    def test_new_observation_pointer_does_not_repair_a_legacy_source(self):
        original = self.data['sources']['claws-wisdom']
        self.assertIsNone(original['observed'])
        changed = deepcopy(original)
        changed['observed'] = '2026-11-16T03:30:06.826Z'
        changed['observed_pointer'] = ['additional_slot_observation', 'started_at_utc']
        self.assertFalse(definitions.observation_context(changed))
        self.assertFalse(audit.source_provenance(changed))

    def test_source_semantics_reject_wrong_effect_variant_host_and_applicability(self):
        original = definitions._source_record
        mutants = (
            ('wiscon-queen-20261116', 'queen-insight-con', ('exact_fragments', 0),
             'granting a +7 Enhancement bonus to Constitution.'),
            ('wiscon-queen-20261116', 'queen-insight-con', ('exact_fragments', 0),
             'granting a +7 Insight bonus to Wisdom.'),
            ('wiscon-dolorous-20261116', 'boots-quality-con', ('context', 'augment_type'),
             'Lamordia: Dolorous (Weapon)'),
            ('wiscon-coldlight-host-20261116', 'boots-quality-con', ('exact_fragments', 0),
             'Lamordia: Dolorous Slot (Armor)'),
            ('wiscon-solar-20261116', 'solar-con', ('context', 'augment_type'), 'Moon'),
            ('wiscon-solar-20261116', 'solar-con', ('context', 'minimum_level'), 1),
            ('wiscon-reflection-host-20261116', 'solar-con', ('context', 'race_absolutely_excluded'), 'Human'),
            ('wiscon-nearly-complete-20261116', 'claws-wisdom', ('context', 'replacement_allowed'), True),
        )
        for sid, cid, path, value in mutants:
            def altered(data, requested, root):
                record = deepcopy(original(data, requested, root))
                if requested == sid:
                    target = record
                    for part in path[:-1]:
                        target = target[part]
                    target[path[-1]] = value
                return record
            with self.subTest(source=sid, field=path), patch.object(definitions, '_source_record', altered):
                self.assertFalse(definitions.validate_component(self.data, component(self.data, cid), ROOT))
                self.assertEqual(audit.subtotal(self.data, EXPECTED_DEFINITIONS[cid][0])['counted'], [])

    def test_retained_all_ability_and_membership_semantics_cannot_be_relabelled(self):
        original_existing, original_retained = definitions._existing_record, definitions._retained_record
        cases = (
            ('celestial-profane-int-live-20261115', 'celestial-abilities-retained',
             'profane_tooltip_html', 'all abilities', 'Intelligence only', 'celestial-profane-wisdom'),
            ('chains-intelligence-membership-20261115', 'ability-membership-retained',
             'ability_members_visible_text', 'Wisdom (WIS)', 'omitted ability', 'celestial-profane-wisdom'),
            ('globe-int-live-20261115', 'globe-abilities-retained',
             'effect_visible_text', 'Wisdom', 'another stat', 'globe-wisdom'),
        )
        for sid, name, field, old, new, cid in cases:
            def existing(data, requested, root, **kwargs):
                record = deepcopy(original_existing(data, requested, root, **kwargs))
                if requested == sid:
                    self.assertIn(old, record[field])
                    record[field] = record[field].replace(old, new)
                return record
            def retained(requested, root):
                record = deepcopy(original_retained(requested, root))
                if requested == name:
                    self.assertIn(old, record[field])
                    record[field] = record[field].replace(old, new)
                return record
            with self.subTest(source=sid), patch.object(definitions, '_existing_record', existing), \
                    patch.object(definitions, '_retained_record', retained):
                self.assertFalse(definitions.validate_component(self.data, component(self.data, cid), ROOT))
                self.assertIsNone(audit.subtotal(self.data, 'Wisdom')['total'])

    def test_new_sources_cannot_be_borrowed_by_foreign_direct_components_or_effects(self):
        source_id = 'wiscon-claws-20261116'
        for alias in (source_id, 'unreviewed-source-alias'):
            data = deepcopy(self.data)
            if alias != source_id:
                data['sources'][alias] = deepcopy(data['sources'][source_id])
            row = deepcopy(component(data, 'claws-wisdom'))
            row.pop('definition_proof')
            row.update(id='foreign-definition', stat='Dexterity', source=alias,
                       value_pattern=r'\+(?P<value>15) Enhancement bonus to Wisdom',
                       type_evidence='Enhancement bonus to Wisdom')
            data['components'].append(row)
            with self.subTest(alias=alias):
                self.assert_invalid(data)
                result = audit.subtotal(data, 'Dexterity')
                self.assertIn('foreign-definition', result['excluded'])
                self.assertIsNone(audit.proof(data, 'Dexterity', row, component(data, 'globe-dexterity')))
            data = deepcopy(self.data)
            data['non_total_effects'].append({'id': 'foreign-effect', 'state': 'verified',
                                              'sources': [source_id], 'note': 'Unreviewed borrowing'})
            self.assert_invalid(data)

    def test_rule_mutants_and_incomplete_profiles_do_not_expand_positive_scope(self):
        rid = 'wisdom-claws-celestial'
        for mutation in ('missing', 'duplicate', 'renamed', 'stat', 'types', 'pair', 'channel'):
            data = deepcopy(self.data)
            rule = next(r for r in data['rules'] if r['id'] == rid)
            if mutation == 'missing':
                data['rules'].remove(rule)
            elif mutation == 'duplicate':
                data['rules'].append(deepcopy(rule))
            elif mutation == 'renamed':
                rule['id'] = 'unknown-rule'
            elif mutation == 'stat':
                rule['stats'] = ['*']
            elif mutation == 'types':
                rule['types'] = ['*']
            elif mutation == 'pair':
                rule['component_pairs'] = [['skull-con', 'queen-insight-con']]
            else:
                rule['channel'] = 'build'
            with self.subTest(mutation=mutation):
                self.assert_family_rejected(data, 'Wisdom')
                self.assert_family_rejected(data, 'Constitution')

    def test_actual_new_packet_bytes_cannot_be_blessed_by_rehashing_caller_metadata(self):
        with self.isolated_sources() as root:
            path = root / PACKET
            path.write_bytes(path.read_bytes() + b'\n')
            for rehash in (False, True):
                data = deepcopy(self.data)
                if rehash:
                    for sid in NEW_SOURCES:
                        data['sources'][sid]['sha256'] = sha256(path.read_bytes()).hexdigest()
                with self.subTest(rehash=rehash):
                    with self.assertRaises((AssertionError, KeyError)):
                        audit.validate(data, root=root)
                    for stat in FAMILIES:
                        self.assertEqual(audit.subtotal(data, stat)['counted'], [])

    def test_actual_reused_and_conflict_source_bytes_are_checked_after_prior_success(self):
        paths = ('evidence/wisdom-loadout/int-evidence-sources-2026-11-15.json',
                 'evidence/wisdom-loadout/recipe-proof-sources-2026-11-15.json',
                 'evidence/wisdom-loadout/int-stacking-sources-2026-11-15.json',
                 'tools/fixtures/lamordia-handling/viktranium-experiment-crafting.browser-capture.json',
                 'evidence/endgame-stacking/skull-714102.json',
                 'evidence/endgame-stacking/nearly-complete-705751.json')
        with self.isolated_sources() as root:
            for path in paths:
                target = root / path
                original = target.read_bytes()
                target.write_bytes(original + b' ')
                with self.subTest(path=path):
                    result = audit.subtotal(self.data, 'Constitution')
                    if path == 'evidence/wisdom-loadout/int-stacking-sources-2026-11-15.json':
                        # Tip 179 supports interactions, not these independent
                        # definitions. Keep the inputs but withhold its edges.
                        self.assertEqual(result['counted'], EXPECTED_RESULTS['Constitution']['counted'])
                        self.assertEqual(result['missing_interactions'], [
                            ['queen-insight-con', 'boots-quality-con'],
                            ['queen-insight-con', 'celestial-profane-constitution'],
                            ['boots-quality-con', 'celestial-profane-constitution'],
                        ])
                        self.assertTrue(all(edge[2] not in PAIR_RULES.values() for edge in result['proofs']))
                        wisdom = audit.subtotal(self.data, 'Wisdom')
                        self.assertEqual(wisdom['counted'], EXPECTED_RESULTS['Wisdom']['counted'])
                        self.assertEqual(wisdom['missing_interactions'], [
                            ['claws-wisdom', 'celestial-profane-wisdom']])
                        self.assertIsNone(wisdom['total'])
                        self.assertFalse(wisdom['complete'])
                    else:
                        self.assertEqual(result['counted'], [])
                    self.assertIsNone(result['total'])
                    self.assertFalse(result['complete'])
                target.write_bytes(original)

    def test_actual_selection_host_socket_and_prerequisite_bytes_are_pinned(self):
        with self.isolated_sources() as root:
            path = root / MANIFEST
            original = path.read_bytes()
            for mutation in ('floor', 'race', 'solar-slot', 'globe-slot', 'queen-craft'):
                data = json.loads(original)
                if mutation == 'floor':
                    data['selection']['full_kit_ml'] = 30
                elif mutation == 'race':
                    data['query']['race'] = 'Warforged'
                else:
                    host = {'solar-slot': "Light Armor of the Warblade's Reflection",
                            'globe-slot': 'Legendary Calamitous Longbow', 'queen-craft': 'The Queen of Rot'}[mutation]
                    item = next(item for item in data['items'] if item['id'] == host)
                    if mutation == 'queen-craft':
                        item['crafts'][0]['name'] = 'Wisdom'
                    else:
                        item['sockets'][0 if mutation == 'solar-slot' else 1]['color'] = 'Moon'
                path.write_text(json.dumps(data))
                with self.subTest(mutation=mutation):
                    for stat in FAMILIES:
                        self.assertEqual(audit.subtotal(self.data, stat)['counted'], [])
                path.write_bytes(original)

    def test_prior_sources_rules_unrelated_components_and_skull_core_remain_literal(self):
        previous = json.loads(preservation.checkpoint_file_text(LEDGER))
        point_one = json.loads(doubleshot.checkpoint_file_text(LEDGER))
        # This is the literal .9-to-.1 addition contract. The current .2
        # Doubleshot addition has its own independently pinned outer contract.
        self.assertEqual(set(point_one['sources']), set(previous['sources']) | NEW_SOURCES)
        for sid, old in previous['sources'].items():
            self.assertEqual(point_one['sources'][sid], old, sid)
            self.assertEqual(point_one['source_roles'][sid],
                             EXPECTED_REUSE_ROLES.get(sid, previous['source_roles'][sid]), sid)
        self.assertEqual({sid for sid in previous['source_roles']
                          if point_one['source_roles'][sid] != previous['source_roles'][sid]},
                         set(EXPECTED_REUSE_ROLES))
        self.assertEqual(point_one['rules'][:len(previous['rules'])], previous['rules'])
        self.assertEqual({r['id'] for r in point_one['rules'][len(previous['rules']):]}, set(PAIR_RULES.values()))
        self.assertEqual([r['id'] for r in point_one['components']], [r['id'] for r in previous['components']])
        for old, new in zip(previous['components'], point_one['components']):
            if old['id'] not in QUALIFIED:
                self.assertEqual(core(new), core(old), old['id'])
        self.assertEqual(component(point_one, 'skull-con'), component(previous, 'skull-con'))
        # Keep real-current checks: every prior source dictionary, all sixteen
        # prior rules and every non-Quickblade component core stay literal.
        # Only Tip 179's role adds the six explicitly scoped Doubleshot pairs;
        # both role strings are pinned independently of the candidate data.
        tip_role = 'tip179-live-20261115'
        self.assertEqual(point_one['source_roles'][tip_role],
                         'current positive premise for exactly ten selected INT pairs and four separately '
                         'named Wisdom/Constitution pairs; original observation and Stack caveat preserved; '
                         'no generic different-type default')
        current_tip_role = (
            'current positive premise for exactly ten selected INT pairs, four separately named '
            'Wisdom/Constitution pairs and six selected Doubleshot pairs; original observation and '
            'Stack caveat preserved; no generic different-type default')
        for sid, old in point_one['sources'].items():
            self.assertEqual(self.data['sources'][sid], old, sid)
            expected_role = current_tip_role if sid == tip_role else point_one['source_roles'][sid]
            self.assertEqual(self.data['source_roles'][sid], expected_role, sid)
        self.assertEqual({sid for sid in point_one['source_roles']
                          if self.data['source_roles'][sid] != point_one['source_roles'][sid]}, {tip_role})
        self.assertEqual(self.data['rules'][:16], point_one['rules'])
        self.assertEqual([r['id'] for r in self.data['rules'][16:]], ['doubleshot-selected-six-pairs'])
        self.assertEqual([r['id'] for r in self.data['components']], [r['id'] for r in point_one['components']])
        for old, current in zip(point_one['components'], self.data['components']):
            if old['id'] != 'quickblade-ds':
                self.assertEqual(core(current), core(old), old['id'])
        self.assertEqual(component(self.data, 'skull-con'), component(point_one, 'skull-con'))

    def test_exact_historical_rule_profiles_remain_inputs_to_the_real_new_engine(self):
        import wisdom_int_stacking_preservation as point_five
        import wisdom_fort_spot_preservation as point_seven
        import wisdom_chains_type_preservation as point_eight
        for count, view in ((7, point_five), (9, point_seven), (10, point_eight),
                            (12, preservation), (16, doubleshot)):
            data = json.loads(view.checkpoint_file_text(LEDGER))
            before = json.dumps(data, sort_keys=True)
            with self.subTest(profile=count):
                self.assertEqual(len(audit.rule_profile(data)), count)
                self.assertTrue(audit.validate(data))
                self.assertEqual(json.dumps(data, sort_keys=True), before)
        self.assertEqual(len(audit.rule_profile(self.data)), 17)

    def test_current_renderers_explain_complete_wisdom_and_only_a_constitution_subset(self):
        import build_stacking_audit as renderer
        renderer = selected_history.historical_module('build_stacking_audit')
        import wisdom_loadout as recipe
        recipe = selected_history.historical_module('wisdom_loadout')
        from build_snapshot import current_build, snapshot_html
        html = (ROOT / 'index.html').read_text()
        paragraph = recipe.render_ability_qualification(self.data)
        self.assertIn('data-wiscon-qualification="selected-definitions"', paragraph)
        self.assertIn('Derived selected-gear Wisdom: +18 at level 36.', paragraph)
        self.assertIn('Supported standing Constitution subset: +17; full total withheld.', paragraph)
        self.assertIn(paragraph, html)
        self.assertIn(paragraph, renderer.summary(self.data))
        self.assertTrue(renderer.validate_guide(html, self.data))
        self.assertEqual(renderer.detail(self.data), (ROOT / 'endgame-stacking-audit.html').read_text())
        self.assertEqual(current_build(html), '11-16-26.2')
        self.assertEqual(snapshot_html(html), (ROOT / 'versions/11-16-26.2.html').read_text())
        for mutation in ('missing-skull', 'changed-wisdom'):
            data = deepcopy(self.data)
            if mutation == 'missing-skull':
                data['components'].remove(component(data, 'skull-con'))
            else:
                component(data, 'claws-wisdom')['amount'] = 16
            with self.subTest(mutation=mutation):
                for render in (recipe.render_ability_qualification, renderer.summary, renderer.detail):
                    with self.assertRaises((AssertionError, ValueError)):
                        render(data)


if __name__ == '__main__':
    unittest.main()
