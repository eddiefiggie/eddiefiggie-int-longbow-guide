"""Source-bound handling instructions; no live-game or other-slot certification."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from html.parser import HTMLParser

def norm(text):
    return ' '.join(text.split())


class Node:
    def __init__(self, tag='', attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []

    def nodes(self, tag):
        return [node for child in self.children if isinstance(child, Node)
                for node in ([child] if child.tag == tag else []) + child.nodes(tag)]

    def text(self, tooltips=False):
        if self.tag in {'script', 'style'}:
            return ''
        if not tooltips and ('tooltip' in self.attrs.get('class', '').split()
                             or 'display: none' in self.attrs.get('style', '')):
            return ''
        return ''.join(c.text(tooltips) if isinstance(c, Node) else c for c in self.children)


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack = [self.root]
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                       'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def one(nodes, label):
    require(len(nodes) == 1, f'{label}: expected one, found {len(nodes)}')
    return nodes[0]



ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'tools/fixtures/lamordia-handling/viktranium-experiment-crafting.browser-capture.json'


def section(html, start, end):
    start_marker, end_marker = f'id="{start}"', f'id="{end}"'
    require(html.count(start_marker) == 1, 'unique source section')
    require(html.count(end_marker) == 1, 'unique source section end')
    begin, finish = html.index(start_marker), html.index(end_marker)
    require(finish > begin, 'ordered source section boundaries')
    return html[begin + len(start_marker):finish]


def source_contract(source):
    require(source['permalink'] == 'https://ddowiki.com/index.php?title=Viktranium_Experiment_crafting&oldid=720728', 'revision')
    require(source['url'] == 'https://ddowiki.com/page/Viktranium_Experiment_crafting', 'identity')
    doc = Document(section(source['html'], 'Lamordia_Augments', 'Items_with_Lamordia_augment_slots')).root
    texts = [norm(n.text()) for n in doc.nodes('p')]
    require(any('Each augment type can only fit into an augment slot that exactly matches its type.' in t and
                '"Melancholic (Weapon)" augment cannot go in a "Melancholic Slot (Armor)" slot' in t and
                'Augment Type row' in t for t in texts), 'family/variant compatibility')
    require('Note that Heroic slots will accept Legendary augments (and vice versa) but a Legendary augment will increase the minimum level of a heroic item to 34.' in texts, 'heroic/legendary level consequence')
    doc = Document(section(source['html'], 'Unslotting', 'External_Links')).root
    items = [norm(n.text()) for n in doc.nodes('li')]
    require('You can destroy a currently-slotted augment by placing a new augment into the slot.' in items, 'overwrite consequence')
    recovery = one([t for t in items if t.startswith('You can unslot a Lamordia augment')], 'recovery context')
    for claim in ('using a Viktranium Pick', 'rare ingredient found within chests in the Chill of Ravenloft pack or purchased in the DDO Store',
                  'returns the augment to you unharmed', 'may also be found as rewards', "A Jeweler's Tool Kit will not work."):
        require(claim in recovery, claim)
    require(any(n.attrs.get('href') == '/page/Item:Viktranium_Pick' for n in doc.nodes('a')), 'Pick identity link')


def guide_contract(html):
    doc = Document(html).root
    block = one([n for n in doc.nodes('section') if n.attrs.get('id') == 'lamordia-augment-handling'], 'handling checklist')
    text = norm(block.text())
    for claim in ('family and variant must match', 'not Melancholic Slot (Armor)',
                  'Legendary augment raises a heroic item’s minimum level to 34',
                  'choose the heroic versions', 'can destroy the slotted augment',
                  'Viktranium Pick removes a Lamordia augment and returns it unharmed',
                  'Jeweler’s Tool Kit does not work', 'rare finds', 'possible Chill of Ravenloft Saga rewards',
                  'does not give a drop rate or guarantee a reward', 'not a fresh live-game check',
                  'ordinary colored augment slots'):
        require(claim in text, claim)
    # A concise exact context guards against additions that negate the cautions.
    expected = (ROOT / 'tools/fixtures/lamordia-handling/handling-guide.txt').read_text().strip()
    require(text == expected, 'reviewed handling context drift')


class LamordiaHandlingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = SOURCE.read_bytes();cls.source = json.loads(cls.raw)
        cls.guide = (ROOT / 'index.html').read_text()

    def test_retained_source_and_reader_checklist(self):
        self.assertEqual(len(self.raw), 612486)
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), 'e40935cdc1a352a7fa3dde5af1fd7a852e0a4e50f9d9ed3c44dfdb3cbbf5458e')
        source_contract(self.source);guide_contract(self.guide)

    def test_source_context_faults(self):
        mutations = [('to 34.', 'to 8.'), ('can destroy a currently-slotted', 'can preserve a currently-slotted'),
                     ('returns the augment to you unharmed', 'destroys the augment'),
                     ('will <i>not</i> work', 'will work'), ('may also be found as rewards', 'are guaranteed rewards'),
                     ('/page/Item:Viktranium_Pick', '/page/Item:Other_Pick'),
                     ('id="Unslotting"', 'id="Unrelated"'),
                     ('id="External_Links"', 'id="Changed_end"'),
                     ('id="Items_with_Lamordia_augment_slots"', 'id="Changed_end"'),
                     ('id="Lamordia_Augments"', 'id="Ordinary_Augments"'),
                     ('exactly matches its type', 'has any type')]
        for old,new in mutations:
            with self.subTest(old=old):
                source=copy.deepcopy(self.source);self.assertIn(old,source['html'])
                source['html']=source['html'].replace(old,new)
                with self.assertRaises(ValueError):source_contract(source)
        source=copy.deepcopy(self.source)
        source['html']=source['html'].replace('id="Unslotting"','id="Temporary"').replace(
            'id="External_Links"','id="Unslotting"').replace('id="Temporary"','id="External_Links"')
        with self.assertRaisesRegex(ValueError, 'ordered source section boundaries'):
            source_contract(source)
        source=copy.deepcopy(self.source);source['permalink']+='changed'
        with self.assertRaises(ValueError):source_contract(source)

    def test_reader_mistakes_and_unsupported_promises(self):
        mutations=[('minimum level to 34','minimum level to 8'), ('family and variant must match','any variant fits'),
                   ('can destroy the slotted augment','always preserves the slotted augment'),
                   ('Jeweler’s Tool Kit does not work','Jeweler’s Tool Kit works'),
                   ('possible Chill of Ravenloft Saga rewards','guaranteed Chill of Ravenloft Saga rewards'),
                   ('returns it unharmed','destroys it'),
                   ('Check that you have the Pick','This also resets minimum level to 8. Check that you have the Pick')]
        for old,new in mutations:
            with self.subTest(old=old):
                self.assertIn(old,self.guide)
                with self.assertRaises(ValueError):guide_contract(self.guide.replace(old,new))


if __name__ == '__main__':unittest.main()
