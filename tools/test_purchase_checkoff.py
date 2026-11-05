"""Listed-purchase arithmetic and native-control contract, not browser certification."""
import json
from pathlib import Path
import re
import subprocess
import unittest
from test_lamordia_handling import Document, Node, norm
from test_calamitous_recipe import source_costs

ROOT = Path(__file__).resolve().parents[1]
IDS = ['purchase-blank', 'purchase-melancholic', 'purchase-dolorous', 'purchase-miserable']
LABELS = ['Blank heroic Calamitous Longbow', 'Heroic Melancholic Flames (Weapon)',
          'Heroic Dolorous Flames (Weapon; the crafting table labels it Dreadful)',
          'Heroic Miserable Armor-Piercing (Weapon)']

def validate(html):
    doc = Document(html).root
    panels = [n for n in doc.nodes('details') if n.attrs.get('id') == 'heroic-purchase-checkoff']
    assert len(panels) == 1
    panel = panels[0]
    assert panel.attrs == {'id': 'heroic-purchase-checkoff', 'hidden': None}
    assert len(panel.nodes('summary')) == 1
    main = next(n for n in doc.nodes('main') if panel in n.children)
    siblings = [n for n in main.children if isinstance(n, Node)]
    assert siblings[siblings.index(panel)+1].attrs.get('id') == 'heroic-calamitous-subtotal'
    labels = panel.nodes('label')
    assert [norm(n.text()) for n in labels] == LABELS
    assert [n.attrs for n in panel.nodes('input')] == [dict(type='checkbox', id=i, autocomplete='off') for i in IDS]
    assert all(len(n.nodes('input')) == 1 for n in labels)
    assert panel.nodes('fieldset')[0].attrs == {'aria-describedby': 'heroic-purchase-help'}
    assert norm(panel.nodes('legend')[0].text()) == 'Already owned / do not need to buy this listed purchase'
    assert 'it is not all possible costs or current availability' in panel.text()
    assert 'Entries are not saved and reset when this page reloads.' in panel.text()
    assert [n.attrs['href'] for n in panel.nodes('a')] == ['#heroic-calamitous-recipe']
    assert panel.nodes('button')[0].attrs == {'type':'button','id':'heroic-purchase-reset'}
    result = next(n for n in panel.nodes('p') if n.attrs.get('id') == 'heroic-purchase-result')
    assert result.attrs == {'id':'heroic-purchase-result','role':'status','aria-live':'polite','aria-atomic':'true'}
    scripts = re.findall(r'<script id="heroic-purchase-script">(.*?)</script>', html, re.S)
    assert len(scripts) == 1
    script = scripts[0]
    actual = json.loads(re.search(r'var purchases=(\[.*?\]);', script).group(1).replace("'", '"'))
    crafting = json.loads((ROOT/'tools/fixtures/lamordia-handling/viktranium-experiment-crafting.browser-capture.json').read_text())
    item = json.loads((ROOT/'tools/fixtures/calamitous-recipe/heroic-dolorous-flames.browser-capture.json').read_text())
    assert actual == [[i,*cost] for i,cost in zip(IDS,source_costs(crafting,item))]
    assert not re.search(r'localStorage|sessionStorage|cookie|fetch|XMLHttpRequest|sendBeacon|innerHTML|eval\(', script)
    return script

HARNESS = r'''
const assert=require('node:assert/strict'),vm=require('node:vm');
const script=JSON.parse(process.argv[1]), ids=['purchase-blank','purchase-melancholic','purchase-dolorous','purchase-miserable'];
const nodes={},win={};
for(const id of [...ids,'heroic-purchase-checkoff','heroic-purchase-result','heroic-purchase-reset'])
 nodes[id]={checked:true,hidden:true,textContent:'',events:{},addEventListener(t,f){this.events[t]=f;}};
const document={getElementById(id){assert.ok(nodes[id],id);return nodes[id];}};
vm.runInNewContext(script,{document,window:{addEventListener(t,f){win[t]=f;}}});
const expected=(p,w)=>`Remaining listed ingredients for unchecked purchases only: ${p} each of Bleak Alternators, Conductors, Insulators and Resistors; ${w} Bleak Wires. Other possible costs and current availability are not established.`;
assert.equal(nodes['heroic-purchase-checkoff'].hidden,false);
assert.ok(ids.every(id=>!nodes[id].checked));
for(let mask=0;mask<16;mask++){
 ids.forEach((id,i)=>nodes[id].checked=Boolean(mask&(1<<i)));
 for(const id of ids){
  nodes[id].events.change();
  const parts=25-((mask&1)?5:0)-((mask&2)?5:0)-((mask&4)?10:0)-((mask&8)?5:0);
  assert.equal(nodes['heroic-purchase-result'].textContent,expected(parts,(mask&8)?0:20));
 }
}
for(const reset of [nodes['heroic-purchase-reset'].events.click,win.pageshow]){
 ids.forEach(id=>nodes[id].checked=true);reset();
 assert.ok(ids.every(id=>!nodes[id].checked));assert.equal(nodes['heroic-purchase-result'].textContent,expected(25,20));
}
console.log('16 combinations, all change handlers, initialization, reset and pageshow passed');
'''

class PurchaseCheckoffTests(unittest.TestCase):
    def test_source_controls_and_all_states(self):
        script=validate((ROOT/'index.html').read_text())
        subprocess.run(['node','-e',HARNESS,json.dumps(script)],check=True,capture_output=True,text=True)

    def test_negative_controls(self):
        html=(ROOT/'index.html').read_text()
        mutations=[("['purchase-blank',5,0]","['purchase-blank',6,0]"),
                   ("['purchase-melancholic',5,0]","['purchase-melancholic',5,20]"),
                   ("['purchase-dolorous',10,0]","['purchase-dolorous',5,0]"),
                   ("['purchase-miserable',5,20]","['purchase-miserable',5,0]"),
                   ('Heroic Melancholic Flames (Weapon)</label>','Legendary Melancholic Flames (Weapon)</label>'),
                   ('Weapon; the crafting table labels it Dreadful)</label>','Weapon)</label>'),
                   ('type="checkbox" id="purchase-blank"','type="number" id="purchase-blank"'),
                   ('role="status" aria-live="polite"','role="status" aria-live="off"'),
                   ('it is not all possible costs or current availability','it is all costs'),
                   ('<label><input type="checkbox" id="purchase-blank"','<span><input type="checkbox" id="purchase-blank"')]
        for old,new in mutations:
            with self.subTest(old=old):
                assert old in html
                with self.assertRaises((AssertionError,ValueError,IndexError,StopIteration)):
                    validate(html.replace(old,new,1))
        for old,new in [('!document.getElementById(p[0]).checked','document.getElementById(p[0]).checked'),
                        ('checked=false','checked=true'),('parts+=p[1]','parts+=p[2]'),
                        ("window.addEventListener('pageshow',reset);",'')]:
            script=validate(html).replace(old,new)
            r=subprocess.run(['node','-e',HARNESS,json.dumps(script)],capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0,old)
