"""Bind the additive browser checkpoint without promoting calculator inputs.

These are source-fidelity, provenance-boundary and preservation checks, not
authentication of a Wiki observation, a live-game test, or a finished-item
tooltip synthesized from several pages. The original qualification checkpoint
remains unchanged until a separately reviewed integration.
"""
import copy
from datetime import datetime
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import unittest
from urllib.parse import parse_qs, urlparse

import stacking_audit as audit


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'evidence/wisdom-loadout/crafting-browser-2026-11-15.json'
CAPTURES = {
    'glabrezu': ('Item:Legendary_Glabrezu_Claw_Pendant', '707320',
                '20:43:29', '20:43:33', 18, '03:07, August 25, 2026 (Update 81.2)'),
    'nearly_complete': ('Nearly_Complete', '705751',
                        '20:43:50', '20:43:59', 5, '04:27, August 16, 2026 (Update 81.1.1)'),
    'chains': ('Item:Legendary_Chains', '631926',
               '20:44:23', '20:44:30', 5, '19:30, April 21, 2025 (Update 73.1)'),
    'slave_lords': ('Slave_Lords_Crafting', '715666',
                    '20:44:30', '20:45:26', 8, '10:46, September 18, 2026 (Update 81.3)'),
    'fortification': ('Fortification', '723727',
                      '20:46:28', '20:46:32', 8, '10:54, October 24, 2026 (Update 82.0.1)'),
    'spell_power': ('Spell_Power', '695517',
                    '20:49:00', '20:49:05', 8, '22:47, July 17, 2026 (Update 80.1)'),
}
FINDINGS = {
    'glabrezu-insight-int': (
        'Legendary Glabrezu Claw Pendant', 'Nearly Complete: Insightful Ability Score',
        'Intelligence', 7, 'Insight', 'direct-item-and-legendary-recipe',
        'direct-item-tooltip', ('glabrezu', 'nearly_complete')),
    'chains-fortification': (
        'Legendary Chains', 'Prefix', 'Fortification', 142, 'Enhancement',
        'legendary-recipe-row', 'general-rule-inference-not-finished-item',
        ('chains', 'slave_lords', 'fortification')),
    'chains-combustion': (
        'Legendary Chains', 'Suffix', 'Combustion', 142, 'Equipment',
        'legendary-recipe-plus-effect-name-mapping', 'explicit-equipment-recipe-table',
        ('chains', 'slave_lords', 'spell_power')),
    'chains-quality-int': (
        'Legendary Chains', 'Bonus', 'Intelligence', 3, 'Quality',
        'legendary-attribute-category-mapping', 'explicit-quality-recipe-table',
        ('chains', 'slave_lords')),
    'chains-spot': (
        'Legendary Chains', 'Extra', 'Spot', 20, 'Competence',
        'legendary-skill-category-mapping', 'unresolved', ('chains', 'slave_lords')),
}
FIELDS = {
    'glabrezu-insight-int': (
        'glabrezu.item_table_visible_text glabrezu.selected_option_html '
        'nearly_complete.table_headers_visible_text nearly_complete.selected_row_visible_text'),
    'chains-fortification': (
        'chains.item_table_visible_text slave_lords.recipe_table_headers '
        'slave_lords.recipe_table_visible_text slave_lords.fortification_row_html '
        'fortification.standard_item_rule_visible_text'),
    'chains-combustion': (
        'chains.item_table_visible_text slave_lords.recipe_table_headers '
        'slave_lords.recipe_table_visible_text slave_lords.spell_power_row_html '
        'spell_power.headers_visible_text spell_power.selected_row_visible_text '
        'spell_power.weapon_limit_visible_text'),
    'chains-quality-int': (
        'chains.item_table_visible_text slave_lords.recipe_table_headers '
        'slave_lords.recipe_table_visible_text slave_lords.quality_attributes_row_visible_text'),
    'chains-spot': (
        'chains.item_table_visible_text slave_lords.recipe_table_headers '
        'slave_lords.recipe_table_visible_text slave_lords.skills_row_visible_text'),
}
FALSE_FLAGS = {
    'selected_recipe_changed', 'priorities_changed', 'old_capture_metadata_repaired',
    'historical_claim_inventory_regraded', 'calculator_components_promoted',
    'counted_totals_changed', 'new_optimizer_run', 'live_game_test',
    'guide_rendering_qa_completed', 'all_release_gates_closed',
    'merge_or_publication_performed',
}
PRESERVED = {
    'index.html': '281c8e4ce94f28d5d23c345f01d34bfcb0423f73ff90d871d82b7ecf8611f048',
    'versions/11-15-26.1.html': '9dcc34e46b405d9917a713d14fb3b63f4b5b10c72284a9d516a95486df4cd17f',
    'versions/11-15-26.2.html': '48e66b9bb02bc32c991545f6d660e66ea53fa7a4dbb1a5d44535e9bf7200cd67',
    'endgame-stacking-audit.html': '0b51824f17b18bcb2533034b653254f411775f898b515d971e1e17e6fcf1e2d7',
    'heroic-crafting-print.html': '87ae7532b16452d35dc20ba9419a1dfe2c40e88a76817d20ff6628cc6f7e12c6',
    'tools/fixtures/endgame-stacking/ledger.json': '381fe7e81573fdb727a103df020270c5b8e66b560325fc9b8825668878607560',
    'tools/fixtures/wisdom-loadout/selection.json': '8223bd8e25ed9dc4ad9454439ead42dfb693cc008d18d0ddfeb270d33863c37d',
    'tools/stacking_audit.py': '97432b1a37543645986a343ec0c6d3c8d58b77c4089e03307dfdf2840d3c606d',
    'tools/wisdom_loadout.py': '25a9bc502ae5afe8e9cdbbc48762c674fa2f62459c96b3a91fe9f3438a055d8c',
    'tools/build_stacking_audit.py': '699bba973b9f08b2df57e2728534a341935e8390e8be641599b695c75ddee49f',
    'evidence/endgame-stacking/source-excerpts.json': '0f13e0875c61c4fb0d5420b6825417f416cb3fa1c18677d24074e3bfd9a77c1f',
    'evidence/wisdom-loadout/claims.json': '2de551db80e4d682da2cd0a3156b1a5e830927a833750b81d370b6c6bbedf1ad',
    'evidence/wisdom-loadout/sources.json': 'cea672fa20445cfda89717a8e04af1a34c73f272ff82bf0ad86630713c1bd92a',
    'evidence/wisdom-loadout/loadout.json': '20f5bca4573d803a196695aa999f4acc07e71db077e3b66fde51a560b6da0843',
    'evidence/wisdom-loadout/production.json': '684215235205fb59ba183cf11d9235661becb2973681afb7dfc6ae9e332413e2',
    'evidence/wisdom-loadout/derivation.json': '215c66ae090b2d25142472634dd8e56c668e08526ed6bbaa6709116ecbc9da02',
    'evidence/wisdom-loadout/corrections.json': 'a6b318f5f71f1f9445e21c19d23a22fddf3ad20f7e4888858bf3ef5effdd591f',
    'evidence/wisdom-loadout/startup.json': 'f4ffd67f7ca1b55a3a44a6ed8e4e28b60d48a9acce4e7294983311adaf0207ef',
    'evidence/wisdom-loadout/verification.json': 'a78f7205b9887f3ac5aa06ffc5f0a8acc446e9c8a9c2739314b510a7e1ee246b',
}


def norm(text):
    return ' '.join(text.split())


class SourceText(HTMLParser):
    def __init__(self, markup):
        super().__init__(convert_charrefs=True)
        self.parts, self.cells, self.in_cell = [], [], False
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        if tag == 'td':
            self.cells.append([])
            self.in_cell = True

    def handle_endtag(self, tag):
        if tag == 'td':
            self.in_cell = False

    def handle_data(self, value):
        self.parts.append(value)
        if self.in_cell:
            self.cells[-1].append(value)

    def text(self):
        return norm(' '.join(self.parts))

    def cell_texts(self):
        return [norm(' '.join(parts)) for parts in self.cells]


def validate_checkpoint(data):
    """Validate this additive record; never return a game or stacking verdict."""
    assert data['schema_version'] == 1
    assert data['record_type'] == 'fresh-browser-source-addendum-not-calculator-promotion'
    assert data['review_date'] == '2026-11-15'
    base = data['baseline']
    assert (base['repository'], base['pull_request'], base['remote_head'],
            base['remote_and_initial_staged_tree'], base['actual_local_head'],
            base['local_branch']) == (
        'eddiefiggie/eddiefiggie-int-longbow-guide', 47,
        '3133c86f54fb21cbe9b8fa3b9551a9ba61525750',
        'e107a09dd6a11f3a4e441c9c9d445915c6b8019c',
        '5ded199eadbade29dcdb0c1eccfad4758a65c328', 'feat/wisdom-loadout-priorities')
    assert set(data['scope']) == FALSE_FLAGS | {'purpose'}
    assert all(data['scope'][key] is False for key in FALSE_FLAGS)
    assert data['preserved_sha256'] == PRESERVED
    assert set(data['captures']) == set(CAPTURES)
    for sid, (page, revision, start, end, cache_hours, modified) in CAPTURES.items():
        capture = data['captures'][sid]
        assert capture['source_url'] == 'https://ddowiki.com/page/' + page, sid
        parsed = urlparse(capture['revision_link'])
        assert (parsed.scheme, parsed.netloc, parsed.path) == ('https', 'ddowiki.com', '/index.php'), sid
        assert parse_qs(parsed.query) == {'title': [page], 'oldid': [revision]}, sid
        window = capture['body_observation']
        assert window == {'started_at_utc': '2026-11-15T' + start + 'Z',
                          'ended_at_utc': '2026-11-15T' + end + 'Z'}, sid
        assert datetime.fromisoformat(window['started_at_utc']) < datetime.fromisoformat(window['ended_at_utc']), sid
        assert not {'observed', 'observed_at_utc', 'capturedAt', 'original_observation'} & set(capture), sid
        assert capture['page_modified_display'] == modified, sid
        assert capture['logged_out_cache_notice_hours'] == cache_hours, sid
    method = data['method']
    assert 'new access windows, not the original historical capture dates' in method['observation_clock']
    assert 'not complete raw HTTP responses' in method['capture_kind']
    assert 'not independently loaded again' in method['revision_limit']
    assert (method['license'], method['license_url']) == (
        'CC BY-SA 2.5', 'https://creativecommons.org/licenses/by-sa/2.5/')
    findings = {finding['component_id']: finding for finding in data['findings']}
    assert len(findings) == len(data['findings']) == 5 and set(findings) == set(FINDINGS)
    for cid, expected in FINDINGS.items():
        finding = findings[cid]
        actual = tuple(finding[key] for key in (
            'host', 'channel', 'stat', 'value', 'bonus_type', 'magnitude_support', 'type_support'))
        assert actual + (tuple(finding['source_ids']),) == expected, cid
        assert finding['evidence_fields'] == FIELDS[cid].split(), cid
        for reference in finding['evidence_fields']:
            sid, field = reference.split('.')
            assert sid in finding['source_ids'] and data['captures'][sid][field], reference
        assert finding['conclusion'] and finding['remaining'], cid

    glabrezu, nearly, chains, slavers, fort, spell = (
        data['captures'][key] for key in CAPTURES)
    assert 'Minimum level\t35' in glabrezu['item_table_visible_text']
    assert 'Nearly Complete: Insightful Ability Score' in glabrezu['item_table_visible_text']
    assert 'Insightful Intelligence +7' in glabrezu['item_table_visible_text']
    assert 'granting a +7 Insight bonus to Intelligence.' in SourceText(glabrezu['selected_option_html']).text()
    assert nearly['table_headers_visible_text'].split('\t') == [
        'Effect set', 'Available upgrades (Heroic)', 'Available upgrades (Legendary)']
    nearly_cells = nearly['selected_row_visible_text'].split('\t')
    assert len(nearly_cells) == 3 and norm(nearly_cells[0]) == 'Insightful Ability Score'
    assert 'Insightful Intelligence +2' in nearly_cells[1]
    assert 'Insightful Intelligence +7' in nearly_cells[2]
    assert 'cannot replace a Nearly Completed upgrade' in nearly['upgrade_rule_visible_text']
    assert 'Legendary Abyssal Gems for Legendary items' in nearly['upgrade_rule_visible_text']
    assert 'Minimum level\t28' in chains['item_table_visible_text']
    assert 'Neck slot or the Waist slot' in chains['item_table_visible_text']
    for channel in ('Prefix', 'Suffix', 'Extra', 'Bonus', 'Augment'):
        label = "Legendary Slaver's " + channel + ' Slot'
        assert label in chains['item_table_visible_text']
        assert 'Apply a Slaver\'s shard to this item.' in chains['slot_tooltip_text'][label]
    assert 'not finished numeric effects' in chains['scope_limit']
    headers = slavers['recipe_table_headers']
    assert [(h['text'], h['column_span'], h['row_span']) for h in headers[0]] == [
        ('Group', 1, 2), ('Enchantment name', 1, 2),
        ('Enchantment value', 2, 1), ('Ingredient cost', 2, 1)]
    assert [(h['text'], h['column_span'], h['row_span']) for h in headers[1]] == [
        ('Heroic\nML 8', 1, 1), ('Legendary\nML 28', 1, 1),
        ('Heroic', 1, 1), ('Legendary', 1, 1)]
    table = slavers['recipe_table_visible_text']
    boundaries = [table.index('\n' + name + '\n')
                  for name in ('Prefix', 'Suffix', 'Extra', 'Bonus', 'Augment Slot addition')]
    assert boundaries == sorted(boundaries)
    groups = [table[start:end] for start, end in zip(boundaries, boundaries[1:])]
    assert 'Fortification\t+70%\t+142%' in groups[0]
    assert 'Spell Power (single type) (Equipment Bonus)\t+70\t+142' in groups[1]
    assert 'Skills (except UMD)\t+10\t+20' in groups[2]
    assert 'Quality Attributes\t+1\t+3' in groups[3]
    assert SourceText(slavers['fortification_row_html']).cell_texts() == ['Fortification', '+70%', '+142%']
    assert SourceText(slavers['spell_power_row_html']).cell_texts() == [
        'Spell Power (single type) (Equipment Bonus)', '+70', '+142']
    skills = slavers['skills_row_visible_text'].split('\t')
    assert [norm(value) for value in skills[:4]] == ['Extra', 'Skills (except UMD)', '+10', '+20']
    assert 'Competence' not in slavers['skills_row_visible_text']
    quality = slavers['quality_attributes_row_visible_text'].split('\t')
    assert quality[0].startswith('Bonus\n')
    assert [norm(value) for value in quality[1:4]] == ['Quality Attributes', '+1', '+3']
    assert slavers['unselected_quality_fortification_row_visible_text'] == 'Quality Fortification\t+17%\t+35%'
    assert 'cannot "erase" or change an effect' in slavers['locked_effect_rule_visible_text']
    assert 'Green\xa0Augment\xa0Slot\t' in table
    assert 'Standard fortification items provide enhancement bonuses to fortification.' in fort['standard_item_rule_visible_text']
    assert 'not a finished Legendary Chains tooltip' in fort['scope_limit']
    assert spell['headers_visible_text'].split('\t') == [
        'Continuous effect (Equipment bonus)', 'Temporary effect (Alchemical bonus)', 'Affects']
    assert spell['selected_row_visible_text'].split('\t') == ['Combustion', 'Inferno', 'Fire Spells']
    assert SourceText(spell['selected_row_html']).cell_texts() == ['Combustion', 'Inferno', 'Fire Spells']
    assert 'does not affect magical damage effects on weapons' in spell['weapon_limit_visible_text']
    assert 'not 142 weapon damage or measured ranged DPS' in findings['chains-combustion']['remaining']
    assert 'not a captured finished-item Intelligence tooltip' in findings['chains-quality-int']['conclusion']
    assert 'model assumption, not a newly verified claim' in findings['chains-spot']['conclusion']
    integration = data['integration_status']
    assert integration['state'] == 'source-findings-recorded-component-qualification-not-integrated'
    assert integration['current_guide_build'] == '11-15-26.2'
    assert 'not automatically promoted' in integration['generated_guide_checkpoint']
    assert 'unresolved Spot type' in integration['next_action']
    assert 'only event/limited-time exception' in integration['owner_exceptions']
    assert 'HA63 acquisition-evidence exception remains narrow' in integration['owner_exceptions']
    assert 'this does not prove that no source exists' in data['bounded_search_limit']['conclusion']
    return True


def qualification_checkpoint(ledger):
    """Check actual current inputs, without treating the addendum as a loader."""
    components = {row['id']: row for row in ledger['components']}
    for cid, expected in FINDINGS.items():
        row = components[cid]
        assert (row['stat'], row['amount'], row['bonus_type']) == expected[2:5], cid
        assert row['state'] == 'unknown' and row['source'] == '', cid
        assert row['value_pattern'] == row['type_evidence'] == '', cid
    return True


class WisdomCraftingBrowserTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(PACKET.read_text())

    def reject(self, mutant):
        with self.assertRaises((AssertionError, KeyError, ValueError, TypeError)):
            validate_checkpoint(mutant)

    def test_fresh_source_checkpoint_and_all_five_findings(self):
        self.assertTrue(validate_checkpoint(self.data))

    def test_nineteen_qualification_checkpoint_files_are_byte_identical(self):
        self.assertEqual(len(PRESERVED), 19)
        self.assertEqual(self.data['preserved_sha256'], PRESERVED)
        for path, expected in PRESERVED.items():
            with self.subTest(path=path):
                self.assertEqual(sha256((ROOT / path).read_bytes()).hexdigest(), expected)

    def test_source_urls_revisions_and_actual_access_windows_cannot_be_forged(self):
        for sid in CAPTURES:
            for field, replacement in (
                ('source_url', 'https://ddowiki.com/page/Item:Different_Item'),
                ('revision_link', 'https://ddowiki.com/index.php?title=Different_Item&oldid=707320'),
                ('body_observation', {}),
                ('body_observation', {'started_at_utc': '2026-11-01T00:00:00Z', 'ended_at_utc': '2026-11-01T00:00:01Z'}),
                ('page_modified_display', '2026-11-15'),
            ):
                changed = copy.deepcopy(self.data)
                changed['captures'][sid][field] = replacement
                with self.subTest(source=sid, field=field):
                    self.reject(changed)
            changed = copy.deepcopy(self.data)
            changed['captures'][sid]['observed_at_utc'] = '2026-11-01T00:00:00Z'
            with self.subTest(source=sid, field='mislabelled original observation'):
                self.reject(changed)

    def test_wrong_selected_amount_type_channel_or_host_is_rejected(self):
        for index, finding in enumerate(self.data['findings']):
            for field, replacement in (('value', finding['value'] + 1),
                                       ('bonus_type', 'Unsupported'), ('channel', 'Other slot'),
                                       ('host', 'Heroic Chains')):
                changed = copy.deepcopy(self.data)
                changed['findings'][index][field] = replacement
                with self.subTest(component=finding['component_id'], field=field):
                    self.reject(changed)

    def test_heroic_and_legendary_columns_cannot_be_swapped(self):
        changed = copy.deepcopy(self.data)
        row = changed['captures']['nearly_complete']['selected_row_visible_text'].split('\t')
        row[1], row[2] = row[2], row[1]
        changed['captures']['nearly_complete']['selected_row_visible_text'] = '\t'.join(row)
        self.reject(changed)
        changed = copy.deepcopy(self.data)
        headers = changed['captures']['slave_lords']['recipe_table_headers'][1]
        headers[0], headers[1] = headers[1], headers[0]
        self.reject(changed)

    def test_wrong_recipe_magnitudes_or_craft_groups_are_rejected(self):
        for field, old, new in (
            ('fortification_row_html', '+142%', '+70%'),
            ('spell_power_row_html', '+142', '+70'),
            ('skills_row_visible_text', '+20', '+10'),
            ('quality_attributes_row_visible_text', '+3', '+1'),
            ('recipe_table_visible_text', '\nPrefix\n', '\nOther\n'),
            ('recipe_table_visible_text', '\nSuffix\n', '\nBonus\n'),
        ):
            changed = copy.deepcopy(self.data)
            before = changed['captures']['slave_lords'][field]
            self.assertIn(old, before)
            changed['captures']['slave_lords'][field] = before.replace(old, new, 1)
            with self.subTest(field=field, old=old):
                self.reject(changed)

    def test_direct_tooltip_binding_does_not_accept_a_changed_bonus_type(self):
        changed = copy.deepcopy(self.data)
        changed['captures']['glabrezu']['selected_option_html'] = changed['captures']['glabrezu']['selected_option_html'].replace('Insight bonus', 'Enhancement bonus')
        self.reject(changed)

    def test_dangling_misbound_and_removed_evidence_fields_are_rejected(self):
        for index, finding in enumerate(self.data['findings']):
            changed = copy.deepcopy(self.data)
            changed['findings'][index]['evidence_fields'][0] = 'glabrezu.missing_field'
            with self.subTest(component=finding['component_id'], case='wrong binding'):
                self.reject(changed)
            changed = copy.deepcopy(self.data)
            source, field = finding['evidence_fields'][-1].split('.')
            del changed['captures'][source][field]
            with self.subTest(component=finding['component_id'], case='missing field'):
                self.reject(changed)

    def test_partial_mappings_and_unresolved_spot_type_cannot_be_upgraded(self):
        for index in range(1, 5):
            for field in ('type_support', 'magnitude_support'):
                changed = copy.deepcopy(self.data)
                changed['findings'][index][field] = 'direct-item-tooltip'
                with self.subTest(component=changed['findings'][index]['component_id'], field=field):
                    self.reject(changed)

    def test_combustion_mapping_does_not_certify_weapon_damage_or_dps(self):
        for source, field, value in (
            ('spell_power', 'selected_row_visible_text', 'Combustion\tInferno\tWeapon Damage'),
            ('spell_power', 'weapon_limit_visible_text', 'Spell power increases all weapon damage'),
        ):
            changed = copy.deepcopy(self.data)
            changed['captures'][source][field] = value
            self.reject(changed)
        changed = copy.deepcopy(self.data)
        changed['findings'][2]['remaining'] = '142 weapon damage and measured ranged DPS are verified.'
        self.reject(changed)

    def test_checkpoint_cannot_claim_release_game_or_component_certification(self):
        for flag in FALSE_FLAGS:
            changed = copy.deepcopy(self.data)
            changed['scope'][flag] = True
            with self.subTest(flag=flag):
                self.reject(changed)
        changed = copy.deepcopy(self.data)
        changed['integration_status']['state'] = 'all-components-certified'
        self.reject(changed)
        changed = copy.deepcopy(self.data)
        changed['preserved_sha256']['index.html'] = '0' * 64
        self.reject(changed)

    def test_current_ledger_retains_all_five_unqualified_inputs(self):
        ledger = audit.load()
        self.assertTrue(qualification_checkpoint(ledger))
        self.assertTrue(audit.validate(ledger))
        for cid, expected in FINDINGS.items():
            with self.subTest(component=cid):
                result = audit.subtotal(ledger, expected[2])
                self.assertIn(cid, result['excluded'])
                self.assertIsNone(result['total'])
                self.assertFalse(result['complete'])
        self.assertIsNone(ledger['sources']['claws-wisdom']['observed'])

    def test_calculator_promotion_is_rejected_even_with_unchanged_model_amount(self):
        for cid in FINDINGS:
            changed = copy.deepcopy(audit.load())
            next(row for row in changed['components'] if row['id'] == cid)['state'] = 'verified'
            with self.subTest(component=cid), self.assertRaises(AssertionError):
                qualification_checkpoint(changed)


if __name__ == '__main__':
    unittest.main()
