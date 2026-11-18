"""Render a report-derived recipe without reusing historical mechanics proofs."""
from collections import Counter
from hashlib import sha256
from html import escape as h
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = 'sinew-rocard-report-v1'
SOURCE = 'evidence/sinew-rocard-report-extract-2026-11-18.json'
SOURCE_SHA256 = '61c58eac3c6166b5f781a6ad153066263e37140495b84a1c9743b70a128eb9eb'

AUDIT_STYLE = '\n:root{color-scheme:dark;background:#101722;color:#e4eaf2;font:17px/1.6 system-ui,sans-serif}body{max-width:1140px;margin:auto;padding:24px}a{color:#9ed1ff}h1,h2,h3{line-height:1.2}h2{margin-top:2.5rem;border-top:1px solid #465568;padding-top:1rem}table{border-collapse:collapse;width:100%;font-size:.92rem}th,td{padding:10px;text-align:left;vertical-align:top;border-bottom:1px solid #465568}th{background:#202d3e}.tw{overflow-x:auto}caption{text-align:left;font-weight:700;padding:12px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.5 ui-monospace,monospace}code{overflow-wrap:anywhere}details{border:1px solid #465568;border-radius:6px;padding:12px;margin:12px 0}summary{cursor:pointer;font-weight:700}.note{border-left:4px solid #e9bd6c;padding-left:14px}.unknown{color:#f2ce92}nav a{margin-right:16px}@media(max-width:600px){body{padding:16px}th,td{padding:8px}table{min-width:650px}}\n'
AUDIT_NAV = '<a href="index.html#selected-stacking-summary">Back to the guide</a><a href="#components">Components</a><a href="#unverified">Unverified log</a><a href="#rules">Rules</a><a href="#sources">Source receipts</a>'
LIMITATIONS = ['Not original solver JSON; complete exclusions and policy cuts were not recovered. No optimizer replay or global optimality claim.', 'No new source-qualified stacking proof is established; all report sums remain conditional modeled gear contributions.', 'Specific Skull INT +16 versus generic +15: gear INT37 versus36.', 'Specific Quality Deadly +4 versus generic +3: gear Deadly20 versus19 if applicable.', 'Healing Amplification +63 procurement remains conditional.', 'No event base gear or augment-set bonuses; explicitly selected Festive ability diamonds remain listed as the recipe exception.', 'Sinew Anarchic imposes one negative level on a Lawful wearer; the reported model uses Neutral alignment.']

def validate(data):
    if data.get('schema') != SCHEMA:
        raise ValueError('Unsupported report recipe')
    def require(condition, message):
        if not condition:
            raise ValueError(message)
    require(data['selection']['certified_mechanics'] is False and data['selection']['status'] == 'report-derived-not-replayed', 'Report promoted into certification/replay')
    require(data['provenance']['path'] == SOURCE, 'Unexpected report provenance')
    raw = (ROOT / SOURCE).read_bytes()
    require(sha256(raw).hexdigest() == data['provenance']['sha256'] == SOURCE_SHA256, 'Report transcription changed')
    source = json.loads(raw)
    require(source['provenance']['version_id'] == '1' and source['provenance']['read_lines'] == [321, 544], 'Wrong report version/range')
    require(data['reported_ledger'] == source['ledger'], 'Report ledger drift')
    require(data['query_summary'] == source['settings_summary']['query_summary'], 'Report query summary drift')
    require(data['augment_sets'] == [], 'Augment sets are prohibited')
    items = data['items']
    require(len(items) == len({i['id'] for i in items}) == 14, 'Fourteen distinct items required')
    require(Counter(i['slot'] for i in items) == Counter(i['slot'] for i in source['items']), 'Slot occupancy drift')
    require([i['id'] for i in items if i['minor_artifact']] == ["Rocard, Champion's Cuffs"], 'Rocard must be sole artifact')
    sockets = occupied = 0
    for item, reported in zip(items, source['items']):
        require((item['slot'], item['id'], item['wiki_url']) == (reported['slot'], reported['id'], reported['wiki_url']), 'Item identity drift')
        require(f"{item['base_ml']} → {item['filled_ml']}" == reported['levels'], 'Level drift')
        require(item['crafts'] == reported['crafts'], 'Selected craft drift')
        rendered = [f"{s['color']}: {s['fill']} · ML{s['ml']}" for s in item['sockets'] if s['fill'] is not None]
        require(rendered == reported['socket_lines'], 'Socket recipe drift')
        empties = [f"{s['color']}: 1 empty" for s in item['sockets'] if s['fill'] is None]
        require(empties == [color + ': 1 empty' for color in re.findall(r'(Green|Colorless): 1 empty', reported['socket_text'])], 'Unreported empty socket')
        require(len(empties) == reported['socket_text'].count('1 empty'), 'Missing empty socket')
        require(item['filled_ml'] == max([item['base_ml']] + [s['ml'] for s in item['sockets'] if s['fill'] is not None]), 'Effective level mismatch')
        sockets += len(item['sockets']); occupied += len(rendered)
    require(max(i['filled_ml'] for i in items) == data['selection']['full_kit_ml'] == 36, 'Finished kit level mismatch')
    for row in data['reported_ledger']:
        if row['total'] is not None:
            require(sum(float(s.split()[0]) for s in row['sources']) == row['total'], 'Displayed numeric contributor sum mismatch: ' + row['stat'])
    require(data['limitations'] == LIMITATIONS, 'Source/eligibility limitations drift')
    return {'items': 14, 'artifacts': 1, 'sockets': sockets, 'occupied': occupied, 'certified_mechanics': False}


def cells(values):
    return '<tr>' + ''.join('<td>'+v+'</td>' for v in values) + '</tr>'


def table(caption, headers, rows):
    return '<div class="tw" tabindex="0" role="region" aria-label="'+h(caption)+'"><table><caption>'+h(caption)+'</caption><thead><tr>'+''.join('<th scope="col">'+h(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'


def listing(values):
    return '<ul>'+''.join('<li>'+h(x)+'</li>' for x in values)+'</ul>' if values else 'None selected'


def limits(data):
    return '<p class="note"><strong>Report evidence only.</strong> The companion report was read through Library; the archive transfer failed. This fixture reconstructs the report’s selected recipe and displayed contributors, not an original solver output or a replay. Passing checks establishes transcription and displayed arithmetic only. No new certified game totals or positive stacking proofs are claimed.</p>'+listing(data['limitations'])


def render_recipe(data):
    counts = validate(data)
    rows=[]
    for item in data['items']:
        sockets=[s['color']+': '+(s['fill']+' (ML'+str(s['ml'])+')' if s['fill'] else 'Empty') for s in item['sockets']]
        craft=list(item['crafts'])
        if item['slot']=='Armor':craft.insert(0,'Mandatory Reflection upgrade: base armor + 120 Barrier Fragments + 1 Sigil of the Warblade; Ritual Table after Threats Old and New. Bring materials before the raid locks.')
        if item['slot']=='Trinket':craft.insert(0,'Mandatory construction: Legendary Planar Compass + Legendary Abyssal Catalyst: Planar Compass + 5 Legendary Abyssal Gems at Strange Catalyst Forge, Gravenhollow.')
        rows.append(cells([h(item['slot']),'<a href="'+h(item['wiki_url'],quote=True)+'">'+h(item['id'])+'</a>'+(' — sole Minor Artifact' if item['minor_artifact'] else ''),f"{item['base_ml']} → {item['filled_ml']}",listing(craft),listing(sockets) if sockets else 'No modeled sockets']))
    return ('<section id="wisdom-loadout-selection" aria-labelledby="wisdom-loadout-title"><h3 id="wisdom-loadout-title">Sinew–Rocard priority kit</h3>'
            '<p><span class="tag">REVIEW RECIPE · REPORTED MODEL</span> Finished level 36; 14 distinct items; Rocard is the sole Minor Artifact; '+str(counts['occupied'])+'/'+str(counts['sockets'])+' sockets occupied. Paralyzing retained; no event base gear or augment-set effects. The five explicitly selected Festive ability diamonds retain the existing exception. Legendary Sun/Moon versions are selected.</p>'
            '<p class="note"><strong>Alignment:</strong> Sinew’s Anarchic effect imposes one negative level on a Lawful wearer. The source model assumes Neutral; this is not unconditional advice for a Lawful life.</p>'
            +table('Exact selected equipment, crafting and every socket',['Slot','Selected item','Base → finished ML','Crafts / construction','Socket recipe'],rows)
            +'<p><strong>Crafting is consequential:</strong> Skull INT and Claws CHA Nearly Complete choices are permanent; an already completed CON Skull or WIS Claws needs another item to match this exact recipe. Queen Insight CON is retained. Boots change Quality CON / Enhancement INT to Quality INT / Enhancement DEX; a Viktranium Pick preserves removed fills, while overwriting destroys them. Claws CHA is a utility fill.</p>'
            +'<p><strong>Source conflicts:</strong> Skull own-item INT +16 versus generic +15 gives modeled gear INT 37 versus 36. Specific Quality Deadly augment +4 versus generic +3 gives modeled Deadly 20 versus 19 if applicable. Both cases remain unresolved. Healing Amplification +63 procurement remains conditional. Armor-Piercing is 46 versus the normalized incumbent’s 76.</p>'
            +limits(data)+'<p><a href="'+SOURCE+'">Derived report transcription and typed contributor ledger</a> · <a href="tools/fixtures/wisdom-loadout/selection.json">Selected manifest</a> · <a href="endgame-stacking-audit.html">Current report audit and limitations</a>. Prior recipes and qualified proofs remain historical evidence; Quickblade is not part of this kit.</p></section>')


def render_priorities(data):
    validate(data); q=data['query_summary'];ledger={r['stat']:r for r in data['reported_ledger']}
    rows=[]
    for n,stat in enumerate(q['targets'],1):
        value=ledger[stat]['reported_value']
        if stat=='Intelligence':value='37 / 36 (Skull +16 / +15)'
        if stat=='Deadly':value='20 / 19 (Quality +4 / +3)'
        rows.append(cells([str(n),h(stat),h(str(q['targetCaps'].get(stat,'None'))),h(str(q['targetFloors'].get(stat,'None'))),h(value)]))
    return '<section id="current-affix-priority"><h3 id="current-affix-priority-title">Reported priority order</h3><p>The source report retains these 32 priorities, then rogue utility. Caps and floors are search settings, not game caps. This is the displayed final-query summary: full exclusions and policy cuts were not recovered, and no optimizer run was replayed. Presence is not uptime or DPS. In particular Fiery and Legendary Salt are absent.</p>'+table('Reported priority settings and gear contributions',['Rank','Affix','Search cap','Search floor','Reported contribution'],rows)+'<p>Human, light armor, Neutral; reported base item floor 29 and cap 36. Reported final query pins this recipe. The saved model is finite and does not establish a global optimum. The normalized incumbent Armor-Piercing comparison is 76 versus this kit’s 46.</p></section>'


def render_onepage_rows(data):
    validate(data)
    return '<tr data-loadout-summary="priority"><th scope="row">Gear priorities</th><td><a href="#current-affix-priority">Reported 32-target order</a>, with rogue utility afterward. No optimizer replay or global optimality claimed.</td></tr>\n<tr data-loadout-summary="kit"><th scope="row">Endgame kit</th><td><a href="#wisdom-loadout-selection">Sinew–Rocard</a>, finished ML36; distinct rings; Rocard sole Minor Artifact; Paralyzing retained; no augment sets. Sinew gives a Lawful wearer one negative level. Reported gear INT37/36 and Deadly20/19 retain the source conflicts; RP44, Doubleshot35 and direct skills29 are modeled contributions, not certified character totals. Armor-Piercing46 versus normalized incumbent76. HA63 procurement conditional; permanent craft replacement implications apply.</td></tr>'


def audit_summary(data):
    validate(data)
    rows=[]
    for stat in ['Intelligence','Doubleshot','Ranged Power','Armor-Piercing','Deadly','Constitution','Physical Sheltering','Magical Sheltering','Fortification','Healing Amplification','Spot','Disable Device','Search','Open Lock']:
        r=next(r for r in data['reported_ledger'] if r['stat']==stat)
        value=r['reported_value']
        if stat=='Intelligence':value='37 / 36 (conflicting Skull cases)'
        if stat=='Deadly':value='20 / 19 (conflicting Quality cases)'
        rows.append(cells([h(stat),h(value),'Unverified combination; report model only']))
    return '<!-- selected-stacking-summary:start --><section id="selected-stacking-summary"><h3 id="selected-stacking-title">Sinew–Rocard report audit</h3>'+limits(data)+table('Reported gear contributions; no certified total',['Contribution','Reported value','Evidence boundary'],rows)+'<p>Direct skill bonuses exclude ranks, ability modifiers, tools and other character sources; overlapping Morale/Luck sources do not add again. The old Quickblade and Calamitous/Yeenoghu ledger describes the previous selection only. <a href="versions/11-16-26.2.html#selected-stacking-summary">Historical selected-kit audit</a> · <a href="endgame-stacking-audit.html">All reported contributors and overlaps</a>.</p></section><!-- selected-stacking-summary:end -->'


def audit_detail(data):
    validate(data)
    rows=[cells([h(r['stat']),h(r['reported_value']),h(r['contributing']),h(r['overlapping'])]) for r in data['reported_ledger']]
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sinew–Rocard report audit</title><style>'
            + AUDIT_STYLE + '</style></head><body><nav>' + AUDIT_NAV + '</nav><h1>Selected Sinew–Rocard report audit</h1>'
            + audit_summary(data)
            + '<h2 id="components">Selected components and reported overlaps</h2>'
            + table('All report contributions and superseded sources',['Affix','Reported value','Contributing sources','Overlap / superseded sources'],rows)
            + '<h2 id="unverified">Unverified log</h2>' + listing(data['limitations'])
            + '<p id="gap-survival-whole-build">Whole-character survival remains unverified: reported gear PRR, MRR, Fortification, Dodge, HP and healing amplification do not establish mitigation, caps or effective survival for a particular character or target.</p>'
            + '<p id="gap-whole-build-doubleshot">Whole-character Doubleshot and DPS remain unverified. This report does not transfer the historical Quickblade proof into the new Solar Doubleshot selection.</p>'
            + '<h2 id="rules">Rules and evidence boundary</h2><p>Displayed numeric contributor sums are checked against the supplied report. This is not a new source-qualified stacking engine. Original component and positive-interaction gates remain intact for their historical recipe; no old proof is applied to the changed selected hosts or effects.</p>'
            + '<h2 id="sources">Source receipts</h2><p><a href="' + SOURCE + '">Derived structured report transcription</a> identifies Library file/version, read range and source classification. <a href="tools/fixtures/wisdom-loadout/selection.json">Current recipe manifest</a> binds that transcription by hash. These are report records, not raw Wiki captures or replayed solver receipts.</p>'
            + '<p><a href="versions/11-16-26.2.html#selected-stacking-summary">Historical Calamitous/Yeenoghu selected summary</a> · <a href="evidence/wisdom-loadout/README.md">Retained historical evidence</a>. The original ledger and proof modules are preserved for historical checks.</p></body></html>')


def build_audit(data):
    validate(data)
    (ROOT/'endgame-stacking-audit.html').write_text(audit_detail(data))
    p=ROOT/'index.html';text=p.read_text();a=text.index('<!-- selected-stacking-summary:start -->');b=text.index('<!-- selected-stacking-summary:end -->',a)+len('<!-- selected-stacking-summary:end -->')
    p.write_text(text[:a]+audit_summary(data)+text[b:])
