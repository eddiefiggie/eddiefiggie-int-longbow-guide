"""Exact retained Legendary Weapon barter name; no new build/stacking claims."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from test_lamordia_handling import Document, norm
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'tools/fixtures/lamordia-handling/viktranium-experiment-crafting.browser-capture.json'
URL='https://ddowiki.com/index.php?title=Viktranium_Experiment_crafting&oldid=720728'

def validate(source,html):
    assert source['permalink']==URL
    raw=source['html'];assert raw.count('id="Miserable_(Weapons)"')==1
    raw=raw.split('id="Miserable_(Weapons)"',1)[1].split('<h3',1)[0]
    doc=Document(raw).root
    rows=[[norm(c.text()) for c in row.children if getattr(c,'tag','') in ('td','th')] for row in doc.nodes('tr')]
    assert rows[0]==['Miserable (Weapon)','Heroic Effect (ML:8)','Legendary Effect (ML:34)']
    chosen=[r for r in rows if r and r[0].startswith('Miserable Dimlight')]
    assert chosen==[['Miserable Dimlight(Heroic) / (Legendary)', '+1 Exceptional bonus to Intelligence.', '+2 Exceptional bonus to Intelligence.']]
    text=norm(doc.text())
    assert 'Legendary versions cost: 25 Legendary Bleak Alternators, 25 Legendary Bleak Conductors, 25 Legendary Bleak Insulators, 25 Legendary Bleak Resistors, 100 Legendary Bleak Wires' in text
    guide=Document(html).root
    rows=guide.nodes('tr')
    craft=[r for r in rows if r.nodes('td') and norm(r.nodes('td')[0].text())=='Miserable']
    assert len(craft)==1
    cells=craft[0].nodes('td')
    assert norm(cells[1].text()).startswith('Legendary Miserable Dimlight (Weapon) — Exceptional Intelligence +2 (selected Calamitous craft), or Miserable Improved Destruction')
    assert norm(cells[3].text())=='25 each of the four Legendary Bleak parts and 100 Legendary Bleak Wires'
    assert [a.attrs['href'] for a in cells[1].nodes('a')]==[URL+'#Miserable_(Weapons)']
    kit=[r for r in rows if len(r.nodes('td'))==6 and norm(r.nodes('td')[1].text())=='Legendary Calamitous Longbow or Legendary Demogorgon’s Sinew']
    assert len(kit)==1
    assert 'Miserable: Legendary Miserable Dimlight (Weapon), Exceptional Intelligence +2;' in norm(kit[0].nodes('td')[4].text())
    assert 'Miserable Exceptional Intelligence +2</strong>' not in html

class DimlightNameTests(unittest.TestCase):
    def test_exact_source_and_selected_name(self):
        data=SOURCE.read_bytes();assert len(data)==612486
        assert hashlib.sha256(data).hexdigest()=='e40935cdc1a352a7fa3dde5af1fd7a852e0a4e50f9d9ed3c44dfdb3cbbf5458e'
        validate(json.loads(data),(ROOT/'index.html').read_text())
    def test_negative_controls(self):
        source=json.loads(SOURCE.read_text());html=(ROOT/'index.html').read_text()
        for old,new in [('Legendary Miserable Dimlight (Weapon)','Heroic Miserable Dimlight (Weapon)'),
                        ('Legendary Miserable Dimlight (Weapon)','Legendary Miserable Dimlight (Accessory)'),
                        ('Legendary Miserable Dimlight (Weapon)','Legendary Miserable Shadows (Weapon)'),
                        ('Weapon), Exceptional Intelligence +2;','Weapon), Exceptional Intelligence +1;'),
                        ('25 each of the four Legendary Bleak parts and 100 Legendary Bleak Wires','25 each of the four Legendary Bleak parts and 20 Legendary Bleak Wires')]:
            with self.subTest(old=old,new=new):
                assert old in html
                with self.assertRaises(AssertionError):validate(source,html.replace(old,new))
        for old,new in [('Legendary Effect (ML:34)','Heroic Effect (ML:8)'),
                        ('Miserable Dimlight','Miserable Shadows'),
                        ('+2 Exceptional bonus to Intelligence.','+2 Quality bonus to Intelligence.'),
                        ('100 Legendary Bleak Wires','20 Legendary Bleak Wires')]:
            broken=copy.deepcopy(source);assert old in broken['html'];broken['html']=broken['html'].replace(old,new)
            with self.subTest(source=old):
                with self.assertRaises(AssertionError):validate(broken,html)
