"""Check the score explanation against actual CLI normalization/formatting."""
import contextlib
import io
from pathlib import Path
import re
import runpy
import unittest

import bowmodel

ROOT = Path(__file__).resolve().parents[1]
TEXT = ('Reading the scores: each comparison sets its highest modeled result to 100. '
        'Other scores are relative to that same row: 75 means approximately three quarters '
        'of its highest modeled per-attack result under the assumptions above. '
        'The table summarizes with approximate whole-number scores; the model script '
        'prints percentages to one decimal place. Rounding can make unequal results look tied. '
        'These are not DPS figures, and scores in different level rows are not comparable.')


def check_note(html):
    matches = re.findall(r'<p id="bow-model-score-scale">(.*?)</p>', html, re.S)
    if len(matches) != 1 or re.sub(r'<[^>]+>', '', matches[0]) != TEXT:
        raise ValueError('score explanation changed')
    section = html.index('<h3 id="bow-damage-model">')
    if not section < html.index('<p id="bow-model-score-scale">') < html.index('<table>', section):
        raise ValueError('explanation must precede its table')


class ScoreExplanationTests(unittest.TestCase):
    def test_visible_explanation_and_semantic_faults(self):
        html = (ROOT / 'index.html').read_text()
        check_note(html)
        for old, new in [('to 100', 'to 1000'), ('same row', 'all rows'),
                         ('three quarters', 'one quarter'), ('one decimal place', 'two decimal places'),
                         ('not DPS figures', 'DPS figures'), ('are not comparable', 'are comparable'),
                         ('can make unequal results look tied', 'proves equal results')]:
            with self.subTest(old=old):
                self.assertIn(old, html)
                with self.assertRaises(ValueError):
                    check_note(html.replace(old, new))

    def test_actual_cli_normalizes_each_comparison_to_100_with_one_decimal(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            runpy.run_path(str(ROOT / 'tools/bowmodel.py'), run_name='__main__')
        level = None
        count = 0
        for line in output.getvalue().splitlines():
            heading = re.match(r'== Level (\d+):', line)
            if heading:
                level = int(heading[1])
                values = {name: bowmodel.dmg(bow, level)[0] for name, bow in bowmodel.BANDS[level]}
                top = max(values.values())
            row = re.match(r'\s*[\d.]+\s+\(\s*([\d.]+)%\).*?per-hit\s+[\d.]+\s+(.+)$', line)
            if row:
                self.assertRegex(row[1], r'^\d+\.\d$')
                self.assertEqual(row[1], f'{values[row[2]] / top * 100:.1f}')
                count += 1
        self.assertEqual(count, 39)

    def test_example_and_rounding_do_not_imply_exact_ties(self):
        scores = [bowmodel.dmg(bow, 8)[0] for _, bow in bowmodel.BANDS[8]]
        sapphire = scores[2] / max(scores) * 100
        self.assertEqual(round(sapphire), 75)
        self.assertAlmostEqual(sapphire / 100, .75, delta=.005)
        values = [bowmodel.dmg(bow, 15)[0] for _, bow in bowmodel.BANDS[15]]
        self.assertNotEqual(values[0], values[1])
        self.assertEqual(round(values[0] / max(values) * 100), 100)
        self.assertEqual(round(values[1] / max(values) * 100), 100)
