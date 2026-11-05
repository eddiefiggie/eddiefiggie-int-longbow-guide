"""Listed five-purchase arithmetic from retained 720728, not complete costs."""
import copy
import hashlib
import json
import re
import unittest
from pathlib import Path
from test_dimlight_name import SOURCE, URL
from test_lamordia_handling import Document, norm
from test_legendary_crafting_route import section
ROOT=Path(__file__).resolve().parents[1]
PARTS=('Alternators','Conductors','Insulators','Resistors')

def validate(data,html):
    assert data['permalink']==URL
    raw=data['html']
    amounts=[]
    for ident,name,n in [('Melancholic_(Weapons)','Melancholic Flames',25),('Dolorous_(Weapons)','Dolorous Flames',50),('Miserable_(Weapons)','Miserable Dimlight',25),('Woeful_(Weapons)_2','Woeful Salt',50)]:
        text=section(data,ident)
        header=ident.split('_')[0]+' (Weapon)'
        assert header in text and name in text
        if ident.endswith('_2'):
            assert 'Effect (ML:34)' in text
            assert raw.index('id="Wicked_Viktranium_Experiment_Crafting"')<raw.index('id="'+ident+'"')
            cost=text.split('Cost: ',1)[1].split('Woeful (Weapon)',1)[0].strip()
            suffix=', 50 Bleak Mementos'
        else:
            assert 'Heroic Effect (ML:8) Legendary Effect (ML:34)' in text
            assert 'Legendary versions cost: ' in text
            cost=text.split('Legendary versions cost: ',1)[1].split(' BUG:',1)[0].split(header,1)[0].strip()
            suffix=', 100 Legendary Bleak Wires' if n==25 and name=='Miserable Dimlight' else ''
        assert cost==', '.join(f'{n} Legendary Bleak {p}' for p in PARTS)+suffix
        amounts.append(n)
    craft=section(data,'Crafting')
    assert 'Legendary Calamitous weapons cost 25 Legendary Bleak Alternators, 25 Legendary Bleak Conductors, 25 Legendary Bleak Insulators and 25 Legendary Bleak Resistors to craft' in craft
    assert 'Legendary Cataclysmic weapons cost the same amount of regular materials as Legendary Calamitous weapons, but additionally require 25 Legendary Bleak Mementos' in craft
    cat=section(data,'Legendary_Cataclysmic_Weapons_and_Shields')
    assert 'Legendary Cataclysmic weapons cost '+', '.join('25 Legendary Bleak '+p for p in PARTS)+', 25 Bleak Mementos to craft' in cat
    # Actual links, not similar ingredient labels, establish identity.
    links=Document(raw).root.nodes('a')
    for label in ['25 Legendary Bleak Mementos','25 Bleak Mementos','50 Bleak Mementos']:
        found=[a for a in links if norm(a.text())==label]
        assert found and all(a.attrs.get('href')=='/page/Item:Legendary_Bleak_Memento' for a in found)
    assert 25+sum(amounts)==175 and 50+25==75
    doc=Document(html).root
    blocks=[n for n in doc.nodes('div') if n.attrs.get('id')=='legendary-bow-subtotal']
    assert len(blocks)==1
    block=blocks[0]
    expected=(ROOT/'tools/fixtures/legendary-budget-visible.txt').read_text().strip()
    assert norm(block.text())==expected
    assert len(block.nodes('li'))==2
    assert [a.attrs['href'] for a in block.nodes('a')]==[URL,URL+'#Woeful_(Weapons)_2','https://ddowiki.com/page/Item:Legendary_Bleak_Memento']
    start=html.index('<div id="legendary-bow-subtotal">')
    assert html.rfind('</table></div>',0,start)>html.index('id="crafted-endgame-bow"')
    assert start<html.index('id="endgame-kit-ml35-36"')

class LegendaryBudgetTests(unittest.TestCase):
    def test_evidence_arithmetic_and_visible_scope(self):
        raw=SOURCE.read_bytes()
        assert len(raw)==612486 and hashlib.sha256(raw).hexdigest()=='e40935cdc1a352a7fa3dde5af1fd7a852e0a4e50f9d9ed3c44dfdb3cbbf5458e'
        validate(json.loads(raw),(ROOT/'index.html').read_text())
    def test_negative_controls(self):
        data=json.loads(SOURCE.read_text());html=(ROOT/'index.html').read_text()
        for old,new in [('175 each','150 each'),('100 Legendary Bleak Wires; 50','20 Legendary Bleak Wires; 50'),('75 Bleak Mementos instead','50 Bleak Mementos instead'),('25 (blank) + ','') ,('25 (blank) + ','25 (blank) + 25 (blank) + '),('selected Legendary Weapon fill','selected Heroic Weapon fill'),('selected Legendary Weapon fill','selected Legendary Accessory fill'),('not a complete-cost or current-availability promise','a complete-cost and current-availability promise'),('Woeful_(Weapons)_2','Woeful_(Weapons)'),('id="legendary-bow-subtotal"','id="hidden-budget"')]:
            assert old in html
            with self.subTest(guide=old),self.assertRaises(AssertionError):validate(data,html.replace(old,new))
        for old,new in [('Legendary versions cost:','Heroic versions cost:'),('Legendary Effect (ML:34)','Legendary Effect (ML:8)'),('100 Legendary Bleak Wires','99 Legendary Bleak Wires'),('50 Bleak Mementos','50 Legendary Bleak Transformers'),('25 Bleak Mementos','50 Bleak Mementos'),('/page/Item:Legendary_Bleak_Memento','/page/Item:Bleak_Memento'),('Woeful Salt','Woeful Shadow'),('Miserable (Weapon)','Miserable (Accessory)')]:
            d=copy.deepcopy(data);assert old in d['html'];d['html']=d['html'].replace(old,new)
            with self.subTest(source=old),self.assertRaises(AssertionError):validate(d,html)
