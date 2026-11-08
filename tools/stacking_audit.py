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
    return (pointer in OBSERVATION_POINTERS and isinstance(value, str)
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
        if component['state'] in {'verified', 'conditional'}:
            source = data['sources'][component['source']]
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
    for rule in data['rules']:
        assert rule['source'] in source_ids
        assert rule['kind'] in {'different_types', 'pair', 'same_type_max'}
        assert rule['quote'] in data['sources'][rule['source']]['quote']
        assert rule['stats'] and rule['types']
        assert (rule['source'], rule['kind'], tuple(rule['types']), tuple(rule['stats'])) == RULE_CONTRACTS[rule['id']]
    assert {r['id'] for r in data['rules']} == set(RULE_CONTRACTS)
    for effect in data['non_total_effects']:
        assert effect['state'] in STATES
        assert effect['sources'] or effect['state'] == 'unknown'
        assert all(s in source_ids for s in effect['sources'])
        assert effect['note']
        if effect['state'] in {'verified', 'conditional'}:
            assert all(source_provenance(data['sources'][sid]) for sid in effect['sources']), effect['id']
    return True


def applies(rule, stat):
    return '*' in rule['stats'] or stat in rule['stats']


def proof(data, stat, a, b):
    """Return an explicit applicable rule; never infer from absent prohibition."""
    if a['channel'] != b['channel']:
        return None
    ta, tb = a['bonus_type'], b['bonus_type']
    for rule in data['rules']:
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
    eligible, excluded = [], []
    for c in rows:
        if (c['state'] not in {'verified', 'conditional'} or level < c['kit_min_level']
                or not source_provenance(data['sources'].get(c['source'], {}))
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
