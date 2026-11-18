"""Current recipe prose versus reported ledger; not game-mechanics certification."""
import json
from pathlib import Path
import unittest
from test_lamordia_handling import Document, Node, norm
ROOT=Path(__file__).resolve().parents[1]
HISTORICAL={'endgame-historical-notes','optimizer-historical-notes','historical-calamitous-crafting'}
def current_nodes(node, historical=False):
    historical=historical or node.attrs.get('id') in HISTORICAL
    if not historical:yield node
    for child in node.children:
        if isinstance(child,Node):yield from current_nodes(child,historical)
def validate(html):
    root=Document(html).root
    nodes=list(current_nodes(root))
    byid={n.attrs['id']:n for n in nodes if 'id' in n.attrs}
    for anchor in ['survivability-gear','doubleshot-at-cap','synergy-audit']:
        assert anchor in byid, 'current navigation enters historical content'
        assert anchor+'-historical' not in byid
    block=byid['current-gear-reconciliation'];text=norm(block.text())
    for phrase in ['Fortification 240%', '35 gear Doubleshot','Armor-Piercing 46',
                   'Reflection armor’s Green socket','No Calamitous weapon crafts, Salt or Dimlight bonus',
                   'No cloak Solar Sneak Attack Dice or Quickblade augment set',
                   'not Pendant of Subtle Pain','not certified stacking']:
        assert phrase in text,phrase
    assert '15% Artifact Doubleshot from the Legendary Solar Gem' in byid['reflection-current-effects'].text()
    forts=[norm(n.text()) for n in nodes if n.attrs.get('data-selected-stat')=='Fortification']
    assert len(forts)==3 and all('240%' in t and 'unverified model' in t for t in forts)
    for n in nodes:
        if n.tag in {'p','td','li'} and not n.nodes('details') and not n.nodes('section'):
            t=norm(n.text())
            for stale in ['no trap item after level 9','no Disable Device or Open Lock item after level 9',
                          '20 on both armors','Legendary Demon’s Arc; ML35-36 kit']:
                assert stale not in t,stale
    return True
class CurrentSelectedProseTests(unittest.TestCase):
    def test_current_claims_and_navigation(self):
        self.assertTrue(validate((ROOT/'index.html').read_text()))
    def test_report_matches_prose_numbers_and_socket(self):
        d=json.loads((ROOT/'tools/fixtures/wisdom-loadout/selection.json').read_text())
        values={r['stat']:r['total'] for r in d['reported_ledger']}
        self.assertEqual({k:values[k] for k in ['Fortification','Doubleshot','Armor-Piercing','Dodge']},
                         {'Fortification':240,'Doubleshot':35,'Armor-Piercing':46,'Dodge':16})
        armor=next(i for i in d['items'] if i['slot']=='Armor')
        self.assertTrue(any(s['color']=='Green' and s['fill']=='Sapphire of Dodge +16%' for s in armor['sockets']))
    def test_stale_current_claims_cannot_hide_behind_historical_allowance(self):
        text=(ROOT/'index.html').read_text()
        for before,after in [('Reported level-36 gear Fortification: 240%','Reported level-36 gear Fortification: 226%'),
                             ('35 gear Doubleshot','36 gear Doubleshot'),('Armor-Piercing 46:','Armor-Piercing 76:'),
                             ('Reflection armor’s Green socket','helmet’s Green socket'),
                             ('id="current-gear-reconciliation"','id="endgame-historical-notes"')]:
            self.assertIn(before,text)
            with self.subTest(before=before),self.assertRaises(AssertionError):validate(text.replace(before,after,1))
