"""Render the selected-loadout audit from source-gated components and rules."""
from html import escape as h
from pathlib import Path
import re
import json
from stacking_audit import ROOT, load, validate, subtotal, source_provenance

BEGIN = '<!-- selected-stacking-summary:start -->'
END = '<!-- selected-stacking-summary:end -->'


def slug(s):
    return re.sub('[^a-z0-9]+', '-', s.lower()).strip('-')


def quoted(text):
    # Preserve captured whitespace in <pre> without trailing source-file whitespace.
    return re.sub(r' +(?=\n)', lambda m: '&#32;' * len(m.group(0)), h(text).replace('\t','&#9;'))


def summary(data):
    validate(data)
    # Fixed factual clauses have explicit prerequisites too; withhold rendering
    # instead of emitting a stale claim after its provenance is lost.
    for sid in ('augment-min-level', 'augment-values', 'skull-con',
                'nearly-complete', 'cut-to-soul-fresh', 'marksmanship-rule'):
        assert source_provenance(data['sources'][sid]), 'unverified summary source: ' + sid
    facts = []
    for stat, label in [('PRR', 'Physical Resistance'), ('MRR', 'Magical Resistance'), ('HP', 'Flat maximum HP')]:
        result = subtotal(data, stat)
        value = str(result['total']) if result['complete'] else 'Unverified'
        parts = [c for c in data['components'] if c['id'] in result['counted']]
        breakdown = ' + '.join(f"{c['amount']} {c['bonus_type']}" for c in parts)
        facts.append(f'<tr data-stat="{h(stat)}"><td>{h(label)}</td><td>{h(value)}</td><td>{h(breakdown)}</td></tr>')
    def established(stat):
        r = subtotal(data, stat)
        return r['total'] if r['complete'] else None
    gm_attack, gm_damage = established('Greater Marksmanship attack'), established('Greater Marksmanship damage')
    gm = (f'Greater Marksmanship counts once (+{gm_attack} ranged attack, +{gm_damage} ranged damage). '
          if gm_attack is not None and gm_damage is not None else 'Greater Marksmanship remains unverified. ')
    overlaps = []
    for stat, cid, message in [
        ('Doubleshot', 'goggles-ds', 'Cloak Doubleshot 10% suppresses goggles 9%.'),
        ('Armor-Piercing', 'pendant-ap', 'Skull Armor-Piercing 25% suppresses Pendant 21%.')]:
        overlaps.append(message if cid in subtotal(data, stat)['suppressed'] else f'{stat} overlap remains unverified.')
    sneak = established('Sneak dice')
    sneak_note = f'The selected Solar gem directly supplies {sneak} Artifact sneak dice.' if sneak is not None else 'The selected Solar sneak-dice input remains unverified.'
    threat, healing = established('Ranged threat reduction'), established('Healing Amplification')
    utility = ((f'The item threat reduction is {threat}% (Pendant 21% is the same type); ' if threat is not None else 'The combined item threat reduction remains unverified; ')
               + (f'Healing Amplification is a single +{healing} Competence component.' if healing is not None else 'Healing Amplification remains unverified.'))
    return BEGIN + '''
<section id="selected-stacking-summary" aria-labelledby="selected-stacking-title">
<h3 id="selected-stacking-title">Selected loadout: stacking checked against Wiki evidence</h3>
<p><strong>The fully filled kit requires character level 36.</strong> The augments raise their hosts’ minimum level. The figures below are derived gear contributions supported by direct item definitions and applicable stacking rules; they are not complete character-sheet totals or an in-game test. Gear, crafts, feats and purchases are unchanged.</p>
<p><strong>Damage first.</strong> ''' + h(gm + ' '.join(overlaps) + ' ' + sneak_note) + ''' The combined RP 44, Doubleshot 36, Seeker 29, Armor-Piercing 76, Intelligence 37 and whole-build Doubleshot/sneak totals remain <strong>unverified</strong>: some inputs lack required provenance or positive interaction rules. They are retained in the detailed log, excluded from asserted totals.</p>
<div class="tw"><table><caption>Supported survival contributions at level 36</caption><thead><tr><th>Contribution</th><th>Derived subtotal</th><th>Counted components</th></tr></thead><tbody>''' + ''.join(facts) + '''</tbody></table></div>
<p>''' + h(utility) + ''' Fortification 283, Constitution 33 and the save totals remain unverified combinations. The Skull’s own item page lists +16 Constitution while the generic Nearly Complete page lists +15; that discrepancy remains unresolved. The historical solver Constitution 32 and the listed-recipe arithmetic 33 are separate records; this audit does not rerun or certify an optimizer result.</p>
<p><strong>Boundaries that matter.</strong> Cut to the Soul’s +3% is offensive Dodge bypass, not defensive Dodge. The full defensive Dodge and its two caps need their complete selected-source check. The preserved bow model uses a different weapon/craft scenario and a level-35 kit assumption; its outputs do not certify this fully filled level-36 Calamitous-and-Salt loadout. Static weapon riders, imbues, sneak damage and procs require their own scaling and activation checks.</p>
<p><a href="endgame-stacking-audit.html">Open the component-by-component audit, exact Wiki evidence, missing interactions and unverified log</a>. “Verified” there means the stated source support, not a guarantee of current live-game behavior. Fresh observations from 7 November supplement the dated retained captures; each source retains its revision, hash and freshness limit.</p>
</section>
''' + END


def detail(data):
    validate(data)
    out = ['''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Selected endgame stacking audit — INT Longbow Guide</title><style>
:root{color-scheme:dark;background:#101722;color:#e4eaf2;font:17px/1.6 system-ui,sans-serif}body{max-width:1140px;margin:auto;padding:24px}a{color:#9ed1ff}h1,h2,h3{line-height:1.2}h2{margin-top:2.5rem;border-top:1px solid #465568;padding-top:1rem}table{border-collapse:collapse;width:100%;font-size:.92rem}th,td{padding:10px;text-align:left;vertical-align:top;border-bottom:1px solid #465568}th{background:#202d3e}.tw{overflow-x:auto}caption{text-align:left;font-weight:700;padding:12px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.5 ui-monospace,monospace}code{overflow-wrap:anywhere}details{border:1px solid #465568;border-radius:6px;padding:12px;margin:12px 0}summary{cursor:pointer;font-weight:700}.note{border-left:4px solid #e9bd6c;padding-left:14px}.unknown{color:#f2ce92}nav a{margin-right:16px}@media(max-width:600px){body{padding:16px}th,td{padding:8px}table{min-width:650px}}
</style></head><body><nav><a href="index.html#selected-stacking-summary">Back to the guide</a><a href="#components">Components</a><a href="#unverified">Unverified log</a><a href="#rules">Rules</a><a href="#sources">Source receipts</a></nav><h1>Selected endgame stacking audit</h1><p>7 November 2026 · source-supported arithmetic for the fully filled level-36 Calamitous/Salt kit</p>''',
    '<p class="note">'+h(data['scope'])+'</p>',
    '<p>Base guide commit: <code>'+h(data['base_commit'])+'</code>. Selected gear, crafts, augments, chassis, feats, AP/DP purchases and historical model outputs are preserved. This is a local review candidate, not a deployed or game-tested result.</p>',
    '<p><strong>Status:</strong> verified = exact component definition or explicit applicable rule; conditional = an activation/acquisition condition remains; conflicting = retained sources or scope disagree; unknown = evidence is missing. A verified component does not imply its entire combination is verified. Every counted component and applied rule also requires an exact revision and genuine source-bound observation context. Every counted pair needs its own applicable rule. Artifact touching two bonuses does not prove those other bonuses stack with one another.</p>',
    summary(data).replace('id="selected-stacking-summary"','id="audit-summary"').replace('id="selected-stacking-title"','id="audit-summary-title"').replace('aria-labelledby="selected-stacking-title"','aria-labelledby="audit-summary-title"'),
    '<h2 id="components">Selected components and interaction results</h2><p>Numbers in component rows are source-defined inputs or explicitly unverified Guide claims. Only a complete, supported subtotal is asserted. Item minimum levels in the guide are base-item values; this audit requires the fully filled level-36 context. Armor proficiency, ability modifiers, base saves, feats, trees, past lives, filigrees, procs and enemy mechanics are outside these gear subtotals unless specifically listed.</p>']
    for stat in dict.fromkeys(c['stat'] for c in data['components'] if c['channel']=='gear'):
        result=subtotal(data,stat)
        out += [f'<h3 id="stat-{slug(stat)}">{h(stat)}</h3>']
        if result['complete']:
            out += [f'<p><strong>Derived selected-gear subtotal: {result["total"]}.</strong> This names the listed contribution family, not a whole-character roll or damage total.</p>']
            if stat.startswith('Greater Marksmanship'):
                out += ['<p>The <a href="#source-marksmanship-rule">pinned Marksmanship definition</a> explicitly permits its ranged attack/damage bonuses to stack with Competence Accuracy/Deadly. This is that named cross-family exception; duplicate Greater Marksmanship still counts once. It does not verify the other Quality/Morale Accuracy combination.</p>']
        else:out += ['<p class="unknown"><strong>Combined total withheld.</strong> Missing components or interaction support are listed below; this is not a finding that the bonuses fail to stack in game.</p>']
        out += ['<div class="tw"><table><thead><tr><th>Host / component</th><th>Input / type</th><th>Evidence status</th><th>Scope and qualification</th></tr></thead><tbody>']
        for c in [c for c in data['components'] if c['stat']==stat and c['channel']=='gear']:
            link=f'<a href="#source-{h(c["source"])}">source</a>' if c['source'] else 'source missing'
            for related in c.get('related_sources', []):
                link += f' · <a href="#source-{h(related)}">conflicting source</a>'
            status='suppressed by same-type maximum' if c['id'] in result['suppressed'] else c['state']
            out += [f'<tr id="component-{h(c["id"])}"><td>{h(c["host"])}<br><small>{h(c["id"])}</small></td><td>{c["amount"]} {h(c["bonus_type"])}</td><td>{h(status)} · {link}</td><td>{h(c["note"])}</td></tr>']
        out += ['</tbody></table></div>']
        if result['missing_interactions']:
            out += ['<p><strong>Unverified pairwise interactions:</strong> '+ '; '.join(h(a)+' + '+h(b) for a,b in result['missing_interactions'])+'. No combined total is asserted.</p>']
        if result['excluded']:out += ['<p><strong>Excluded inputs:</strong> '+', '.join(h(x) for x in result['excluded'])+'.</p>']
        if result['proofs']:
            out += ['<details><summary>Applicable rules for this calculation</summary><ul>']
            for a,b,r in result['proofs']:out += [f'<li>{h(a)} / {h(b)}: <a href="#rule-{h(r)}">{h(r)}</a></li>']
            out += ['</ul></details>']
    out += ['<h2 id="other-effects">Other selected effects and qualifications</h2><p>These effects are kept separate from the additive gear subtotals. Conditional, unknown and non-numerical effects do not contribute an invented standing value.</p><div class="tw"><table><thead><tr><th>Host / effect</th><th>Status</th><th>Source scope and qualification</th></tr></thead><tbody>']
    for e in data['non_total_effects']:
        links=', '.join(f'<a href="#source-{h(x)}">{h(x)}</a>' for x in e['sources']) or 'Own-effect source missing'
        out += [f'<tr id="effect-{h(e["id"])}"><td>{h(e["host"])}: {h(e["claim"])}</td><td>{h(e["state"])}</td><td>{h(e["note"])}<br>{links}</td></tr>']
    out += ['</tbody></table></div>']
    out += ['<h2 id="unverified">Whole-build and unverified claims</h2><p>The historical headline arithmetic remains logged: RP 44, Doubleshot 36, Seeker 29, INT 37, Armor-Piercing 76, CON 33 (the solver recorded 32), Fortification 283 and saves 25/25/26. It does not become verified merely because the arithmetic is correct. Damage has priority in this ledger; no enhancement comparison or item replacement is made.</p>']
    for g in data['unresolved']:
        out += [f'<h3 id="gap-{h(g["id"])}">{h(g["claim"])}</h3><p><strong>{h(g["state"])}</strong> — {h(g["detail"])}</p><p>Direct-source scope: '+', '.join(f'<a href="#source-{h(s)}">{h(s)}</a>' for s in g['sources'])+'.</p>']
    out+=['<div class="tw"><table><caption>Additional selected build inputs, excluded from asserted totals</caption><thead><tr><th>Input</th><th>Guide amount</th><th>Direct source / unresolved scope</th></tr></thead><tbody>']
    for c in [c for c in data['components'] if c['channel']=='build']:
        out += [f'<tr><td>{h(c["host"])}</td><td>{c["amount"]} {h(c["stat"])}</td><td><a href="#source-{h(c["source"])}">Source context</a>. {h(c["note"])}</td></tr>']
    out+=['</tbody></table></div><h2 id="rules">Explicit rules used by the calculator</h2>']
    for r in data['rules']:
        status = 'Eligible: exact revision and bound observation context.' if source_provenance(data['sources'][r['source']]) else 'Unverified provenance: excluded from calculations until revision and genuine observation context are complete.'
        out += [f'<p class="note">{h(status)}</p>']
        out += [f'<h3 id="rule-{h(r["id"])}">{h(r["id"])}</h3><p>Applies to {h(", ".join(r["stats"]))}; type scope {h(", ".join(r["types"]))}; operation {h(r["kind"])}. Same-type suppression stays within the same statistic and channel.</p><blockquote>{h(r["quote"])}</blockquote><p><a href="#source-{h(r["source"])}">Exact source and provenance</a></p>']
    out += ['<h2 id="sources">Exact source receipts and limits</h2><p>Fresh browser captures are exact visible-DOM excerpts, not raw response bytes. Anonymous pages may lag by up to five hours. Older records are retained observations, not fresh checks. Source-reported revision metadata does not prove that a historical endpoint was independently read. Missing revisions/timestamps remain missing. Extracted original receipts preserve their original package hash and pointer; editor and review metadata are omitted. These are documentary checks, not game tests.</p><p>Source text: <a href="https://ddowiki.com/">DDO Wiki contributors</a>, <a href="https://creativecommons.org/licenses/by-sa/2.5/">CC BY-SA 2.5</a>. Original articles and revision histories supply attribution. Reused source excerpts retain that license.</p>']
    for sid,s in data['sources'].items():
        pin=s['revision']
        if pin and pin.startswith('/'):pin='https://ddowiki.com'+pin
        revision=f'<a href="{h(pin)}">Observed revision</a>' if pin else 'Revision not retained'
        out += [f'<details id="source-{h(sid)}"><summary>{h(sid)}</summary><p><a href="{h(s["url"])}">Wiki article</a> · {revision} · observed {h(s["observed"] or "timestamp unavailable in this source record")}</p><p>{h(s["freshness_limit"])}</p><p><a href="evidence/endgame-stacking/source-excerpts.json">Selected source excerpts</a><br>Original capture: <code>{h(s["path"])}</code><br>SHA-256: <code>{h(s["sha256"])}</code><br>JSON pointer: <code>{h(str(s["pointer"]))}</code></p><pre>{quoted(s["quote"])}</pre></details>']
    return ''.join(out)+'</body></html>\n'


def validate_guide(html,data):
    from test_lamordia_handling import Document, norm
    doc=Document(html)
    sections=[n for n in doc.root.nodes('section') if n.attrs.get('id')=='selected-stacking-summary']
    assert len(sections)==1
    section=sections[0]
    def check_ancestors(node, blocked=False):
        blocked = blocked or 'hidden' in node.attrs or 'inert' in node.attrs or node.tag in {'template','script','style'} or (node.tag == 'details' and 'open' not in node.attrs)
        if node is section:
            assert not blocked
        for child in node.children:
            if hasattr(child, 'tag'):
                check_ancestors(child, blocked)
    check_ancestors(doc.root)
    def descendants(node):
        yield node
        for child in node.children:
            if hasattr(child, 'tag'):
                yield from descendants(child)
    assert not any('hidden' in n.attrs or n.tag in {'template','script'} for n in descendants(section))
    assert norm(section.text())==norm(Document(summary(data)).root.text())
    # Current body cross-references must agree with the calculated gear family,
    # while archived model/optimizer records remain separate historical text.
    for stat, count in [('PRR', 3), ('MRR', 1)]:
        references=[n for n in doc.root.nodes('a') if n.attrs.get('data-selected-stat')==stat]
        assert len(references)==count
        result=subtotal(data,stat)
        assert result['complete']
        for reference in references:
            match=re.fullmatch(r'(\d+) gear '+stat, norm(reference.text()))
            assert match and int(match.group(1))==result['total']
            assert reference.attrs.get('href')=='#selected-stacking-summary'
    fort_references=[n for n in doc.root.nodes('span') if n.attrs.get('data-unverified-stat')=='Fortification']
    assert len(fort_references)==3
    assert not subtotal(data,'Fortification')['complete']
    for reference in fort_references:
        assert 'unverified' in norm(reference.text()).lower()
        assert not re.search(r'\d',reference.text())
    layer4=[n for n in doc.root.nodes('p') if norm(n.text()).startswith('Layer 4:')]
    assert len(layer4)==1
    if not source_provenance(data['sources']['fortification-rule']):
        assert not re.search(r'\bstacks?\s+with\s+Insightful\s+Fortification\b',layer4[0].text(),re.I)
    historical=[n for n in doc.root.nodes('details') if n.attrs.get('id')=='endgame-historical-notes']
    assert len(historical)==1
    assert historical[0].attrs.get('open') is None
    return True


def main():
    data=load();validate(data)
    (ROOT/'evidence/endgame-stacking/source-excerpts.json').write_text(json.dumps({'scope':'Selected source contexts only; exact excerpts with origin file hashes/pointers. Original mixed capture files are not linked as audit payload.', 'sources':data['sources']}, ensure_ascii=False, indent=2)+'\n')
    (ROOT/'endgame-stacking-audit.html').write_text(detail(data))
    path=ROOT/'index.html';text=path.read_text()
    if BEGIN in text:
        a=text.index(BEGIN);b=text.index(END,a)+len(END)
        text=text[:a]+summary(data)+text[b:]
        path.write_text(text)

if __name__=='__main__':main()
