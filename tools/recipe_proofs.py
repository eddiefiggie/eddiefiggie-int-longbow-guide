"""Bounded source-supported recipe derivations for the selected Chains crafts.

This is not a general inference engine. Only reviewed host, recipe-table and
category-membership relationships are admitted. Original source wording stays
separate; no joined sentence is presented as a finished-item tooltip. Every
qualification rereads its pinned source records and unchanged selection.
"""
from datetime import datetime
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = 'slave-lords-selected-v1'
MANIFEST_PATH = 'tools/fixtures/wisdom-loadout/selection.json'
MANIFEST_SHA256 = '8223bd8e25ed9dc4ad9454439ead42dfb693cc008d18d0ddfeb270d33863c37d'
PACKETS = {
    'crafting': ('evidence/wisdom-loadout/crafting-browser-2026-11-15.json',
                 '4394f8f408d6d448a99f473ece71ce26248d3710e8e9243a0d98d532cbd77d01'),
    'membership': ('evidence/wisdom-loadout/recipe-proof-sources-2026-11-15.json',
                   '32b74bbce3d952f71dae94f22845e8ea414fcc821932e915bd9821f950ac3830'),
}
# (packet, exact source record, displayed field, page identity)
SOURCE_BINDINGS = {
    'host': ('crafting', 'chains', 'item_table_visible_text', 'Item:Legendary_Chains'),
    'recipe': ('crafting', 'slave_lords', 'recipe_table_visible_text', 'Slave_Lords_Crafting'),
    'combustion': ('crafting', 'spell_power', 'selected_row_html', 'Spell_Power'),
    'intelligence': ('membership', 'ability', 'ability_members_visible_text', 'Ability'),
}
# (craft channel, statistic, amount, bonus type); these are selected tuples,
# not proof that the corresponding mechanics are qualified.
SELECTED = {
    'chains-fortification': ('Prefix', 'Fortification', 142, 'Enhancement'),
    'chains-combustion': ('Suffix', 'Combustion', 142, 'Equipment'),
    'chains-quality-int': ('Bonus', 'Intelligence', 3, 'Quality'),
    'chains-spot': ('Extra', 'Spot', 20, 'Competence'),
}
BOUNDED_COMPONENT_IDS = frozenset(SELECTED)
UNRESOLVED = {
    'chains-fortification': 'Selected Prefix membership in the standard-Fortification class is unproved',
    'chains-spot': 'Competence type for the selected Chains skill craft is unproved',
}
HEADER_ROWS = [
    [{'column_span': 1, 'row_span': 2, 'text': 'Group'},
     {'column_span': 1, 'row_span': 2, 'text': 'Enchantment name'},
     {'column_span': 2, 'row_span': 1, 'text': 'Enchantment value'},
     {'column_span': 2, 'row_span': 1, 'text': 'Ingredient cost'}],
    [{'column_span': 1, 'row_span': 1, 'text': 'Heroic\nML 8'},
     {'column_span': 1, 'row_span': 1, 'text': 'Legendary\nML 28'},
     {'column_span': 1, 'row_span': 1, 'text': 'Heroic'},
     {'column_span': 1, 'row_span': 1, 'text': 'Legendary'}],
]
CATEGORY_OFFER_RULE = (
    'The next step is to speak to a barter NPC to exchange the basic ingredients '
    'for "gems" of different sorts (see below), which will be used to give you the '
    'effects on your items. Each of the 3 common and 3 uncommon ingredients '
    'allows a different kind of effect on the item, and there are 6 possible '
    'to create for each item you will create - prefix, suffix, bonus, extra, '
    'augment slot (clear, yellow, blue, or green), and set bonus (your choice '
    'of 3 possible). Tables below show what sort of effects can go into each of these.')
ABILITY_MEMBERS = (
    'Almost everything a Player Character does is affected by his abilities: '
    'Strength (STR), Dexterity (DEX), Constitution (CON), Intelligence (INT), '
    'Wisdom (WIS), and Charisma (CHA). Play Tabletop RPGs')
ATTRIBUTE_SYNONYM = (
    'The "comeliness" statistic is used in some versions of tabletop D&D but is '
    'not used in DDO. Abilities are also sometimes named attributes or stats.')


def _require(condition, message):
    if not condition:
        raise AssertionError(message)


def _norm(text):
    return ' '.join(text.split())


def _resolve(value, pointer):
    for key in pointer:
        value = value[key]
    return value


def _pinned_json(root, path, digest):
    target = root / path
    _require(target.resolve().is_relative_to(root.resolve()), 'Source path escapes root')
    raw = target.read_bytes()
    _require(sha256(raw).hexdigest() == digest, 'Reviewed file hash mismatch: ' + path)
    return json.loads(raw)


def _source_record(data, source_id, binding, root):
    """Validate each real leaf, including when subtotal bypasses validate()."""
    packet, record_name, field, page = SOURCE_BINDINGS[binding]
    path, digest = PACKETS[packet]
    source = data['sources'][source_id]
    expected_record = ['captures', record_name]
    _require((source['path'], source['sha256']) == (path, digest), 'Unreviewed proof capture')
    _require(source['record_pointer'] == expected_record, 'Wrong source record')
    _require(source['pointer'] == expected_record + [field], 'Wrong source context')
    _require(source['url_key'] == 'source_url', 'Wrong source identity field')
    _require(source['revision_pointer'] == ['revision_link'], 'Wrong revision context')
    _require(source['observed_pointer'] == ['body_observation', 'started_at_utc'],
             'A receipt date or missing observation is not source provenance')
    _require(not source.get('url_from_revision'), 'Unexpected source identity rewriting')
    capture = _pinned_json(root, path, digest)
    record = _resolve(capture, expected_record)
    url = 'https://ddowiki.com/page/' + page
    _require(source['url'] == record['source_url'] == url, 'Wrong page identity')
    _require(isinstance(source['quote'], str) and source['quote'] == record[field]
             and bool(source['quote']), 'Quote is not the complete retained role context')
    revision = source['revision']
    _require(revision == record['revision_link'], 'Wrong revision')
    parsed = urlparse(revision)
    query = parse_qs(parsed.query)
    _require((parsed.scheme, parsed.netloc, parsed.path) == ('https', 'ddowiki.com', '/index.php')
             and set(query) == {'title', 'oldid'} and query['title'] == [page]
             and len(query['oldid']) == 1 and query['oldid'][0].isdigit(), 'Unqualified revision')
    window = record['body_observation']
    start, end = window['started_at_utc'], window['ended_at_utc']
    for value in (start, end):
        _require(isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', value),
                 'Missing genuine source observation window')
    _require(datetime.fromisoformat(start) < datetime.fromisoformat(end), 'Reversed capture window')
    _require(source['observed'] == start, 'Observation is not source-bound')
    _require(isinstance(source['freshness_limit'], str) and bool(source['freshness_limit'].strip()),
             'Missing source limitations')
    return record


class _Row(HTMLParser):
    """Read one retained table row, preserving cell order and link identities."""
    def __init__(self, markup):
        super().__init__(convert_charrefs=True)
        self.cells, self.links, self.active, self.rows = [], [], False, 0
        self.feed(markup)
        self.close()

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.rows += 1
        elif tag == 'td':
            _require(not self.active, 'Nested cells')
            self.cells.append([])
            self.links.append([])
            self.active = True
        elif tag == 'a' and self.active:
            self.links[-1].append(dict(attrs).get('href'))

    def handle_endtag(self, tag):
        if tag == 'td':
            self.active = False

    def handle_data(self, value):
        if self.active:
            self.cells[-1].append(value)

    def values(self):
        _require(self.rows == 1 and len(self.cells) == 3 and not self.active, 'Wrong recipe row structure')
        return [_norm(''.join(cell)) for cell in self.cells]


def _selection(root, component):
    selected = _pinned_json(root, MANIFEST_PATH, MANIFEST_SHA256)
    _require(selected['selection']['id'] == 'artifact-wisdom-canonical-spot-luck'
             and selected['selection']['full_kit_ml'] == 36, 'Wrong selected loadout')
    _require([i['id'] for i in selected['items'] if i['minor_artifact']] == ["Yeenoghu's Reign"],
             'Selected one-Minor-Artifact requirement changed')
    hosts = [i for i in selected['items'] if i['id'] == 'Legendary Chains']
    _require(len(hosts) == 1, 'Missing or duplicate selected host')
    host = hosts[0]
    _require((host['slot'], host['base_ml'], host['filled_ml'], host['minor_artifact']) ==
             ('Belt', 28, 30, False), 'Wrong selected host applicability')
    expected = {(slot, stat, amount, kind) for slot, stat, amount, kind in SELECTED.values()}
    actual = []
    for craft in host['crafts']:
        _require((craft['host'], craft['family'], craft['tier']) ==
                 ('Legendary Chains', 'Slave Lords', 'legendary'), 'Wrong selected crafting family/tier')
        _require(craft['pool'] is None and craft['category'] is None and len(craft['affixes']) == 1,
                 'Unexpected selected craft constraints')
        affix = craft['affixes'][0]
        actual.append((craft['slot'], affix['stat'], affix['value'], affix['type']))
    _require(len(actual) == len(expected) and set(actual) == expected, 'Selected craft tuple changed')
    slot, stat, amount, kind = SELECTED[component['id']]
    _require((component['host'], component['stat'], component['amount'], component['bonus_type'],
              component['channel'], component['kit_min_level'], component['requires']) ==
             ('Legendary Chains / ' + slot, stat, amount, kind, 'gear', 36, []),
             'Proof does not match the selected component tuple')
    _require(type(component['amount']) is int, 'Unexpected recipe numeric type')
    return slot


def _host_and_recipe(host, recipe, slot):
    text = host['item_table_visible_text']
    _require('Minimum level\t28\t' in text and '\nUpgradeable?\tSlave Lords Crafting\n' in text,
             'Host is not the Legendary recipe variant')
    _require(text.count('\nLegendary Slaver\'s ' + slot + ' Slot\n') == 1,
             'Selected crafting channel is not offered by this host')
    _require('This unusual item can be worn in the Neck slot or the Waist slot - '
             'it will default to the Neck if both slots are empty when you equip it.' in text,
             'Selected Waist placement is not supported')
    label = "Legendary Slaver's " + slot + ' Slot'
    _require(host['slot_tooltip_text'][label] == label + label + ': Apply a Slaver\'s shard to this item.',
             'Host channel does not authorize a Slaver shard')
    _require(recipe['recipe_table_headers'] == HEADER_ROWS, 'Heroic/Legendary value headers changed')
    _require(recipe['gem_slot_rule_visible_text'] == CATEGORY_OFFER_RULE,
             'Recipe category offer is missing or altered')
    table = recipe['recipe_table_visible_text']
    _require(table.startswith('Group\tEnchantment name\tEnchantment value\tIngredient cost\n'
                              'Heroic\nML 8\tLegendary\nML 28\tHeroic\tLegendary\n'),
             'Recipe column roles are not the reviewed hierarchy')
    next_group = {'Suffix': 'Extra', 'Bonus': 'Augment Slot addition'}[slot]
    start, end = '\n' + slot + '\n', '\n' + next_group + '\n'
    _require(table.count(start) == table.count(end) == 1, 'Missing or duplicate recipe group')
    left, right = table.index(start) + len(start), table.index(end)
    _require(left < right, 'Wrong recipe group order')
    return table[left:right]


def _combustion(recipe, group, member):
    row = _Row(recipe['spell_power_row_html'])
    _require(row.values() == ['Spell Power (single type) (Equipment Bonus)', '+70', '+142']
             and row.links[0] == ['/page/Spell_Power'], 'Wrong typed Spell Power value row')
    _require(group.splitlines().count('Spell Power (single type) (Equipment Bonus)\t+70\t+142') == 1,
             'Spell Power row is not the offered Legendary Suffix')
    _require(member['headers_visible_text'] ==
             'Continuous effect (Equipment bonus)\tTemporary effect (Alchemical bonus)\tAffects',
             'Effect definition headers changed')
    mapping = _Row(member['selected_row_html'])
    _require(mapping.values() == ['Combustion', 'Inferno', 'Fire Spells']
             and mapping.links == [['/page/Combustion'], ['/page/Inferno'], ['/page/Category:Fire_spells']],
             'Combustion is not the sourced continuous Fire Spell Power member')
    _require(member['selected_row_visible_text'] == 'Combustion\tInferno\tFire Spells',
             'Effect definition contexts disagree')
    _require(member['weapon_limit_visible_text'] ==
             'Spell power affects Spells and SLAs, but does not affect magical damage effects on weapons '
             'from augments, filigrees, crafted enchantments etc. unless the description specifically indicates that it does',
             'Spell Power applicability limit lost')


def _quality_intelligence(recipe, group, member):
    row = recipe['quality_attributes_row_visible_text']
    _require(row.startswith('Bonus\n') and row.count('\tQuality Attributes\t+1\t+3\t\n') == 1,
             'Wrong Quality Attributes recipe/value/variant')
    _require(group.count(row[len('Bonus\n'):]) == 1, 'Quality Attributes is not the offered Bonus row')
    _require(member['requested_url'] == 'https://ddowiki.com/page/Attributes',
             'Attributes terminology connection lost')
    _require(member['ability_members_visible_text'] == ABILITY_MEMBERS,
             'Intelligence category membership is not the reviewed source statement')
    _require(member['attribute_synonym_visible_text'] == ATTRIBUTE_SYNONYM,
             'Attributes/abilities terminology is not source-supported')


def validate_component(data, component, root=ROOT):
    """Fail closed for every incomplete, malformed, hybrid or unreviewed proof.

    A positive return qualifies only the selected gear component. It creates no
    positive stacking edge, ownership fact, imbue applicability or DPS result.
    """
    try:
        cid = component['id']
        _require(cid in BOUNDED_COMPONENT_IDS, 'Recipe proof used on an unapproved component')
        matches = [c for c in data['components'] if c['id'] == cid]
        _require(len(matches) == 1 and matches[0] == component, 'Duplicate or detached proof component')
        proof = component['recipe_proof']
        _require(isinstance(proof, dict) and set(proof) == {'contract', 'sources'}
                 and proof['contract'] == CONTRACT, 'Unknown or malformed recipe-proof contract')
        _require(component['state'] == 'verified', 'An incomplete proof cannot be declared qualified')
        _require(all(component[key] == '' for key in ('source', 'value_pattern', 'type_evidence')),
                 'Hybrid direct and recipe binding is forbidden')
        _require(cid not in UNRESOLVED, UNRESOLVED.get(cid, 'Unresolved proof'))
        sources = proof['sources']
        _require(isinstance(sources, dict) and set(sources) == {'host', 'recipe', 'membership'}
                 and all(isinstance(v, str) and v for v in sources.values())
                 and len(set(sources.values())) == 3, 'Missing, duplicate or unexpected proof legs')
        root = Path(root)
        slot = _selection(root, component)
        host = _source_record(data, sources['host'], 'host', root)
        recipe = _source_record(data, sources['recipe'], 'recipe', root)
        member = _source_record(data, sources['membership'],
                                'combustion' if cid == 'chains-combustion' else 'intelligence', root)
        group = _host_and_recipe(host, recipe, slot)
        if cid == 'chains-combustion':
            _combustion(recipe, group, member)
        else:
            _quality_intelligence(recipe, group, member)
        return True
    except (KeyError, TypeError, ValueError, IndexError, AttributeError, OSError) as error:
        raise AssertionError('Missing or malformed source-supported recipe proof') from error
