"""Check guide arithmetic against model assumptions, not attack-speed game rules."""

from pathlib import Path
import re
import unittest

import bowmodel
from test_editorial_consistency import GuideText


ROOT = Path(__file__).resolve().parents[1]
FRACTION = r"(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)"


class ModelArithmeticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guide = GuideText((ROOT / "index.html").read_text(encoding="utf-8"))

    def alacrity_paragraph(self):
        matches = [block for blocks in self.guide.blocks.values() for block in blocks
                   if block.startswith("Ranged Alacrity on a bow.")]
        self.assertEqual(len(matches), 1, "Expected one alacrity explanation")
        return matches[0]

    def test_displayed_ratio_and_gain_match_the_documented_model_assumption(self):
        paragraph = self.alacrity_paragraph()
        displayed = re.search(FRACTION + r"\s*≈\s*(\d+(?:\.\d+)?)", paragraph)
        assumption = re.search(FRACTION, bowmodel.__doc__)
        self.assertIsNotNone(displayed, "Missing displayed ratio and approximation")
        self.assertIsNotNone(assumption, "Missing documented model ratio")
        numerator, denominator, approximation = map(float, displayed.groups())
        self.assertEqual((numerator, denominator), tuple(map(float, assumption.groups())))
        ratio = numerator / denominator
        self.assertAlmostEqual(approximation, ratio, places=4)
        gain = re.search(r"about\s*\+?(\d+(?:\.\d+)?)\s*%", paragraph[displayed.end():])
        self.assertIsNotNone(gain, "Missing percentage gain after the ratio")
        self.assertAlmostEqual(float(gain.group(1)), (ratio - 1) * 100, places=2)

    def test_alacrity_changes_only_the_synthetic_bows_model_multiplier(self):
        # Identical synthetic inputs except the model's item-alacrity field.
        # The 15% baseline is the model's existing assumption, not a rules check.
        baseline = (1, "1d8", 0, "none", 0, 0, 0, 0, 0)
        alacrity = (*baseline[:7], 0.20, baseline[8])
        baseline_result = bowmodel.dmg(baseline, 25)
        alacrity_result = bowmodel.dmg(alacrity, 25)
        self.assertAlmostEqual(alacrity_result[0] / baseline_result[0], 1.20 / 1.15,
                               places=12)
        self.assertEqual(alacrity_result[1:], baseline_result[1:])

    def test_alacrity_explanation_retains_assumption_and_review_scope(self):
        paragraph = self.alacrity_paragraph()
        self.assertRegex(paragraph, r"\bmodel\b[^.]*Haste-always-up")
        self.assertIn("model arithmetic", paragraph)
        self.assertRegex(paragraph, r"stacking[^.]*still needs[^.]*direct-source review")


if __name__ == "__main__":
    unittest.main()
