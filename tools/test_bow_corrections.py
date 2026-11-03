"""Focused regressions for the source-backed Spectral/Sapphire correction."""
import re
import unittest
from pathlib import Path
import bowmodel

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'index.html').read_text()
SPECTRAL_URL = 'https://ddowiki.com/page/Item:Spectral_Longbow_(level_4)'
SAPPHIRE_URL = 'https://ddowiki.com/page/Item:Sapphire_Sting'


def row_containing(text):
    rows = re.findall(r'<tr>.*?</tr>', HTML, re.S)
    return [row for row in rows if text in row]


class BowCorrectionTests(unittest.TestCase):
    def test_build_and_snapshot(self):
        self.assertIn('build 11-02-26.1', HTML)
        self.assertEqual((ROOT / 'index.html').read_bytes(),
                         (ROOT / 'versions/11-02-26.1.html').read_bytes())

    def test_spectral_ladder_level(self):
        rows = row_containing('>Spectral Longbow (level 4)</a></td>')
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0].startswith('<tr><td>4</td>'))
        self.assertIn('</a></td><td>4</td><td>20/x3</td>', rows[0])

    def test_spectral_discrepancy_visible(self):
        self.assertIn('Spectral source discrepancy:', HTML)
        self.assertIn('level-1 eligibility is not verified', HTML)

    def test_sapphire_ladder_profile(self):
        rows = row_containing('>Sapphire Sting</a></td>')
        self.assertEqual(len(rows), 1)
        self.assertIn('<td>7</td><td>native 19-20/x3 (not Keen)</td>', rows[0])

    def test_level_one_roadmap(self):
        rows = row_containing('<td>Harper: Strategic Combat I</td>')
        self.assertEqual(len(rows), 1)
        self.assertIn('Any level-1-eligible bow', rows[0])
        self.assertIn('Nicked Longbow from 2', rows[0])
        self.assertIn('Spectral Longbow from 4', rows[0])

    def test_level_four_roadmap(self):
        rows = row_containing('<tr><td>4-5</td>')
        self.assertEqual(len(rows), 1)
        self.assertIn('Sapphire Sting from 7 (not at 4-5)', rows[0])

    def test_no_blanket_keen_expiry(self):
        self.assertNotIn('worth nothing after it', HTML)
        self.assertNotIn('Keen bows are a level 1-8 choice only', HTML)
        self.assertIn('the bow’s other properties can still matter', HTML)

    def test_no_sapphire_stacking_inference(self):
        self.assertIn('post-Improved-Critical interaction is not verified here', HTML)
        self.assertNotIn('So a bow printed 19-20 without Keen', HTML)

    def test_sapphire_comparison_level_eight_only(self):
        self.assertIn('<tr><td>8 (19-20 x3)</td>', HTML)
        self.assertNotIn('<tr><td>8-9 (19-20 x3)</td>', HTML)
        self.assertIn('its comparison below is evaluated at level 8 only', HTML)

    def test_own_item_links(self):
        self.assertIn(SPECTRAL_URL, HTML)
        self.assertIn(SAPPHIRE_URL, HTML)

    def test_audit_scope_honest(self):
        self.assertNotIn('<p class="verified">All 35 bows checked', HTML)
        self.assertIn('These errors were missed by the 31 October check', HTML)
        self.assertIn('No full-ladder recertification', HTML)

    def test_spectral_not_level_one_reaper_swap(self):
        self.assertIn('The level-4 version is not a level-1 option', HTML)
        self.assertNotIn('it is the swap bow for every Reaper you meet before 23', HTML)

    def test_model_label_and_pre_ic_values(self):
        name, bow = next(entry for entry in bowmodel.BANDS[8] if entry[0].startswith('Sapphire Sting'))
        self.assertNotIn('Keen', name)
        self.assertEqual(bow[3], 'native19_unverified_ic')
        old_bow = (*bow[:3], 'keen', *bow[4:])
        self.assertEqual(bowmodel.dmg(bow, 8), bowmodel.dmg(old_bow, 8))

    def test_unverified_post_ic_rejected(self):
        bow = next(bow for name, bow in bowmodel.BANDS[8] if name.startswith('Sapphire Sting'))
        with self.assertRaisesRegex(ValueError, 'not source-verified'):
            bowmodel.dmg(bow, 12)

    def test_all_shipped_scenarios_still_run(self):
        entries = [(level, name, bow) for level, bows in bowmodel.BANDS.items() for name, bow in bows]
        self.assertEqual(len(entries), 39)
        for level, name, bow in entries:
            with self.subTest(level=level, bow=name):
                self.assertGreater(bowmodel.dmg(bow, level)[0], 0)


if __name__ == '__main__':
    unittest.main()
