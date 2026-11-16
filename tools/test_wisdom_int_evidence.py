"""Historical .5 direct-source qualification and unchanged-calculator boundaries.

The strict outer .6-to-.5 view supplies this historical ledger and its own
renderers. The unchanged .4 contract remains the earlier comparison. These
checks preserve the original .5 claims; actual .6 acceptance and direct-source
negative controls must run separately on real production modules. Neither
historical rendering nor source contracts certify live DDO behavior or DPS.
"""
import copy
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
import unittest
from urllib.parse import parse_qs, urlparse

import wisdom_int_stacking_preservation as int_stacking
import wisdom_int_evidence_preservation as preservation
from test_lamordia_handling import Document, norm


ROOT = Path(__file__).resolve().parents[1]
LEDGER = 'tools/fixtures/endgame-stacking/ledger.json'
PACKET = 'evidence/wisdom-loadout/int-evidence-sources-2026-11-15.json'
PACKET_SHA = '0cdf2530b114dce4f99ad818da0d905752150768940bcc1112f2187b550b71a2'
RECORD = 'evidence/wisdom-loadout/int-evidence-integration-2026-11-15.json'
SOURCE_ROLE = 'current selected INT definition; source-qualified in build 11-15-26.5'
BINDINGS = {
    'boots-int': ('melancholic-int-live-20261115', 'melancholic-int', '702267'),
    'solar-int': ('solar-int-live-20261115', 'solar-int', '700860'),
    'lunar-int': ('lunar-int-live-20261115', 'lunar-int', '691752'),
    'festive-int': ('festive-int-live-20261115', 'festive-int', '720823'),
    'dimlight-int': ('dimlight-int-live-20261115', 'dimlight', '702294'),
    'globe-intelligence': ('globe-int-live-20261115', 'globe', '643056'),
    'celestial-profane-intelligence': ('celestial-profane-int-live-20261115', 'celestial-host', '631921'),
}
PROMOTED = tuple(BINDINGS)
NOTE_ONLY = {'chains-quality-int', 'chains-spot'}
WITHHELD = ('chains-fortification', 'chains-spot')
IMMUTABLE = {
    'tools/stacking_audit.py': 'cd87217a2a49435f2caf2e84c9fa785a6d5462f43d829dca0212103861279d98',
    'tools/recipe_proofs.py': 'b4c2b4fd95a0a9de4b5f8155245ba8934a8f1ae89c3e2f1d7e8eac545bb627ec',
    'tools/fixtures/wisdom-loadout/selection.json': '8223bd8e25ed9dc4ad9454439ead42dfb693cc008d18d0ddfeb270d33863c37d',
}
EXPECTED_INT = {
    'stat': 'Intelligence', 'channel': 'gear', 'total': None,
    'counted': ['boots-int', 'solar-int', 'lunar-int', 'festive-int',
                'dimlight-int', 'glabrezu-insight-int', 'chains-quality-int'],
    'suppressed': ['celestial-profane-intelligence', 'globe-intelligence'],
    'excluded': [],
    'missing_interactions': [
        ['boots-int', 'lunar-int'], ['boots-int', 'festive-int'],
        ['boots-int', 'glabrezu-insight-int'], ['boots-int', 'chains-quality-int'],
        ['lunar-int', 'festive-int'], ['lunar-int', 'glabrezu-insight-int'],
        ['lunar-int', 'chains-quality-int'], ['festive-int', 'glabrezu-insight-int'],
        ['festive-int', 'chains-quality-int'], ['glabrezu-insight-int', 'chains-quality-int'],
    ],
    'proofs': [
        ['lunar-int', 'celestial-profane-intelligence', 'same-type-best'],
        ['dimlight-int', 'globe-intelligence', 'same-type-best'],
        ['boots-int', 'solar-int', 'artifact-other-types'],
        ['boots-int', 'dimlight-int', 'exceptional-other-types'],
        ['solar-int', 'lunar-int', 'artifact-other-types'],
        ['solar-int', 'festive-int', 'artifact-other-types'],
        ['solar-int', 'dimlight-int', 'artifact-other-types'],
        ['solar-int', 'glabrezu-insight-int', 'artifact-other-types'],
        ['solar-int', 'chains-quality-int', 'artifact-other-types'],
        ['lunar-int', 'dimlight-int', 'exceptional-other-types'],
        ['festive-int', 'dimlight-int', 'exceptional-other-types'],
        ['dimlight-int', 'glabrezu-insight-int', 'exceptional-other-types'],
        ['dimlight-int', 'chains-quality-int', 'exceptional-other-types'],
    ],
    'complete': False,
}


def components(data):
    return {row['id']: row for row in data['components']}


def current_scope_contract(current, previous):
    """Permit only this approved qualification, not arbitrary host reassignment.

The generic engine binds direct numeric/type/stat clauses but does not establish
an arbitrary caller's ownership, crafting, host selection or level. Those fixed
loadout boundaries therefore have their own explicit regression contract.
"""
    assert set(current) == set(previous)
    edited = {'sources', 'source_roles', 'components', 'unresolved'}
    for key in set(current) - edited:
        assert current[key] == previous[key], key
    new_ids = {binding[0] for binding in BINDINGS.values()}
    assert not new_ids & set(previous['sources'])
    assert set(current['sources']) == set(previous['sources']) | new_ids
    for sid, source in previous['sources'].items():
        assert current['sources'][sid] == source, sid
    assert current['source_roles'] == {
        **previous['source_roles'], **{sid: SOURCE_ROLE for sid in new_ids}}
    assert [row['id'] for row in current['components']] == [row['id'] for row in previous['components']]
    for row, old in zip(current['components'], previous['components']):
        cid = row['id']
        assert set(row) == set(old), cid
        allowed = ({'state', 'source', 'value_pattern', 'type_evidence', 'note'}
                   if cid in PROMOTED else {'note'} if cid in NOTE_ONLY else set())
        assert {k: v for k, v in row.items() if k not in allowed} == {
            k: v for k, v in old.items() if k not in allowed}, cid
        if allowed:
            assert row['note'] and row['note'] != old['note'], cid
        if cid in PROMOTED:
            assert old['state'] == 'unknown' and row['state'] == 'verified', cid
            assert row['source'] == BINDINGS[cid][0], cid
            assert row['value_pattern'] and row['type_evidence'], cid
    assert len(current['unresolved']) == len(previous['unresolved'])
    for row, old in zip(current['unresolved'], previous['unresolved']):
        assert set(row) == set(old)
        if row['id'] == 'provenance-gaps':
            assert {k: v for k, v in row.items() if k != 'detail'} == {
                k: v for k, v in old.items() if k != 'detail'}
            assert row['detail'] and row['detail'] != old['detail']
        else:
            assert row == old
    int_stacking.historical_calculator().validate(current)
    return True


def historical_spot_contract(packet):
    """The dated Slavers example may corroborate, never silently qualify."""
    row = packet['historical_spot_example']
    assert row['source_url'] == 'https://imgur.com/vrK75CU'
    assert row['linked_from'] == 'https://ddowiki.com/page/Slave_Lords_Crafting'
    assert row['link_href'] == 'http://i.imgur.com/vrK75CU.png'
    assert row['page_displayed_date'] == 'August 19 2016'
    assert row['item_identity_visible_text'] == 'Legendary Five Rings'
    assert row['minimum_level_visible_text'] == 'Minimum Level: 28'
    assert row['effect_visual_transcription'] == 'Spot +22: +22 Competence bonus to Spot.'
    assert row['other_observed_values'] == {'intelligence_enhancement': 17, 'intelligence_quality': 4}
    assert row['current_component_qualified'] is False
    assert 'not direct current +20 Chains proof' in row['assessment']
    assert 'continuity premise' in row['assessment']
    assert 'No Fortification effect is shown.' in row['assessment']
    assert 'not claimed to be the exact in-game capture date' in row['method']
    assert 'no local image archive' in row['method']
    return True


class HistoricalIntEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous = json.loads(preservation.checkpoint_file_text(LEDGER))

    def setUp(self):
        self.audit = int_stacking.historical_calculator()
        self.recipe = int_stacking.historical_recipe_renderer()
        self.page = int_stacking.historical_audit_renderer()
        self.data = self.audit.load()

    def test_scope_qualifies_exactly_seven_inputs_without_new_rules_or_model_changes(self):
        self.assertTrue(current_scope_contract(self.data, self.previous))
        self.assertEqual(len(self.data['components']), 104)
        self.assertEqual(len(self.data['rules']), 7)
        self.assertEqual(self.data['rules'], self.previous['rules'])
        self.assertEqual(self.data['non_total_effects'], self.previous['non_total_effects'])

    def test_calculator_recipe_engine_and_selection_are_byte_identical(self):
        for path, digest in IMMUTABLE.items():
            with self.subTest(path=path):
                self.assertEqual(sha256(int_stacking.checkpoint_file_bytes(path)).hexdigest(), digest)

    def test_seven_bindings_resolve_to_separate_genuine_source_records(self):
        raw = (ROOT / PACKET).read_bytes()
        packet = json.loads(raw)
        digest = sha256(raw).hexdigest()
        self.assertEqual(digest, PACKET_SHA)
        rows = components(self.data)
        for cid, (sid, capture, oldid) in BINDINGS.items():
            with self.subTest(component=cid):
                source = self.data['sources'][sid]
                record = packet['captures'][capture]
                field = ('profane_tooltip_html' if cid == 'celestial-profane-intelligence'
                         else 'effect_visible_text')
                self.assertEqual(source['path'], PACKET)
                self.assertEqual(source['sha256'], digest)
                self.assertEqual(source['record_pointer'], ['captures', capture])
                self.assertEqual(source['pointer'], ['captures', capture, field])
                if cid == 'celestial-profane-intelligence':
                    self.assertEqual(source['quote'],
                                     '+2 <a href="/page/Profane_bonus" title="Profane bonus">'
                                     'Profane bonus</a> to all abilities.')
                    self.assertIn(source['quote'], record[field])
                else:
                    self.assertEqual(source['quote'], record[field])
                self.assertEqual(source['url'], record['source_url'])
                self.assertEqual(source['url_key'], 'source_url')
                self.assertEqual(source['revision'], record['revision_link'])
                self.assertEqual(source['revision_pointer'], ['revision_link'])
                self.assertEqual(parse_qs(urlparse(source['revision']).query)['oldid'], [oldid])
                self.assertEqual(source['observed'], record['body_observation']['started_at_utc'])
                self.assertEqual(source['observed_pointer'], ['body_observation', 'started_at_utc'])
                start = datetime.fromisoformat(record['body_observation']['started_at_utc'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(record['body_observation']['ended_at_utc'].replace('Z', '+00:00'))
                self.assertLessEqual(start, end)
                self.assertEqual(start.date().isoformat(), '2026-11-15')
                self.assertTrue(self.audit.source_provenance(source))
                match = re.search(rows[cid]['value_pattern'], source['quote'])
                self.assertIsNotNone(match)
                self.assertEqual(float(match.group('value')), rows[cid]['amount'])
                self.assertIn(rows[cid]['type_evidence'], source['quote'])

    def test_packet_records_observation_and_revision_limits_without_repairing_old_captures(self):
        packet = json.loads((ROOT / PACKET).read_text())
        self.assertEqual(packet['schema_version'], 1)
        self.assertEqual(packet['record_type'], 'scoped-browser-source-observations')
        self.assertIn('not individual page-load timestamps', packet['method']['observation_clock'])
        self.assertIn('does not repair older source packets', packet['method']['retention'])
        self.assertIn('Historical revision endpoints were not independently reloaded',
                      packet['method']['revision_limit'])
        self.assertIn('community-maintained secondary source', packet['method']['source_authority'])
        self.assertEqual(packet['captures']['celestial-host']['cache_notice'], '(this is up to -4 hours old)')
        self.assertIn('not interpreted as a freshness guarantee',
                      packet['captures']['celestial-host']['scope_limit'])
        self.assertTrue(historical_spot_contract(packet))

    def test_historical_spot_example_cannot_be_relabelled_as_current_chains_proof(self):
        for field, value in [('current_component_qualified', True),
                             ('item_identity_visible_text', 'Legendary Chains'),
                             ('page_displayed_date', 'November 15 2026'),
                             ('effect_visual_transcription', 'Spot +20: +20 Competence bonus to Spot.'),
                             ('assessment', 'Direct current Chains proof')]:
            changed = json.loads((ROOT / PACKET).read_text())
            changed['historical_spot_example'][field] = value
            with self.subTest(field=field), self.assertRaises(AssertionError):
                historical_spot_contract(changed)

    def test_source_levels_slot_families_and_selected_physical_placements_are_distinct(self):
        packet = json.loads((ROOT / PACKET).read_text())
        captures = packet['captures']
        selection = self.recipe.load()
        items = {row['id']: row for row in selection['items']}
        # Augment ML is not the whole-kit applicability floor. Named families
        # remain exact; in particular, Dimlight is a Weapon, not an Accessory.
        for key, level, family in [('melancholic-int', 34, 'Lamordia: Melancholic (Accessory)'),
                                   ('dimlight', 34, 'Lamordia: Miserable (Weapon)'),
                                   ('globe', 25, 'Colorless'), ('solar-int', 30, 'Sun'),
                                   ('lunar-int', 30, 'Moon'), ('festive-int', 22, 'Colorless')]:
            header = norm(captures[key]['item_header_visible_text'])
            with self.subTest(capture=key):
                self.assertRegex(header, r'Minimum Level\s+' + str(level) + r'\b')
                self.assertIn('Augment Type ' + family, header)
        for key, slot in [('coldlight-host', 'Lamordia: Melancholic Slot (Accessory)'),
                           ('calamitous-host', 'Lamordia: Miserable Slot (Weapon)'),
                           ('calamitous-host', 'Purple Augment Slot'), ('compass-host', 'Sun Augment Slot'),
                           ('glabrezu-host', 'Moon Augment Slot'), ('unnatural-host', 'Green Augment Slot')]:
            self.assertIn(slot, norm(captures[key]['slots_visible_text']))
        for item, slot, category, name in [
                ('Legendary Coldlight Runners', 'Melancholic', 'Accessory', 'Melancholic Intelligence (legendary)'),
                ('Legendary Calamitous Longbow', 'Miserable', 'Weapon', 'Miserable Dimlight (legendary)')]:
            craft = next(row for row in items[item]['crafts'] if row['slot'] == slot)
            self.assertEqual((craft['category'], craft['tier'], craft['name']), (category, 'legendary', name))
        for item, color, name in [
                ('Legendary Calamitous Longbow', 'Purple', 'Globe of True Imperial Blood'),
                ('Legendary Abyssal Compass', 'Sun', 'Solar Gem of Intelligence (Legendary)'),
                ('Legendary Glabrezu Claw Pendant', 'Moon', 'Lunar Gem of Intelligence (Legendary)'),
                ('Legendary Ring of Unnatural Accuracy', 'Green', 'Diamond of Festive Intelligence +2')]:
            slot = next(row for row in items[item]['sockets'] if row['color'] == color)
            self.assertEqual(slot['fill']['id'], name)
        rules = captures['augment-slots']
        self.assertEqual(rules['compatibility_headers_visible_text'].split('\t')[7], 'Colorless Augment')
        self.assertEqual({norm(row.split('\t')[0]): row.split('\t')[7]
                          for row in rules['selected_rows_visible_text']},
                         {'Purple Augment Slot': '✔', 'Green Augment Slot': '✔'})
        self.assertIn('not transferred automatically to special Slavers', rules['scope_limit'])
        self.assertIn('Nearly Finished remains deliberately empty', captures['celestial-host']['scope_limit'])

    def test_all_76_level36_results_match_the_complete_approved_delta(self):
        pairs = sorted({(row['stat'], row['channel']) for row in self.data['components']})
        self.assertEqual(len(pairs), 38)
        changed, unchanged = [], 0
        for stat, channel in pairs:
            for active in ((), ('force',)):
                before = self.audit.subtotal(self.previous, stat, channel=channel, active=active)
                after = self.audit.subtotal(self.data, stat, channel=channel, active=active)
                expected = EXPECTED_INT if (stat, channel) == ('Intelligence', 'gear') else before
                with self.subTest(stat=stat, channel=channel, active=active):
                    self.assertEqual(after, expected)
                if before == after:
                    unchanged += 1
                else:
                    changed.append((stat, channel, active))
        self.assertEqual(changed, [('Intelligence', 'gear', ()), ('Intelligence', 'gear', ('force',))])
        self.assertEqual(unchanged, 74)

    def test_all_76_level35_results_stay_identical_and_full_kit_floor_stays_36(self):
        count = 0
        for stat, channel in sorted({(c['stat'], c['channel']) for c in self.data['components']}):
            for active in ((), ('force',)):
                self.assertEqual(self.audit.subtotal(self.data, stat, channel=channel, active=active, level=35),
                                 self.audit.subtotal(self.previous, stat, channel=channel, active=active, level=35))
                count += 1
        self.assertEqual(count, 76)
        chosen = self.recipe.load()
        self.assertEqual(chosen['selection']['full_kit_ml'], 36)
        self.assertEqual([i['id'] for i in chosen['items'] if i['minor_artifact']], ["Yeenoghu's Reign"])
        self.assertFalse(chosen['optional']['ring_dexterity_13']['selected'])

    def test_no_incomplete_int_result_becomes_a_certified_37_total(self):
        result = self.audit.subtotal(self.data, 'Intelligence')
        self.assertEqual(result, EXPECTED_INT)
        self.assertEqual(len(result['missing_interactions']), 10)
        self.assertIsNone(result['total'])
        self.assertFalse(result['complete'])
        rows = components(self.data)
        self.assertEqual(sum(rows[cid]['amount'] for cid in result['counted']), 37)
        # This sum is explicitly model arithmetic, not a new proof edge.
        self.assertIsNone(self.audit.proof(self.data, 'Intelligence', rows['boots-int'], rows['lunar-int']))

    def test_same_type_overlaps_are_suppressed_without_transitive_stacking(self):
        result = self.audit.subtotal(self.data, 'Intelligence')
        self.assertEqual(result['suppressed'], ['celestial-profane-intelligence', 'globe-intelligence'])
        rows = components(self.data)
        for winner, loser in [('lunar-int', 'celestial-profane-intelligence'),
                              ('dimlight-int', 'globe-intelligence')]:
            self.assertEqual(self.audit.proof(self.data, 'Intelligence', rows[winner], rows[loser]), 'same-type-best')
        changed = copy.deepcopy(self.data)
        changed['rules'] = [r for r in changed['rules'] if r['id'] != 'same-type-best']
        without_rule = self.audit.subtotal(changed, 'Intelligence')
        self.assertEqual(without_rule['suppressed'], [])
        self.assertEqual(len(without_rule['missing_interactions']), 12)
        self.assertIsNone(without_rule['total'])

    def test_other_globe_and_celestial_stats_are_not_implicitly_promoted(self):
        old = components(self.previous)
        for row in self.data['components']:
            if row['id'].startswith(('globe-', 'celestial-')) and row['id'] not in PROMOTED:
                with self.subTest(component=row['id']):
                    self.assertEqual(row, old[row['id']])
                    self.assertEqual(row['state'], 'unknown')
                    self.assertIn(row['id'], self.audit.subtotal(self.data, row['stat'])['excluded'])

    def test_missing_revision_or_observation_excludes_each_promoted_input(self):
        for cid, (sid, _, _) in BINDINGS.items():
            for field, pointer in [('observed', 'observed_pointer'), ('revision', 'revision_pointer')]:
                changed = copy.deepcopy(self.data)
                changed['sources'][sid][field] = None
                changed['sources'][sid][pointer] = None
                with self.subTest(component=cid, missing=field):
                    with self.assertRaises(AssertionError):
                        self.audit.validate(changed)
                    self.assertIn(cid, self.audit.subtotal(changed, 'Intelligence')['excluded'])

    def test_source_identity_context_quote_hash_and_nonnull_metadata_are_checked(self):
        mutations = [
            ('url', 'https://ddowiki.com/page/Fortification'),
            ('revision', 'https://ddowiki.com/index.php?title=Intelligence&oldid=1'),
            ('observed', '2099-01-01T00:00:00Z'),
            ('pointer', ['captures', 'missing', 'effect_visible_text']),
            ('record_pointer', ['captures', 'missing']),
            ('quote', '+999 Artifact Bonus to Intelligence'),
            ('sha256', '0' * 64),
        ]
        # Exercise all seven real sources; do not substitute fabricated fixtures.
        for cid, (sid, _, _) in BINDINGS.items():
            for field, value in mutations:
                changed = copy.deepcopy(self.data)
                changed['sources'][sid][field] = value
                with self.subTest(component=cid, field=field), self.assertRaises((AssertionError, KeyError)):
                    self.audit.validate(changed)

    def test_direct_numeric_type_stat_and_channel_mutations_are_rejected(self):
        for cid in PROMOTED:
            row = components(self.data)[cid]
            for field, value in [('amount', row['amount'] + 1), ('bonus_type', 'Untyped'),
                                 ('stat', 'Ranged Power'), ('channel', 'build')]:
                changed = copy.deepcopy(self.data)
                components(changed)[cid][field] = value
                with self.subTest(component=cid, field=field), self.assertRaises(AssertionError):
                    self.audit.validate(changed)

    def test_direct_clause_assertions_cannot_replace_the_observed_clause(self):
        for cid in PROMOTED:
            for field, value in [('value_pattern', r'(?P<value>999)'),
                                 ('type_evidence', 'Invented typed Intelligence claim')]:
                changed = copy.deepcopy(self.data)
                components(changed)[cid][field] = value
                with self.subTest(component=cid, field=field), self.assertRaises(AssertionError):
                    self.audit.validate(changed)

    def test_selected_scope_rejects_host_level_condition_and_qualification_drift(self):
        # Host/selection preservation is a scoped integration contract, not a
        # claim that generic direct-source validation proves item applicability.
        for cid in PROMOTED:
            for field, value in [('host', 'An unselected host'), ('kit_min_level', 25),
                                 ('requires', ['force']), ('state', 'unknown')]:
                changed = copy.deepcopy(self.data)
                components(changed)[cid][field] = value
                with self.subTest(component=cid, field=field), self.assertRaises(AssertionError):
                    current_scope_contract(changed, self.previous)

    def test_selected_scope_rejects_old_source_regrading_and_out_of_scope_edits(self):
        mutations = [
            lambda d: d['sources']['globe'].update(observed='2026-11-15T22:19:27Z'),
            lambda d: d['rules'][0].update(types=['Exceptional']),
            lambda d: components(d)['globe-constitution'].update(state='verified'),
            lambda d: components(d)['chains-combustion'].update(amount=143),
            lambda d: d['non_total_effects'][0].update(note='Unapproved change'),
        ]
        for index, mutate in enumerate(mutations):
            changed = copy.deepcopy(self.data)
            mutate(changed)
            with self.subTest(mutation=index), self.assertRaises(AssertionError):
                current_scope_contract(changed, self.previous)

    def test_chains_types_remain_unqualified_without_direct_source_fallback(self):
        for cid in WITHHELD:
            row = components(self.data)[cid]
            self.assertEqual((row['state'], row['source'], row['value_pattern'], row['type_evidence']),
                             ('unknown', '', '', ''))
            self.assertNotIn('recipe_proof', row)
            self.assertIn(cid, self.audit.subtotal(self.data, row['stat'])['excluded'])
            changed = copy.deepcopy(self.data)
            components(changed)[cid].update(state='verified', source=BINDINGS['boots-int'][0])
            with self.subTest(component=cid):
                with self.assertRaises(AssertionError):
                    self.audit.validate(changed)
                with self.assertRaises(AssertionError):
                    self.audit.subtotal(changed, row['stat'])

    def test_fortification_and_spot_totals_keep_all_prior_gaps(self):
        for stat, excluded in [('Fortification', ['queen-fortification', 'chains-fortification']),
                               ('Spot', ['chains-spot', 'heroism-spot', 'luck-spot'])]:
            result = self.audit.subtotal(self.data, stat)
            self.assertEqual(result, self.audit.subtotal(self.previous, stat))
            self.assertEqual(result['excluded'], excluded)
            self.assertEqual(result['counted'], [])
            self.assertIsNone(result['total'])
            self.assertFalse(result['complete'])
        self.assertFalse(self.audit.source_provenance(self.data['sources']['fortification-rule']))

    def test_point_five_generated_outputs_use_its_exact_source_qualifications(self):
        html = int_stacking.checkpoint_file_text('index.html')
        full = self.recipe.render_crafting_qualification(self.data)
        compact = self.recipe.render_crafting_qualification(self.data, compact=True)
        self.assertIn(full, html)
        self.assertEqual(html.count(compact), 2)
        self.assertIn('build 11-15-26.5', html)
        self.assertNotIn('seven other inputs', full)
        self.assertNotIn('seven other inputs', self.page.summary(self.data))
        self.assertTrue(self.page.validate_guide(html, self.data))
        self.assertEqual(int_stacking.checkpoint_file_text('endgame-stacking-audit.html'), self.page.detail(self.data))
        excerpts = json.loads(int_stacking.checkpoint_file_text('evidence/endgame-stacking/source-excerpts.json'))
        self.assertEqual(excerpts['sources'], self.data['sources'])
        self.assertEqual(excerpts['source_roles'], self.data['source_roles'])

    def test_each_promoted_audit_row_links_its_new_direct_source(self):
        document = Document(self.page.detail(self.data))
        for cid, (sid, _, _) in BINDINGS.items():
            rows = [n for n in document.root.nodes('tr') if n.attrs.get('id') == 'component-' + cid]
            with self.subTest(component=cid):
                self.assertEqual(len(rows), 1)
                label = ('suppressed by same-type maximum' if cid in EXPECTED_INT['suppressed']
                         else 'verified')
                self.assertIn(label, norm(rows[0].text()))
                self.assertNotIn('source missing', norm(rows[0].text()))
                self.assertEqual([n.attrs['href'] for n in rows[0].nodes('a')], ['#source-' + sid])

    def test_point_five_renderer_rejects_withdrawn_or_unsupported_qualification(self):
        for cid in PROMOTED:
            changed = copy.deepcopy(self.data)
            components(changed)[cid]['state'] = 'unknown'
            with self.subTest(component=cid), self.assertRaisesRegex(ValueError, 'seven-INT qualification'):
                self.recipe.render_crafting_qualification(changed)
        for cid in WITHHELD:
            changed = copy.deepcopy(self.data)
            components(changed)[cid]['state'] = 'verified'
            with self.subTest(component=cid), self.assertRaises(AssertionError):
                self.recipe.render_crafting_qualification(changed)

    def test_integration_receipt_does_not_claim_a_new_engine_or_release(self):
        record = json.loads((ROOT / RECORD).read_text())
        self.assertEqual(record['schema_version'], 1)
        self.assertEqual(record['record_type'], 'seven-int-direct-source-integration')
        self.assertEqual(record['build'], '11-15-26.5')
        self.assertEqual(record['baseline']['remote_head'], 'd05e7865da76a47a92741cb79029a35fbd0f7712')
        self.assertEqual(record['baseline']['remote_and_initial_staged_tree'], 'c1b236d5cafc7695af9ec77410d329c7a0b9cc44')
        self.assertEqual(record['scope']['promoted_component_ids'], list(PROMOTED))
        self.assertEqual(record['scope']['unqualified_component_ids'], list(WITHHELD))
        for field in ('existing_rules_changed', 'calculator_code_changed', 'recipe_proof_engine_changed',
                      'selected_recipe_changed', 'priorities_changed', 'numeric_core_tuples_changed',
                      'historical_claim_inventory_regraded', 'old_capture_metadata_repaired',
                      'new_optimizer_run', 'new_event_or_acquisition_exception', 'crafting_or_purchase',
                      'live_game_test', 'merge_or_publication'):
            self.assertFalse(record['scope'][field], field)
        self.assertEqual(record['result_delta']['changed_level36_records'], 2)
        self.assertEqual(record['result_delta']['unchanged_level36_records'], 74)
        self.assertEqual(record['result_delta']['unchanged_level35_records'], 76)


if __name__ == '__main__':
    unittest.main()
