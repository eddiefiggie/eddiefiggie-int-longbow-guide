"""Retained-source recipe guardrail; does not certify bow stats or live mechanics."""
import copy
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tools/fixtures/calamitous-recipe'
CAPTURES = (
    ('../lamordia-handling/viktranium-experiment-crafting.browser-capture.json', 612486,
     'e40935cdc1a352a7fa3dde5af1fd7a852e0a4e50f9d9ed3c44dfdb3cbbf5458e',
     'Viktranium_Experiment_crafting', 720728),
    ('heroic-dolorous-flames.browser-capture.json', 177106,
     '14ed74d4fc2848f1287920a924f9b19c6e7f901b4bf0fbba25564f617ef945b8',
     'Item:Dolorous_Flames_(heroic)', 702384),
)
PARTS = ('Alternators', 'Conductors', 'Insulators', 'Resistors')


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def source_costs(crafting, item):
    for data, (_, _, _, title, revision) in zip((crafting, item), CAPTURES):
        require(data['url'] == 'https://ddowiki.com/page/' + title, 'source identity')
        require(data['permalink'] == f'https://ddowiki.com/index.php?title={title}&oldid={revision}', 'source revision')
        require(data['canonical'] is None, 'canonical metadata changed')
    text = crafting['visibleText']
    blank = re.search(r'Heroic Calamitous weapons cost (.*?) to craft', text)
    require(blank is not None, 'separate heroic blank cost')
    costs = [blank.group(1)]
    for family in ('Melancholic', 'Dolorous', 'Miserable'):
        # Bound the source to the standard Weapon section, before accessories,
        # armor and the separate Wicked machine. Never search globally for costs.
        weapon = text.split('Weapons[edit]\n', 1)[1].split('Woeful (Weapons)[edit]', 1)[0]
        section = weapon.split(f'{family} (Weapons)[edit]', 1)[1]
        section = section.split('(Weapons)[edit]', 1)[0]
        match = re.search(r'Heroic versions cost: ([^\n]+)\nLegendary versions cost: ([^\n]+)', section)
        require(match is not None, 'heroic/legendary costs')
        require(f'{family} (Weapon)\tHeroic Effect (ML:8)\tLegendary Effect (ML:34)' in section, 'weapon column context')
        costs.append(match.group(1))
        selected = {'Melancholic': 'Melancholic Flames\n(Heroic) / (Legendary)\tAdds Adamantine material type. On hit: 2d6 Fire Damage.\tAdds Adamantine material type. On hit: 16d6 Fire Damage.',
                    'Dolorous': 'Dolorous Flames\n(Heroic - Dreadful) / (Legendary)\tAdds Good alignment bypass and Flaming.',
                    'Miserable': 'Miserable Armor-Piercing\n(Heroic) / (Legendary)\tAdds Armor-Piercing. +8% Enhancement bonus to bypass enemy Fortification\tAdds Armor-Piercing. +23% Enhancement bonus to bypass enemy Fortification'}[family]
        require(selected in section, 'selected augment identity and heroic column')
        if family == 'Dolorous':
            require('BUG: Certain Heroic augments are listed as Dreadful instead of Dolorous' in section, 'naming warning')
    parsed = []
    for cost, quantity, wires in zip(costs, (5, 5, 10, 5), (0, 0, 0, 20)):
        pairs = re.findall(r'(\d+) (Bleak \w+)', cost)
        expected = [(str(quantity), 'Bleak ' + part) for part in PARTS]
        if wires:
            expected.append((str(wires), 'Bleak Wires'))
        require(pairs == expected, 'ingredient identities and quantities')
        # Reject unparsed extras, including Legendary ingredients.
        residue = re.sub(r'\d+ Bleak \w+', '', cost).replace('and', '').replace(',', '').strip()
        require(not residue, 'unparsed ingredients')
        parsed.append((quantity, wires))
    require('Augment Type\tLamordia: Dolorous (Weapon)' in item['visibleText'], 'item weapon context')
    require('Minimum Level\t8\t' in item['visibleText'], 'item heroic context')
    require('Item:Dolorous Flames (heroic)' in item['visibleText'], 'item identity')
    require('6d6 Fire damage on each critical hit.' in item['visibleText'], 'item context')
    return parsed


class RecipeHTML(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.parts = []
        self.rows = []
        self.row = None
        self.count = 0
        self.feed(html)
    def handle_starttag(self, tag, attrs):
        if tag == 'div' and dict(attrs).get('id') == 'heroic-calamitous-recipe':
            self.count += 1
            self.depth = 1
        elif self.depth and tag == 'div':
            self.depth += 1
        if self.depth and tag == 'li':
            self.row = []
    def handle_endtag(self, tag):
        if self.depth and tag == 'li':
            self.rows.append(''.join(self.row))
            self.row = None
        if self.depth and tag == 'div':
            self.depth -= 1
    def handle_data(self, data):
        if self.depth:
            self.parts.append(data)
            if self.row is not None:
                self.row.append(data)


def validate_recipe(html, crafting, item):
    costs = source_costs(crafting, item)
    # Anchor the purchase list to its actual ladder row and selected fills.
    rows = [row for row in re.findall(r'<tr>.*?</tr>', html, re.S)
            if 'id="heroic-calamitous-recipe"' in row]
    require(len(rows) == 1, 'recipe must belong to one ladder row')
    cells = re.findall(r'<td>(.*?)</td>', rows[0], re.S)
    require(len(cells) == 6, 'ladder row shape')
    require(cells[:3] == ['8', '<strong>Calamitous Longbow</strong> (crafted)', '8'],
            'heroic Calamitous ladder identity')
    selected = ('Fill: Melancholic Flames (2d6 Fire on hit, Adamantine), '
                'Dolorous Flames (Good bypass, 6d6 Fire on critical), '
                'Miserable Armor-Piercing 8%')
    require(cells[4].endswith(selected), 'selected ladder fills must match purchases')
    require('id="heroic-calamitous-recipe"' in cells[5], 'recipe acquisition cell')
    recipe = RecipeHTML(html)
    require(recipe.count == 1, 'one separate recipe block')
    names = ('Blank Calamitous Longbow', 'Heroic Melancholic Flames (Weapon)',
             'Heroic Dolorous Flames (Weapon)', 'Heroic Miserable Armor-Piercing (Weapon)')
    expected = [f'{name}: {q} of each part' + (f' plus {w} Bleak Wires.' if w else '; no Bleak Wires listed.')
                for name, (q, w) in zip(names, costs)]
    require(recipe.rows == expected, 'selected purchases must match heroic source costs')
    text = ''.join(recipe.parts)
    require('separate purchases; “parts” below means Bleak Alternators, Conductors, Insulators and Resistors.' in text, 'ingredient key')
    require('some heroic Dolorous augments are named Dreadful in game and marks Flames “Heroic - Dreadful”' in text, 'guide naming qualifier')
    require('not all possible costs or current availability' in text, 'partial scope')
    context = ('Heroic Viktranium Experiment crafting — separate purchases; “parts” below means '
               'Bleak Alternators, Conductors, Insulators and Resistors.' + ''.join(expected) +
               'The captured crafting table warns that some heroic Dolorous augments are named '
               'Dreadful in game and marks Flames “Heroic - Dreadful”; the heroic item page calls '
               'this selected augment Dolorous Flames. These retained sources clarify the listed '
               'purchases, not all possible costs or current availability.')
    require(' '.join(text.split()) == ' '.join(context.split()), 'reviewed recipe context')


class CalamitousRecipeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = [json.loads((FIXTURES / c[0]).read_bytes()) for c in CAPTURES]
        cls.html = (ROOT / 'index.html').read_text()

    def test_exact_retained_capture_bytes(self):
        for name, size, digest, _, _ in CAPTURES:
            with self.subTest(name=name):
                raw = (FIXTURES / name).read_bytes()
                self.assertEqual(len(raw), size)
                self.assertEqual(hashlib.sha256(raw).hexdigest(), digest)
                self.assertIsInstance(json.loads(raw)['html'], str)

    def test_selected_recipe_matches_actual_heroic_source(self):
        validate_recipe(self.html, *self.sources)

    def test_guide_negative_controls(self):
        changes = [
            ('Miserable Armor-Piercing 8%</td>', 'Miserable Dimlight +1 INT</td>'),
            ('<strong>Calamitous Longbow</strong> (crafted)', '<strong>Different Longbow</strong> (crafted)'),
            ('Blank Calamitous Longbow: 5', 'Blank Calamitous Longbow: 25'),
            ('Heroic Melancholic Flames (Weapon): 5 of each part; no Bleak Wires listed.', 'Heroic Melancholic Flames (Weapon): 5 of each part plus 20 Bleak Wires.'),
            ('Heroic Dolorous Flames (Weapon): 10', 'Heroic Dolorous Flames (Weapon): 5'),
            ('plus 20 Bleak Wires.', 'plus 100 Bleak Wires.'),
            ('Blank Calamitous Longbow:', 'Included bow:'),
            ('Bleak Alternators, Conductors', 'Bleak Transformers, Conductors'),
            ('Heroic Miserable Armor-Piercing (Weapon):', 'Heroic Miserable Dimlight (Weapon):'),
            ('some heroic Dolorous augments are named Dreadful in game', 'no naming warning'),
            ('Heroic Melancholic Flames (Weapon):', 'Legendary Melancholic Flames (Weapon):'),
            ('no Bleak Wires listed.', 'no Bleak Wires.'),
            ('not all possible costs or current availability.',
             'not all possible costs or current availability. No other costs apply.'),
            ('not all possible costs or current availability.',
             'not all possible costs or current availability. These purchases are always available.'),
        ]
        for old, new in changes:
            with self.subTest(old=old):
                self.assertIn(old, self.html)
                with self.assertRaises(AssertionError):
                    validate_recipe(self.html.replace(old, new), *self.sources)
        block = re.search(r'<div id="heroic-calamitous-recipe">.*?</div>', self.html, re.S).group()
        with self.assertRaises(AssertionError):
            validate_recipe(self.html.replace(block, '') + block, *self.sources)
        with self.assertRaises(AssertionError):
            validate_recipe(re.sub(r'<li>Blank Calamitous Longbow:.*?</li>', '', self.html), *self.sources)

    def test_source_semantic_negative_controls_even_without_hash_check(self):
        changes = [
            ('Heroic Calamitous weapons cost 5', 'Heroic Calamitous weapons cost 25'),
            ('5 Bleak Alternators', '5 Bleak Transformers'),
            ('Heroic versions cost: 5 Bleak Alternators, 5 Bleak Conductors, 5 Bleak Insulators, 5 Bleak Resistors\n', 'Heroic versions cost: 5 Bleak Alternators, 5 Bleak Conductors, 5 Bleak Insulators, 5 Bleak Resistors, 20 Bleak Wires\n'),
            ('Heroic Effect (ML:8)\tLegendary Effect (ML:34)', 'Legendary Effect (ML:34)\tHeroic Effect (ML:8)'),
            ('Melancholic (Weapon)\t', 'Melancholic (Armor)\t'),
            ('Miserable Armor-Piercing\n', 'Miserable Dimlight\n'),
            ('Heroic - Dreadful', 'Heroic'),
            ('BUG: Certain Heroic augments are listed as Dreadful instead of Dolorous', 'Warning removed'),
            ('On hit: 2d6 Fire Damage.\tAdds Adamantine material type. On hit: 16d6 Fire Damage.', 'On hit: 16d6 Fire Damage.\tAdds Adamantine material type. On hit: 2d6 Fire Damage.'),
        ]
        for old, new in changes:
            with self.subTest(old=old):
                sources = copy.deepcopy(self.sources)
                self.assertIn(old, sources[0]['visibleText'])
                sources[0]['visibleText'] = sources[0]['visibleText'].replace(old, new)
                with self.assertRaises(AssertionError):
                    validate_recipe(self.html, *sources)
        for index in (0, 1):
            for field in ('permalink', 'url'):
                sources = copy.deepcopy(self.sources)
                sources[index][field] += 'altered'
                with self.assertRaises(AssertionError):
                    validate_recipe(self.html, *sources)
        sources = copy.deepcopy(self.sources)
        sources[1]['visibleText'] = sources[1]['visibleText'].replace('Minimum Level\t8\t', 'Minimum Level\t34\t')
        with self.assertRaises(AssertionError):
            validate_recipe(self.html, *sources)


if __name__ == '__main__':
    unittest.main()
