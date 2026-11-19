"""Selected recipe transcription checks; not independent DDO mechanics proof."""
from html import unescape
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


def band(text, level):
    anchor = 'gear-band-' + ('15-19' if level == 15 else '20-29')
    start = text.index('id="' + anchor + '"')
    stop = text.find('<h4 ', start)
    if stop < 0:
        stop = text.find('<h3 ', start)
    return text[start:stop]


class SelectedLevelingRecipes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guide = (ROOT / 'index.html').read_text()

    def test_selected_named_items_and_source_links(self):
        required = {
            15: ['Wallwatch Circlet', 'Wildwood Vest', 'Family Recruit Sigil',
                 'Celestial Sapphire Ring', 'Wildwood Gauntlets',
                 'Demogorgon', 'Belt of the Burrower', 'Cloak of the Forest',
                 'Shackles', 'Mysterious Ring', 'Quiver of Alacrity'],
            20: ['University Bulwark', 'University Archer', 'Study Spectacles',
                 'Bladesworn Bandolier', 'Wristbound Register', 'Helm of the Warblade',
                 'Gilvaenor', 'Neglected Wedding Ring', 'Epic Dustless Boots',
                 'Epic Thornlord', 'Epic Raven', 'Epic Gem of Many Facets',
                 'Epic Quiver of Alacrity'],
        }
        for level, names in required.items():
            section = unescape(band(self.guide, level))
            for name in names:
                with self.subTest(level=level, name=name):
                    self.assertIn(name, section)
            self.assertIn('https://chatgpt.com/c/', section)
            self.assertIn('https://ddowiki.com/', section)

    def test_each_primary_table_has_fourteen_equipped_rows(self):
        for level in (15, 20):
            section = band(self.guide, level)
            table = section[section.index('<table'):section.index('</table>')]
            body = table.split('<tbody>', 1)[1]
            self.assertEqual(len(re.findall(r'<tr\b', body)), 14)

    def test_essential_limits_remain_visible(self):
        heroic = unescape(re.sub('<[^>]+>', ' ', band(self.guide, 15)))
        epic = unescape(re.sub('<[^>]+>', ' ', band(self.guide, 20)))
        self.assertIn('None', heroic)
        self.assertRegex(heroic, r'(?i)lawful')
        self.assertRegex(heroic, r'(?i)negative level')
        self.assertIn('Good Luck +1', heroic)
        self.assertIn('Open Lock +13', heroic)
        self.assertRegex(epic, r'(?i)unspent|unselected|not selected')
        self.assertRegex(epic, r'(?i)reroll')
        self.assertRegex(epic, r'(?i)untested|unverified|not.*verified')
        self.assertNotIn('Topaz of Ranged Power +6', epic)
        self.assertNotIn('Epic Saltmarsh', epic)

    def test_current_transition_and_emerald_host_match_selected_recipe(self):
        self.assertIn('id="historical-calamitous-crafting"', self.guide)
        self.assertNotIn('ML34 Coldlight Runners host is equipped', self.guide)
        self.assertIn('Bound Elemental Ring of Flames host (finished ML30)', self.guide)
        self.assertTrue(re.search(r'<tr><td>15</td><td>(?:<[^>]+>)*Demogorgon', self.guide))
        self.assertNotIn('Unbreakable Cord are not in the current loadout', self.guide)


if __name__ == '__main__':
    unittest.main()
