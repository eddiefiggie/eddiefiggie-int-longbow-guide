"""Bow-ladder scroll affordance structure; browser and assistive-tech QA separate."""
import hashlib
from pathlib import Path
import re
import unittest
from test_lamordia_handling import Document, Node, guide_content, guide_text

ROOT = Path(__file__).resolve().parents[1]
CUE = ('All six columns: on narrow screens, scroll this table horizontally to see '
       '“Where”. With a keyboard, focus the table area and use the Left and Right Arrow keys.')
REGION = {'class': 'tw', 'tabindex': '0', 'role': 'region',
          'aria-labelledby': 'bow-ladder-levels-1-36', 'aria-describedby': 'bow-ladder-scroll-help'}
TABLE_SHA256 = '6a437f2298fba8703567235ac392145672658ce5cbaa35ca9c790a6501fda39d'


def validate(html):
    nodes = list(guide_content(Document(html).root))
    cues = [n for n in nodes if n.attrs.get('id') == 'bow-ladder-scroll-help']
    assert len(cues) == 1 and cues[0].tag == 'p', 'one actual cue paragraph'
    cue = cues[0]
    assert cue.attrs == {'id': 'bow-ladder-scroll-help'}, 'ordinary cue paragraph'
    assert guide_text(cue) == CUE, 'complete six-column and keyboard instruction'
    regions = [n for n in nodes if n.tag == 'div' and
               n.attrs.get('aria-labelledby') == 'bow-ladder-levels-1-36']
    assert len(regions) == 1 and regions[0].attrs == REGION, 'focusable labelled/described region'
    region = regions[0]
    mains = [n for n in nodes if n.tag == 'main' and cue in n.children and region in n.children]
    assert len(mains) == 1, 'cue outside scrolling region in normal main flow'
    siblings = [n for n in mains[0].children if isinstance(n, Node)]
    i = siblings.index(cue)
    assert siblings[i + 1] is region, 'cue immediately before its region'
    assert siblings[i - 1].attrs.get('id') == 'heroic-calamitous-subtotal', 'subtotal preserved before cue'
    headings = [n for n in siblings[:i] if n.tag in {'h2', 'h3'}]
    assert headings[-1].attrs.get('id') == REGION['aria-labelledby'], 'correct heading labels region'
    tables = [n for n in guide_content(region) if n.tag == 'table']
    assert len(tables) == 1 and not tables[0].attrs, 'native table semantics retained'
    headers = [guide_text(n) for n in tables[0].nodes('th')]
    assert len(headers) == 6 and headers[-1].startswith('Where'), 'six columns including Where'
    table = re.search(r'<table>.*?</table>', html[html.index('<h3 id="bow-ladder-levels-1-36">'):], re.S)[0]
    assert hashlib.sha256(table.encode()).hexdigest() == TABLE_SHA256, 'exact released ladder table preserved'
    assert '.tw{overflow-x:auto;' in html, 'native horizontal scroll retained'
    assert ':focus-visible{outline:2px solid var(--accent);outline-offset:2px}' in html, 'existing focus styling retained'


class BowLadderScrollCueTests(unittest.TestCase):
    def test_cue_region_and_exact_table(self):
        validate((ROOT / 'index.html').read_text())

    def test_discoverability_and_content_regressions(self):
        html = (ROOT / 'index.html').read_text()
        region = '<div class="tw" tabindex="0" role="region" aria-labelledby="bow-ladder-levels-1-36" aria-describedby="bow-ladder-scroll-help">'
        for old, new in [
            (region, region.replace('tabindex="0"', 'tabindex="-1"')),
            (region, region.replace('role="region"', 'role="presentation"')),
            ('aria-labelledby="bow-ladder-levels-1-36"', 'aria-labelledby="sources"'),
            ('aria-describedby="bow-ladder-scroll-help"', 'aria-describedby="missing"'),
            ('<p id="bow-ladder-scroll-help">', '<p id="bow-ladder-scroll-help" hidden>'),
            ('All six columns:', 'All five columns:'),
            ('to see “Where”', 'to see “Bow”'),
            ('.tw{overflow-x:auto;', '.tw{overflow-x:hidden;'),
            (':focus-visible{outline:2px solid var(--accent);outline-offset:2px}', ':focus-visible{outline:none}'),
            ('<td>The Sharn Syndicate</td>', '<td>Changed acquisition</td>'),
        ]:
            with self.subTest(old=old):
                self.assertIn(old, html)
                with self.assertRaises(AssertionError):
                    validate(html.replace(old, new))
        cue = re.search(r'<p id="bow-ladder-scroll-help">.*?</p>\n', html)[0]
        for changed in [html.replace(cue, ''), html.replace(cue, '<!--' + cue + '-->'),
                        html.replace(cue, '').replace(region, region + cue),
                        html.replace(cue, cue + cue)]:
            with self.assertRaises(AssertionError):
                validate(changed)


if __name__ == '__main__':
    unittest.main()
