"""Evidence-gated arithmetic for the selected endgame kit, not a game simulator.

A different type is not a proof edge. Missing edges withhold combined totals.
Only sourced, applicable components enter a subtotal; unresolved claims stay visible.
"""
from __future__ import annotations
import hashlib
import itertools
import json
from pathlib import Path
import re
from urllib.parse import unquote, parse_qs, urlparse
from recipe_proofs import BOUNDED_COMPONENT_IDS, validate_component as validate_recipe_component
import fort_spot_proofs as fort_spot

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tools/fixtures/endgame-stacking/ledger.json'
STATES = {'verified', 'conditional', 'conflicting', 'unknown'}
# Reviewed interpretations of exact source sentences. Changing a fixture cannot
# silently broaden a rule's stat/type scope; a new rule requires code review.
OBSERVATION_POINTERS = {('capturedAt',), ('observed_start',), ('observed',),
                        ('body_observation', 'started_at_utc')}

RULE_CONTRACTS = {
    'same-type-best': ('stack', 'same_type_max', ('*',), ('*',)),
    'artifact-other-types': ('artifact', 'different_types', ('Artifact',), ('*',)),
    'exceptional-other-types': ('exceptional', 'different_types', ('Exceptional',), ('*',)),
    'prr-combination': ('prr-rule', 'different_types', ('*',), ('PRR',)),
    'mrr-combination': ('mrr-rule', 'different_types', ('*',), ('MRR',)),
    'vitality-combination': ('vitality-rule', 'different_types', ('Vitality',), ('HP',)),
    'fort-enh-insight': ('fortification-rule', 'pair', ('Enhancement', 'Insight'), ('Fortification',)),
    'int-selected-ten-pairs': ('tip179-live-20261115', 'selected_pairs',
                               ('Enhancement', 'Insight', 'Quality', 'Profane', 'Festive'), ('Intelligence',)),
    'fort-enh-insight-observed': ('fort-rule-live-20261115', 'pair',
                                 ('Enhancement', 'Insight'), ('Fortification',)),
    'spot-heroism-luck': ('fort-spot-tip179-20261115', 'selected_pairs',
                         ('Morale', 'Luck'), ('Spot',)),
}
# The seven-rule historical profile remains an input to the real current
# engine. The additive profile must contain BOTH reviewed rules, never a
# fixture-selected subset or a wildcard different-type rule.
SCOPED_RULE_IDS = frozenset({'int-selected-ten-pairs', 'fort-enh-insight-observed'})
LEGACY_RULE_IDS = frozenset({'same-type-best', 'artifact-other-types',
                            'exceptional-other-types', 'prr-combination',
                            'mrr-combination', 'vitality-combination', 'fort-enh-insight'})
INT_RULE_IDS = LEGACY_RULE_IDS | SCOPED_RULE_IDS
FORT_SPOT_RULE_IDS = INT_RULE_IDS | {fort_spot.RULE_ID}
SELECTED_INT_IDS = ('boots-int', 'glabrezu-insight-int', 'chains-quality-int',
                    'lunar-int', 'festive-int')
SELECTED_INT_PAIRS = tuple(itertools.combinations(SELECTED_INT_IDS, 2))
SCOPED_RULES = {
    'int-selected-ten-pairs': {
        'id': 'int-selected-ten-pairs', 'source': 'tip179-live-20261115',
        'quote': 'Different types of bonuses stack', 'kind': 'selected_pairs',
        'types': ['Enhancement', 'Insight', 'Quality', 'Profane', 'Festive'],
        'stats': ['Intelligence'], 'channel': 'gear',
        'component_pairs': [list(pair) for pair in SELECTED_INT_PAIRS],
    },
    'fort-enh-insight-observed': {
        'id': 'fort-enh-insight-observed', 'source': 'fort-rule-live-20261115',
        'quote': 'Standard fortification items provide enhancement bonuses to fortification. '
                 'Multiple effects do not stack with each other. You can combine them with '
                 'rarer Insightful Fortification items (insight bonus).',
        'kind': 'pair', 'types': ['Enhancement', 'Insight'],
        'stats': ['Fortification'], 'channel': 'gear',
    },
}
# Independent pins bind the exact reviewed metadata, including original
# observation/revision pointers and the immutable packet hash. Runtime checks
# also reread actual packet bytes; a caller-supplied replacement hash is not
# authority. These constants do not refresh or repair any legacy source.
SCOPED_SOURCE_SHA256 = {
    'tip179-live-20261115': '1a69280033c40da1478ebf5380e8b3be50a9369026eee721ecaeb7ea771a1355',
    'fort-rule-live-20261115': '1b79021c6aca469baeebb737fd3e3c837ffda616038c8de7c2fb188061670b90',
}
# All nine INT definitions (including suppressed inputs) are fixed except the
# explanatory note. Completeness cannot survive a missing/forged Artifact or
# Exceptional input merely because those interactions use older rules. The new
# rule itself still covers only the five IDs and ten pairs above.
SELECTED_INT_CORE_SHA256 = {
    'boots-int': 'cd334290891f79e7b28f68f36474bc8734048f9769d87e7610ea1c636a54cb8e',
    'glabrezu-insight-int': '603e83b40e98ada7494d9c86ed1c116640edb860acb136f8d0cf1d0014202590',
    'chains-quality-int': 'fb3ca04e6950f0680f6936683e634697bb63452af761d6b8c25ccd074e06dfa1',
    'lunar-int': '4ebe2ec3bef933349cbeb96ccf512a128a36f2bea183e1bf4a472a5d4ea22375',
    'festive-int': 'fe01aa60300f8b881db840b7261bcab74c49c5ad3c0c6d8db457e828cb58f9cb',
    'solar-int': '0f498b787921a7140692fc86d408f81ad715cf0fbdef479a018978efe2def7bf',
    'dimlight-int': 'ef82bf3d66c01b0e693536140c3daec9660e07aae91a626cf01b85790448f346',
    'globe-intelligence': 'b76d5835172d649b8610d6be4ae6b140d2c3e14001e475ee556b55b96488f628',
    'celestial-profane-intelligence': 'd4cb4814f184da259dc02d23a0e2ac39e380a11528434a160e5828e4f270a715',
}
SELECTED_INT_SOURCE_SHA256 = {
    'melancholic-int-live-20261115': 'b26d57efc5775d29bb9e299d6b822cc76deeb3db8985faf91e91249d9efd9fa1',
    'glabrezu-insight-int-live-20261115': '21463fd81667048ce07c00506e2d26a75a9183d2dcdd9561aa1dbfe7b37ae85f',
    'lunar-int-live-20261115': '3ce3b3b5dfca71aecd8eacade30b6bf6f2fe4037973afe318ee9a01fdcfd22cb',
    'festive-int-live-20261115': 'bca0bc45129dbcab7b5d1b7c7e41b432be3c9ad2b8d96749af20b4c2f9acb4ef',
    'solar-int-live-20261115': 'e0630536f81a0a1ef5b11b04f990be4afef93b624a3064799b356abb71ac5a0c',
    'dimlight-int-live-20261115': '439c1029d2d59474be366cecaf68687411c1d9fab07d1b1c53d8a522704391f0',
    'globe-int-live-20261115': '53c8207000552fa7541f6761aa87aae61bfa3f4ce4cc51f3ea70e9c814fa9613',
    'celestial-profane-int-live-20261115': 'c657f4353b3a013f1f5f0ac95669dce6ba31d02aeefe742d28ed590ee8e633d7',
}
STAT_WORDS = {
    'PRR': ('physical',), 'MRR': ('magical',), 'HP': ('hit points', 'maximum hp'),
    'Seeker': ('critical',), 'Armor-Piercing': ('fortification bypass',),
    'Deadly': ('weapon damage',), 'Accuracy': ('attack',),
    'Fortitude': ('fortitude', 'saves', 'saving throws'),
    'Reflex': ('reflex', 'saves', 'saving throws'),
    'Will': ('will', 'saves', 'saving throws'),
    'Ranged threat reduction': ('threat generated from ranged damage',),
    'Ranged damage': ('ranged damage',), 'Ranged attack': ('ranged attack',),
    'Greater Marksmanship damage': ('ranged damage',),
    'Greater Marksmanship attack': ('ranged attack',),
    'Ranged alacrity': ('ranged attack speed',), 'Dodge bypass': ('dodge bypass',),
    'Sneak dice': ('sneak attack',),
}


def canonical(url):
    return unquote(url).replace('_', ' ').rstrip('/').lower()



def load():
    return json.loads(FIXTURE.read_text())


def resolve(root, pointer):
    for part in pointer:
        if part == '$json':
            root = json.loads(root)
        else:
            root = root[part]
    return root


def observation_context(source):
    pointer = tuple(source.get('observed_pointer') or ())
    value = source.get('observed')
    return fort_spot.observation_context(source) or (pointer in OBSERVATION_POINTERS and isinstance(value, str)
            and re.fullmatch(r'\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))?', value) is not None)


def source_provenance(source):
    """Require an exact revision and a genuine source-bound observation context.

    Observation dates/windows may be coarser than a timestamp, but must resolve
    through observed_pointer in the hashed source record. Filenames, mtimes and
    later receipt creation dates are not substitutes for an observation.
    """
    revision = source.get('revision') or ''
    oldid = parse_qs(urlparse(revision).query).get('oldid', [])
    return (len(oldid) == 1 and oldid[0].isdigit()
            and bool(source.get('revision_pointer'))
            and observation_context(source))


def component_provenance(data, component, *, root=None):
    """Recheck bounded recipe proofs at every counting entrypoint.

    The fixed Chains IDs cannot escape to legacy provenance by deleting a
    proof. Unrelated direct-source components retain their original behavior.
    """
    if component['id'] in fort_spot.DEFINITION_IDS or 'definition_proof' in component:
        return (rule_profile(data) == FORT_SPOT_RULE_IDS and current_rule_profile(data)
                and fort_spot.validate_component(data, component, ROOT if root is None else root))
    if uses_scoped_rules(data) and component['id'] in SELECTED_INT_CORE_SHA256:
        return (current_rule_profile(data)
                and selected_int_members(data, (component,), root=root))
    if component['id'] in BOUNDED_COMPONENT_IDS or 'recipe_proof' in component:
        return validate_recipe_component(data, component, ROOT if root is None else root)
    source = data['sources'].get(component['source'], {})
    if fort_spot.bounded_source(source, component['source']):
        return False
    return source_provenance(source)


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def uses_scoped_rules(data):
    """Recognize the additive profile even if a caller renames a rule."""
    return (bool(set(data['sources']) & set(SCOPED_SOURCE_SHA256))
            or any(r.get('id') in SCOPED_RULE_IDS
                   or r.get('source') in SCOPED_SOURCE_SHA256
                   or r.get('kind') == 'selected_pairs' for r in data['rules']))


def rule_profile(data):
    """Return the exact reviewed ID profile, or None; duplicates are invalid."""
    ids = [rule.get('id') for rule in data['rules']]
    if len(ids) != len(set(ids)) or set(ids) not in (LEGACY_RULE_IDS, INT_RULE_IDS, FORT_SPOT_RULE_IDS):
        return None
    for rule in data['rules']:
        contract = (rule.get('source'), rule.get('kind'),
                    tuple(rule.get('types', ())), tuple(rule.get('stats', ())))
        if contract != RULE_CONTRACTS.get(rule.get('id')):
            return None
        if rule['id'] in SCOPED_RULES and rule != SCOPED_RULES[rule['id']]:
            return None
        if rule['id'] == fort_spot.RULE_ID and rule != fort_spot.SPOT_RULE:
            return None
    return frozenset(ids)


def current_rule_profile(data):
    """Preserve exact seven/nine-rule history; partial new inputs fail closed."""
    profile = rule_profile(data)
    return (profile in (INT_RULE_IDS, FORT_SPOT_RULE_IDS)
            and (not fort_spot.uses_contract(data) or profile == FORT_SPOT_RULE_IDS)
            and all(fingerprint(data['sources'].get(sid)) == digest
                    for sid, digest in SCOPED_SOURCE_SHA256.items()))


def pinned_source(data, sid, digest, *, root=None):
    """Recheck a reviewed source binding AND its actual bytes on every use."""
    root = ROOT if root is None else root
    source = data['sources'][sid]
    assert fingerprint(source) == digest, sid
    path = root / source['path']
    assert path.resolve().is_relative_to(root.resolve()), sid
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source['sha256'], sid
    capture = json.loads(raw)
    record = resolve(capture, source['record_pointer'])
    assert source['quote'] in resolve(capture, source['pointer']), sid
    assert canonical(record[source['url_key']]) == canonical(source['url']), sid
    assert resolve(record, source['revision_pointer']) == source['revision'], sid
    assert resolve(record, source['observed_pointer']) == source['observed'], sid
    assert source_provenance(source), sid
    return True


def selected_int_members(data, arguments=(), *, root=None):
    """The complete nine-definition family, not interchangeable type labels.

    A forged argument, a simultaneously edited ledger row, a duplicate/missing
    member, or any changed source binding fails closed. Recipe derivation is
    still independently checked by its existing bounded proof engine.
    """
    try:
        family = [row for row in data['components']
                  if row['stat'] == 'Intelligence' and row['channel'] == 'gear']
        assert len(family) == len(SELECTED_INT_CORE_SHA256)
        assert {row['id'] for row in family} == set(SELECTED_INT_CORE_SHA256)
        selected = {}
        for cid, digest in SELECTED_INT_CORE_SHA256.items():
            matches = [row for row in data['components'] if row['id'] == cid]
            assert len(matches) == 1, cid
            row = matches[0]
            assert fingerprint({k: v for k, v in row.items() if k != 'note'}) == digest, cid
            selected[cid] = row
            if cid in BOUNDED_COMPONENT_IDS:
                assert validate_recipe_component(data, row, ROOT if root is None else root), cid
            else:
                assert pinned_source(data, row['source'], SELECTED_INT_SOURCE_SHA256[row['source']], root=root), cid
        assert all(argument == selected[argument['id']] for argument in arguments)
        return True
    except (AssertionError, KeyError, TypeError, ValueError, OSError):
        return False


def scoped_proof(data, rule, stat, a, b):
    """Only the two reviewed positive statements can enter this new route."""
    try:
        assert current_rule_profile(data)
        assert rule == SCOPED_RULES[rule['id']]
        assert a['id'] != b['id']
        assert a['channel'] == b['channel'] == rule['channel'] == 'gear'
        assert a['stat'] == b['stat'] == stat and rule['stats'] == [stat]
        assert pinned_source(data, rule['source'], SCOPED_SOURCE_SHA256[rule['source']])
        if rule['id'] == 'int-selected-ten-pairs':
            assert selected_int_members(data, (a, b))
            assert frozenset((a['id'], b['id'])) in {
                frozenset(pair) for pair in SELECTED_INT_PAIRS}
        else:
            assert {a['bonus_type'], b['bonus_type']} == {'Enhancement', 'Insight'}
        return rule['id']
    except (AssertionError, KeyError, TypeError, ValueError, OSError):
        return None


def validate(data, root=ROOT):
    """Validate source identities, exact contexts and machine-extracted inputs."""
    source_ids = set()
    captures = {}
    for sid, source in data['sources'].items():
        assert sid not in source_ids
        source_ids.add(sid)
        path = root / source['path']
        assert path.resolve().is_relative_to(root.resolve())
        if path not in captures:
            raw = path.read_bytes()
            captures[path] = (hashlib.sha256(raw).hexdigest(), json.loads(raw))
        digest, capture = captures[path]
        assert digest == source['sha256'], sid
        context = resolve(capture, source['pointer'])
        assert isinstance(context, str), sid
        assert source['quote'] in context, sid
        assert source['url'].startswith('https://ddowiki.com/'), sid
        assert source['freshness_limit'], sid
        record = resolve(capture, source['record_pointer'])
        identity = record[source['url_key']]
        if source['url_key'] == 'requested':
            identity = 'https://ddowiki.com/page/' + identity
        if source.get('url_from_revision'):
            identity = 'https://ddowiki.com/page/' + parse_qs(urlparse(identity).query)['title'][0]
        assert canonical(source['url']) == canonical(identity), sid
        observed_revision = resolve(record, source['revision_pointer']) if source['revision_pointer'] else None
        assert source['revision'] == observed_revision, sid
        observed_time = resolve(record, source['observed_pointer']) if source['observed_pointer'] else None
        assert source['observed'] == observed_time, sid
        if source['observed'] is not None:
            assert observation_context(source), sid
        assert source['pointer'][:len(source['record_pointer'])] == source['record_pointer'], sid
    seen = set()
    for component in data['components']:
        cid = component['id']
        assert cid not in seen, cid
        seen.add(cid)
        assert component['state'] in STATES
        assert component['channel'] and component['stat'] and component['host']
        assert isinstance(component['amount'], (int, float)) and component['amount'] >= 0
        assert component['note']
        if ('definition_proof' in component or
                cid in fort_spot.DEFINITION_IDS and component['state'] in {'verified', 'conditional'}):
            assert fort_spot.validate_component(data, component, root), cid
        elif ('recipe_proof' in component or
                component['id'] in BOUNDED_COMPONENT_IDS and component['state'] in {'verified', 'conditional'}):
            validate_recipe_component(data, component, root)
        elif component['state'] in {'verified', 'conditional'}:
            source = data['sources'][component['source']]
            assert not fort_spot.bounded_source(source, component['source']), cid
            assert source_provenance(source), cid
            match = re.search(component['value_pattern'], source['quote'])
            assert match and float(match.group('value')) == component['amount'], cid
            assert component['type_evidence'] in source['quote'], cid
            assert component['bonus_type'] != 'unknown', cid
            assert component['channel'] == 'gear', cid
            if component['stat'] == 'Dodge':
                assert 'bypass' not in source['quote'].lower(), cid
            assert component['bonus_type'].lower() in component['type_evidence'].lower(), cid
            words = STAT_WORDS.get(component['stat'], (component['stat'].lower(),))
            # Bind the numeric clause, not a whole tooltip line or sentence:
            # one sentence can grant +3 attack AND +2 damage, for example.
            text = source['quote']
            value_start, value_end = match.span('value')
            numbers = list(re.finditer(r'(?<![\w.])[+-]?\d+(?:\.\d+)?(?:%|\b)', text))
            number = next(n for n in numbers if n.start() <= value_start < n.end())
            begin = number.start()
            limits = [n.start() for n in numbers if n.start() >= value_end]
            limits += [b.start() for b in re.finditer(r'[.!?;](?:\s+|$)|\n', text) if b.start() >= value_end]
            end = min(limits, default=len(text))
            effect = text[begin:end].lower()
            assert component['bonus_type'].lower() in effect, cid
            assert any(word in effect for word in words) or (component['stat'] in {'Intelligence', 'Constitution'} and 'all abilities' in effect), cid
        if component['state'] == 'conditional':
            assert component['requires'], cid
    assert rule_profile(data) is not None, 'Unreviewed, partial or duplicate rule profile'
    for rule in data['rules']:
        assert rule['source'] in source_ids
        assert rule['kind'] in {'different_types', 'pair', 'same_type_max', 'selected_pairs'}
        assert rule['quote'] in data['sources'][rule['source']]['quote']
        assert rule['stats'] and rule['types']
        assert (rule['source'], rule['kind'], tuple(rule['types']), tuple(rule['stats'])) == RULE_CONTRACTS[rule['id']]
        if rule['id'] in SCOPED_RULE_IDS:
            assert pinned_source(data, rule['source'], SCOPED_SOURCE_SHA256[rule['source']], root=root)
        if rule['id'] == fort_spot.RULE_ID:
            assert fort_spot.validate_rule_source(data, root), 'Unqualified named Spot interaction source'
    if rule_profile(data) in (INT_RULE_IDS, FORT_SPOT_RULE_IDS):
        assert current_rule_profile(data)
        assert selected_int_members(data, root=root), 'Changed selected INT definitions or bindings'
    if fort_spot.uses_contract(data):
        assert rule_profile(data) == FORT_SPOT_RULE_IDS, 'Incomplete Fortification/Spot rule profile'
        for stat in fort_spot.FAMILIES:
            assert fort_spot.family_valid(data, stat, root=root), 'Changed selected ' + stat + ' family'
    for effect in data['non_total_effects']:
        assert effect['state'] in STATES
        assert effect['sources'] or effect['state'] == 'unknown'
        assert all(s in source_ids for s in effect['sources'])
        assert effect['note']
        if effect['state'] in {'verified', 'conditional'}:
            assert not any(fort_spot.bounded_source(data['sources'][sid], sid)
                           for sid in effect['sources']), effect['id']
            assert all(source_provenance(data['sources'][sid]) for sid in effect['sources']), effect['id']
    return True


def applies(rule, stat):
    return '*' in rule['stats'] or stat in rule['stats']


def proof(data, stat, a, b):
    """Return an explicit applicable rule; never infer from absent prohibition."""
    if a['channel'] != b['channel']:
        return None
    if any(fort_spot.bounded_source(data['sources'].get(row.get('source'), {}), row.get('source'))
           for row in (a, b)):
        return None
    if fort_spot.uses_contract(data) and (stat in fort_spot.FAMILIES
                                         or a['id'] in fort_spot.FAMILY_IDS
                                         or b['id'] in fort_spot.FAMILY_IDS):
        if (rule_profile(data) != FORT_SPOT_RULE_IDS or not current_rule_profile(data)
                or a['channel'] != 'gear'
                or not fort_spot.family_valid(data, stat, (a, b), ROOT)
                or not all(fort_spot.validate_component(data, row, ROOT) for row in (a, b))):
            return None
    if uses_scoped_rules(data):
        if a['id'] == b['id'] or not current_rule_profile(data):
            return None
        members = tuple(row for row in (a, b) if row['id'] in SELECTED_INT_CORE_SHA256)
        if members:
            if any(row['stat'] != stat or row['channel'] != 'gear' for row in members):
                return None
            if not selected_int_members(data, members):
                return None
    ta, tb = a['bonus_type'], b['bonus_type']
    for rule in data['rules']:
        if rule['id'] == fort_spot.RULE_ID:
            if (rule == fort_spot.SPOT_RULE and stat == 'Spot'
                    and a['channel'] == b['channel'] == 'gear'
                    and {a['id'], b['id']} == {'heroism-spot', 'luck-spot'}
                    and fort_spot.validate_rule_source(data, ROOT)):
                return rule['id']
            continue
        if rule['id'] in SCOPED_RULE_IDS:
            found = scoped_proof(data, rule, stat, a, b)
            if found is not None:
                return found
            continue
        if not source_provenance(data['sources'][rule['source']]):
            continue
        if not applies(rule, stat):
            continue
        types = rule['types']
        if ta == tb:
            if ta not in {'Untyped', 'Feat'} and rule['kind'] == 'same_type_max' and ('*' in types or ta in types):
                return rule['id']
        elif rule['kind'] == 'different_types' and (ta in types or tb in types or '*' in types):
            return rule['id']
        elif rule['kind'] == 'pair' and {ta, tb} == set(types):
            return rule['id']
    return None


def subtotal(data, stat, *, channel='gear', active=(), level=36):
    """A total is null unless ALL counted pairs have explicit rule coverage.

    unknown/conflicting inputs cannot be enabled with a caller flag. Conditional
    inputs require all named conditions. No capped or proc amount is silently
    treated as standing. Suppression is scoped to statistic AND channel.
    """
    rows = [c for c in data['components'] if c['stat'] == stat and c['channel'] == channel]
    # The newly complete INT result must describe the unchanged entire selected
    # family. Deleting/adding an input cannot turn a supported subset into a
    # falsely complete kit, even when validate() was never called.
    family_valid = (not (uses_scoped_rules(data) and stat == 'Intelligence' and channel == 'gear')
                    or current_rule_profile(data) and selected_int_members(data))
    if fort_spot.uses_contract(data) and stat in fort_spot.FAMILIES and channel == 'gear':
        family_valid = (rule_profile(data) == FORT_SPOT_RULE_IDS and current_rule_profile(data)
                        and fort_spot.family_valid(data, stat, root=ROOT))
    eligible, excluded = [], []
    for c in rows:
        if (not family_valid or c['state'] not in {'verified', 'conditional'} or level < c['kit_min_level']
                or not component_provenance(data, c)
                or not set(c['requires']).issubset(active)):
            excluded.append(c['id'])
        else:
            eligible.append(c)
    groups = {}
    for c in eligible:
        groups.setdefault(c['bonus_type'], []).append(c)
    counted, suppressed, edges, gaps = [], [], [], []
    for same_type in groups.values():
        winner = max(same_type, key=lambda c: (c['amount'], c['id']))
        counted.append(winner)
        for c in same_type:
            if c is winner:
                continue
            rule = proof(data, stat, winner, c)
            if rule is None:
                gaps.append([winner['id'], c['id']])
            else:
                suppressed.append(c['id'])
                edges.append([winner['id'], c['id'], rule])
    for a, b in itertools.combinations(counted, 2):
        rule = proof(data, stat, a, b)
        if rule is None:
            gaps.append([a['id'], b['id']])
        else:
            edges.append([a['id'], b['id'], rule])
    return {'stat': stat, 'channel': channel,
            'total': sum(c['amount'] for c in counted) if counted and not gaps and not excluded else None,
            'counted': [c['id'] for c in counted], 'suppressed': suppressed,
            'excluded': excluded, 'missing_interactions': gaps, 'proofs': edges,
            'complete': bool(rows) and not excluded and not gaps}


def doubleshot_effective(value):
    assert value >= 0
    return min(value, 200) + max(0, value - 200) / 2


if __name__ == '__main__':
    ledger = load()
    validate(ledger)
    for stat in dict.fromkeys(c['stat'] for c in ledger['components']):
        print(json.dumps(subtotal(ledger, stat), sort_keys=True))
