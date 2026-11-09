"""A-074 selection/model boundaries and exact scope; not a source or game test."""
import copy
import hashlib
import json
from pathlib import Path
import re
import unittest

from test_lamordia_handling import Document, guide_content, guide_text, norm
import stacking_audit as audit

ROOT = Path(__file__).resolve().parents[1]
SCOPE = json.loads((ROOT/'tools/fixtures/queen-basic/scope.json').read_text())
BASELINE = 'dbc4dc349173ce61ba2b6818e7cd270735dca0d7'


def restore_queen_release(html):
    """Reverse only exact A-074 replacements before previous release hashes."""
    from test_skill_training_timing import restore_training_release
    html = restore_training_release(html)
    from test_fixed_selection_wording import restore_fixed_selection_release
    html = restore_fixed_selection_release(html)
    for change in reversed(SCOPE['reviewed_replacements']):
        assert html.count(change['after']) == 1, 'exact approved A-074 replacement'
        html = html.replace(change['after'], change['before'])
    return html


def restore_queen_kit(html):
    from test_skill_training_timing import restore_training_prose
    html = restore_training_prose(html)
    from test_fixed_selection_wording import restore_fixed_selection_prose
    html = restore_fixed_selection_prose(html)
    change = SCOPE['kit_table']
    assert html.count(change['after']) == 1, 'exact approved A-074 kit table'
    return html.replace(change['after'], change['before'])


def selected_table(html):
    start = html.index('<h3 id="endgame-kit-ml35-36">')
    # The comparison has its own table. The complete equipment table is the
    # first table with the six named inventory columns.
    tables = list(Document(html[start:]).root.nodes('table'))
    candidates = [table for table in tables if [norm(n.text()) for n in table.nodes('th')][:3] == ['Slot','Item','ML']]
    assert len(candidates) == 1
    return candidates[0]


def selected_rows(html):
    result = {}
    for row in selected_table(html).nodes('tr'):
        cells = [norm(n.text()) for n in row.nodes('td')]
        if cells:
            assert len(cells) == 6 and cells[0] not in result
            result[cells[0]] = cells
    return result


def visible_section(html, ident):
    sections = [n for n in guide_content(Document(html).root) if n.attrs.get('id') == ident]
    assert len(sections) == 1 and sections[0].tag == 'section'
    return guide_text(sections[0])


def validate_current(html):
    # Literal scope restoration also rejects unapproved changes inside the new
    # table or explanations. Semantic checks below keep important invariants
    # independent of the approved replacement packet.
    assert SCOPE['baseline_commit'] == BASELINE
    restored = restore_queen_release(html)
    assert hashlib.sha256(restored.encode()).hexdigest() == SCOPE['baseline_index_sha256']
    rows = selected_rows(html)
    assert len(rows) == 14
    assert rows['Cloak'][1:3] == ['The Queen of Rot', '35']
    assert 'Green, Yellow and Sun slots.' in rows['Cloak'][3]
    assert 'Bound to Character on Acquire' in rows['Cloak'][3]
    assert 'Nearly Complete: Insightful Constitution +7' in rows['Cloak'][4]
    assert 'Diamond of Spot +22' in rows['Ring 1'][4]
    assert 'Green (Colorless augment)' in rows['Ring 1'][4]
    assert rows['Weapon'][1] == 'Legendary Calamitous Longbow or Legendary Demogorgon’s Sinew'
    assert rows['Weapon'][2] == '34 / 35'
    assert rows['Quiver'][4] == 'No sockets'
    assert rows['Quiver'][5] == 'Oath of Vengeance (Legendary), end chest (Mists of Ravenloft)'
    selection = visible_section(html, 'queen-basic-selection')
    for text in ('33 sockets: 24 ordinary + 9 Sun/Moon; 28 filled',
                 'Every Solar and Lunar Gem in the table is the Legendary version',
                 'Both filled bows and the complete outfit require level 36',
                 'offhand stays empty', 'acquisition route is unknown',
                 'Original capture bytes, an exact revision permalink and every tooltip bonus type were not retained here',
                 'none is a new local optimizer run or an in-game check'):
        assert text in selection, text
    delta = visible_section(html, 'queen-basic-deltas')
    for text in ('model only', '36 → 35', '132 → 133 / 72 → 73', '283 → 286',
                 '25 / 25 / 26 → 26 / 26 / 27', '108 → 108',
                 '32 → 32 in the solver case; 33 → 33 in the Skull item-page case',
                 'INT 37 with Calamitous / 36 with Sinew',
                 'Gain Freedom of Movement; lose Light Absorption 24%',
                 'objective cap of 132 must not hide raw PRR 133',
                 'Apply MRR caps to whole-character MRR',
                 'KTA and Insightful Deadly use the higher applicable Insight damage value, not their sum',
                 'rejected the two strict Doubleshot-36 / Light-Absorption-24 diagnostics',
                 'relayed metadata, not retained original solver output or a local rerun'):
        assert text in delta, text
    assert '1,022 phases' in delta
    return rows


def validate_reflection(html, data, enhancement):
    audit.validate(data)
    nodes = [n for n in guide_content(Document(html).root)
             if n.attrs.get('id') == 'reflection-current-effects']
    assert len(nodes) == 1 and nodes[0].tag == 'p'
    text = guide_text(nodes[0])
    for claim in ('3% Profane Doubleshot', '15% Artifact Doubleshot',
                  '18 Doubleshot percentage points from these two sources',
                  'not an 18% DPS gain or certification of the full modeled 35',
                  'selected Lunar gem and Monolith descriptions list no Doubleshot or attack speed',
                  '20% Enhancement ranged attack speed',
                  'only the highest applicable Enhancement speed bonus applies',
                  'armor and Haste do not add',
                  'does not establish Haste’s current magnitude'):
        assert claim in text, claim
    # The already-qualified rule proves this pair, not every other pair in the
    # selected aggregate. Keep the full selected result withheld.
    pair = copy.deepcopy(data)
    pair['components'] = [c for c in data['components']
                          if c['id'] in {'armor-ds','solar-ds'}]
    assert audit.subtotal(pair,'Doubleshot')['complete']
    assert audit.subtotal(pair,'Doubleshot')['total'] == 18
    assert audit.subtotal(data,'Doubleshot')['total'] is None
    assert data['sources']['artifact']['quote'] == 'This bonus stacks with all other bonuses.'
    assert enhancement['url'] == 'https://ddowiki.com/page/Enhancement_bonus'
    assert enhancement['revision'] == 'https://ddowiki.com/index.php?title=Enhancement_bonus&oldid=699462'
    assert enhancement['observed_start'] == '2026-11-02T01:45:04.528Z'
    assert enhancement['observed_end'] == '2026-11-02T01:45:09.911Z'
    for clause in ('Multiple enhancement bonuses of the same type do not stack.',
                   'Only the highest enhancement bonus applies for each type.',
                   'Attack speed (e.g. from a Melee Alacrity item, a speed item, items or Haste spell)'):
        assert clause in enhancement['text']
    for sid in ('lunar-con','lunar-int','lunar-prr','rp-lunar','monolith'):
        description = data['sources'][sid]['quote'].lower()
        assert 'doubleshot' not in description and 'attack speed' not in description


class QueenBasicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT/'index.html').read_text()

    def test_complete_recipe_and_exact_predecessor_reconstruction(self):
        validate_current(self.html)

    def test_physical_socket_compatibility_empties_and_fill_count(self):
        rows = selected_rows(self.html)
        expected = {
            'Weapon': [('Purple','Sapphire of Defense +40'),('Orange','A Treatise on Battle')],
            'Armor': [('Green','Legendary Sapphire of Riposte'),('Colorless','Diamond of Festive Constitution +2'),('Sun','Solar Gem of Critical Confirmation')],
            'Helmet': [('Green','Sapphire of Dodge +16%'),('Yellow','Ravil’s Book of Legendary Recipes'),('Sun','Solar Gem of Doubleshot')],
            'Goggles': [('Green','Sapphire of False Life +60'),('Colorless','Diamond of Festive Dexterity +2'),('Sun','Solar Gem of Fortification Bypass')],
            'Necklace': [('Blue','Sapphire of Good Luck +3')],
            'Trinket': [('Green','Sapphire of Greater Heroism'),('Sun','Solar Gem of Intelligence'),('Colorless','empty')],
            'Cloak': [('Green','Sapphire of Resistance +12'),('Yellow','empty'),('Sun','Solar Gem of Sneak Attack Dice')],
            'Belt': [('Green','Sapphire of Healing Amplification +63'),('Blue','Diamond of Festive Intelligence +2'),('Moon','Lunar Gem of Constitution')],
            'Ring 1': [('Green','Diamond of Spot +22'),('Colorless','Diamond of Insightful Dexterity +5')],
            'Ring 2': [('Blue','Essence of the Epic Litany of the Dead')],
            'Gloves': [('Green','empty'),('Colorless','Globe of True Imperial Blood'),('Moon','Lunar Gem of Intelligence')],
            'Boots': [('Moon','Lunar Gem of Physical Protection'),('Green','Topaz of Blindness Immunity'),('Colorless','empty')],
            'Bracers': [('Moon','Lunar Gem of Ranged Power'),('Yellow','Topaz of Ranged Power +14'),('Green','empty')],
        }
        sockets = []
        for slot, picks in expected.items():
            actual = re.findall(r'(Green|Blue|Purple|Orange|Yellow|Colorless|Sun|Moon)(?: \([^)]*\))?: ([^.]+)', rows[slot][4])
            self.assertEqual(len(actual), len(picks), slot)
            for (host, fill), (want_host, want_fill) in zip(actual, picks):
                self.assertEqual(host, want_host, slot)
                self.assertTrue(fill.startswith(want_fill), (slot,fill,want_fill))
            sockets.extend(actual)
        self.assertEqual(len(sockets), 33)
        self.assertEqual(sum(host in ('Sun','Moon') for host, _ in sockets), 9)
        self.assertEqual(sum(host not in ('Sun','Moon') for host, _ in sockets), 24)
        self.assertEqual(sum(fill != 'empty' for _, fill in sockets), 28)
        # Cross-color fits are explicitly identified, not mislabeled host slots.
        for slot, label in [('Weapon','Purple (Blue augment)'),('Armor','Green (Blue augment)'),
                            ('Helmet','Yellow (Colorless augment)'),('Belt','Blue (Colorless augment)'),
                            ('Ring 1','Green (Colorless augment)'),('Ring 2','Blue (Colorless augment)'),
                            ('Boots','Green (Yellow augment)')]:
            self.assertIn(label, rows[slot][4])

    def test_model_only_same_type_maxima_and_cap_do_not_become_certified_totals(self):
        # Recompute the explicitly modeled cases independently of optimizer
        # metadata; these expected values are not evidence of game stacking.
        ds = 9 + 3 + 5 + 15 + 3
        raw_prr = max(40,41) + 30 + 30 + 21 + 11
        raw_mrr = max(40,41) + 21 + 11
        fort = 162 + max(81,84) + 40
        saves = (max(12,13)+6+4+3,)*2 + (max(12,13)+max(6,7)+4+3,)
        self.assertEqual((ds,raw_prr,raw_mrr,fort,saves),(35,133,73,286,(26,26,27)))
        self.assertEqual(min(raw_prr,132),132)
        self.assertGreater(raw_prr,min(raw_prr,132))
        self.assertEqual(min(raw_mrr+50,100),100)
        self.assertEqual((15+7+3+4+2+1,16+7+3+4+2+1),(32,33))
        self.assertEqual(60+48,108)
        data = audit.load()
        for stat in ('PRR','MRR','Fortification','Constitution','Will','Reflex','Fortitude','Spot','Doubleshot','Intelligence','Ranged Power'):
            self.assertIsNone(audit.subtotal(data,stat)['total'],stat)
        self.assertEqual(audit.subtotal(data,'HP')['total'],108)

    def test_replaced_effects_absent_and_new_inputs_cannot_be_force_verified(self):
        data = audit.load()
        by_id = {c['id']:c for c in data['components']}
        self.assertFalse({'cloak-ds','cloak-con','cloak-insight-con'} & by_id.keys())
        self.assertFalse(any(e['id']=='light-absorption' for e in data['non_total_effects']))
        self.assertIn('goggles-ds',audit.subtotal(data,'Doubleshot')['counted'])
        for cid in ('queen-prr','queen-mrr','queen-insight-con','queen-fortification',
                    'queen-fortitude','queen-reflex','queen-will','spot-diamond'):
            self.assertEqual(by_id[cid]['state'],'unknown')
            self.assertEqual(by_id[cid]['source'],'')
            self.assertIn(cid,audit.subtotal(data,by_id[cid]['stat'],active=['force'])['excluded'])
            mutated = copy.deepcopy(data)
            next(c for c in mutated['components'] if c['id']==cid)['state']='verified'
            with self.subTest(cid=cid),self.assertRaises((AssertionError,KeyError)):
                audit.validate(mutated)

    def test_mutations_cannot_hide_recipe_changes_or_certify_the_model(self):
        for before,after in (
            ('Nearly Complete: Insightful Constitution +7','Nearly Complete: Insightful Intelligence +7'),
            ('Green (Colorless augment): Diamond of Spot +22','Green: empty'),
            ('Yellow: empty. Sun: Solar Gem of Sneak Attack Dice','Colorless: empty. Sun: Solar Gem of Sneak Attack Dice'),
            ('Viktranium: Dolorous Quality Constitution +3','Viktranium: Dolorous Quality Deadly +3'),
            ('33 sockets: 24 ordinary + 9 Sun/Moon; 28 filled','33 sockets: 24 ordinary + 9 Sun/Moon; 29 filled'),
            ('132 → 133 / 72 → 73','132 → 132 / 72 → 73'),
            ('Gain Freedom of Movement; lose Light Absorption 24%','Gain Freedom of Movement and Light Absorption 24%'),
            ('Its acquisition route is <strong>unknown</strong>','Buy it from an invented vendor'),
            ('Original capture bytes, an exact revision permalink and every tooltip bonus type were not retained here','Every tooltip type was freshly verified'),
            ('<section id="queen-basic-selection"','<section hidden id="queen-basic-selection"'),
            ('<h2 id="class-split">','<h2 id="changed-class-split">'),
        ):
            self.assertIn(before,self.html)
            with self.subTest(before=before),self.assertRaises(AssertionError):
                validate_current(self.html.replace(before,after))

    def test_reflection_pair_and_speed_rule_use_actual_retained_contexts(self):
        path = ROOT/'evidence/endgame-stacking/retained-selected.json'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                         'eed0083b8454a40a249acf5b0c3b93714e68ee496a857e889c724bc0e278dc78')
        validate_reflection(self.html,audit.load(),json.loads(path.read_text())[2])

    def test_reflection_overclaims_and_rule_loss_are_rejected(self):
        data = audit.load()
        enhancement = json.loads((ROOT/'evidence/endgame-stacking/retained-selected.json').read_text())[2]
        for before,after in (
            ('18 Doubleshot percentage points from these two sources','18% DPS from these two sources'),
            ('not an 18% DPS gain or certification of the full modeled 35','a certified 18% DPS gain and full 35 total'),
            ('armor and Haste do not add','armor and Haste add together'),
            ('does not establish Haste’s current magnitude','establishes Haste as 15% today'),
            ('<p id="reflection-current-effects"','<p hidden id="reflection-current-effects"'),
        ):
            self.assertIn(before,self.html)
            with self.subTest(before=before),self.assertRaises(AssertionError):
                validate_reflection(self.html.replace(before,after),data,enhancement)
        bad_rule = copy.deepcopy(data)
        bad_rule['sources']['artifact']['observed'] = None
        bad_rule['sources']['artifact']['observed_pointer'] = None
        with self.assertRaises(AssertionError):
            validate_reflection(self.html,bad_rule,enhancement)
        for clause in ('Only the highest enhancement bonus applies for each type.',
                       'Attack speed (e.g. from a Melee Alacrity item, a speed item, items or Haste spell)'):
            altered = copy.deepcopy(enhancement)
            altered['text'] = altered['text'].replace(clause,'')
            with self.subTest(clause=clause),self.assertRaises(AssertionError):
                validate_reflection(self.html,data,altered)

    def test_relay_and_historical_boundaries_remain_explicit(self):
        text = (ROOT/'docs/knowledge-base/A-074-QUEEN-BASIC.md').read_text()
        for claim in ('not an original browser capture', 'No original study files are',
                      '22 solves', '1,022 phases', '20 feasible cases',
                      'zero Minor Artifacts', 'not an', 'exactly-one requirement',
                      'Diamond of Spot +22', 'acquisition route is\nunknown'):
            self.assertIn(claim,text)
        self.assertIn('Historical Summer’s End kit rationale and scenarios',self.html)
        self.assertIn('lost Freedom of Movement are not the current recipe',self.html)
        detail = (ROOT/'endgame-stacking-audit.html').read_text()
        self.assertNotIn('Cloak Doubleshot 10% suppresses goggles 9%',detail)
        headings = [n for n in Document(detail).root.nodes('h3')
                    if n.attrs.get('id') == 'gap-whole-build-doubleshot']
        self.assertEqual(len(headings),1)
        self.assertIn('current combination unverified',norm(headings[0].text()))
        self.assertNotRegex(headings[0].text(),r'\b(?:128|177)\b')


if __name__ == '__main__':
    unittest.main()
