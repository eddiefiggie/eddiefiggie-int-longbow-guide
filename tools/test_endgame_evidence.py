"""Retained-source editorial regressions; not live-game mechanics certification."""
import copy
import hashlib
import json
import re
import unittest
from pathlib import Path
from test_lamordia_handling import Document, norm

ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/'tools/fixtures/endgame-evidence'
CONTRACT=json.loads((FIX/'contract.json').read_text())
BASE=json.loads((FIX/'inventory.json').read_text())

def sha(data): return hashlib.sha256(data).hexdigest()
def span(html,start,end):
    return html[html.index(start):html.index(end)]
def kit_rows(html):
    block=html.split('<h3 id="endgame-kit-ml35-36">',1)[1].split('</tbody>',1)[0]
    out={}
    for row in Document(block).root.nodes('tr'):
        cells=[norm(c.text()) for c in row.nodes('td')]
        if cells:
            assert len(cells)==6
            assert cells[0] not in out
            out[cells[0]]=cells
    return out

FILL_CORRECTIONS={
 'Armor': [('Blue: Legendary Sapphire','Green (Blue augment): Legendary Sapphire')],
 'Helmet': [('Colorless: Ravil’s Book','Yellow (Colorless augment): Ravil’s Book')],
 'Belt': [('Colorless: Diamond of Festive Intelligence','Blue (Colorless augment): Diamond of Festive Intelligence')],
 'Ring 2': [('Colorless: Essence','Blue (Colorless augment): Essence')],
 'Boots': [('Yellow: Topaz','Green (Yellow augment): Topaz')],
 'Bracers': [('Yellow: empty','Green: empty')]
}
SOCKET_TEXT={'Armor':'Green, Colorless and Sun slots.','Helmet':'Green, Yellow and Sun slots.','Belt':'Green, Blue and Moon slots.','Ring 1':'Green and Colorless slots.','Ring 2':'Blue slot.','Boots':'Green, Colorless and Moon slots.','Bracers':'Green, Yellow and Moon slots.'}

def validate_kit(html):
    rows=kit_rows(html)
    assert set(rows)=={b['slot'] for b in BASE}
    for b in BASE:
        cells=rows[b['slot']]
        assert cells[1]==b['item'] and cells[2]==str(b['guide_ml'])
        # Acquisition fields and every chosen fill/craft are preserved. Only
        # physical host-label corrections and the empty bracer slot may differ.
        assert cells[5]==b['guide_acquisition']
        expected=b['guide_augments_and_crafts']
        for old,new in FILL_CORRECTIONS.get(b['slot'],[]):
            assert expected.count(old)==1
            expected=expected.replace(old,new)
        assert cells[4]==expected,(b['slot'],cells[4],expected)
    for slot,text in SOCKET_TEXT.items(): assert text in rows[slot][3]
    assert 'Blunted Ammunition' in rows['Quiver'][3]
    assert 'deals bludgeoning damage in addition to its other damage types' in rows['Quiver'][3]
    assert 'weapon-specific interactions remain unverified' in rows['Quiver'][3]
    fills=' '.join(c[4] for c in rows.values())
    assert fills.count('Solar Gem of ')==5 and fills.count('Lunar Gem of ')==4

def validate_claims(html):
    area=span(html,'<h3 id="endgame-kit-ml35-36">','<h2 id="reaper-10">')
    visible=norm(Document(area).root.text())
    for text in [
        '21 timestamped browser page captures on 5 November',
        'not an in-game check',
        'Eight base items had retained revision links',
        'eleven of fourteen',
        'the Pendant, Compass and level-36 cloak still lack revision receipts',
        'the nine Solar and Lunar Gems',
        'Constitution contribution is 33',
        '16 Enhancement + 7 Insight + 3 Quality + 4 Profane + 2 Festive + 1 Exceptional',
        'historical solver total of 32',
        '5 Insight (boots)',
        'Separate listing or the absence of a non-stacking note does not establish stacking',
        'a bonus without a keyword is not necessarily untyped',
        'Point Blank Shot appears under “Untyped / unclear bonus type”',
        'Timing unresolved:',
        'Pierce Deception automatically grants the feat',
        'purchase schedule is unchanged pending review',
        'standing RP, Archer’s Focus stacks and short boosts separate',
        'the RP summary says +4 per core, a retained source conflict',
        'Track reaches 20% at full stacks',
        'separate Sunder entries explicitly do not stack',
        'These factors stack additively',
        'no floor or clamp is established here',
        'imbues, damaging affixes and procs can still draw aggro',
        'this is not guaranteed immunity against every champion’s bypass',
        'equal totals do not prove zero DPS opportunity cost',
        'Sapphire of Healing Amplification +63 (belt)',
        'a chance on a killing blow for 5% Enhancement damage',
        'lower chance against weaker enemies',
        'while reducing AC; no standing bonus assumed here',
        'Selected gear Constitution +33 across six bonus types',
        'or +37 with the Solar Gem of Constitution',
        'not a complete mechanics certification'
    ]: assert text in visible,text
    for text in [
        'lists the sources separately or says they stack',
        'No non-stacking rule on the tree or feat pages',
        'sections with no non-stacking note',
        'Pierce Deception’s Doubleshot is counted from 30, not 24',
        'a champion with Fortification Bypass still cannot reach the criticals',
        'The single open item is still',
        'so it costs nothing in the offence stack',
        'the eight Solar and Lunar Gems',
        '5 Insight (belt)',
    ]: assert text not in visible,text
    links={a.attrs.get('href') for a in Document(area).root.nodes('a')}
    for title,rev in [('Stack',669682),('Doubleshot',719351),('Watchful_Eye',703660),('Ranged_Power',675695),('Fatesinger',726700),('Fortification',723727),('Hate',713587)]:
        assert f'https://ddowiki.com/index.php?title={title}&oldid={rev}' in links

def validate_preservation(html):
    chosen_build=span(html,'<h2 id="class-split">','<h2 id="gear">')
    # Exact explanation-only cross-references qualify timing and kit-total claims.
    # After reversing exactly those edits, all choices and purchase rows must
    # still be byte-identical to the verified target tree.
    for correction in CONTRACT['allowed_build_prose_corrections']:
        assert chosen_build.count(correction['after'])==1
        chosen_build=chosen_build.replace(correction['after'],correction['before'])
    # A-019: reverse only the reviewed Shadowstrike save-condition sentence.
    # Preserve the original contract hash; the dedicated source/Guide tests
    # require the corrected condition and reject its removal or alteration.
    shadow_before = ('AoE ranged strike with +30% damage, +2 multiplier, '
                     '+3 threat range, Shadow Loss curse')
    shadow_after = ('AoE ranged strike with +30% damage, +2 multiplier, '
                    '+3 threat range; Shadow Loss curse only if the struck '
                    'opponent fails its Fortitude save')
    assert chosen_build.count(shadow_after) == 1, 'A-019 exact reviewed correction'
    chosen_build = chosen_build.replace(shadow_after, shadow_before)
    assert sha(chosen_build.encode())==CONTRACT['class_to_gear_sha256']
    model = span(html,'<h3 id="bow-damage-model">','<h3 id="crafted-endgame-bow">')
    # The bow-only release changes only the concluding recommendation/link.
    # Retain the historical hash for every assumption, table value and output.
    scope = json.loads((ROOT/'tools/fixtures/endgame-bow-options/scope.json').read_text())
    verdicts = [c for c in scope['reviewed_replacements']
                if c['before'].startswith('<p><strong>Verdict by band:</strong>')]
    assert len(verdicts) == 1 and model.count(verdicts[0]['after']) == 1
    model = model.replace(verdicts[0]['after'], verdicts[0]['before'])
    assert sha(model.encode())==CONTRACT['bow_model_section_sha256']

class EndgameEvidenceTests(unittest.TestCase):
    def setUp(self): self.html=(ROOT/'index.html').read_text()
    def test_unchanged_choices_and_all_selected_fills(self): validate_kit(self.html)
    def test_visible_evidence_limits_and_corrections(self): validate_claims(self.html)
    def test_repeated_timing_and_globe_constitution_are_consistent(self):
        self.assertNotIn('so from level 30 on this build',self.html)
        self.assertEqual(self.html.count('href="#pierce-deception-source-note"'),3)
        self.assertIn('the Globe still contributes +1 Exceptional Constitution',self.html)
        self.assertNotIn('those two augments pay on the other abilities only',self.html)
    def test_class_feat_enhancement_destiny_and_model_preservation(self):
        validate_preservation(self.html)
        self.assertEqual(sha((ROOT/'tools/bowmodel.py').read_bytes()),CONTRACT['bow_model_file_sha256'])
    def test_retained_evidence_file_identities(self):
        prov=json.loads((FIX/'provenance.json').read_text())
        for record in prov['captures']:
            with self.subTest(path=record['path']):
                data=(FIX/record['path']).read_bytes()
                self.assertEqual(sha(data),record['sha256'])
                self.assertEqual(len(data),record['bytes'])
        self.assertEqual(sha((FIX/'sources.json').read_bytes()),CONTRACT['source_ledger_sha256'])
        self.assertEqual(sha((FIX/'inventory.json').read_bytes()),CONTRACT['inventory_sha256'])
    def test_explicit_rules_are_present_in_actual_retained_sources(self):
        stack=json.loads((FIX/'retained/Stack.json').read_text())['text']
        self.assertIn("a bonus without a keyword isn't necessarily an untyped bonus",stack)
        self.assertIn('Feat bonuses stack.',stack)
        fort=json.loads((FIX/'retained/Fortification.json').read_text())['text']
        self.assertIn('does not stack with Sunder',fort)
        we=json.loads((FIX/'retained/INTiana-DDO-Wiki-source-evidence-batch-2.json').read_text())['pages'][1]['evidence']
        self.assertIn('Pierce Deception automatically grants this feat.',we['exact_excerpts'][3]['text'])
        threat=json.loads((FIX/'retained/INTiana-DDO-Wiki-defense-enemies-02-evidence.json').read_text())['source_receipts'][3]['sources'][1]
        self.assertEqual(threat['exact_source_sections'][3]['complete_relevant_additive_clause'],'These factors stack additively')
    def test_socket_corrections_match_retained_item_observations(self):
        expected={'Armor':['Green','Colorless','Sun'],'Helmet':['Green','Yellow','Sun'],'Belt':['Green','Blue','Moon'],'Ring 1':['Green','Colorless'],'Ring 2':['Blue'],'Boots':['Green','Colorless','Moon'],'Bracers':['Green','Yellow','Moon']}
        inv={b['slot']:b for b in BASE}
        for slot,colors in expected.items(): self.assertEqual(inv[slot]['retained_host_sockets'],colors)
        # Lower-confidence observations are never silently supplied an oldid.
        self.assertIsNone(inv['Belt']['pinned_url']);self.assertIsNone(inv['Ring 2']['pinned_url'])
    def test_constitution_is_a_derived_gear_total(self):
        self.assertEqual(max(16,15)+7+3+max(4,2)+2+1,33)
        self.assertEqual(33+4,37)
        src={s['source_id']:s for s in json.loads((FIX/'sources.json').read_text())}
        self.assertIn('Constitution +16',src['S021']['data']['text'])
        self.assertIn('+1 Exceptional',src['S075']['data']['text'])
    def test_wrong_host_labels_are_rejected(self):
        for old,new in [('Green (Blue augment): Legendary Sapphire','Blue: Legendary Sapphire'),('Green and Colorless slots.','Two Colorless slots.'),('Green (Yellow augment): Topaz','Yellow: Topaz'),('Green, Yellow and Moon slots.','Moon and two Yellow slots.'),('Yellow (Colorless augment): Ravil','Colorless: Ravil')]:
            with self.subTest(old=old),self.assertRaises(AssertionError): validate_kit(self.html.replace(old,new))
    def test_changed_or_removed_gear_and_fills_are_rejected(self):
        for old,new in [('Lunar Gem of Constitution (+4 Profane)',''),('Legendary Calamitous Longbow</td><td>34','Legendary Cataclysmic Longbow</td><td>34'),('Quality Constitution +3, Quality Seeker +3','Quality Constitution +3'),('Nearly Complete: Constitution +16','Nearly Complete: Intelligence +16')]:
            assert old in self.html
            with self.subTest(old=old),self.assertRaises(AssertionError): validate_kit(self.html.replace(old,new))
    def test_overclaim_and_wrong_arithmetic_mutations_are_rejected(self):
        for old,new in [('does not establish stacking','establishes stacking'),('Timing unresolved:','Timing verified:'),('automatically grants the feat','requires a separate feat'),('not guaranteed immunity','guaranteed immunity'),('5 Insight (boots)','5 Insight (belt)'),('the nine Solar and Lunar','the eight Solar and Lunar'),('Constitution contribution is <strong>33</strong>','Constitution contribution is <strong>32</strong>'),('not an in-game check','an in-game verification'),('equal totals do not prove zero DPS opportunity cost','Salt has zero DPS opportunity cost')]:
            assert old in self.html
            with self.subTest(old=old),self.assertRaises(AssertionError): validate_claims(self.html.replace(old,new))

if __name__=='__main__': unittest.main()
