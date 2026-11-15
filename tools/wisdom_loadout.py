"""One read-only source and static renderer for the selected Wisdom loadout.

This validates a frozen, explicitly manual recipe and independently recomputes
its catalog arithmetic. It is neither an optimizer nor a mechanics certifier.
The older stacking ledger remains the authority for source-qualified subtotals.
"""
from collections import Counter, defaultdict
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'tools/fixtures/wisdom-loadout/selection.json'
MARKERS = {
    'recipe': ('<!-- wisdom-loadout-recipe:start -->', '<!-- wisdom-loadout-recipe:end -->'),
    'priorities': ('<!-- wisdom-affix-priority:start -->', '<!-- wisdom-affix-priority:end -->'),
    'onepage': ('<!-- wisdom-onepage-summary:start -->', '<!-- wisdom-onepage-summary:end -->'),
}
COLORS = {
    'Colorless': {'Colorless'}, 'Red': {'Colorless', 'Red'},
    'Blue': {'Colorless', 'Blue'}, 'Yellow': {'Colorless', 'Yellow'},
    'Orange': {'Colorless', 'Red', 'Yellow', 'Orange'},
    'Purple': {'Colorless', 'Red', 'Blue', 'Purple'},
    'Green': {'Colorless', 'Blue', 'Yellow', 'Green'},
    'Sun': {'Sun'}, 'Moon': {'Moon'},
}
TYPE_EQUIVALENTS = {'Insight Natural': 'Insight', 'Primal Natural': 'Primal', 'Profane Natural': 'Profane'}


def load(path=None):
    """Read the manifest without changing files or deriving new game facts."""
    return json.loads(Path(path or MANIFEST).read_text(encoding='utf-8'))


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _record(relative, expected_hash=None):
    path = (ROOT / relative).resolve()
    _require(path.is_relative_to(ROOT), 'Evidence record escapes the repository')
    raw = path.read_bytes()
    if expected_hash:
        _require(sha256(raw).hexdigest() == expected_hash, 'Derived evidence hash mismatch: ' + relative)
    return json.loads(raw)


def _affix_tuple(affixes):
    return sorted((a['stat'], a['type'], a['value']) for a in affixes)


def _craft_tuple(craft):
    return (craft['host'], craft['family'], craft['slot'], craft['pool'],
            craft['category'], craft['tier'], craft['name'], tuple(_affix_tuple(craft['affixes'])))


def aggregate(data):
    """Independent highest-per-type arithmetic over this explicit recipe only.

    Boolean/proc presence remains separate. No uptime, weapon profile, damage
    simulation, filigree effect, ability modifier, armor cap or set suppression
    rule is invented by this helper.
    """
    buckets, flags = {}, {}
    inputs = []
    for item in data['items']:
        inputs.append((item['id'], item['model_affixes']))
        inputs.extend((item['id'], craft['affixes']) for craft in item['crafts'])
        inputs.extend((socket['fill']['id'], socket['fill']['affixes'])
                      for socket in item['sockets'] if socket['fill']['kind'] == 'augment')
    inputs.extend((aset['name'], aset['effects']) for aset in data['augment_sets'])
    for source, affixes in inputs:
        for affix in affixes:
            stat, kind, value = affix['stat'], affix['type'], affix['value']
            _require(isinstance(value, (int, float)) and not isinstance(value, bool), 'Non-numeric model affix')
            if kind == 'Bool':
                flags[stat] = max(flags.get(stat, 0), value)
                continue
            kind = TYPE_EQUIVALENTS.get(kind, kind)
            names = ['Physical Sheltering', 'Magical Sheltering'] if stat == 'Sheltering' else [stat]
            for name in names:
                key = (name, kind)
                old = buckets.get(key)
                if old is None or value > old['value']:
                    buckets[key] = {'stat': name, 'type': kind, 'value': value, 'sources': [source]}
                elif value == old['value']:
                    old['sources'].append(source)
    totals = defaultdict(float)
    for bucket in buckets.values():
        totals[bucket['stat']] += bucket['value']
    totals = {key: int(value) if value.is_integer() else value for key, value in totals.items()}
    effective = {**totals, **flags}
    exclusions = data['query'].get('excludedTypes', {})
    exclusions = exclusions if isinstance(exclusions, list) else exclusions.values()
    for bucket in buckets.values():
        if any(row['stat'] == bucket['stat'] and row['bonus_type'] == bucket['type'] for row in exclusions):
            effective[bucket['stat']] -= bucket['value']
    effective['Combustion'] = totals.get('Combustion', 0) + totals.get('Universal Spell Power', 0)
    return {'totals': totals, 'presence_flags': flags, 'effective': effective, 'buckets': list(buckets.values())}


def validate(data):
    """Reject drift from frozen recipe/query and invalid construction/math.

    A pass says the authored guide is faithful to the retained analysis; it
    cannot promote a source grade, certify the game, or declare optimal DPS.
    Raises ValueError with the first failed invariant. Does not write files.
    """
    _require(data.get('schema') == 'wisdom-loadout-v1', 'Unsupported manifest schema')
    provenance = data['provenance']
    production = _record(provenance['production']['path'], provenance['production']['record_sha256'])
    selected = _record(provenance['selected']['path'], provenance['selected']['record_sha256'])
    startup = _record(provenance['startup_record'])
    evidence = data['evidence']
    claims = _record(evidence['claim_inventory'], evidence['record_sha256']['claims'])
    derivation = _record(evidence['derivation'], evidence['record_sha256']['derivation'])
    _record(evidence['sources'], evidence['record_sha256']['sources'])
    _require(provenance['selected']['sha256'] == selected['origin']['sha256'] == startup['selected_loadout_sha256'], 'Selected original source SHA differs from startup')
    _require(provenance['production']['sha256'] == production['origin']['sha256'], 'Production original source SHA mismatch')
    _require(production['status'] == provenance['production']['status'] == 'optimal', 'Actual ancestor is not optimal')
    _require(provenance['production']['passes'] == production['passes'] and provenance['production']['seconds'] == production['elapsed_seconds'], 'Actual run receipt drift')
    _require(data['selection']['status'] == selected['status'] == 'manual-feasible', 'Manual derivative mislabeled as an actual solve')
    _require(data['selection']['certified_mechanics'] is False, 'Model promoted to mechanics certification')
    _require(data['query'] == production['query'], 'Exact original query, target order, caps, floors or pins changed')
    _require(len(data['query']['targets']) == 32 and data['query']['targets'][28] == 'Wisdom', 'Wisdom is objective 29, not objective one')
    _require(data['query']['mlCap'] == data['selection']['full_kit_ml'] == 36, 'Full-kit level drift')
    _require(provenance['guide_commit'] == startup['immutable_base_sha'] == selected['guide_commit'], 'Guide base drift')
    _require(provenance['optimizer_commit'] == production['optimizer_commit'] == selected['optimizer_commit'], 'Optimizer commit drift')
    _require(provenance['dataset_sha256'] == production['dataset_sha256'] == selected['dataset_sha256'], 'Dataset identity drift')
    items = data['items']
    catalog = selected['catalog_metadata']
    _require(catalog['origin']['sha256'] == provenance['dataset_sha256'], 'Selected catalog metadata identity drift')
    native_items = {item['id']: item for item in catalog['items']}
    native_gems = {gem['id']: gem for gem in catalog['augments']}
    def native_grade(component, affix):
        return next((claim['status'] for claim in claims['claims']
                     if claim['kind'] == 'item' and claim['component'] == component
                     and (claim['stat'], claim['type'], claim['value'])
                     == (affix['stat'], affix['type'], affix['value'])), 'model-only')
    _require([(i['slot'], i['id']) for i in items] == [(i['slot'], i['id']) for i in selected['chosen']], 'Selected item identity or slot changed')
    _require(len(items) == len({i['id'] for i in items}) == 14, 'Fourteen distinct equipment items required')
    artifacts = [i['id'] for i in items if i['minor_artifact']]
    _require(artifacts == ["Yeenoghu's Reign"], 'Exactly the selected Yeenoghu minor artifact is required')
    slots = Counter(i['slot'] for i in items)
    _require(slots['Ring'] == 2 and all(n == (2 if k == 'Ring' else 1) for k, n in slots.items()) and not slots['Off Hand'], 'Equipment cardinality mismatch')
    _require(data['selection']['primary_bow'] == 'Legendary Calamitous Longbow', 'Primary bow changed')
    for slot, pin in data['query']['slotConstraints'].items():
        if pin['type'] == 'pin':
            _require(any(i['id'] == pin['variant_id'] and i['slot'] == slot for i in items), 'Pinned item missing: ' + slot)
    ordinary, set_placements, physical = [], [], []
    set_hosts = set()
    for item, original in zip(items, selected['chosen']):
        _require(item['base_ml'] == original['base_ml'] and item['minor_artifact'] == original['artifact'], 'Item level/artifact drift: ' + item['id'])
        _require(item['model_affixes'] == original['affixes'], 'Selected item affix drift: ' + item['id'])
        native = native_items[item['id']]
        expected_native = [{**a, 'evidence_status': native_grade(item['id'], a)} for a in native['native_affixes']]
        _require(item['native_affixes'] == expected_native, 'Visible native affix value or evidence grade changed: ' + item['id'])
        _require(not native['native_sets'], 'A new native set requires an explicit suppression audit')
        _require([s['color'] for s in item['sockets']] == original['sockets'], 'Physical socket list changed: ' + item['id'])
        _require([s['index'] for s in item['sockets']] == list(range(len(item['sockets']))), 'Duplicate or reordered physical socket')
        _require(item['id'] not in data['query']['blocklist'], 'Blocked item selected')
        used_crafts = set()
        for craft in item['crafts']:
            _require(craft['host'] == item['id'], 'Craft moved to a wrong host')
            key = (craft['family'], craft['pool'] or craft['slot'])
            _require(key not in used_crafts, 'Duplicate craft choice on one slot')
            used_crafts.add(key)
        for socket in item['sockets']:
            fill = socket['fill']
            _require(fill['color'] in COLORS.get(socket['color'], set()), 'Augment color does not fit its host')
            _require(isinstance(fill['ml'], int) and 0 <= fill['ml'] <= data['query']['mlCap'], 'Augment minimum level invalid')
            _require(fill['id'] not in data['query']['blocklist'], 'Blocked augment selected')
            physical.append(socket)
            if fill['kind'] == 'set-augment':
                _require(set(fill) == {'kind', 'id', 'color', 'ml', 'affixes'}, 'Undeclared set-fill metadata or source-grade promotion')
                _require(item['id'] not in set_hosts and socket['color'] not in {'Sun', 'Moon'}, 'Two set augments on one host or nonstandard set socket')
                _require(fill['color'] == 'Colorless' and fill['ml'] == 30 and not fill['affixes'], 'Set augment metadata drift')
                set_hosts.add(item['id'])
                set_placements.append({'name': fill['id'], 'host': item['id'], 'color': socket['color']})
            else:
                _require(fill['kind'] == 'augment', 'Unknown socket fill kind')
                _require(set(fill) == {'kind', 'id', 'color', 'ml', 'wiki_url', 'affixes', 'native_affixes', 'festive_exception'}, 'Undeclared gem metadata or source-grade promotion')
                _require(fill['id'] in native_gems, 'Gem not in frozen selected catalog extraction')
                gem = native_gems[fill['id']]
                _require(fill['ml'] == gem['ml'] and fill['color'] == gem['color'] and fill['native_affixes'] == gem['native_affixes'], 'Visible augment value, color or minimum level changed')
                _require(fill['festive_exception'] == ('Festive' in fill['id']), 'Festive exception labeling changed')
                ordinary.append({'id': fill['id'], 'color': fill['color'], 'slot_color': socket['color'], 'affixes': fill['affixes']})
        _require(item['filled_ml'] == max([item['base_ml']] + [s['fill']['ml'] for s in item['sockets']]), 'Filled-host minimum level drift: ' + item['id'])
    key = lambda x: json.dumps(x, sort_keys=True)
    _require(sorted(map(_craft_tuple, (c for i in items for c in i['crafts']))) == sorted(map(_craft_tuple, selected['crafts'])), 'Exact craft host, family, slot, value or option changed')
    _require(sorted(ordinary, key=key) == sorted(selected['augments'], key=key), 'Non-set augment recipe changed')
    _require(len(ordinary) == len({x['id'] for x in ordinary}), 'Repeated non-set gem')
    _require(sorted(set_placements, key=key) == sorted(selected['set_placements'], key=key), 'Selected set host allocation changed')
    for aset, original in zip(data['augment_sets'], selected['sets']):
        _require({k: aset[k] for k in ['name', 'threshold']} == {k: original[k] for k in ['name', 'threshold']}, 'Set identity/threshold drift')
        _require(aset['effects'] == original['effects'], 'Set effect changed')
        _require(aset['evidence_status'] == 'retained-source supported; combined totals remain subject to the current ledger gates', 'Set source grade promoted')
        _require(len(aset['placements']) == aset['threshold'] == 3 and len({x['host'] for x in aset['placements']}) == 3, 'Set lacks three distinct hosts')
        _require(sorted([{'name': aset['name'], **x} for x in aset['placements']], key=key) == sorted([x for x in set_placements if x['name'] == aset['name']], key=key), 'Set summary disagrees with physical placements')
    _require(len(data['augment_sets']) == 4, 'Exactly four selected augment sets required')
    counts = {'items': len(items), 'artifacts': len(artifacts), 'sockets': len(physical), 'occupied': len(physical), 'ordinary': sum(x['color'] not in {'Sun', 'Moon'} for x in physical), 'sun_moon': sum(x['color'] in {'Sun', 'Moon'} for x in physical), 'set_placements': len(set_placements), 'ordinary_augment_placements': len(ordinary)}
    _require(counts == data['counts'], 'Socket/count summary drift')
    _require(counts['sockets'] == 34 and counts['set_placements'] == 12, 'Primary capacity changed')
    ring = next(i for i in items if i['id'] == 'Legendary Celestial Sapphire Ring')
    _require(not ring['crafts'] and ring['empty_craft_slots'] == [{'family': 'Nearly Finished', 'slot': 'Nearly Finished', 'selected': False}], 'Optional ring craft leaked into primary')
    _require(data['optional']['ring_dexterity_13']['selected'] is False and data['optional']['ring_dexterity_13']['evidence_status'] == 'model-only', 'Optional ring branch selected or source-promoted')
    optional = data['optional']['ring_dexterity_13']
    _require((optional['host'], optional['pool'], optional['stat'], optional['type'], optional['value']) == ('Legendary Celestial Sapphire Ring', 'Nearly Finished', 'Dexterity', 'Enhancement', 13), 'Optional ring identity or provisional magnitude changed')
    _require(optional['gear_dexterity_if_selected'] == data['model']['totals']['Dexterity'] + optional['value'], 'Optional-only gear Dexterity arithmetic changed')
    _require(data['optional']['sinew']['selected'] is False and data['optional']['sinew']['studied_by_this_run'] is False, 'Sinew falsely represented as a solved output')
    calculated = aggregate(data)
    model = data['model']
    _require(model['raw_production_totals'] == production['independent_raw_totals'], 'Full raw production receipt changed')
    _require(calculated['totals'] == model['totals'], 'Independent raw arithmetic mismatch')
    _require(calculated['presence_flags'] == model['presence_flags'], 'Presence/proc flag mismatch')
    _require(calculated['effective'] == model['objective_comparable_totals'], 'Objective exclusions or effective totals changed')
    normalize = lambda rows: sorted((r['stat'], r['type'], r['value'], tuple(sorted(r['sources']))) for r in rows)
    _require(normalize(calculated['buckets']) == normalize(model['type_buckets']), 'Typed maximum buckets/source identities changed')
    for stat in data['query']['targets']:
        achieved = min(calculated['effective'].get(stat, 0), data['query']['targetCaps'].get(stat, float('inf')))
        _require(achieved == model['ranked'][stat] == selected['per_target'][stat], 'Capped target arithmetic mismatch: ' + stat)
    for stat, minimum in data['query']['targetFloors'].items():
        _require(calculated['effective'].get(stat, 0) >= minimum, 'Independent floor shortfall: ' + stat)
    _require(model['totals']['Wisdom'] == 18 and model['totals']['Dexterity'] == 6, 'Primary WIS/DEX identity changed')
    _require(model['raw_production_totals']['Constitution'] == 34 and model['totals']['Constitution'] == 32, 'Raw-versus-practical utility tradeoff hidden')
    _require(model['independent_checks']['count'] == derivation['independent_review']['check_count'] == 373 and derivation['independent_review']['passed'], 'Original independent audit receipt drift')
    _require(model['floor_checks'] == derivation['independent_review']['floors'], 'Original independent floor receipt drift')
    _require(claims['coverage']['selectedAffixes'] == len(claims['claims']) == 130, 'Claim inventory coverage drift')
    _require(dict(Counter(c['status'] for c in claims['claims'])) == claims['coverage']['byStatus'], 'Claim evidence-grade counts changed')
    _require(data['manual_adjustments'] == selected['manual_derivation'], 'Manual provenance changed')
    festive = [s['fill']['id'] for i in items for s in i['sockets'] if s['fill'].get('festive_exception')]
    _require(data['policy']['primary_festive_items'] == festive == ['Diamond of Festive Intelligence +2'], 'Selected event exception changed')
    _require(len(data['comparison']['guide_item_changes']) == 4, 'Old-guide equipment replacement count changed')
    for row in data['comparison']['rows']:
        for field, model_key in [('guide', 'guide_totals'), ('prior', 'prior_totals'), ('selected', 'totals')]:
            _require(row[field] == model[model_key].get(row['stat'], 0), 'Three-way comparison drift')
    for comparison in derivation['comparison']['comparisons']:
        if comparison['from'] in {'guide-queen-basic', 'prior-artifact-luck'}:
            source = model['guide_totals' if comparison['from'] == 'guide-queen-basic' else 'prior_totals']
            for row in comparison['allNumericRows']:
                _require(row['from'] == source.get(row['stat'], 0), 'Former-guide/prior model receipt changed')
    return {'passed': True, 'items': len(items), 'artifacts': len(artifacts), 'sockets': len(physical), 'floors': len(data['query']['targetFloors']), 'claim_count': len(claims['claims']), 'certified_mechanics': False}


def _h(value):
    return escape(str(value), quote=True)


def _link(url, label):
    _require(not re.match(r'\s*(?:javascript|data):', url, re.I), 'Unsafe rendered URL')
    return '<a href="' + _h(url) + '">' + _h(label) + '</a>'


def _affix_text(affix):
    if affix['type'] == 'Bool':
        return affix['stat'] + ' — present; conditions apply'
    if affix['stat'] == 'Improved Deception':
        return 'Improved Deception — conditional proc; catalog +5 is Bluff, not proc chance'
    return f"{affix['stat']} +{affix['value']} ({affix['type']})"


def _list(lines):
    return '<ul>' + ''.join('<li>' + line + '</li>' for line in lines) + '</ul>' if lines else 'None selected'


def _table(identifier, caption, headers, rows):
    return ('<p class="note">Wide table: focus this region and scroll horizontally if needed.</p>\n'
            f'<div class="tw" tabindex="0" role="region" aria-labelledby="{identifier}">'
            f'<table><caption id="{identifier}">{_h(caption)}</caption><thead><tr>'
            + ''.join('<th scope="col">' + _h(x) + '</th>' for x in headers)
            + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>')


def _cells(values):
    return '<tr>' + ''.join(('<th scope="row">' if n == 0 else '<td>') + value + ('</th>' if n == 0 else '</td>') for n, value in enumerate(values)) + '</tr>'


def render_recipe(data):
    """Render the complete physical primary recipe, model context and limits."""
    validate(data)
    p = data['provenance']['production']
    model, counts = data['model'], data['counts']
    current, raw = model['totals'], model['raw_production_totals']
    prior, guide = model['prior_totals'], model['guide_totals']
    out = ['<section id="wisdom-loadout-selection" aria-labelledby="wisdom-loadout-title">',
           '<h3 id="wisdom-loadout-title">' + _h(data['selection']['label']) + '</h3>',
           '<p><span class="tag">PRIMARY RECIPE · MODEL-ONLY COMBINATIONS</span> '
           f'{counts["items"]} items, exactly {counts["artifacts"]} Minor Artifact and {counts["occupied"]} occupied sockets. The fully filled kit requires level {data["selection"]["full_kit_ml"]}. '
           'Base and filled minimum levels are shown separately below; Calamitous remains filled ML 34.</p>',
           f'<p>The actual optimizer ancestor completed {_h(p["passes"])} stages in {_h(p["seconds"])} seconds. '
           'The selected practical recipe is an independently checked <strong>manual derivative</strong>, not another solve or the unchanged lexicographic optimum. '
           'Equal-type craft rotations, an unused Chains Spot slot and Good Luck replacing Festive Constitution restore utility: '
           f'raw-run CON {raw["Constitution"]} becomes CON {current["Constitution"]}; direct Spot {raw["Spot"]} becomes Spot {current["Spot"]} and direct saves rise by {current["Will Save"] - raw["Will Save"]}. '
           'The explicit query order below still describes the actual search, not this subsequent utility choice.</p>',
           '<p>No event or limited-time gear is selected; the user-authorized Festive ability diamonds are the only exception. '
           'The primary uses Festive Intelligence +2 only. Shard-auction availability and prices are not guaranteed. '
           'No filigree loadout, proc uptime, total DPS improvement, critical-range increase or global optimum is established.</p>']
    rows = []
    for item in data['items']:
        crafts = [_h(c['family'] + ' / ' + c['slot'] + ': ') + _h('; '.join(map(_affix_text, c['affixes']))) for c in item['crafts']]
        crafts += [_h(c['family'] + ': explicitly unselected') for c in item['empty_craft_slots']]
        gems = []
        for socket in item['sockets']:
            fill = socket['fill']
            label = ('Set augment: ' if fill['kind'] == 'set-augment' else '') + fill['id']
            gems.append('<strong>' + _h(socket['color']) + ':</strong> ' + _h(label) + ' (ML' + _h(fill['ml']) + ')')
        note = _list([_h(x) for x in item['notes']]) if item['notes'] else ''
        rows.append(_cells([_h(item['slot']), _link(item['wiki_url'], item['id']) + (' <span class="tag">MINOR ARTIFACT</span>' if item['minor_artifact'] else ''),
                            _h(f"{item['base_ml']} → {item['filled_ml']}"), _list(crafts), _list(gems) + note]))
    out.append(_table('wisdom-recipe-table', 'Exact selected equipment, crafting and every socket', ['Slot', 'Selected item', 'Base → filled ML', 'Selected crafting', 'Exact socket recipe and prerequisites'], rows))
    out.append('<p class="note"><strong>Construction prerequisites:</strong> Chains requires the Legendary Slaver’s Green Augment Slot upgrade '
               '(100 Legendary Staff Splinters and 50 each Legendary Broken Shackles, Chain Links and Broken Collars). '
               'Claws Nearly Complete is irreversible: changing an already finished Dexterity pair to Wisdom requires a new pair. '
               'Coldlight retains Melancholic Intelligence but changes the former guide’s Dolorous Quality Intelligence to Quality Constitution. '
               'The Celestial Sapphire ring’s Nearly Finished slot is deliberately empty. No Slaver set membership or extra ordinary socket is invented.</p>')
    set_rows = [_cells([_h(s['name']), _h('; '.join(map(_affix_text, s['effects']))), _list([_h(x['host'] + ' — ' + x['color']) for x in s['placements']])]) for s in data['augment_sets']]
    out.append(_table('wisdom-set-table', 'Four augment sets — three distinct hosts each', ['Set', 'Catalog effects, not certified combined totals', 'Exact three hosts'], set_rows))
    out.append('<p>Each set uses one ordinary socket on each of three distinct hosts; at most one set augment is placed on a host. '
               'Set augments suppress their host’s native set membership, if any; the retained selected audit found no native set to suppress. '
               f'The {counts["sockets"]} sockets are {counts["ordinary"]} ordinary-color positions plus {counts["sun_moon"]} Sun/Moon positions. '
               f'{counts["set_placements"]} hold set augments; the remaining {counts["ordinary_augment_placements"]} hold non-set gems.</p>')
    change_rows = [_cells([_h(x['slot']), _h(', '.join(x['before'])), _h(', '.join(x['after']))]) for x in data['comparison']['guide_item_changes']]
    out.append(_table('wisdom-equipment-changes', 'Four equipment replacements from the former guide kit', ['Slot', 'Former guide', 'Selected Wisdom recipe'], change_rows))
    rows = [_cells([_h(x['stat']), _h(x['guide']), _h(x['prior']), _h(x['selected'])]) for x in data['comparison']['rows']]
    out.append(_table('wisdom-model-comparison', 'Modeled gear contributions only — not full character scores or certified totals', ['Stat / direct contribution', 'Former guide kit', 'Prior artifact kit', 'Primary Wisdom kit'], rows))
    out.append('<p class="note"><strong>Tradeoffs remain visible:</strong> the primary keeps the prior artifact kit’s modeled offense and direct saves, '
               f'but its DEX contribution falls {prior["Dexterity"]} → {current["Dexterity"]} as WIS rises {prior["Wisdom"]} → {current["Wisdom"]}. '
               f'Against the former guide, Fortification falls {guide["Fortification"]} → {current["Fortification"]} and direct Spot {guide["Spot"]} → {current["Spot"]}; '
               'the retained three-way record includes the other utility and resistance losses. This is not a dominance claim. '
               'Whole-character ability changes require same-type overlap reconciliation: for each type, compare max(new gear, other source) '
               'with max(old gear, other source). A +15 Enhancement WIS gear change can be partly or fully masked by another Enhancement source. '
               'Only the no-overlap cases yield +7 or +8 to the Wisdom modifier. DEX-linked skills and AC require the same reconciliation; AC also depends on armor’s maximum Dexterity bonus. '
               'Unchanged direct Reflex and INT preserve intended Reflex only while Insightful Reflexes uses INT in both kits.</p>')
    out.append(f'<p><strong>Optional, not selected:</strong> the ring’s catalog Nearly Finished Dexterity +13 choice would make the modeled gear DEX contribution {data["optional"]["ring_dexterity_13"]["gear_dexterity_if_selected"]}. '
               'Its exact magnitude remains independently unconfirmed; it is not silently included in any primary total. '
               'Sinew remains the guide’s separate conditional bow alternate, not a result explored by this pinned-Calamitous run.</p>')
    out.append('<details><summary>Selected native affixes and typed model contributors</summary><p>Catalog inputs below are inventory, not source-qualified totals. '
               'Conditional names are not permanent combat bonuses. Bloodrage refers to conditional Melee Power, not Ranged Power; Major Anger is not an always-on ability increase. '
               'Seeker is not critical threat range. See the separate component ledger for source-qualified evidence.</p>')
    for item in data['items']:
        out.append('<h4>' + _h(item['id']) + '</h4>' + _list([_h(_affix_text(a) + ' — ' + a['evidence_status']) for a in item['native_affixes']]))
    bucket_rows = [_cells([_h(x['stat']), _h(x['type']), _h(x['value']), _h('; '.join(x['sources']))]) for x in data['model']['type_buckets']]
    out.append(_table('wisdom-type-buckets', 'Highest-of-type catalog buckets — not certified stacking', ['Stat', 'Type', 'Modeled maximum', 'Source of maximum'], bucket_rows))
    out.append('</details>')
    claims = _record(data['evidence']['claim_inventory'], data['evidence']['record_sha256']['claims'])
    grades = '; '.join(f'{n} {status}' for status, n in claims['coverage']['byStatus'].items())
    out.append('<p class="note"><strong>Evidence coverage:</strong> ' + _h(grades) + '. These are independent inventory grades, not the current ledger’s certification decisions. '
               'The five exact crafting gaps are Pendant Insightful INT 7 and Chains Fortification 142, Combustion 142, Quality INT 3 and Spot 20. '
               'Queen retains the A-074 relay limitations. Skull’s generic CON 15 versus item-page 16 conflict yields separate modeled 32 and own-page 33 cases; '
               'the same Skull Constitution choice appears in the compared kits. No unresolved input is promoted by passing arithmetic.</p>')
    out.append('<p>' + _link('tools/fixtures/wisdom-loadout/selection.json', 'Shared selection manifest') + ' · '
               + _link(data['provenance']['production']['path'], 'Actual-run receipt and exact query') + ' · '
               + _link(data['evidence']['derivation'], 'Manual changes and three-way audit') + ' · '
               + _link(data['evidence']['claim_inventory'], 'Complete claim inventory') + ' · '
               + _link(data['evidence']['sources'], 'Source review and exclusion limits') + '. '
               'Full source hashes are retained in these records. Derived analysis copies are not new browser captures.</p></section>')
    return '\n'.join(out)


def render_priorities(data):
    """Render exact original lexicographic order, not a sorted stat wishlist."""
    validate(data)
    query, model = data['query'], data['model']
    rows = []
    for rank, stat in enumerate(query['targets'], 1):
        cap, floor = query['targetCaps'].get(stat), query['targetFloors'].get(stat)
        actual = model['objective_comparable_totals'].get(stat, 0)
        achieved = 'Present — conditional effect held' if rank <= 8 else str(actual)
        notes = 'Presence guard; no uptime or DPS credited' if rank <= 8 else 'Catalog arithmetic; not a full-character result'
        if stat == 'Improved Deception':
            notes = 'Presence guard. Catalog 5 is Bluff, not proc chance, damage or five effects.'
        elif stat == 'Bloodrage':
            notes = 'Conditional Melee Power effect held; not a Ranged Power contribution.'
        elif stat == 'Seeker':
            notes = 'Critical confirmation / damage input, not critical threat range.'
        elif stat == 'Constitution':
            notes = 'Raw solve 34; practical Good Luck derivative 32. Skull source conflict remains.'
        elif stat == 'Wisdom':
            notes = 'Replaces the previous Dexterity target at rank 29; not the first priority.'
        elif stat == 'Deadly':
            notes = 'Insight type excluded from objective because of Know the Angles; no proc DPS.'
        elif stat in {'Physical Sheltering', 'Magical Sheltering', 'Dodge'}:
            notes = 'Raw gear contribution, before whole-character adjustments and applicable game caps.'
        elif stat == 'Sneak Attack Damage':
            notes = 'Flat sneak damage; distinct from the preceding sneak dice target.'
        body = ''.join('<td>' + _h(x) + '</td>' for x in [cap if cap is not None else 'None', floor if floor is not None else 'None', achieved, notes])
        rows.append(f'<tr data-priority-rank="{rank}" data-stat="{_h(stat)}"><th scope="row">{rank}</th><td>{_h(stat)}</td>{body}</tr>')
    out = ['<section id="current-affix-priority" aria-labelledby="current-affix-priority-title">',
           '<h3 id="current-affix-priority-title">Affixes in the actual loadout search order</h3>',
           '<p>This is the completed optimizer query’s exact 32-target lexicographic order: each earlier target is settled before the next. '
           'The first eight are named-effect presence guards, not eight damage scores. Caps and floors are <strong>search settings</strong>, not the game’s stat caps. '
           'Achieved values below belong to the selected practical manual recipe, not a claim that this derivative remains the raw optimum.</p>',
           _table('wisdom-priority-table', 'Actual priority sequence with search caps, floors and selected modeled contributions', ['Rank', 'Exact optimizer target', 'Search cap', 'Search floor', 'Primary achieved / presence', 'Interpretation'], rows)]
    floors = [_cells([_h(stat), _h(value), _h(model['objective_comparable_totals'].get(stat, 0)), 'Pass in independent arithmetic']) for stat, value in query['targetFloors'].items()]
    out.append(_table('wisdom-floor-table', 'All independent search floors, including utility effects outside the ranked list', ['Constraint', 'Minimum', 'Selected modeled value / presence', 'Result'], floors))
    out.append('<p class="note">Improved Deception’s floor/cap 1 tests presence only; its numeric 5 is a Bluff bonus, not a proc percentage. '
               'The search pins ten items, including Calamitous and Yeenoghu, and searches the necklace, belt and rings. '
               'It is not an unrestricted all-gear optimum. The query’s Human and null-alignment fields are search eligibility settings, not proof that every class, race, life or alignment qualifies. '
               'The selected light-armor kit, weapon proficiency, feat/tree prerequisites, artifact unlocks and nongear contributions still need their own applicable checks.</p>')
    pins = [_cells([_h(slot), _h(value['variant_id'])]) for slot, value in query['slotConstraints'].items() if value['type'] == 'pin']
    out.append('<details><summary>Fixed equipment in this search</summary>' + _table('wisdom-query-pins', 'Exact ten equipment pins in the original query', ['Slot', 'Pinned item'], pins) + '</details>')
    out.append('<p>The shared manifest preserves the complete query, including every exclusion, target order, type exclusion, pin, cap and floor. '
               'Insight Deadly is not added on top of Know the Angles. Gear alone does not establish final critical range, critical damage, Doubleshot effectiveness, imbue scaling or sustained DPS.</p></section>')
    return '\n'.join(out)


def render_onepage_rows(data):
    validate(data)
    targets = data['query']['targets']
    model, counts = data['model']['totals'], data['counts']
    totals = ' / '.join(f'{label} {model[stat]}' for label, stat in [('WIS', 'Wisdom'), ('DEX', 'Dexterity'), ('INT', 'Intelligence'), ('CON', 'Constitution'), ('direct Spot', 'Spot')])
    return ('<tr data-loadout-summary="priority"><th scope="row">Gear affixes, in order</th><td>'
            '<a href="#current-affix-priority">Exact 32-target search order</a>: eight named-effect presence guards, then '
            + _h(' → '.join(targets[8:])) + '. Wisdom replaces Dexterity at rank 29; caps/floors and conditions are explicit. '
            'Practical Spot / Good Luck refinements are a manual utility tradeoff, not another optimal solve.</td></tr>\n'
            '<tr data-loadout-summary="kit"><th scope="row">Kit</th><td>'
            f'<a href="#wisdom-loadout-selection">Wisdom-priority artifact recipe</a>: full kit ML {data["selection"]["full_kit_ml"]}; {counts["items"]} items; Yeenoghu’s Reign is the sole Minor Artifact; '
            f'{counts["occupied"]}/{counts["sockets"]} sockets. Claws selects WIS 15; ring Nearly Finished is empty. Model-only gear {_h(totals)}. '
            'Optional ring DEX 13 is separate and provisional. No event/limited gear except permitted Festive diamonds; source gaps remain visible.</td></tr>')


def replace_blocks(html, data):
    """Replace exactly the three named blocks; never touch unrelated HTML."""
    validate(data)
    renderers = {'recipe': render_recipe, 'priorities': render_priorities, 'onepage': render_onepage_rows}
    for kind, (start, end) in MARKERS.items():
        _require(html.count(start) == html.count(end) == 1, 'Expected one marker pair: ' + kind)
        left, right = html.index(start), html.index(end)
        _require(left < right, 'Reversed markers: ' + kind)
        html = html[:left + len(start)] + '\n' + renderers[kind](data) + '\n' + html[right:]
    return html
