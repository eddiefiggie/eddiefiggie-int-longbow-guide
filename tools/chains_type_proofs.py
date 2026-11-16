"""Two exact Legendary recipe-type derivations, not a new generic source gate.

Wiki records supply values, selected host applicability and skill membership.
Nexus records supply recipe-associated types with their numeric placeholders
left empty. No revision, client build or finished-item tooltip is invented.
Every use rechecks independently pinned source bytes and complete selected rows.
"""
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = 'slave-lords-selected-types-v1'
PACKET_PATH = 'evidence/wisdom-loadout/chains-type-sources-2026-11-15.json'
PACKET_SHA256 = 'a949c385294d81804e6770632fdcb0277c4307bfefc6c1f5396eade2c3946c96'
SOURCE_SHA256 = {
    'chains-types-shared-host-20261115': '28dbedb833ec82cba0e7b24d3296302598c1fa74c8932b1f5edee6c7d9fd0486',
    'chains-types-fortification-20261115': '6764c3135752ca00b8f630a941f1fe0a32f5ffa4ba888ed06f30bf65b1a33e52',
    'chains-types-spot-20261115': 'b068bf44969f075cf3bd297d43e83c84caeb33519bbbec35859293c6d512ef28',
}
SOURCE_BINDINGS = {
    'chains-types-shared-host-20261115':
        (0, ['shared_host_statement_exact'], 'https://ddowiki.com/page/Slave_Lords_Crafting'),
    'chains-types-fortification-20261115':
        (2, ['application', 'added_effect_markup_exact'],
         'https://ddonexus.com/Item/Legendary_Slaver_Fortification'),
    'chains-types-spot-20261115':
        (3, ['application', 'added_effect_markup_exact'],
         'https://ddonexus.com/Item/Legendary_Slavers_Spot/2C66B'),
}
CORE_SHA256 = {
    'chains-fortification': 'e9c2e3c9b74c9e9d574e6851ba3bd195a4f89eb76b2c054c277789ec3ac731ad',
    'chains-spot': '47e4225ac13ff9afc33f48145e4f6d93c47b53dc04ed32547041ce161b25529d',
}
COMPONENT_IDS = frozenset(CORE_SHA256)
PROOFS = {
    'chains-fortification': {'contract': CONTRACT, 'sources': {
        'host': 'chains-host-recipe-20261115',
        'recipe': 'chains-legendary-recipe-20261115',
        'shared_host': 'chains-types-shared-host-20261115',
        'type': 'chains-types-fortification-20261115'}},
    'chains-spot': {'contract': CONTRACT, 'sources': {
        'host': 'chains-host-recipe-20261115',
        'recipe': 'chains-legendary-recipe-20261115',
        'shared_host': 'chains-types-shared-host-20261115',
        'type': 'chains-types-spot-20261115',
        'skill': 'fort-spot-skill-20261115',
        'spot': 'fort-spot-spot-20261115'}},
}
RULES = {
    'spot-chains-heroism': {
        'id': 'spot-chains-heroism', 'source': 'fort-spot-tip179-20261115',
        'quote': 'Different types of bonuses stack', 'kind': 'selected_pairs',
        'types': ['Competence', 'Morale'], 'stats': ['Spot'], 'channel': 'gear',
        'component_pairs': [['chains-spot', 'heroism-spot']]},
    'spot-chains-luck': {
        'id': 'spot-chains-luck', 'source': 'fort-spot-tip179-20261115',
        'quote': 'Different types of bonuses stack', 'kind': 'selected_pairs',
        'types': ['Competence', 'Luck'], 'stats': ['Spot'], 'channel': 'gear',
        'component_pairs': [['chains-spot', 'luck-spot']]},
}
RULE_IDS = frozenset(RULES)


def _require(condition, message):
    if not condition:
        raise AssertionError(message)


def _fingerprint(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _resolve(value, pointer):
    for part in pointer:
        value = value[part]
    return value


def bounded_source(source, sid=None):
    """Also catch renamed/altered Nexus aliases before any legacy fallback."""
    hostname = (urlparse(source.get('url') or '').hostname or '').rstrip('.')
    return (sid in SOURCE_SHA256 or source.get('path') == PACKET_PATH
            or source.get('source_contract') == CONTRACT
            or _fingerprint(source) in SOURCE_SHA256.values()
            or hostname == 'ddonexus.com' or hostname.endswith('.ddonexus.com'))


def uses_contract(data):
    """Partial deletion of new evidence or either edge cannot look historical."""
    return (any(bounded_source(source, sid) for sid, source in data.get('sources', {}).items())
            or any(rule.get('id') in RULE_IDS for rule in data.get('rules', ()))
            or any(row.get('id') in COMPONENT_IDS and row.get('state') in {'verified', 'conditional'}
                   or row.get('recipe_proof', {}).get('contract') == CONTRACT
                   for row in data.get('components', ())))


def _source_record(data, sid, root=ROOT):
    _require(sid in SOURCE_SHA256, 'Unreviewed recipe-type source identity')
    source = data['sources'][sid]
    _require(_fingerprint(source) == SOURCE_SHA256[sid], 'Changed recipe-type source binding')
    root = Path(root)
    path = root / PACKET_PATH
    _require(path.resolve().is_relative_to(root.resolve()), 'Source path escapes root')
    raw = path.read_bytes()
    _require(sha256(raw).hexdigest() == PACKET_SHA256, 'Changed recipe-type capture bytes')
    packet = json.loads(raw)
    index, suffix, url = SOURCE_BINDINGS[sid]
    pointer = ['sources', index]
    record = _resolve(packet, pointer)
    _require(source['path'] == PACKET_PATH and source['sha256'] == PACKET_SHA256
             and source['source_contract'] == CONTRACT, 'Wrong source contract')
    _require(source['record_pointer'] == pointer and source['pointer'] == pointer + suffix,
             'Wrong recipe-associated context')
    _require(source['quote'] == _resolve(record, suffix), 'Altered or joined source quotation')
    _require(source['url_key'] == 'url' and source['url'] == record['url'] == url,
             'Wrong recipe or source variant')
    _require(source['observed_pointer'] == ['observed_at_utc']
             and source['observed'] == record['observed_at_utc']
             and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z', source['observed']),
             'Missing source-bound observation')
    if index == 0:
        _require(source['revision_pointer'] == ['permalink_href']
                 and source['revision'] == record['permalink_href'] ==
                 'https://ddowiki.com/index.php?title=Slave_Lords_Crafting&oldid=715666'
                 and record['permalink_reopened'] is False,
                 'Changed Wiki revision or observation limits')
    else:
        _require(source['revision_pointer'] is None and source['revision'] is None
                 and record['source_version_observed'] is None
                 and record['numeric_parameter_observed'] is None,
                 'Nexus version or numeric placeholder was fabricated')
    return record


def validate_source(data, sid, root=ROOT):
    try:
        _source_record(data, sid, root)
        return True
    except (AssertionError, KeyError, TypeError, ValueError, IndexError, AttributeError, OSError):
        return False


class _Effect(HTMLParser):
    """Parse the exact added-effect node, keeping title and label separate."""
    def __init__(self, markup):
        super().__init__(convert_charrefs=True)
        self.nodes, self.ends, self.parts = [], [], []
        self.feed(markup)
        self.close()

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))

    def handle_endtag(self, tag):
        self.ends.append(tag)

    def handle_data(self, value):
        self.parts.append(value)


def _typed_recipe(record, cid):
    fort = cid == 'chains-fortification'
    slot, ingredient = ('Prefix', 'shackles') if fort else ('Extra', 'collars')
    _require(record['item_name'] == ('Legendary Slaver Fortification' if fort else "Legendary Slaver's Spot"),
             'Wrong Legendary shard identity')
    if not fort:
        _require(record['variant'] == '0x7002C66B', 'Wrong same-name Spot variant')
    _require(record['found_recipe'] == {'quantity': 100,
                                      'ingredient': 'broken ' + ingredient + ', Legendary tier'},
             'Wrong recipe ingredients or tier')
    application = record['application']
    _require(application['target'] == 'Generic craftable Slave Lords base of Legendary tier'
             and application['removed_slot_exact'] == "Legendary Slaver's " + slot + ' Slot',
             'Wrong recipe target or removed slot')
    effect = _Effect(application['added_effect_markup_exact'])
    title = ('+% Enhancement bonus to the reduced chance of taking bonus damage on a critical hit.'
             if fort else '+ Competence bonus to Spot.')
    label = 'Fortification +%' if fort else 'Spot +'
    _require(effect.nodes == [('li', {'class': 'recipe-mutation-known', 'title': title})]
             and effect.ends == ['li'] and ''.join(effect.parts) == label,
             'Wrong added effect/type association or filled numeric placeholder')


def validate_component(data, component, root=ROOT):
    """Only these two definitions may combine the retained source premises."""
    import recipe_proofs as recipes
    import fort_spot_proofs as fort_spot
    try:
        cid = component['id']
        _require(cid in COMPONENT_IDS, 'Unapproved recipe-type component')
        matches = [row for row in data['components'] if row['id'] == cid]
        _require(len(matches) == 1 and matches[0] == component, 'Duplicate or detached definition')
        _require(_fingerprint({k: v for k, v in component.items() if k != 'note'}) == CORE_SHA256[cid],
                 'Changed selected definition core')
        _require(component['recipe_proof'] == PROOFS[cid], 'Unreviewed type proof')
        root = Path(root)
        slot = recipes._selection(root, component)
        sources = component['recipe_proof']['sources']
        host = recipes._source_record(data, sources['host'], 'host', root)
        recipe = recipes._source_record(data, sources['recipe'], 'recipe', root)
        group = recipes._host_and_recipe(host, recipe, slot)
        shared = _source_record(data, sources['shared_host'], root)
        _require(shared['shared_host_statement_exact'] == 'All base items may use all ingredients.',
                 'Missing shared base-item applicability')
        typed = _source_record(data, sources['type'], root)
        _typed_recipe(typed, cid)
        if cid == 'chains-fortification':
            row = recipes._Row(recipe['fortification_row_html'])
            _require(row.values() == ['Fortification', '+70%', '+142%']
                     and row.links[0] == ['/page/Fortification']
                     and group.splitlines().count('Fortification\t+70%\t+142%') == 1
                     and '100   Legendary Broken Shackles' in group,
                     'Wrong Legendary Prefix value or ingredient association')
        else:
            row = recipe['skills_row_visible_text']
            _require(row.startswith('Extra\n')
                     and row.count('\tSkills (except UMD)\t+10\t+20\t\n') == 1
                     and group.count(row[len('Extra\n'):]) == 1
                     and '100   Legendary Broken Collars' in group,
                     'Wrong Legendary Extra value/category or ingredient association')
            skill = fort_spot._source_record(data, sources['skill'], root)
            spot = fort_spot._source_record(data, sources['spot'], root)
            _require(skill['exact_spot_row'].startswith('\tSpot\tYes\tWisdom\tPassive\t')
                     and spot['exact_excerpts'][1] ==
                     'The Spot skill enables you to sense secret doors, hidden enemies, and possibly traps.',
                     'Missing explicit Spot skill membership')
        return True
    except (AssertionError, KeyError, TypeError, ValueError, IndexError, AttributeError, OSError):
        return False


def family_valid(data, stat, arguments=(), root=ROOT):
    """The .9 profile keeps all five selected members and each separate proof."""
    import fort_spot_proofs as fort_spot
    try:
        expected = fort_spot.FAMILIES[stat]
        rows = data['components']
        family = [row for row in rows if row['stat'] == stat and row['channel'] == 'gear']
        _require(len(family) == len(expected) and {row['id'] for row in family} == set(expected),
                 'Missing, extra, duplicated or substituted selected family')
        selected = {}
        for cid in expected:
            matches = [row for row in rows if row['id'] == cid]
            _require(len(matches) == 1, 'Duplicate or moved selected member')
            row = matches[0]
            digest = CORE_SHA256[cid] if cid in COMPONENT_IDS else fort_spot.CORE_SHA256[cid]
            _require(_fingerprint({k: v for k, v in row.items() if k != 'note'}) == digest,
                     'Changed selected family core')
            qualified = (validate_component(data, row, root) if cid in COMPONENT_IDS
                         else fort_spot.validate_component(data, row, root))
            _require(qualified, 'Unqualified selected definition')
            selected[cid] = row
        _require(all(argument == selected[argument['id']] for argument in arguments),
                 'Detached selected argument')
        return True
    except (AssertionError, KeyError, TypeError, ValueError, IndexError, AttributeError, OSError):
        return False


def validate_pair(data, rule, stat, a, b, root=ROOT):
    import fort_spot_proofs as fort_spot
    try:
        _require(rule == RULES[rule['id']] and stat == a['stat'] == b['stat'] == 'Spot'
                 and a['channel'] == b['channel'] == 'gear'
                 and {a['id'], b['id']} == set(rule['component_pairs'][0]),
                 'Unreviewed pair, statistic or channel')
        return (family_valid(data, stat, (a, b), root)
                and fort_spot.validate_rule_source(data, root))
    except (AssertionError, KeyError, TypeError, ValueError, IndexError, AttributeError, OSError):
        return False
