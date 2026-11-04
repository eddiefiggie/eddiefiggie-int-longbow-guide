"""Check the score explanation against actual CLI normalization/formatting."""
import contextlib
import io
from html.parser import HTMLParser
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


class ScoreNoteDocument(HTMLParser):
    """Locate the real paragraph, not markup inside comments or inert content.

    This is an HTML-structure guard, not a CSS/browser visibility check.
    """
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.section = None
        self.table_seen = False
        self.inert = []
        self.notes = []
        self.note = None
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style', 'template'}:
            self.inert.append(tag)
        if self.inert:
            return
        attrs = dict(attrs)
        if tag in {'h2', 'h3'}:
            self.section = attrs.get('id')
            self.table_seen = False
        if tag == 'table':
            self.table_seen = True
        if tag == 'p' and attrs.get('id') == 'bow-model-score-scale':
            self.note = {'text': [], 'section': self.section,
                         'before_table': not self.table_seen, 'closed': False}
            self.notes.append(self.note)

    def handle_endtag(self, tag):
        if self.inert:
            if tag == self.inert[-1]:
                self.inert.pop()
            return
        if tag == 'p' and self.note is not None:
            self.note['closed'] = True
            self.note = None

    def handle_data(self, data):
        if self.note is not None and not self.inert:
            self.note['text'].append(data)


def check_note(html):
    notes = ScoreNoteDocument(html).notes
    if len(notes) != 1 or ''.join(notes[0]['text']) != TEXT or not notes[0]['closed']:
        raise ValueError('score explanation changed or missing from document content')
    if notes[0]['section'] != 'bow-damage-model' or not notes[0]['before_table']:
        raise ValueError('explanation must precede its table in the bow model section')


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

    def test_inert_or_misplaced_note_is_rejected(self):
        html = (ROOT / 'index.html').read_text()
        note = re.search(r'<p id="bow-model-score-scale">.*?</p>', html, re.S)[0]
        without = html.replace(note, '')
        table_end = without.index('</table>', without.index('<h3 id="bow-damage-model">')) + len('</table>')
        cases = {
            'commented out': html.replace(note, '<!--' + note + '-->'),
            'script string': html.replace(note, '<script type="text/plain">' + note + '</script>'),
            'uninstantiated template': html.replace(note, '<template>' + note + '</template>'),
            'wrong section': without.replace('<h3 id="bow-damage-model">', note + '<h3 id="bow-damage-model">'),
            'after model table': without[:table_end] + note + without[table_end:],
            'duplicate paragraph': html.replace(note, note + note),
        }
        for label, mutated in cases.items():
            with self.subTest(case=label):
                with self.assertRaises(ValueError):
                    check_note(mutated)
        # Comments containing an obsolete copy must not count as another real note.
        check_note(html.replace(note, '<!--' + note + '-->' + note))
        # Attribute order and harmless inline markup do not affect the paragraph.
        check_note(html.replace('id="bow-model-score-scale"', 'class="note" id="bow-model-score-scale"')
                   .replace('Other scores', '<em>Other</em> scores'))

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
