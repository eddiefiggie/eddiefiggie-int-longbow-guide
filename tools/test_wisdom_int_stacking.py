"""Actual .6 source/rule contracts, full-result deltas and negative controls.

The current engine is imported normally. Exact historical views are comparison
inputs only; passing this suite does not measure live-game INT, DPS or crits.
"""
import copy
from datetime import datetime
import hashlib
import itertools
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import stacking_audit as audit
import wisdom_int_stacking_preservation as preservation
import wisdom_offense_preservation as offense
from test_lamordia_handling import Document, norm


ROOT = Path(__file__).resolve().parents[1]
LEDGER = 'tools/fixtures/endgame-stacking/ledger.json'
PACKET = 'evidence/wisdom-loadout/int-stacking-sources-2026-11-15.json'
PACKET_SHA = '765a1f9061f8aaa533553569c7496df87ba465faea9893fb331de8c87590905d'
RECORD = 'evidence/wisdom-loadout/int-stacking-integration-2026-11-15.json'
INT_RULE = 'int-selected-ten-pairs'
FORT_RULE = 'fort-enh-insight-observed'
NEW_SOURCE_IDS = {'tip179-live-20261115', 'fort-rule-live-20261115'}
FIVE = ('boots-int', 'glabrezu-insight-int', 'chains-quality-int', 'lunar-int', 'festive-int')
NINE = set(FIVE) | {'solar-int', 'dimlight-int', 'globe-intelligence', 'celestial-profane-intelligence'}
COUNTED = ['boots-int', 'solar-int', 'lunar-int', 'festive-int',
           'dimlight-int', 'glabrezu-insight-int', 'chains-quality-int']
SUPPRESSED = ['celestial-profane-intelligence', 'globe-intelligence']


def component(data, cid):
    return next(row for row in data['components'] if row['id'] == cid)


def rule(data, rid):
    return next(row for row in data['rules'] if row['id'] == rid)


def digest(value):
    return hashlib.sha256(value).hexdigest()


class CurrentScopedIntSourceTests(unittest.TestCase):
    def setUp(self):
        self.data = audit.load()

    def assert_withheld(self, data):
        for active in ((), ('force',), ('force', 'equipped', 'enabled')):
            result = audit.subtotal(data, 'Intelligence', active=active)
            self.assertFalse(result['complete'])
            self.assertIsNone(result['total'])

    def assert_invalid(self, data):
        with self.assertRaises((AssertionError, KeyError, TypeError, ValueError, IndexError)):
            audit.validate(data)

    def test_actual_current_engine_and_exact_new_packet_validate(self):
        self.assertEqual(Path(audit.__file__).resolve(), ROOT / 'tools/stacking_audit.py')
        self.assertTrue(audit.validate(self.data))
        self.assertEqual(digest((ROOT / PACKET).read_bytes()), PACKET_SHA)
        self.assertEqual(len(self.data['sources']), 116)
        self.assertEqual(len(self.data['rules']), 9)
        self.assertEqual(len(self.data['components']), 104)

    def test_observation_windows_are_original_not_new_file_dates(self):
        packet = json.loads((ROOT / PACKET).read_text())
        expected = {
            'loading-screen-tips': ('514316', '2026-11-15T22:48:38.253Z', '2026-11-15T22:48:38.329Z'),
            'fortification': ('723727', '2026-11-15T22:49:28.036Z', '2026-11-15T22:49:28.137Z'),
        }
        for key, (oldid, start, end) in expected.items():
            record = packet['captures'][key]
            self.assertTrue(record['revision_link'].endswith('oldid=' + oldid))
            self.assertEqual(record['body_observation'], {'started_at_utc': start, 'ended_at_utc': end})
            self.assertLess(datetime.fromisoformat(start), datetime.fromisoformat(end))
            self.assertTrue(record['cache_notice'])
        self.assertIn('2022', packet['captures']['loading-screen-tips']['page_modified_display'])
        self.assertIn('not independently reloaded', packet['method']['revision_limit'])
        self.assertIn('Different types of bonuses stack', packet['captures']['loading-screen-tips']['scoped_visible_text'])
        self.assertIn('Benefits from the same family', packet['captures']['stack']['scoped_visible_text'])
        self.assertEqual(len(packet['captures']), 9)

    def test_public_source_derivative_omits_editor_identifiers_without_altering_mechanics(self):
        from test_public_evidence_privacy import validate_public
        packet = json.loads((ROOT / PACKET).read_text())
        validate_public(packet)
        for sid in NEW_SOURCE_IDS:
            validate_public(self.data['sources'][sid])
        redaction = packet['method']['public_redaction']
        self.assertEqual(redaction['original_packet_sha256'],
                         '457b0b2324c5c84383c10d65164cebf9a18b5df4d40bd90c1cfc83dff7508df8')
        self.assertIn('nine page-modification footer suffixes only', redaction['omitted'])
        self.assertIn('mechanics excerpts', redaction['preserved'])
        self.assertTrue(all(' by ' not in row['page_modified_display'] for row in packet['captures'].values()))
        self.assertEqual(rule(self.data, INT_RULE)['quote'], 'Different types of bonuses stack')

    def test_new_sources_bind_exact_contexts_and_keep_old_fort_observation_missing(self):
        for sid, key in (('tip179-live-20261115', 'loading-screen-tips'),
                         ('fort-rule-live-20261115', 'fortification')):
            source = self.data['sources'][sid]
            self.assertEqual((source['path'], source['sha256']), (PACKET, PACKET_SHA))
            self.assertEqual(source['record_pointer'], ['captures', key])
            self.assertEqual(source['pointer'], ['captures', key, 'scoped_visible_text'])
            self.assertEqual(source['observed_pointer'], ['body_observation', 'started_at_utc'])
            self.assertTrue(audit.pinned_source(self.data, sid, audit.SCOPED_SOURCE_SHA256[sid]))
        self.assertIsNone(self.data['sources']['fortification-rule']['observed'])
        self.assertFalse(audit.source_provenance(self.data['sources']['fortification-rule']))
        self.assertEqual(rule(self.data, 'fort-enh-insight')['source'], 'fortification-rule')

    def test_closed_five_member_ten_pair_rule_not_type_wildcard(self):
        current = rule(self.data, INT_RULE)
        self.assertEqual(current['kind'], 'selected_pairs')
        self.assertEqual((current['stats'], current['channel']), (['Intelligence'], 'gear'))
        self.assertEqual(current['types'], ['Enhancement', 'Insight', 'Quality', 'Profane', 'Festive'])
        self.assertEqual(current['component_pairs'], [list(pair) for pair in itertools.combinations(FIVE, 2)])
        self.assertEqual(len(current['component_pairs']), 10)
        self.assertNotIn('*', current['types'] + current['stats'])
        self.assertEqual(set(audit.SELECTED_INT_CORE_SHA256), NINE)

    def test_all_twenty_ordered_selected_pairs_have_only_the_new_int_rule(self):
        count = 0
        for left, right in itertools.permutations(FIVE, 2):
            with self.subTest(left=left, right=right):
                self.assertEqual(audit.proof(self.data, 'Intelligence', component(self.data, left),
                                            component(self.data, right)), INT_RULE)
            count += 1
        self.assertEqual(count, 20)

    def test_same_member_unknown_id_other_stat_and_channel_cannot_use_new_rule(self):
        left, right = component(self.data, FIVE[0]), component(self.data, FIVE[1])
        self.assertIsNone(audit.proof(self.data, 'Intelligence', left, left))
        for stat in ('Wisdom', 'Doubleshot', 'Spot', 'Fortification'):
            self.assertIsNone(audit.proof(self.data, stat, left, right))
        for field, value in (('id', 'other-enhancement-item'), ('channel', 'build'),
                             ('stat', 'Wisdom'), ('bonus_type', 'Artifact')):
            mutant = dict(left, **{field: value})
            with self.subTest(field=field):
                self.assertIsNone(audit.proof(self.data, 'Intelligence', mutant, right))
        unrelated = [dict(row, id='not-selected-' + row['id'], stat='Ranged Power') for row in (left, right)]
        self.assertIsNone(audit.proof(self.data, 'Ranged Power', *unrelated))

    def test_exact_rules_reject_widening_replacement_missing_duplicate_and_renamed_ids(self):
        edits = (
            ('kind', 'different_types'), ('stats', ['*']), ('types', ['*']),
            ('channel', 'build'), ('quote', 'Bonuses of the same type do not stack:'),
            ('source', 'stack'), ('id', 'same-type-best'),
            ('component_pairs', [list(pair) for pair in itertools.combinations(FIVE, 2)][:-1]),
            ('component_pairs', [list(pair) for pair in itertools.combinations(FIVE, 2)] + [['solar-int', 'dimlight-int']]),
        )
        for field, value in edits:
            changed = copy.deepcopy(self.data)
            rule(changed, INT_RULE)[field] = value
            with self.subTest(field=field, value=value):
                self.assert_invalid(changed)
                self.assert_withheld(changed)
        for rid in (INT_RULE, FORT_RULE):
            for operation in ('remove', 'duplicate', 'rename', 'replace-source'):
                changed = copy.deepcopy(self.data)
                row = rule(changed, rid)
                if operation == 'remove':
                    changed['rules'].remove(row)
                elif operation == 'duplicate':
                    changed['rules'].append(copy.deepcopy(row))
                elif operation == 'rename':
                    row['id'] = 'unreviewed-positive-rule'
                else:
                    row['source'] = 'artifact'
                with self.subTest(rule=rid, operation=operation):
                    self.assert_invalid(changed)
                    self.assert_withheld(changed)

    def test_current_result_is_existing_37_not_extra_int_or_character_total(self):
        for active in ((), ('force',)):
            result = audit.subtotal(self.data, 'Intelligence', active=active, level=36)
            self.assertTrue(result['complete'])
            self.assertEqual(result['total'], 37)
            self.assertEqual(result['counted'], COUNTED)
            self.assertEqual(result['suppressed'], SUPPRESSED)
            self.assertEqual(result['excluded'], [])
            self.assertEqual(result['missing_interactions'], [])
            self.assertEqual(len(result['proofs']), 23)
            new_pairs = {frozenset(edge[:2]) for edge in result['proofs'] if edge[2] == INT_RULE}
            self.assertEqual(new_pairs, {frozenset(pair) for pair in itertools.combinations(FIVE, 2)})
            self.assertEqual(sum(component(self.data, cid)['amount'] for cid in result['counted']), 37)

    def test_existing_artifact_exceptional_and_same_type_rules_remain_distinct(self):
        cases = (('solar-int', 'boots-int', 'artifact-other-types'),
                 ('dimlight-int', 'boots-int', 'exceptional-other-types'),
                 ('lunar-int', 'celestial-profane-intelligence', 'same-type-best'),
                 ('dimlight-int', 'globe-intelligence', 'same-type-best'))
        for left, right, expected in cases:
            with self.subTest(pair=(left, right)):
                self.assertEqual(audit.proof(self.data, 'Intelligence', component(self.data, left),
                                            component(self.data, right)), expected)

    def test_level35_never_becomes_a_complete_selected_kit(self):
        for active in ((), ('force',)):
            result = audit.subtotal(self.data, 'Intelligence', active=active, level=35)
            self.assertFalse(result['complete'])
            self.assertIsNone(result['total'])
            self.assertEqual(set(result['excluded']), NINE)
            self.assertEqual(result['counted'], [])

    def test_all_nine_numeric_core_definitions_are_runtime_guarded(self):
        edits = (('amount', 999), ('bonus_type', 'Untyped'), ('stat', 'Wisdom'),
                 ('channel', 'build'), ('host', 'Unselected host'), ('kit_min_level', 35),
                 ('state', 'unknown'), ('state', 'conflicting'), ('state', 'conditional'),
                 ('requires', ['force']))
        for cid in sorted(NINE):
            for field, value in edits:
                changed = copy.deepcopy(self.data)
                component(changed, cid)[field] = value
                with self.subTest(component=cid, field=field, value=value):
                    self.assert_invalid(changed)
                    self.assert_withheld(changed)

    def test_missing_duplicate_renamed_and_extra_family_members_do_not_make_subset_complete(self):
        for cid in sorted(NINE):
            for operation in ('remove', 'duplicate', 'rename'):
                changed = copy.deepcopy(self.data)
                row = component(changed, cid)
                if operation == 'remove':
                    changed['components'].remove(row)
                elif operation == 'duplicate':
                    changed['components'].append(copy.deepcopy(row))
                else:
                    row['id'] = 'replacement-' + cid
                with self.subTest(component=cid, operation=operation):
                    self.assert_invalid(changed)
                    self.assert_withheld(changed)
        changed = copy.deepcopy(self.data)
        changed['components'].append(dict(component(changed, 'solar-int'), id='extra-artifact'))
        self.assert_invalid(changed)
        self.assert_withheld(changed)
        changed = copy.deepcopy(self.data)
        for row in changed['components']:
            if row['id'] in NINE:
                row['id'] = 'replacement-' + row['id']
        self.assert_invalid(changed)
        self.assert_withheld(changed)

    def test_forged_arguments_and_simultaneously_changed_rows_fail_closed(self):
        left, right = component(self.data, 'boots-int'), component(self.data, 'glabrezu-insight-int')
        for field, value in (('amount', 16), ('source', 'solar-int-live-20261115'),
                             ('value_pattern', r'(?P<value>15)'), ('type_evidence', 'Insight')):
            forged = dict(left, **{field: value})
            with self.subTest(field=field):
                self.assertIsNone(audit.proof(self.data, 'Intelligence', forged, right))
                changed = copy.deepcopy(self.data)
                component(changed, 'boots-int')[field] = value
                self.assertIsNone(audit.proof(changed, 'Intelligence', component(changed, 'boots-int'),
                                              component(changed, 'glabrezu-insight-int')))
                self.assert_withheld(changed)

    def test_note_only_editorial_change_does_not_redefine_the_effect(self):
        changed = copy.deepcopy(self.data)
        component(changed, 'boots-int')['note'] += ' Editorial clarification only.'
        self.assertTrue(audit.validate(changed))
        self.assertEqual(audit.subtotal(changed, 'Intelligence'), audit.subtotal(self.data, 'Intelligence'))

    def test_all_eight_direct_int_source_bindings_are_checked_without_validate(self):
        edits = (('quote', '+999 Intelligence'), ('url', 'https://ddowiki.com/page/Wisdom'),
                 ('revision', 'https://ddowiki.com/index.php?title=Ability&oldid=1'),
                 ('observed', '2099-01-01T00:00:00Z'), ('observed_pointer', ['receipt_created']),
                 ('pointer', ['captures', 'missing']), ('record_pointer', []),
                 ('path', '../forged.json'), ('sha256', '0' * 64))
        self.assertEqual(len(audit.SELECTED_INT_SOURCE_SHA256), 8)
        for sid in audit.SELECTED_INT_SOURCE_SHA256:
            for field, value in edits:
                changed = copy.deepcopy(self.data)
                changed['sources'][sid][field] = value
                with self.subTest(source=sid, field=field):
                    self.assert_withheld(changed)
                    self.assertIsNone(audit.proof(changed, 'Intelligence', component(changed, FIVE[0]),
                                                  component(changed, FIVE[1])))

    def test_both_new_source_metadata_bindings_are_pinned_for_direct_entrypoints(self):
        edits = (('quote', 'Different types of bonuses do not stack'),
                 ('revision', 'https://ddowiki.com/index.php?title=Stack&oldid=1'),
                 ('observed', None), ('observed', '2099-01-01T00:00:00Z'),
                 ('path', '../forged.json'), ('sha256', '0' * 64),
                 ('pointer', ['captures', 'stack', 'scoped_visible_text']),
                 ('record_pointer', ['captures', 'stack']),
                 ('url', 'https://ddowiki.com/page/Stack'),
                 ('observed_pointer', ['review_date']))
        for sid in NEW_SOURCE_IDS:
            for field, value in edits:
                changed = copy.deepcopy(self.data)
                changed['sources'][sid][field] = value
                with self.subTest(source=sid, field=field):
                    self.assert_invalid(changed)
                    self.assert_withheld(changed)

    def test_actual_source_bytes_are_reread_and_cannot_be_blessed_by_rehashing(self):
        original_read = Path.read_bytes
        real = original_read(ROOT / PACKET)
        forged = real + b'\n'
        def tampered(path):
            return forged if path == ROOT / PACKET else original_read(path)
        self.assertEqual(audit.subtotal(self.data, 'Intelligence')['total'], 37)
        with patch.object(Path, 'read_bytes', tampered):
            self.assert_invalid(self.data)
            self.assert_withheld(self.data)
            changed = copy.deepcopy(self.data)
            for sid in NEW_SOURCE_IDS:
                changed['sources'][sid]['sha256'] = digest(forged)
            self.assert_invalid(changed)
            self.assert_withheld(changed)
        self.assertEqual(audit.subtotal(self.data, 'Intelligence')['total'], 37)

    def test_real_direct_and_recipe_capture_corruption_cannot_pass_runtime(self):
        paths = {self.data['sources'][sid]['path'] for sid in audit.SELECTED_INT_SOURCE_SHA256}
        paths.add('evidence/wisdom-loadout/recipe-proof-sources-2026-11-15.json')
        paths.add('tools/fixtures/wisdom-loadout/selection.json')
        original_read = Path.read_bytes
        for target in paths:
            def tampered(path):
                raw = original_read(path)
                return raw + b'\n' if path == ROOT / target else raw
            with self.subTest(path=target), patch.object(Path, 'read_bytes', tampered):
                self.assert_withheld(self.data)

    def test_fortification_source_supplies_only_the_relationship(self):
        # Synthetic labels exercise an interaction, not asserted current items.
        left = {'id': 'example-enhancement', 'stat': 'Fortification', 'channel': 'gear', 'bonus_type': 'Enhancement'}
        right = {'id': 'example-insight', 'stat': 'Fortification', 'channel': 'gear', 'bonus_type': 'Insight'}
        self.assertEqual(audit.proof(self.data, 'Fortification', left, right), FORT_RULE)
        self.assertEqual(audit.proof(self.data, 'Fortification', right, left), FORT_RULE)
        self.assertIsNone(audit.proof(self.data, 'Spot', left, right))
        self.assertIsNone(audit.proof(self.data, 'Fortification', left, dict(right, bonus_type='Quality')))
        self.assertIsNone(audit.proof(self.data, 'Fortification', dict(left, channel='build'), dict(right, channel='build')))
        result = audit.subtotal(self.data, 'Fortification', active=('force',))
        self.assertIsNone(result['total'])
        self.assertFalse(result['complete'])
        self.assertEqual(result['excluded'], ['queen-fortification', 'chains-fortification'])

    def test_chains_unknown_types_cannot_be_promoted_from_new_general_rule_or_old_images(self):
        for cid, stat in (('chains-fortification', 'Fortification'), ('chains-spot', 'Spot')):
            row = component(self.data, cid)
            self.assertEqual(row['state'], 'unknown')
            self.assertEqual(row['source'], '')
            self.assertNotIn('recipe_proof', row)
            self.assertIn(cid, audit.subtotal(self.data, stat, active=('force',))['excluded'])
            changed = copy.deepcopy(self.data)
            component(changed, cid).update(state='verified', source='fort-rule-live-20261115')
            self.assert_invalid(changed)
            with self.assertRaises((AssertionError, KeyError)):
                audit.subtotal(changed, stat)

    def test_historical_images_and_release_note_limits_are_explicit(self):
        packet = json.loads((ROOT / PACKET).read_text())
        images = packet['historical_images']
        self.assertEqual([(row['minimum_level'], row['spot_visual_transcription']) for row in images],
                         [(8, 'Spot +10: +10 Competence bonus to Spot.'),
                          (28, 'Spot +22: +22 Competence bonus to Spot.')])
        self.assertTrue(all(row['page_displayed_date'] == 'August 19 2016' for row in images))
        self.assertTrue(all(not row['current_component_qualified'] and not row['fortification_visible'] for row in images))
        findings = packet['historical_corroboration']
        self.assertEqual(findings[0]['release_date'], '2016-09-13')
        self.assertIn('plausible but unverified', findings[0]['finding'])
        self.assertIn('did not explicitly guarantee', findings[1]['finding'])


class CurrentScopedIntDeltaTests(unittest.TestCase):
    def setUp(self):
        self.data = audit.load()
        self.previous = json.loads(preservation.checkpoint_file_text(LEDGER))
        self.old = preservation.historical_calculator()

    def test_two_rule_profiles_are_valid_and_old_metadata_and_numeric_tuples_are_literal(self):
        self.assertTrue(audit.validate(self.previous))
        self.assertTrue(audit.validate(self.data))
        self.assertEqual(self.data['rules'][:7], self.previous['rules'])
        self.assertEqual({r['id'] for r in self.data['rules'][7:]}, {INT_RULE, FORT_RULE})
        self.assertEqual(set(self.data['sources']) - set(self.previous['sources']), NEW_SOURCE_IDS)
        for sid, source in self.previous['sources'].items():
            self.assertEqual(self.data['sources'][sid], source)
        old_rows = {row['id']: row for row in self.previous['components']}
        for row in self.data['components']:
            self.assertEqual({k: v for k, v in row.items() if k != 'note'},
                             {k: v for k, v in old_rows[row['id']].items() if k != 'note'})
        for key in ('non_total_effects', 'selection_record', 'selection_sha256', 'selection_base_commit'):
            self.assertEqual(self.data[key], self.previous[key])

    def test_actual_engine_preserves_every_old_complete_result_at_both_levels(self):
        families = sorted({(row['stat'], row['channel']) for row in self.previous['components']})
        self.assertEqual(len(families), 38)
        totals = {}
        for level in (35, 36):
            records = []
            for stat, channel in families:
                for active in ((), ('force',)):
                    before = self.old.subtotal(self.previous, stat, channel=channel, active=active, level=level)
                    after = audit.subtotal(self.previous, stat, channel=channel, active=active, level=level)
                    self.assertEqual(after, before)
                    records.append({'stat': stat, 'channel': channel, 'active': active, 'result': after})
            self.assertEqual(len(records), 76)
            totals[level] = digest(json.dumps(records, sort_keys=True, separators=(',', ':')).encode())
        self.assertEqual(totals, {
            35: '0d60701f94ebf9e064e7c594be45c3afa44d27c40a71b8076c514cc4845913e8',
            36: 'fe3ce7df6aae2ac225c1715af8afe18a01c4c7555e6937dd85982065817414ef',
        })

    def test_current_input_changes_exactly_two_level36_int_results_and_no_level35_result(self):
        families = sorted({(row['stat'], row['channel']) for row in self.previous['components']})
        for level in (35, 36):
            changed = []
            for stat, channel in families:
                for active in ((), ('force',)):
                    before = audit.subtotal(self.previous, stat, channel=channel, active=active, level=level)
                    after = audit.subtotal(self.data, stat, channel=channel, active=active, level=level)
                    if after != before:
                        changed.append((stat, channel, active))
                        self.assertEqual(after['total'], 37)
                        self.assertEqual(len(before['missing_interactions']), 10)
                        for key in ('counted', 'suppressed', 'excluded'):
                            self.assertEqual(after[key], before[key])
                        self.assertEqual([edge for edge in after['proofs'] if edge[2] != INT_RULE], before['proofs'])
            self.assertEqual(changed, [] if level == 35 else [('Intelligence', 'gear', ()), ('Intelligence', 'gear', ('force',))])

    def test_selected_recipe_priorities_exceptions_and_model_files_are_unchanged(self):
        for path in ('tools/fixtures/wisdom-loadout/selection.json',
                     'evidence/wisdom-loadout/claims.json', 'evidence/wisdom-loadout/loadout.json',
                     'evidence/wisdom-loadout/production.json', 'tools/recipe_proofs.py', 'tools/bowmodel.py'):
            self.assertEqual(preservation.checkpoint_file_bytes(path), (ROOT / path).read_bytes())
        self.assertEqual(digest((ROOT / 'tools/fixtures/wisdom-loadout/selection.json').read_bytes()),
                         '8223bd8e25ed9dc4ad9454439ead42dfb693cc008d18d0ddfeb270d33863c37d')


class CurrentScopedIntPresentationTests(unittest.TestCase):
    def test_onepage_distinguishes_derived_int_from_other_modeled_values(self):
        from wisdom_loadout import load, render_onepage_rows
        text = norm(Document('<table>' + render_onepage_rows(load()) + '</table>').root.text())
        self.assertIn('Model-only gear WIS 18 / DEX 6 / CON 32 / direct Spot 27.', text)
        self.assertIn('Derived selected-gear INT +37 at level 36', text)
        self.assertNotIn('DEX 6 / INT 37', text)
        changed = audit.load()
        component(changed, 'solar-int')['amount'] = 999
        with patch('stacking_audit.load', return_value=changed), self.assertRaises(ValueError):
            render_onepage_rows(load())

    def test_live_renderers_expose_derived_int_and_preserve_remaining_limits(self):
        from build_stacking_audit import detail, summary
        from wisdom_loadout import render_crafting_qualification
        data = audit.load()
        for html in (summary(data), detail(data), render_crafting_qualification(data)):
            text = norm(Document(html).root.text())
            self.assertIn('Derived selected-gear INT: +37 at level 36.', text)
            self.assertIn('exactly the ten pairs', text)
            self.assertIn('Chains Fortification and Spot remain excluded.', text)
            self.assertIn('not additional INT', text)
            self.assertIn('DPS/critical-range result', text)
            self.assertNotIn('The combined Intelligence total is still withheld', text)
        audit_text = norm(Document(detail(data)).root.text())
        self.assertIn('exactly these ten selected gear-INT pairs', audit_text)
        self.assertIn('Tip 179 was last modified in 2022', audit_text)
        self.assertIn('old Fortification record', audit_text)

    def test_point_six_generated_outputs_and_path_rebased_snapshot_match(self):
        from build_snapshot import snapshot_html
        renderer = offense.historical_audit_renderer()
        recipe = offense.historical_recipe_renderer()
        current = offense.checkpoint_file_text('index.html')
        self.assertTrue(renderer.validate_guide(current, audit.load()))
        self.assertIn(recipe.render_recipe(recipe.load()), current)
        self.assertEqual(offense.checkpoint_file_text('endgame-stacking-audit.html'), renderer.detail(audit.load()))
        self.assertEqual((ROOT / 'versions/11-15-26.6.html').read_text(), snapshot_html(current))
        excerpts = json.loads((ROOT / 'evidence/endgame-stacking/source-excerpts.json').read_text())
        self.assertEqual(excerpts['sources'], audit.load()['sources'])
        self.assertEqual(excerpts['source_roles'], audit.load()['source_roles'])

    def test_integration_record_is_scoped_draft_work_not_release_or_dps_certification(self):
        record = json.loads((ROOT / RECORD).read_text())
        self.assertEqual(record['baseline']['remote_head'], preservation.BASE_COMMIT)
        self.assertEqual(record['baseline']['remote_tree'], preservation.BASE_TREE)
        self.assertEqual(record['build'], '11-15-26.6')
        self.assertEqual(record['new_rule_ids'], [INT_RULE, FORT_RULE])
        self.assertEqual(record['result']['intelligence']['total'], 37)
        self.assertEqual(record['result']['level36_changed_results'], 2)
        self.assertEqual(record['result']['level35_changed_results'], 0)
        for key in ('new_optimizer_solve', 'gear_changed', 'priorities_changed', 'merged', 'published', 'live_game_test'):
            self.assertFalse(record['scope'][key])
        self.assertEqual(record['remaining_excluded']['Fortification'], ['queen-fortification', 'chains-fortification'])
        self.assertEqual(record['remaining_excluded']['Spot'], ['chains-spot', 'heroism-spot', 'luck-spot'])


if __name__ == '__main__':
    unittest.main()
