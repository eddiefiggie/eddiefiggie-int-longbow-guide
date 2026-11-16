"""Exact selected Queen/Spot definitions and one named Spot interaction.

This is a closed interpretation of one observed item popup and two observed
skill-check clauses, not a generic stat alias or inference engine. Independent
pins preserve the actual source fields, observation context and selected hosts.
Every public check rereads source/selection bytes; successful checks are not
cached across calls. The original unresolved Chains profile remains supported;
the later exact Legendary-type contract has its own complete-family validation.
"""
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = 'evidence/wisdom-loadout/fort-spot-sources-2026-11-15.json'
PACKET_SHA256 = 'a9b2ef77eb3ca10dc77ab93e22a201517920a709615c0905e3e21d77a1cc3456'
MANIFEST_PATH = 'tools/fixtures/wisdom-loadout/selection.json'
MANIFEST_SHA256 = '8223bd8e25ed9dc4ad9454439ead42dfb693cc008d18d0ddfeb270d33863c37d'
RULE_ID = 'spot-heroism-luck'

SOURCE_SHA256 = {'fort-spot-queen-20261115': '93f7dfd5b1a5543bcfe2bee6d5e99aedf53158f5b387e5cb05433881a292d525',
 'fort-spot-heroism-20261115': '1433bac05e4bfd1630808d69cac46d036186f08f3004647160f0deaecd15080c',
 'fort-spot-luck-20261115': '795ebf30bd6d17abe9c57ad93d9e522cff7a3531360c75f0022e024bb83c5af1',
 'fort-spot-skill-20261115': '3aa0979857e8b4fbc53f0e588657f848651ba9da73c9c4d72b9895d1a7e08eef',
 'fort-spot-spot-20261115': '5876c85574f61efad2fdcf1854aa83eff81f2a69ce1601a7e30aa4e1a37ea435',
 'fort-spot-luck-type-20261115': '5e96770b92a1bd02b2e373e0daaecaf22a69d9215131052520df0f69c318ccfa',
 'fort-spot-morale-20261115': '2cc8af6cb524fdb87ef846f37de16ba9fc8f7e95bb7d0d541cc73c1997d4c074',
 'fort-spot-tip179-20261115': '3b4affbf1c6d7415a2cffe4383ff541c434bbfc12409e9729e29d49150ca14dc',
 'fort-spot-pendant-host-20261115': 'ef917f10e5452f7794ab14448423c117d4618e03cafd96d473133a80f68574ef',
 'fort-spot-pendant-level-20261115': '7b7f5c856ea4303b62490c99f4fb4635dae913473b5dd9a2d378a84139b8e110',
 'fort-spot-artifact-host-20261115': '0634636344491f761bfc1c93690ede91caca593674faec199872d07d00614887',
 'fort-spot-artifact-level-20261115': '4df389e6492464d937335cb70d6a2f98b90f05a06cf51f3aa33d3c714a0f1231'}

SOURCE_BINDINGS = {'fort-spot-queen-20261115': (0, ['exact_dom_markup']),
 'fort-spot-heroism-20261115': (4, ['exact_item_text']),
 'fort-spot-luck-20261115': (5, ['exact_item_text']),
 'fort-spot-skill-20261115': (6, ['exact_spot_row']),
 'fort-spot-spot-20261115': (7, ['exact_excerpts', 1]),
 'fort-spot-luck-type-20261115': (8, ['exact_excerpts', 0]),
 'fort-spot-morale-20261115': (9, ['exact_excerpts', 0]),
 'fort-spot-tip179-20261115': (11, ['exact_excerpts', 0]),
 'fort-spot-pendant-host-20261115': (14, ['exact_excerpts', 2]),
 'fort-spot-pendant-level-20261115': (14, ['exact_excerpts', 1]),
 'fort-spot-artifact-host-20261115': (15, ['exact_excerpts', 2]),
 'fort-spot-artifact-level-20261115': (15, ['exact_excerpts', 1])}

DEFINITION_PROOFS = {'queen-fortification': {'contract': 'selected-fort-spot-v1',
                         'method': 'same-item-popup',
                         'sources': {'item': 'fort-spot-queen-20261115'}},
 'heroism-spot': {'contract': 'selected-fort-spot-v1',
                  'method': 'skill-check-membership',
                  'sources': {'item': 'fort-spot-heroism-20261115',
                              'skill': 'fort-spot-skill-20261115',
                              'spot': 'fort-spot-spot-20261115',
                              'host': 'fort-spot-pendant-host-20261115',
                              'host_level': 'fort-spot-pendant-level-20261115'}},
 'luck-spot': {'contract': 'selected-fort-spot-v1',
               'method': 'skill-check-membership',
               'sources': {'item': 'fort-spot-luck-20261115',
                           'skill': 'fort-spot-skill-20261115',
                           'spot': 'fort-spot-spot-20261115',
                           'host': 'fort-spot-artifact-host-20261115',
                           'host_level': 'fort-spot-artifact-level-20261115'}}}

FAMILIES = {'Fortification': ('queen-fortification', 'chains-fortification'),
 'Spot': ('chains-spot', 'heroism-spot', 'luck-spot')}

CORE_SHA256 = {'queen-fortification': '58757c116e9f03b57a15419e424f3f5a46d620271bf79f97803a81491d519407',
 'chains-fortification': 'd629e611d93912c2e6986a503b42f2bee7c7667b6ed6c9ab57f9ae8677a1da67',
 'chains-spot': '3dd01351b731f768456aa8998f5a76fb79247693276131b40a68b33a0d4fa0d7',
 'heroism-spot': 'cc05a02ca92e3964df34df950db9a0dbdb1f343f008d045dc8234735af5c4522',
 'luck-spot': 'ade1056d90f80c51c7ff9dcad42c75f06c131fac3158edfaf0d354887f3eca0e'}

SPOT_RULE = {'id': 'spot-heroism-luck',
 'source': 'fort-spot-tip179-20261115',
 'quote': 'Different types of bonuses stack',
 'kind': 'selected_pairs',
 'types': ['Morale', 'Luck'],
 'stats': ['Spot'],
 'channel': 'gear',
 'component_pairs': [['heroism-spot', 'luck-spot']]}

DEFINITION_IDS = frozenset(DEFINITION_PROOFS)
FAMILY_IDS = frozenset(CORE_SHA256)


def _require(condition, message):
    if not condition:
        raise AssertionError(message)


def _fingerprint(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _resolve(value, pointer):
    for part in pointer:
        value = value[part]
    return value


def _pinned_json(root, path, digest):
    root = Path(root)
    target = root / path
    _require(target.resolve().is_relative_to(root.resolve()), 'Source path escapes root')
    raw = target.read_bytes()
    _require(sha256(raw).hexdigest() == digest, 'Changed reviewed file: ' + path)
    return json.loads(raw)


def uses_contract(data):
    """Detect partial upgrades even after a rule or proof marker is removed."""
    return (any(sid in SOURCE_SHA256 or source.get('path') == PACKET_PATH
                for sid, source in data.get('sources', {}).items())
            or any(rule.get('id') == RULE_ID or rule.get('source') in SOURCE_SHA256
                   for rule in data.get('rules', ()))
            or any('definition_proof' in row
                   or row.get('id') in DEFINITION_IDS and row.get('state') in {'verified', 'conditional'}
                   for row in data.get('components', ())))


def observation_context(source):
    """Admit observed_utc only for an independently pinned new source binding.

    The caller's normal source validation and these definition/rule routes also
    check actual packet bytes. This does not widen the legacy pointer whitelist.
    """
    return (source.get('observed_pointer') == ['observed_utc']
            and _fingerprint(source) in SOURCE_SHA256.values()
            and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z',
                             source.get('observed', '')) is not None)


def bounded_source(source, sid=None):
    """Recognize aliases too; these records cannot qualify unrelated effects."""
    return (sid in SOURCE_SHA256 or source.get('path') == PACKET_PATH
            or _fingerprint(source) in SOURCE_SHA256.values())


def _source_record(data, sid, root):
    _require(sid in SOURCE_SHA256, 'Unreviewed source identity')
    source = data['sources'][sid]
    _require(_fingerprint(source) == SOURCE_SHA256[sid], 'Changed source binding: ' + sid)
    index, suffix = SOURCE_BINDINGS[sid]
    pointer = ['observations', index]
    _require(source['path'] == PACKET_PATH and source['sha256'] == PACKET_SHA256,
             'Unreviewed source packet')
    _require(source['record_pointer'] == pointer and source['pointer'] == pointer + suffix,
             'Changed exact source context')
    packet = _pinned_json(root, PACKET_PATH, PACKET_SHA256)
    record = _resolve(packet, pointer)
    _require(source['quote'] == _resolve(record, suffix), 'Source clause changed or combined')
    _require(source['url_key'] == 'url' and source['url'] == record['url'], 'Wrong source page')
    _require(source['revision_pointer'] == ['revision_link']
             and source['revision'] == record['revision_link'], 'Wrong displayed revision')
    parsed = urlparse(source['revision'])
    query = parse_qs(parsed.query)
    _require((parsed.scheme, parsed.netloc, parsed.path) == ('https', 'ddowiki.com', '/index.php')
             and set(query) == {'title', 'oldid'} and len(query['oldid']) == 1
             and query['oldid'][0].isdigit(), 'Unqualified revision')
    _require(observation_context(source) and source['observed'] == record['observed_utc'],
             'Missing genuine source observation')
    return record


class _Popup(HTMLParser):
    """Preserve node ancestry in the one retained own-item popup fragment."""
    def __init__(self, markup):
        super().__init__(convert_charrefs=True)
        self.root = {'tag': 'root', 'attrs': {}, 'children': []}
        self.stack = [self.root]
        self.feed(markup)
        self.close()
        _require(len(self.stack) == 1, 'Unclosed popup markup')

    def handle_starttag(self, tag, attrs):
        node = {'tag': tag, 'attrs': dict(attrs), 'children': []}
        self.stack[-1]['children'].append(node)
        if tag not in {'img', 'br', 'hr', 'input', 'meta', 'link'}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        _require(len(self.stack) > 1 and self.stack[-1]['tag'] == tag, 'Mismatched popup markup')
        self.stack.pop()

    def handle_data(self, text):
        self.stack[-1]['children'].append(text)


def _nodes(node):
    yield node
    for child in node['children']:
        if isinstance(child, dict):
            yield from _nodes(child)


def _text(node):
    return ''.join(child if isinstance(child, str) else _text(child) for child in node['children'])


def _queen(record):
    tree = _Popup(record['exact_dom_markup']).root
    roots = [child for child in tree['children'] if isinstance(child, dict)]
    _require(len(roots) == 1 and roots[0]['tag'] == 'span'
             and 'has_tooltip' in roots[0]['attrs'].get('class', '').split(), 'Wrong outer item popup')
    outer = roots[0]
    labels = [node for node in outer['children'] if isinstance(node, dict) and node['tag'] == 'a']
    _require(len(labels) == 1 and labels[0]['attrs'].get('href') == '/page/Fortification'
             and _text(labels[0]) == 'Insightful Fortification  +84%', 'Wrong effect label/value')
    tips = [node for node in _nodes(outer) if 'tooltip' in node['attrs'].get('class', '').split()]
    _require(len(tips) == 1, 'Missing or multiple associated tooltips')
    tip = tips[0]
    links = [(node['attrs'].get('href'), _text(node)) for node in _nodes(tip) if node['tag'] == 'a']
    _require(links == [('/page/Fortification', 'Insightful Fortification  +84%'),
                       ('/page/Insight_bonus', 'Insight bonus')], 'Wrong popup effect/type relationship')
    _require(_text(tip) == 'Insightful Fortification  +84%: +84% Insight bonus to reduced chance '
                           'of taking critical damage on a critical hit.', 'Changed typed numeric clause')


def _selection(root, cid):
    selected = _pinned_json(root, MANIFEST_PATH, MANIFEST_SHA256)
    _require(selected['selection']['id'] == 'artifact-wisdom-canonical-spot-luck'
             and selected['selection']['full_kit_ml'] == 36, 'Wrong selected loadout or level floor')
    _require([item['id'] for item in selected['items'] if item['minor_artifact']] == ["Yeenoghu's Reign"],
             'Changed selected Minor Artifact')
    host_id, slot, filled = {
        'queen-fortification': ('The Queen of Rot', 'Cloak', 35),
        'heroism-spot': ('Legendary Glabrezu Claw Pendant', 'Necklace', 35),
        'luck-spot': ("Yeenoghu's Reign", 'Bracers', 36),
    }[cid]
    hosts = [item for item in selected['items'] if item['id'] == host_id]
    _require(len(hosts) == 1, 'Missing or duplicate selected host')
    host = hosts[0]
    _require((host['slot'], host['base_ml'], host['filled_ml']) == (slot, 35, filled),
             'Changed selected host or minimum level')
    if cid == 'queen-fortification':
        _require(any((a['stat'], a['type'], a['value']) == ('Fortification', 'Insight', 84)
                     for a in host['native_affixes']), 'Changed selected Queen contribution')
    else:
        index, color, name, amount, kind = {
            'heroism-spot': (1, 'Green', 'Sapphire of Greater Heroism', 4, 'Morale'),
            'luck-spot': (3, 'Blue', 'Sapphire of Good Luck +3', 3, 'Luck'),
        }[cid]
        sockets = [socket for socket in host['sockets'] if socket['index'] == index]
        _require(len(sockets) == 1 and sockets[0]['color'] == color, 'Changed selected socket')
        fill = sockets[0]['fill']
        _require((fill['id'], fill['kind'], fill['color'], fill['ml']) == (name, 'augment', 'Blue', 28),
                 'Changed selected augment or level')
        _require(any((a['stat'], a['type'], a['value']) == ('Spot', kind, amount)
                     for a in fill['affixes']), 'Changed selected Spot contribution')


def validate_component(data, component, root=ROOT):
    """Qualify only these three exact definitions, never their entire families."""
    try:
        cid = component['id']
        _require(cid in DEFINITION_IDS, 'Definition proof on an unreviewed component')
        matches = [row for row in data['components'] if row['id'] == cid]
        _require(len(matches) == 1 and matches[0] == component, 'Duplicate or detached component')
        _require(_fingerprint({k: v for k, v in component.items() if k != 'note'}) == CORE_SHA256[cid],
                 'Changed selected definition core')
        _require(component['definition_proof'] == DEFINITION_PROOFS[cid], 'Changed proof contract')
        _selection(root, cid)
        records = {role: _source_record(data, sid, root)
                   for role, sid in component['definition_proof']['sources'].items()}
        if cid == 'queen-fortification':
            _queen(records['item'])
        else:
            text = records['item']['exact_item_text']
            name, clause, color = {
                'heroism-spot': ('Sapphire of Greater Heroism',
                                '+4 Morale Bonus to Attack Rolls, Saving Throws, and Skill Checks.', 'Green'),
                'luck-spot': ('Sapphire of Good Luck +3',
                             '+3 Luck bonus to Saving Throws and Skill Checks.', 'Blue'),
            }[cid]
            _require(text.startswith(name + '\nMinimum Level\t28\t') and clause in text,
                     'Wrong own-augment identity or typed skill-check clause')
            _require('Augment Type\tBlue\n' in text
                     and 'This augment can go in a Blue, Green, or Purple Augment Slot.' in text,
                     'Missing augment compatibility')
            _require(records['skill']['exact_spot_row'].startswith('\tSpot\tYes\tWisdom\tPassive\t'),
                     'Missing Spot skill membership')
            _require(records['spot']['exact_excerpts'][1] ==
                     'The Spot skill enables you to sense secret doors, hidden enemies, and possibly traps.'
                     and records['spot']['exact_excerpts'][2].startswith('With a successful Spot check'),
                     'Missing Spot skill/check connection')
            _require(records['host']['exact_excerpts'][2] == color + '\u00a0Augment\u00a0Slot'
                     and records['host_level']['exact_excerpts'][1] == 'Minimum level\t35\t',
                     'Missing own-host socket/level context')
        return True
    except (AssertionError, KeyError, TypeError, ValueError, IndexError, AttributeError, OSError):
        return False


def family_valid(data, stat, arguments=(), root=ROOT):
    """Require the complete reviewed .8 or .9 family before any completeness."""
    import chains_type_proofs as chains_types
    if chains_types.uses_contract(data):
        return chains_types.family_valid(data, stat, arguments, root)
    try:
        expected = FAMILIES[stat]
        rows = data['components']
        family = [row for row in rows if row['stat'] == stat and row['channel'] == 'gear']
        _require(len(family) == len(expected) and {row['id'] for row in family} == set(expected),
                 'Missing, duplicated or substituted selected family')
        selected = {}
        for cid in expected:
            matches = [row for row in rows if row['id'] == cid]
            _require(len(matches) == 1, 'Duplicate or moved selected member')
            row = matches[0]
            _require(_fingerprint({k: v for k, v in row.items() if k != 'note'}) == CORE_SHA256[cid],
                     'Changed selected family core')
            if cid in DEFINITION_IDS:
                _require(validate_component(data, row, root), 'Unqualified selected definition')
            else:
                _require(row['state'] == 'unknown' and 'recipe_proof' not in row,
                         'Unresolved Chains definition promoted')
            selected[cid] = row
        _require(all(argument == selected[argument['id']] for argument in arguments),
                 'Detached selected argument')
        return True
    except (AssertionError, KeyError, TypeError, ValueError, IndexError, AttributeError, OSError):
        return False


def validate_rule_source(data, root=ROOT):
    """One positive pair premise with the retained same-type overlap limits."""
    try:
        tip = _source_record(data, SPOT_RULE['source'], root)['exact_excerpts'][0]
        _require('such as enhancement, morale, or luck.' in tip
                 and 'Different types of bonuses stack' in tip, 'Missing affirmative type statement')
        luck = _source_record(data, 'fort-spot-luck-type-20261115', root)['exact_excerpts'][0]
        morale = _source_record(data, 'fort-spot-morale-20261115', root)['exact_excerpts'][0]
        _require('Only the highest luck bonus applies.' in luck
                 and 'Only the highest morale bonus applies.' in morale, 'Lost same-type overlap limits')
        return True
    except (AssertionError, KeyError, TypeError, ValueError, IndexError, AttributeError, OSError):
        return False
