"""Narrow newly-used retained acquisition/slotting context, not live access."""
import copy
import json
import re
from pathlib import Path
import unittest
from test_lamordia_handling import Document,norm
from test_dimlight_name import SOURCE,URL
ROOT=Path(__file__).resolve().parents[1]

def section(data,ident):
    html=data['html'];assert html.count('id="'+ident+'"')==1
    return norm(Document(re.split(r'<h[1-6](?:\s|>)',html.split('id="'+ident+'"',1)[1],maxsplit=1)[0]).root.text())

def validate(data,html):
    assert data['permalink']==URL
    craft=section(data,'Crafting')
    for text in ['workbenches in Ludendorf City Hall (one workbench each for the Heroic and Legendary systems)',
                 'create Lamordia augments and Calamitous weapons',
                 'use the Augment Item UI accessible through your Inventory Panel',
                 'Legendary Cataclysmic weapons','crafted inside of the raid, using a special crafting station']:
        assert text in craft,text
    wicked=section(data,'Wicked_Viktranium_Experiment_Crafting')
    for text in ['before the wax statues activate','Ludendorf Wax Museum in the Lamordia wilderness',
                 'target the doors with the target key, then press the interact key']:
        assert text in wicked,text
    raw=data['html'];assert raw.index('id="Wicked_Viktranium_Experiment_Crafting"')<raw.index('id="Woeful_(Weapons)_2"')
    assert 'Woeful Salt' in section(data,'Woeful_(Weapons)_2')
    guide=html.split('<p id="legendary-crafting-route">',1)[1].split('</p>',1)[0]
    text=norm(Document(guide).root.text())
    for phrase in ['separate Heroic and Legendary workbenches; use the Legendary system for this recipe',
                   'Woeful Salt belongs to the Wicked Weapon recipes',
                   'separate Cataclysmic blank option','before the wax statues activate',
                   'Ludendorf Wax Museum location in the Lamordia wilderness',
                   'target the door, then use the interact key',
                   'does not supply the required ingredients or establish current availability',
                   'Inventory Panel’s Augment Item UI','slot-matching and recovery instructions']:
        assert phrase in text,phrase
    assert [a.attrs['href'] for a in Document(guide).root.nodes('a')]==[URL+'#Crafting',URL+'#Woeful_(Weapons)_2','#lamordia-augment-handling']

class LegendaryRouteTests(unittest.TestCase):
    def test_source_and_route(self):validate(json.loads(SOURCE.read_text()),(ROOT/'index.html').read_text())
    def test_faults(self):
        data=json.loads(SOURCE.read_text());html=(ROOT/'index.html').read_text()
        for old,new in [('Legendary system for this recipe','Heroic system for this recipe'),
                        ('Wicked Weapon recipes','ordinary Weapon recipes'),
                        ('does not supply the required ingredients or establish current availability','guarantees all ingredients'),
                        ('target the door, then use the interact key','click the door'),
                        ('Inventory Panel’s Augment Item UI','crafting device'),
                        ('href="#lamordia-augment-handling"','href="#sources"')]:
            with self.subTest(guide=old):
                with self.assertRaises(AssertionError):validate(data,html.replace(old,new))
        for old,new in [('Ludendorf City Hall','Another City Hall'),
                        ('before the wax statues activate','after the wax statues activate'),
                        ('Woeful Salt','Woeful Sugar')]:
            d=copy.deepcopy(data);assert old in d['html'];d['html']=d['html'].replace(old,new)
            with self.subTest(source=old):
                with self.assertRaises(AssertionError):validate(d,html)
