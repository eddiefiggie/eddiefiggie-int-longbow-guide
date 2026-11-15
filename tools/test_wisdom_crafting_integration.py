"""Actual-current crafting qualification, separate from frozen source grades.

The exact-restored fbb1 ledger is a comparison input, never a substitute for the
production ledger. These checks bind one newly qualified input and all complete
calculator results; they do not certify a live-game craft, stacking or DPS.
"""
import copy
from hashlib import sha256
import json
from pathlib import Path
import re
import unittest

import stacking_audit as audit
import wisdom_crafting_integration as integration
import wisdom_loadout as recipe


ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = 'tools/fixtures/endgame-stacking/ledger.json'
PACKET_PATH = 'evidence/wisdom-loadout/crafting-browser-2026-11-15.json'
RECORD_PATH = 'evidence/wisdom-loadout/crafting-integration-2026-11-15.json'
PACKET_SHA = '4394f8f408d6d448a99f473ece71ce26248d3710e8e9243a0d98d532cbd77d01'
SOURCE_ID = 'glabrezu-insight-int-live-20261115'
COMPONENT_ID = 'glabrezu-insight-int'
CHAINS = ('chains-fortification', 'chains-combustion', 'chains-quality-int', 'chains-spot')
SOURCE_ROLE = 'current component, rule, effect or unresolved context'
VALUE_PATTERN = (r'granting a \+(?P<value>\d+) <a href="/page/Insight_bonus" '
                 r'title="Insight bonus">Insight bonus</a> to Intelligence\.')
SOURCE = {
    'path': PACKET_PATH,
    'sha256': PACKET_SHA,
    'pointer': ['captures', 'glabrezu', 'selected_option_html'],
    'quote': ('This item focuses the power of the wearer\'s mind, granting a +7 '
              '<a href="/page/Insight_bonus" title="Insight bonus">Insight bonus</a> '
              'to Intelligence.'),
    'url': 'https://ddowiki.com/page/Item:Legendary_Glabrezu_Claw_Pendant',
    'revision': 'https://ddowiki.com/index.php?title=Item:Legendary_Glabrezu_Claw_Pendant&oldid=707320',
    'observed': '2026-11-15T20:43:29Z',
    'freshness_limit': (
        'New hosted-browser DOM extraction observed 2026-11-15T20:43:29Z through '
        '2026-11-15T20:43:33Z; the page warned logged-out content may lag up to '
        '18 hours. Scoped tooltip HTML, not a raw HTTP response or live-game test. '
        'The Permanent link was read from that page, not independently loaded. '
        'Source modification time and previous missing capture metadata are distinct.'),
    'record_pointer': ['captures', 'glabrezu'],
    'url_key': 'source_url',
    'revision_pointer': ['revision_link'],
    'observed_pointer': ['body_observation', 'started_at_utc'],
}
IMMUTABLE = {
    PACKET_PATH: PACKET_SHA,
    'tools/fixtures/wisdom-loadout/selection.json': '8223bd8e25ed9dc4ad9454439ead42dfb693cc008d18d0ddfeb270d33863c37d',
    'tools/stacking_audit.py': '97432b1a37543645986a343ec0c6d3c8d58b77c4089e03307dfdf2840d3c606d',
    'tools/bowmodel.py': '7d9e0843939310214d73b00e7e936ca4e842bf7bf0fc3f8da1b849e8c8faf236',
    'evidence/wisdom-loadout/claims.json': '2de551db80e4d682da2cd0a3156b1a5e830927a833750b81d370b6c6bbedf1ad',
    'evidence/wisdom-loadout/sources.json': 'cea672fa20445cfda89717a8e04af1a34c73f272ff82bf0ad86630713c1bd92a',
    'evidence/wisdom-loadout/loadout.json': '20f5bca4573d803a196695aa999f4acc07e71db077e3b66fde51a560b6da0843',
    'evidence/wisdom-loadout/production.json': '684215235205fb59ba183cf11d9235661becb2973681afb7dfc6ae9e332413e2',
    'evidence/wisdom-loadout/derivation.json': '215c66ae090b2d25142472634dd8e56c668e08526ed6bbaa6709116ecbc9da02',
    'evidence/wisdom-loadout/corrections.json': 'a6b318f5f71f1f9445e21c19d23a22fddf3ad20f7e4888858bf3ef5effdd591f',
    'evidence/wisdom-loadout/startup.json': 'f4ffd67f7ca1b55a3a44a6ed8e4e28b60d48a9acce4e7294983311adaf0207ef',
    'evidence/wisdom-loadout/verification.json': 'a78f7205b9887f3ac5aa06ffc5f0a8acc446e9c8a9c2739314b510a7e1ee246b',
}


def components(data):
    return {row['id']: row for row in data['components']}


def current_scope_contract(current, checkpoint):
    """Preserve selection/applicability as well as the generic clause gate.

    The generic calculator checks source clauses, not whether an arbitrary
    caller has silently reassigned a host. This reviewed integration contract
    independently forbids that reassignment and all other out-of-scope edits.
    """
    audit.validate(current)
    assert set(current) == set(checkpoint)
    changed_fields = {'sources', 'source_roles', 'components', 'non_total_effects'}
    for field in set(current) - changed_fields:
        assert current[field] == checkpoint[field], field
    assert set(current['sources']) == set(checkpoint['sources']) | {SOURCE_ID}
    assert SOURCE_ID not in checkpoint['sources']
    assert current['sources'][SOURCE_ID] == SOURCE
    for sid, source in checkpoint['sources'].items():
        assert current['sources'][sid] == source, sid
    assert current['source_roles'] == {**checkpoint['source_roles'], SOURCE_ID: SOURCE_ROLE}
    assert set(current['source_roles']) == set(current['sources'])
    assert [c['id'] for c in current['components']] == [c['id'] for c in checkpoint['components']]
    for current_row, old_row in zip(current['components'], checkpoint['components']):
        cid = current_row['id']
        assert set(current_row) == set(old_row), cid
        allowed = ({'state', 'source', 'value_pattern', 'type_evidence', 'note'}
                   if cid == COMPONENT_ID else {'note'} if cid in CHAINS else set())
        assert {k: v for k, v in current_row.items() if k not in allowed} == {
            k: v for k, v in old_row.items() if k not in allowed}, cid
        if allowed:
            assert current_row['note'] and current_row['note'] != old_row['note'], cid
    rows = components(current)
    assert tuple(rows[COMPONENT_ID][key] for key in (
        'state', 'source', 'value_pattern', 'type_evidence')) == (
            'verified', SOURCE_ID, VALUE_PATTERN, 'Insight bonus')
    for cid in CHAINS:
        assert tuple(rows[cid][key] for key in (
            'state', 'source', 'value_pattern', 'type_evidence')) == ('unknown', '', '', ''), cid
    assert [e['id'] for e in current['non_total_effects']] == [e['id'] for e in checkpoint['non_total_effects']]
    for current_row, old_row in zip(current['non_total_effects'], checkpoint['non_total_effects']):
        if current_row['id'] == 'chains-construction':
            assert set(current_row) == set(old_row)
            assert {k: v for k, v in current_row.items() if k != 'note'} == {
                k: v for k, v in old_row.items() if k != 'note'}
            assert current_row['note'] and current_row['note'] != old_row['note']
        else:
            assert current_row == old_row, current_row['id']
    return True


class CurrentCraftingIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checkpoint = json.loads(integration.checkpoint_file_text(LEDGER_PATH))

    def setUp(self):
        self.data = audit.load()
        self.packet = json.loads((ROOT / PACKET_PATH).read_text())
        self.record = json.loads((ROOT / RECORD_PATH).read_text())

    def test_actual_current_ledger_matches_exact_one_input_scope(self):
        self.assertTrue(current_scope_contract(self.data, self.checkpoint))
        self.assertTrue(audit.validate(self.checkpoint))
        source = self.data['sources'][SOURCE_ID]
        capture = audit.resolve(self.packet, source['record_pointer'])
        self.assertIn(source['quote'], capture['selected_option_html'])
        self.assertEqual(float(re.search(VALUE_PATTERN, source['quote']).group('value')), 7)
        self.assertEqual(source['observed'], capture['body_observation']['started_at_utc'])
        self.assertEqual(capture['body_observation']['ended_at_utc'], '2026-11-15T20:43:33Z')
        self.assertEqual(source['revision'], capture['revision_link'])
        self.assertIn('Minimum level\t35', capture['item_table_visible_text'])
        self.assertEqual(components(self.data)[COMPONENT_ID]['kit_min_level'], 36)

    def test_frozen_source_packet_models_selection_and_original_receipts_remain_bytes(self):
        for path, expected in IMMUTABLE.items():
            with self.subTest(path=path):
                self.assertEqual(sha256((ROOT / path).read_bytes()).hexdigest(), expected)
        # Historical checkpoint flags are not retroactively rewritten to describe .3.
        self.assertFalse(self.packet['scope']['calculator_components_promoted'])
        self.assertFalse(self.packet['scope']['historical_claim_inventory_regraded'])
        self.assertEqual(self.data['rules'], self.checkpoint['rules'])

    def test_all_76_complete_calculator_results_change_only_two_intelligence_metadata_rows(self):
        families = sorted({(c['stat'], c['channel']) for c in self.data['components']})
        self.assertEqual(families, sorted({(c['stat'], c['channel']) for c in self.checkpoint['components']}))
        self.assertEqual(len(families), 38)
        changed, unchanged = [], 0
        for stat, channel in families:
            for active in ((), ('force',)):
                before = audit.subtotal(self.checkpoint, stat, channel=channel, active=active)
                after = audit.subtotal(self.data, stat, channel=channel, active=active)
                expected = copy.deepcopy(before)
                if (stat, channel) == ('Intelligence', 'gear'):
                    self.assertEqual(before['counted'], [])
                    expected['counted'] = [COMPONENT_ID]
                    expected['excluded'].remove(COMPONENT_ID)
                    self.assertEqual(len(expected['excluded']), 8)
                    self.assertIsNone(expected['total'])
                    self.assertFalse(expected['complete'])
                    for key in ('suppressed', 'proofs', 'missing_interactions'):
                        self.assertEqual(expected[key], [])
                with self.subTest(stat=stat, channel=channel, active=active):
                    self.assertEqual(after, expected)
                if before != after:
                    changed.append((stat, channel, active))
                else:
                    unchanged += 1
        self.assertEqual(changed, [('Intelligence', 'gear', ()), ('Intelligence', 'gear', ('force',))])
        self.assertEqual(unchanged, 74)

    def test_item_ml_35_does_not_lower_selected_filled_kit_floor_or_complete_intelligence(self):
        for active in ((), ('force',)):
            at35 = audit.subtotal(self.data, 'Intelligence', level=35, active=active)
            self.assertEqual(at35, audit.subtotal(self.checkpoint, 'Intelligence', level=35, active=active))
            self.assertIn(COMPONENT_ID, at35['excluded'])
            at36 = audit.subtotal(self.data, 'Intelligence', level=36, active=active)
            self.assertEqual(at36['counted'], [COMPONENT_ID])
            self.assertIsNone(at36['total'])
            self.assertFalse(at36['complete'])

    def test_wrong_missing_observation_revision_identity_and_capture_are_rejected(self):
        mutants = {
            'missing observation': {'observed': None, 'observed_pointer': None},
            'wrong observation': {'observed': '2026-11-15T21:10:28Z'},
            'end window substituted': {'observed': '2026-11-15T20:43:33Z',
                                       'observed_pointer': ['body_observation', 'ended_at_utc']},
            'page modification substituted': {
                'observed': self.packet['captures']['glabrezu']['page_modified_display'],
                'observed_pointer': ['page_modified_display']},
            'missing revision': {'revision': None, 'revision_pointer': None},
            'wrong revision': {'revision': SOURCE['revision'].replace('707320', '707321')},
            'wrong record': {'record_pointer': ['captures', 'chains']},
            'missing record': {'record_pointer': ['captures', 'not-a-capture']},
            'wrong context': {'pointer': ['captures', 'chains', 'item_table_visible_text']},
            'wrong source identity': {'url': 'https://ddowiki.com/page/Item:Legendary_Chains'},
            'wrong packet': {'path': 'evidence/wisdom-loadout/sources.json'},
            'wrong hash': {'sha256': '0' * 64},
            'fabricated clause': {'quote': SOURCE['quote'].replace('+7 ', '+8 ')},
            'missing freshness limits': {'freshness_limit': ''},
        }
        for label, fields in mutants.items():
            changed = copy.deepcopy(self.data)
            changed['sources'][SOURCE_ID].update(fields)
            with self.subTest(mutation=label), self.assertRaises((AssertionError, KeyError)):
                audit.validate(changed)
        changed = copy.deepcopy(self.data)
        del changed['sources'][SOURCE_ID]
        with self.assertRaises(KeyError):
            audit.validate(changed)

    def test_wrong_component_value_stat_type_pattern_and_source_are_rejected(self):
        for field, value in (
                ('amount', 8), ('stat', 'Wisdom'), ('bonus_type', 'Enhancement'),
                ('type_evidence', 'Enhancement bonus'), ('type_evidence', ''),
                ('value_pattern', r'granting a \+(?P<value>8)'), ('value_pattern', ''),
                ('source', 'claws-wisdom'), ('source', '')):
            changed = copy.deepcopy(self.data)
            components(changed)[COMPONENT_ID][field] = value
            # An empty regex matches but has no required named value group.
            error = IndexError if field == 'value_pattern' and value == '' else (AssertionError, KeyError)
            with self.subTest(field=field, value=value), self.assertRaises(error):
                audit.validate(changed)

    def test_item_label_number_cannot_replace_the_exact_typed_effect_clause(self):
        changed = copy.deepcopy(self.data)
        changed['sources'][SOURCE_ID]['quote'] = self.packet['captures']['glabrezu']['selected_option_html']
        components(changed)[COMPONENT_ID]['value_pattern'] = r'Insightful Intelligence \+(?P<value>\d+)</a>'
        with self.assertRaises(AssertionError):
            audit.validate(changed)

    def test_scope_rejects_host_level_requirements_models_and_old_source_drift(self):
        for cid, field, value in (
                (COMPONENT_ID, 'host', 'Legendary Chains / Bonus'),
                (COMPONENT_ID, 'kit_min_level', 35),
                (COMPONENT_ID, 'requires', ['force']),
                ('chains-quality-int', 'amount', 7),
                ('chains-combustion', 'host', 'Weapon'),
                ('claws-wisdom', 'amount', 16)):
            changed = copy.deepcopy(self.data)
            components(changed)[cid][field] = value
            with self.subTest(component=cid, field=field), self.assertRaises(AssertionError):
                current_scope_contract(changed, self.checkpoint)
        changed = copy.deepcopy(self.data)
        changed['sources']['claws-wisdom']['freshness_limit'] += ' New review is not an original capture.'
        with self.assertRaises(AssertionError):
            current_scope_contract(changed, self.checkpoint)
        changed = copy.deepcopy(self.data)
        changed['source_roles'][SOURCE_ID] = 'historical/background only — not a current equipped input'
        with self.assertRaises(AssertionError):
            current_scope_contract(changed, self.checkpoint)

    def test_no_new_or_broadened_positive_interaction_is_allowed(self):
        for edit in ('additional', 'broadened'):
            changed = copy.deepcopy(self.data)
            if edit == 'additional':
                extra = copy.deepcopy(changed['rules'][0])
                extra['id'] = 'unreviewed-intelligence-combination'
                changed['rules'].append(extra)
            else:
                next(r for r in changed['rules'] if r['id'] == 'fort-enh-insight')['stats'].append('Intelligence')
            with self.subTest(edit=edit), self.assertRaises((AssertionError, KeyError)):
                audit.validate(changed)

    def test_chains_remain_unknown_excluded_and_cannot_be_enabled_with_activity_flags(self):
        for cid in CHAINS:
            row = components(self.data)[cid]
            self.assertEqual((row['state'], row['source'], row['value_pattern'], row['type_evidence']),
                             ('unknown', '', '', ''))
            for active in ((), ('force',), ('force', 'unknown', 'verified')):
                with self.subTest(component=cid, active=active):
                    self.assertIn(cid, audit.subtotal(self.data, row['stat'], active=active)['excluded'])
            changed = copy.deepcopy(self.data)
            components(changed)[cid]['state'] = 'verified'
            with self.subTest(component=cid), self.assertRaises((AssertionError, KeyError)):
                audit.validate(changed)

    def test_retained_recipe_categories_do_not_pass_as_exact_chains_effect_clauses(self):
        capture = self.packet['captures']['slave_lords']
        cases = (
            ('chains-fortification', 'fortification_row_html', r'\+(?P<value>142)%', 'Enhancement'),
            ('chains-combustion', 'spell_power_row_html', r'\+(?P<value>142)', 'Equipment Bonus'),
            ('chains-quality-int', 'quality_attributes_row_visible_text', r'\+(?P<value>3)\t', 'Quality'),
            ('chains-spot', 'skills_row_visible_text', r'\+(?P<value>20)\t', 'Competence'),
        )
        for cid, field, pattern, typed in cases:
            changed = copy.deepcopy(self.data)
            sid = 'negative-test-' + cid
            changed['sources'][sid] = {
                **SOURCE, 'pointer': ['captures', 'slave_lords', field],
                'record_pointer': ['captures', 'slave_lords'], 'quote': capture[field],
                'url': capture['source_url'], 'revision': capture['revision_link'],
                'observed': capture['body_observation']['started_at_utc'],
                'freshness_limit': 'Negative test of retained recipe context, not a finished effect.'}
            components(changed)[cid].update(state='verified', source=sid,
                                           value_pattern=pattern, type_evidence=typed)
            with self.subTest(component=cid), self.assertRaises(AssertionError):
                audit.validate(changed)

    def test_borrowing_the_pendant_clause_cannot_promote_a_different_selected_host(self):
        for cid in CHAINS:
            changed = copy.deepcopy(self.data)
            row = components(changed)[cid]
            row.update(stat='Intelligence', amount=7, bonus_type='Insight', state='verified',
                       source=SOURCE_ID, value_pattern=VALUE_PATTERN, type_evidence='Insight bonus')
            with self.subTest(component=cid):
                with self.assertRaises(AssertionError):
                    current_scope_contract(changed, self.checkpoint)
                with self.assertRaises(ValueError):
                    recipe.render_crafting_qualification(changed)

    def test_integration_record_binds_observation_scope_and_no_unapproved_actions(self):
        record = self.record
        self.assertEqual((record['schema_version'], record['record_type'], record['build']),
                         (1, 'bounded-crafting-source-integration', '11-15-26.3'))
        self.assertEqual(record['baseline']['remote_head'], integration.BASE_COMMIT)
        self.assertEqual(record['baseline']['remote_and_initial_staged_tree'], integration.BASE_TREE)
        self.assertEqual(record['scope']['promoted_component_ids'], [COMPONENT_ID])
        self.assertEqual(record['scope']['unqualified_component_ids'], list(CHAINS))
        flags = set(record['scope']) - {'purpose', 'promoted_component_ids', 'unqualified_component_ids'}
        self.assertTrue(flags)
        for flag in flags:
            self.assertIs(record['scope'][flag], False, flag)
        self.assertEqual((record['source_packet']['path'], record['source_packet']['sha256']),
                         (PACKET_PATH, PACKET_SHA))
        qualified = record['qualified_component']
        row = components(self.data)[COMPONENT_ID]
        self.assertEqual((qualified['id'], qualified['source_id'], qualified['stat'],
                          qualified['amount'], qualified['bonus_type']),
                         (COMPONENT_ID, row['source'], row['stat'], row['amount'], row['bonus_type']))
        self.assertEqual(qualified['source_pointer'], SOURCE['pointer'])
        self.assertEqual(qualified['record_pointer'], SOURCE['record_pointer'])
        self.assertEqual(qualified['revision'], SOURCE['revision'])
        self.assertEqual(qualified['body_observation'], self.packet['captures']['glabrezu']['body_observation'])
        self.assertEqual((qualified['host_base_ml'], qualified['filled_kit_applicability_ml']), (35, 36))
        self.assertEqual([finding['id'] for finding in record['chains_findings']], list(CHAINS))
        self.assertEqual(record['expected_calculator_delta']['unchanged_results'], 74)

    def test_generic_other_item_spot_capture_is_not_a_selected_chains_source(self):
        followup = self.record['targeted_followup']
        category = followup['spot_category']
        self.assertEqual(category['generic_other_host'], 'Legendary Keylock Ring')
        self.assertEqual(category['exact_named_chains_link_count'], 0)
        self.assertIn('Competence bonus', category['spot_option_html'])
        self.assertIn('not the selected finished Chains craft', category['limit'])
        self.assertIn('not evidence that the Wiki or game lacks the effect', followup['focused_search']['assessment'])
        self.assertFalse(any(s['path'] == RECORD_PATH for s in self.data['sources'].values()))
        self.assertEqual(components(self.data)['chains-spot']['source'], '')

    def test_actual_current_renderer_and_generated_outputs_use_same_qualified_data(self):
        full = recipe.render_crafting_qualification(self.data)
        compact = recipe.render_crafting_qualification(self.data, compact=True)
        self.assertEqual(recipe.render_crafting_qualification(), full)
        self.assertEqual(recipe.render_crafting_qualification(compact=True), compact)
        self.assertTrue(full.startswith(compact))
        self.assertEqual(full.count('id="wisdom-crafting-evidence"'), 1)
        self.assertIn('SOURCE-QUALIFIED INPUT', full)
        self.assertEqual(full.count('RECIPE SUPPORTED · INPUT WITHHELD'), 4)
        self.assertIn('complete Intelligence combination is still withheld', compact)
        self.assertIn('not weapon damage or measured DPS', full)
        html = (ROOT / 'index.html').read_text()
        detail = (ROOT / 'endgame-stacking-audit.html').read_text()
        self.assertEqual(html.count(full), 1)
        self.assertEqual(html.count(compact), 2)
        self.assertEqual(detail.count(compact), 1)
        self.assertNotIn('id="wisdom-crafting-evidence"', detail)
        excerpts = json.loads((ROOT / 'evidence/endgame-stacking/source-excerpts.json').read_text())
        self.assertEqual(excerpts['sources'], self.data['sources'])
        self.assertEqual(excerpts['source_roles'], self.data['source_roles'])

    def test_renderer_rejects_current_source_loss_demotion_and_unreviewed_chains_promotion(self):
        for mode in ('source loss', 'demotion', 'unknown chains binding'):
            changed = copy.deepcopy(self.data)
            if mode == 'source loss':
                changed['sources'][SOURCE_ID].update(observed=None, observed_pointer=None)
            elif mode == 'demotion':
                components(changed)[COMPONENT_ID]['state'] = 'unknown'
            else:
                components(changed)['chains-spot']['source'] = SOURCE_ID
            with self.subTest(mode=mode), self.assertRaises((AssertionError, ValueError)):
                recipe.render_crafting_qualification(changed)

    def test_missing_duplicate_or_stale_current_guide_qualification_is_rejected(self):
        from test_wisdom_loadout import current_render_contract
        html = (ROOT / 'index.html').read_text()
        full = recipe.render_crafting_qualification(self.data)
        selected = recipe.load()
        current_render_contract(html, selected)
        mutants = (
            html.replace(full, '', 1),
            html.replace(full, full + full, 1),
            html.replace(full, full.replace('SOURCE-QUALIFIED INPUT', 'UNQUALIFIED INPUT'), 1),
            html.replace(full, full.replace('four Chains recipe magnitudes', 'four Chains certified totals'), 1),
        )
        for mutant in mutants:
            with self.subTest(mutation=mutants.index(mutant)), self.assertRaises(AssertionError):
                current_render_contract(mutant, selected)


if __name__ == '__main__':
    unittest.main()
