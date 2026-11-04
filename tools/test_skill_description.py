"""Internal consistency only: existing allocations are not verified game rules."""
from pathlib import Path
import re
import unittest
from test_editorial_consistency import GuideText

ROOT = Path(__file__).resolve().parents[1]


def check_skill_description(html):
    guide = GuideText(html)
    summary = [row[1] for table in guide.tables['the-build-in-one-page']
               for row in table if row and row[0] == 'Skills']
    assert len(summary) == 1, 'Skills summary missing or duplicated'
    descriptions = [b for b in guide.blocks['skills']
                    if b.startswith('Other skills and life-specific exceptions.')]
    assert len(descriptions) == 1, 'Exception description missing or duplicated'
    description = descriptions[0]
    assert 'outside the general priority list' in summary[0]
    assert 'life-specific allocations' in summary[0]
    assert 'not necessarily untrained on every life' in description
    assert 'Diplomacy for spare class-life points' in description
    assert 'Hide, Move Silently and Concentration in the Scourge level-1 example' in description
    tables = [t for t in guide.tables['skills'] if t and t[0] ==
              ['Life', 'Level 1', 'Levels 2-10', 'Levels 11-20']]
    assert len(tables) == 1, 'Allocation table missing or duplicated'
    rows = tables[0][1:]
    class_row = [r for r in rows if r[0].startswith('Class life')]
    scourge_row = [r for r in rows if r[0].startswith('Aasimar Scourge life')]
    assert len(class_row) == len(scourge_row) == 1
    assert '4 more where you like (Diplomacy is the least bad)' in class_row[0][1]
    assert 'Hide, Move Silently and Concentration' in scourge_row[0][1]
    for block in [summary[0], *guide.blocks['skills']]:
        assert not re.search(r'\bnot trained\b|nothing in the build uses them', block, re.I), block


class SkillDescriptionTests(unittest.TestCase):
    def test_description_matches_existing_examples(self):
        check_skill_description((ROOT / 'index.html').read_text())

    def test_contradictions_and_missing_context_are_rejected(self):
        html = (ROOT / 'index.html').read_text()
        mutations = [
            ('Bluff and Diplomacy are outside the general priority list; see Skills for life-specific allocations.', 'Bluff and Diplomacy not trained.'),
            ('Other skills and life-specific exceptions.', 'Not trained, and why.'),
            ('not necessarily untrained on every life', 'untrained on every life'),
            ('Diplomacy for spare class-life points', 'Bluff for spare class-life points'),
            ('Hide, Move Silently and Concentration in the Scourge level-1 example', 'Hide, Move Silently and Concentration on every life'),
            ('4 more where you like (Diplomacy is the least bad)', '4 more where you like'),
            ('Search, Jump, Listen, Spot, Hide, Move Silently and Concentration', 'Search, Jump, Listen, Spot'),
            ('are outside the general priority list; the life-specific examples below still include some of them.', ': nothing in the build uses them.'),
        ]
        for old, new in mutations:
            with self.subTest(old=old):
                self.assertEqual(html.count(old), 1)
                with self.assertRaises(AssertionError):
                    check_skill_description(html.replace(old, new))


if __name__ == '__main__':
    unittest.main()
