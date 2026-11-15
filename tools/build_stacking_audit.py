"""Render the selected-loadout audit from source-gated components and rules."""
from html import escape as h
from pathlib import Path
import re
import json
from stacking_audit import ROOT, load, validate, subtotal, source_provenance
from wisdom_loadout import (load as load_selection, validate as validate_selection,
                           render_crafting_qualification)

BEGIN = '<!-- selected-stacking-summary:start -->'
END = '<!-- selected-stacking-summary:end -->'


def slug(s):
    return re.sub('[^a-z0-9]+', '-', s.lower()).strip('-')


def quoted(text):
    # Preserve captured whitespace in <pre> without trailing source-file whitespace.
    return re.sub(r' +(?=\n)', lambda m: '&#32;' * len(m.group(0)), h(text).replace('\t','&#9;'))


def selection(data):
    """Join the selected recipe without upgrading its independent source grades."""
    chosen = load_selection()
    validate_selection(chosen)
    assert data['selection_record'] == 'tools/fixtures/wisdom-loadout/selection.json'
    assert data['selection_sha256'] == chosen['provenance']['selected']['sha256']
    assert data['selection_base_commit'] == chosen['provenance']['guide_commit']
    assert not chosen['optional']['ring_dexterity_13']['selected']
    return chosen


def model_table(chosen):
    """Display model arithmetic separately from the evidence-gated calculator."""
    keys = [('Ranged Power', 'Ranged Power'), ('Doubleshot', 'Doubleshot'),
            ('Seeker', 'Seeker'), ('Armor-Piercing', 'Armor-Piercing'),
            ('Deadly', 'Deadly (flat weapon damage)'), ('Accuracy', 'Accuracy'),
            ('Intelligence', 'Intelligence contribution'),
            ('Wisdom', 'Wisdom contribution'), ('Dexterity', 'Dexterity contribution'),
            ('Constitution', 'Constitution contribution — model case'),
            ('Spot', 'Direct Spot bonus, before ability modifier'),
            ('Sneak Attack Dice', 'Sneak dice'), ('Sneak Attack Damage', 'Flat sneak damage'),
            ('Imbue Dice', 'Imbue dice'), ('Combustion', 'Combustion'),
            ('Physical Sheltering', 'Raw PRR before whole-character calculation'),
            ('Magical Sheltering', 'Raw MRR before caps'),
            ('Fortification', 'Fortification'), ('False Life', 'Flat maximum HP'),
            ('Healing Amplification', 'Healing Amplification'), ('Dodge', 'Dodge before caps'),
            ('Will Save', 'Direct Will save'), ('Reflex Save', 'Direct Reflex save'),
            ('Fortitude Save', 'Direct Fortitude save')]
    model = chosen['model']
    rows = []
    for key, label in keys:
        values = [model[name].get(key, 0) for name in ('guide_totals', 'prior_totals', 'totals')]
        rows.append('<tr><th scope="row">'+h(label)+'</th>'+''.join('<td>'+h(str(v))+'</td>' for v in values)+'</tr>')
    return ('<div class="tw"><table data-model-only="wisdom-comparison"><caption>'
            'Model-only gear comparison — not source-certified totals or character-sheet results'
            '</caption><thead><tr><th>Contribution</th><th>Former guide kit</th>'
            '<th>Previous artifact kit</th><th>Primary Wisdom kit</th></tr></thead><tbody>'
            + ''.join(rows) + '</tbody></table></div><p>Zero means no contribution in that supplied model bucket, not independently verified absence in the live game.</p>')


def summary(data):
    validate(data)
    chosen = selection(data)
    model = chosen['model']['totals']
    production = chosen['provenance']['production']
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
        if not result['complete']:
            breakdown = 'Supported inputs only (not a subtotal): ' + breakdown + '; excluded inputs: ' + ', '.join(result['excluded'])
            if result['missing_interactions']:
                breakdown += f"; {len(result['missing_interactions'])} unverified pairwise interactions"
        facts.append(f'<tr data-stat="{h(stat)}"><td>{h(label)}</td><td>{h(value)}</td><td>{h(breakdown)}</td></tr>')
    def established(stat):
        r = subtotal(data, stat)
        return r['total'] if r['complete'] else None
    gm_attack, gm_damage = established('Greater Marksmanship attack'), established('Greater Marksmanship damage')
    gm = (f'Greater Marksmanship counts once (+{gm_attack} ranged attack, +{gm_damage} ranged damage). '
          if gm_attack is not None and gm_damage is not None else 'Greater Marksmanship remains unverified. ')
    goggles = ('Goggles provide the selected 9% Enhancement Doubleshot. '
               if 'goggles-ds' in subtotal(data, 'Doubleshot')['counted']
               else 'The goggles Doubleshot input remains unverified. ')
    threat, healing = established('Ranged threat reduction'), established('Healing Amplification')
    utility = ((f'The selected ring threat-reduction contribution is {threat}%; ' if threat is not None else 'The item threat-reduction contribution remains unverified; ')
               + (f'Healing Amplification is a single +{healing} Competence component.' if healing is not None else 'Healing Amplification remains unverified.'))
    offense = (f"Modeled Ranged Power {model['Ranged Power']}, Doubleshot {model['Doubleshot']}, "
               f"Seeker {model['Seeker']}, Armor-Piercing {model['Armor-Piercing']}, "
               f"Deadly {model['Deadly']} and Intelligence {model['Intelligence']}")
    survival = (f"Raw modeled PRR {model['Physical Sheltering']}, MRR {model['Magical Sheltering']}, "
                f"Fortification {model['Fortification']}, Constitution {model['Constitution']} "
                f"and direct Will/Reflex/Fortitude saves {model['Will Save']}/{model['Reflex Save']}/{model['Fortitude Save']}")
    wis_dex = (f"The primary model has Wisdom {model['Wisdom']}, Dexterity {model['Dexterity']} "
               f"and direct Spot {model['Spot']} before ability modifiers. ")
    return BEGIN + '''
<section id="selected-stacking-summary" aria-labelledby="selected-stacking-title">
<h3 id="selected-stacking-title">Primary Wisdom loadout: modeled results and source-gated evidence</h3>
<p><strong>The fully filled kit requires character level 36.</strong> Selected augments raise their hosts’ minimum level. The primary recipe has one Minor Artifact, Yeenoghu’s Reign; Claws Nearly Complete selects Wisdom +15; the Celestial Sapphire Ring’s Nearly Finished slot is empty. The no-event/no-limited policy allows only Festive ability diamonds as the exception. Acquisition screening, legal construction and source-certified effect totals are different checks.</p>
<p><strong>Actual run, followed by manual refinements.</strong> The retained production run completed ''' + h(str(production['passes'])) + ''' stages in ''' + h(str(production['seconds'])) + ''' seconds. The documented canonical craft rotation, Spot/Good Luck choices and Wisdom refinement derive the selected recipe; they are not a new solver run or proof of a global optimum. The raw output modeled Constitution ''' + h(str(chosen['model']['raw_production_totals']['Constitution'])) + '''; this practical selection models ''' + h(str(model['Constitution'])) + ''' after choosing Good Luck for saves/skills, and adds the provisional Slavers Extra Spot +20. The production run’s status is not an optimality claim for those manual changes. See the <a href="evidence/wisdom-loadout/README.md">run, derivation and source-limit packet</a> and <a href="tools/fixtures/wisdom-loadout/selection.json">exact selected manifest</a>.</p>
<p><strong>Damage first; certification is limited.</strong> ''' + h(gm + goggles + offense) + ''' remain <strong>unverified combinations</strong>. Dusk Raider, Tough Shields, Quickblade and Perfect Silence each require three selected hosts; their model inputs are not certified by arithmetic alone. Perfect Silence’s modeled three sneak dice are separate from the selected Solar gem’s modeled three flat sneak damage. The Emerald’s modeled one imbue die and Chains Combustion require activation and scaling checks; no DPS percentage or wider critical range is asserted.</p>
<div class="tw"><table><caption>Current survival evidence at level 36</caption><thead><tr><th>Contribution</th><th>Derived subtotal</th><th>Supported component inputs</th></tr></thead><tbody>''' + ''.join(facts) + '''</tbody></table></div>
<p>''' + h(utility + ' ' + survival) + ''' remain unverified combinations. The HP subtotal still uses the selected False Life +60 in Goggles Green and Vitality +48 in Claws Green. Queen and newly selected unresolved sources remain in the ledger rather than being dropped to make totals appear complete. The objective PRR cap is not raw PRR; armor caps apply to whole-character MRR. Skull own-page Constitution +16 conflicts with the generic/model +15: modeled CON 32 and the own-page sensitivity 33 remain separate, uncertified cases.</p>
<p><strong>Wisdom priority, with a visible tradeoff.</strong> ''' + h(wis_dex) + '''These are gear contributions, not final ability or skill scores. The own Claws page lists Wisdom +15, but its retained source lacks an observation timestamp and cannot enter certified totals. The source review identifies Nearly Complete as irreversible: plan for another Claws copy if the existing one is already finished with Dexterity. The optional ring Dexterity +13 branch would model Dexterity ''' + h(str(chosen['optional']['ring_dexterity_13']['gear_dexterity_if_selected'])) + '''; it is <strong>unselected and model-only</strong>. Neither it nor the quarantined Insightful +5/Spot +22 diamonds is silently added to the primary kit.</p>
''' + render_crafting_qualification(data, compact=True) + '''
<p><strong>Boundaries that matter.</strong> Cut to the Soul’s +3% is offensive Dodge bypass, not defensive Dodge. Defensive Dodge and its two caps still need their full check, including the newly selected ring input. Improved Deception remains a conditional ring proc, not a guaranteed sneak-attack uptime. Static weapon riders, imbues, sneak damage and procs are separate damage channels. The preserved level-35 bow-model scenario does not certify this level-36 Calamitous-and-Salt recipe or its critical range.</p>
<p><a href="endgame-stacking-audit.html">Open the component-by-component audit, exact source contexts, missing interactions and unverified log</a>. “Verified” means the specific gated source support, not a live-game guarantee. The <a href="evidence/wisdom-loadout/claims.json">independent claim inventory</a> and <a href="evidence/wisdom-loadout/sources.json">source review</a> retain their own grades: retained-source-supported does not mean certified by this ledger. Old A-074 and earlier source records remain preserved history; unused old item/augment effects are not current components.</p>
</section>
''' + END


def detail(data):
    validate(data)
    chosen = selection(data)
    out = ['''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Selected endgame stacking audit — INT Longbow Guide</title><style>
:root{color-scheme:dark;background:#101722;color:#e4eaf2;font:17px/1.6 system-ui,sans-serif}body{max-width:1140px;margin:auto;padding:24px}a{color:#9ed1ff}h1,h2,h3{line-height:1.2}h2{margin-top:2.5rem;border-top:1px solid #465568;padding-top:1rem}table{border-collapse:collapse;width:100%;font-size:.92rem}th,td{padding:10px;text-align:left;vertical-align:top;border-bottom:1px solid #465568}th{background:#202d3e}.tw{overflow-x:auto}caption{text-align:left;font-weight:700;padding:12px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.5 ui-monospace,monospace}code{overflow-wrap:anywhere}details{border:1px solid #465568;border-radius:6px;padding:12px;margin:12px 0}summary{cursor:pointer;font-weight:700}.note{border-left:4px solid #e9bd6c;padding-left:14px}.unknown{color:#f2ce92}nav a{margin-right:16px}@media(max-width:600px){body{padding:16px}th,td{padding:8px}table{min-width:650px}}
</style></head><body><nav><a href="index.html#selected-stacking-summary">Back to the guide</a><a href="#components">Components</a><a href="#unverified">Unverified log</a><a href="#rules">Rules</a><a href="#sources">Source receipts</a></nav><h1>Selected Wisdom endgame stacking audit</h1>''',
    '<p>'+h(chosen['selection']['date'])+' · '+h(chosen['selection']['label'])+' · fully filled level-36 Calamitous/Salt recipe; optional ring craft absent</p>',
    '<p class="note">'+h(data['scope'])+'</p>',
    '<p>Original evidence audit base: <code>'+h(data['base_commit'])+'</code>. Current selection implementation base: <code>'+h(data['selection_base_commit'])+'</code>. The <a href="tools/fixtures/wisdom-loadout/selection.json">shared manifest</a> identifies the production run, selected derivation, exact placements and optional branch. The <a href="evidence/wisdom-loadout/README.md">evidence packet</a> preserves source grades and limits. Chassis, feats, AP/DP purchases and historical damage-model outputs are not silently recomputed. Publication and live-game validation remain separate.</p>',
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
    out += ['<h2 id="unverified">Model-only comparisons and unresolved claims</h2><p>The following table comes from the shared selected-recipe manifest, not the source-gated subtotal calculator. Correct arithmetic and independent construction checks do not make a model total certified. Ability entries are gear contributions; Spot and saves exclude ability modifiers and other character inputs. The ring Dexterity +13 branch remains unselected. The Skull Constitution +15/model versus +16/own-page conflict is preserved as separate sensitivity cases.</p>', model_table(chosen), '<p>Removed items, Monolith, Litany, obsolete gems and previous crafting choices are not current inputs. Prior guide and artifact columns are named comparisons, not alternative current selections. Original A-074, Summer’s End and bow-model evidence remain historical records.</p>']
    for g in data['unresolved']:
        sources = ', '.join(f'<a href="#source-{h(s)}">{h(s)}</a>' for s in g['sources']) or 'No qualified original receipt joined here; see the selected manifest and source packet'
        out += [f'<h3 id="gap-{h(g["id"])}">{h(g["claim"])}</h3><p><strong>{h(g["state"])}</strong> — {h(g["detail"])}</p><p>Source context: '+sources+'.</p>']
    out+=['<div class="tw"><table><caption>Additional selected build inputs, excluded from asserted totals</caption><thead><tr><th>Input</th><th>Guide amount</th><th>Direct source / unresolved scope</th></tr></thead><tbody>']
    for c in [c for c in data['components'] if c['channel']=='build']:
        out += [f'<tr><td>{h(c["host"])}</td><td>{c["amount"]} {h(c["stat"])}</td><td><a href="#source-{h(c["source"])}">Source context</a>. {h(c["note"])}</td></tr>']
    out+=['</tbody></table></div><h2 id="rules">Explicit rules used by the calculator</h2>']
    for r in data['rules']:
        status = 'Eligible: exact revision and bound observation context.' if source_provenance(data['sources'][r['source']]) else 'Unverified provenance: excluded from calculations until revision and genuine observation context are complete.'
        out += [f'<p class="note">{h(status)}</p>']
        out += [f'<h3 id="rule-{h(r["id"])}">{h(r["id"])}</h3><p>Applies to {h(", ".join(r["stats"]))}; type scope {h(", ".join(r["types"]))}; operation {h(r["kind"])}. Same-type suppression stays within the same statistic and channel.</p><blockquote>{h(r["quote"])}</blockquote><p><a href="#source-{h(r["source"])}">Exact source and provenance</a></p>']
    out += ['<h2 id="sources">Exact source contexts, roles and limits</h2><p>Retained browser captures are scoped DOM excerpts, not raw response bytes. Each underlying capture retains its own actual observation window and cache limits, including the fresh 15 November crafting addendum. Reusing an older capture does not refresh its observation date; missing revisions/timestamps remain missing. Source-reported revision metadata does not prove that a historical endpoint was independently read. The generated source-excerpts.json collection is a derived index of those original records, not a new browser observation. Exact package hashes and pointers preserve the distinction; editor and review metadata are omitted. A source marked historical/background below does not describe a currently equipped input. These are documentary checks, not game tests.</p><p>Source text: <a href="https://ddowiki.com/">DDO Wiki contributors</a>, <a href="https://creativecommons.org/licenses/by-sa/2.5/">CC BY-SA 2.5</a>. Original articles and revision histories supply attribution. Reused source excerpts retain that license.</p>']
    for sid,s in data['sources'].items():
        pin=s['revision']
        if pin and pin.startswith('/'):pin='https://ddowiki.com'+pin
        revision=f'<a href="{h(pin)}">Observed revision</a>' if pin else 'Revision not retained'
        role = data['source_roles'][sid]
        out += [f'<details id="source-{h(sid)}"><summary>{h(sid)} — {h(role)}</summary><p><a href="{h(s["url"])}">Wiki article</a> · {revision} · observed {h(s["observed"] or "timestamp unavailable in this source record")}</p><p>{h(s["freshness_limit"])}</p><p><a href="evidence/endgame-stacking/source-excerpts.json">Retained source excerpts and role labels</a><br>Original capture: <code>{h(s["path"])}</code><br>SHA-256: <code>{h(s["sha256"])}</code><br>JSON pointer: <code>{h(str(s["pointer"]))}</code></p><pre>{quoted(s["quote"])}</pre></details>']
    return ''.join(out)+'</body></html>\n'


def validate_guide(html,data):
    chosen = selection(data)
    model = chosen['model']['totals']
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
        for reference in references:
            if result['complete']:
                match=re.fullmatch(r'(\d+) gear '+stat, norm(reference.text()))
                assert match and int(match.group(1))==result['total']
            else:
                expected = {'PRR': f"unverified gear PRR (modeled raw {model['Physical Sheltering']})",
                            'MRR': f"unverified gear MRR (modeled raw {model['Magical Sheltering']}, before caps)"}
                assert norm(reference.text()) == expected[stat]
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
    (ROOT/'evidence/endgame-stacking/source-excerpts.json').write_text(json.dumps({'scope':'Exact retained source contexts with origin file hashes/pointers and current versus historical/background roles. Original mixed capture files are not linked as audit payload; new model claims are not promoted to original source receipts.', 'source_roles':data['source_roles'], 'sources':data['sources']}, ensure_ascii=False, indent=2)+'\n')
    (ROOT/'endgame-stacking-audit.html').write_text(detail(data))
    path=ROOT/'index.html';text=path.read_text()
    if BEGIN in text:
        a=text.index(BEGIN);b=text.index(END,a)+len(END)
        text=text[:a]+summary(data)+text[b:]
        path.write_text(text)

if __name__=='__main__':main()
