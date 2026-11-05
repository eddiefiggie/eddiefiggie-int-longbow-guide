"""Standalone structural cue checks. Exact-source browser QA remains separate."""
import hashlib
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
CUE = ('All five columns: on narrow screens, scroll this table horizontally to see '
       '“What switches on”. With a keyboard, focus the table area and use the Left and Right Arrow keys.')


class CueDocument(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.cues = []
        self.regions = []
        self.cue_text = None
        self.region_depth = 0
        self.tables = 0
        self.cue_inside_region = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'p' and attrs.get('id') == 'roadmap-scroll-help':
            self.cues.append(attrs)
            self.cue_inside_region |= self.region_depth > 0
            self.cue_text = []
        if tag == 'div':
            if attrs.get('aria-labelledby') == 'levelling-roadmap':
                self.regions.append(attrs)
                self.region_depth = 1
            elif self.region_depth:
                self.region_depth += 1
        if tag == 'table' and self.region_depth:
            self.tables += 1

    def handle_data(self, data):
        # Capture cue until its closing paragraph; inline strong text is included.
        if self.cue_text is not None:
            self.cue_text.append(data)

    def handle_endtag(self, tag):
        if tag == 'p' and self.cue_text is not None:
            self.text = ' '.join(''.join(self.cue_text).split())
            self.cue_text = None
        if tag == 'div' and self.region_depth:
            self.region_depth -= 1


def validate(html):
    doc = CueDocument(html)
    assert doc.cues == [{'id':'roadmap-scroll-help'}], 'one ordinary visible cue'
    assert doc.text == CUE, 'complete instructions'
    assert not doc.cue_inside_region, 'cue outside horizontally scrolled content'
    assert doc.regions == [{'class':'tw', 'tabindex':'0', 'role':'region',
                            'aria-labelledby':'levelling-roadmap', 'aria-describedby':'roadmap-scroll-help'}], 'focus and accessible relationships'
    assert doc.tables == 1, 'one native table within region'
    assert html.index('id="roadmap-scroll-help"') < html.index('aria-describedby="roadmap-scroll-help"'), 'cue before region'
    assert '.tw{overflow-x:auto;' in html, 'horizontal scrolling retained'
    start = html.index('<h2 id="levelling-roadmap">')
    table = re.search(r'<table>.*?</table>', html[start:], re.S).group()
    # The only content delta is the retained-source timing cross-reference.
    # test_endgame_evidence also proves purchase choices match the prior tree.
    assert hashlib.sha256(table.encode()).hexdigest() == '2ac414502cccb1ce3ff12a147f33d64ee6bcd89d4e1f5522477764b851d93fc1', 'main roadmap table matches reviewed timing annotation'


class RoadmapScrollCueTests(unittest.TestCase):
    def test_cue_focus_relationships_and_table_preservation(self):
        validate((ROOT/'index.html').read_text())

    def test_discoverability_regressions_rejected(self):
        html = (ROOT/'index.html').read_text()
        for old,new in [('tabindex="0"','tabindex="-1"'),
                        ('aria-describedby="roadmap-scroll-help"','aria-describedby="missing"'),
                        ('<p id="roadmap-scroll-help">','<p id="roadmap-scroll-help" hidden>'),
                        ('scroll this table horizontally','read this table'),
                        ('.tw{overflow-x:auto;','.tw{overflow-x:hidden;'),
                        ('<th>What switches on</th>','<th>Changed column</th>')]:
            with self.subTest(old=old),self.assertRaises(AssertionError):
                validate(html.replace(old,new))
        cue = re.search(r'<p id="roadmap-scroll-help">.*?</p>\n',html).group()
        moved = html.replace(cue,'').replace('aria-describedby="roadmap-scroll-help">',
                                            'aria-describedby="roadmap-scroll-help">'+cue)
        with self.assertRaisesRegex(AssertionError, 'outside'):
            validate(moved)


if __name__ == '__main__':
    unittest.main()
