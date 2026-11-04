"""Quick-reference routing and preservation, not feat legality certification."""
import hashlib
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
DETAIL_SHA = '47cccc7724c1ea271cf83f02a26d38822987a88d4159020b02afb51bb7b55321'


def validate(html):
    html = re.sub(r'<!--.*?-->', '', html, flags=re.S)
    row = next(r for r in re.findall(r'<tr>.*?</tr>', html, re.S)
               if r.startswith('<tr><td><a href="#heroic-feats">Heroic feats</a>'))
    assert 'Point Blank Shot 1, Precision 3, Insightful Reflexes 6, Improved Critical: Ranged 9.' in row
    assert 'For levels 12–18, follow the <a href="#heroic-feats">full-BAB and 3/4-BAB schedules</a>' in row
    assert '<a href="#aasimar-scourge-feats">Aasimar Scourge has a separate schedule and class grant</a>' in row
    assert 'See those instructions for the selected order and optional alternative.' in row
    assert 'Improved Precise Shot 12' not in row, 'no unconditional late schedule'
    target = '<p id="aasimar-scourge-feats"><strong>Aasimar Scourge lives, feat by feat.</strong>'
    assert html.count('id="aasimar-scourge-feats"') == 1 and target in html
    detail = html.split('<h2 id="heroic-feats">',1)[1].split('<h2 ',1)[0]
    # Pin the full pre-existing detailed section, normalizing only the added anchor.
    detail = detail.replace(target, '<p><strong>Aasimar Scourge lives, feat by feat.</strong>')
    assert hashlib.sha256(detail.encode()).hexdigest() == DETAIL_SHA, 'all detailed schedules, grant and alternatives preserved'


class FeatSummaryRoutingTests(unittest.TestCase):
    def test_routing_and_exact_schedules(self):
        validate((ROOT/'index.html').read_text())

    def test_negative_controls(self):
        html = (ROOT/'index.html').read_text()
        mutations = [
            ('full-BAB and 3/4-BAB schedules', 'full-BAB schedule'),
            ('href="#aasimar-scourge-feats"', 'href="#heroic-feats"'),
            ('id="aasimar-scourge-feats"', 'id="wrong-target"'),
            ('separate schedule and class grant', 'same schedule'),
            ('selected order and optional alternative', 'selected order'),
            ('<td><strong>Improved Precise Shot</strong></td><td>Weapon Finesse</td>', '<td>Weapon Finesse</td><td>Weapon Finesse</td>'),
            ('<td><strong>Weapon Finesse</strong></td><td><strong>Improved Precise Shot</strong></td>', '<td><strong>Weapon Finesse</strong></td><td>Weapon Finesse</td>'),
            ('<td><strong>Power Critical</strong></td>', '<td>Weapon Focus: Ranged</td>'),
            ('Improved Precise Shot is granted by Ranger 11 at this level;', 'Improved Precise Shot is selected at this level;'),
            ('Sneak of Shadows is the alternative at 18 if you hold a Rogue past life and want the skulk;', 'There is no alternative at 18;'),
        ]
        for old,new in mutations:
            with self.subTest(old=old):
                self.assertIn(old,html)
                with self.assertRaises(AssertionError): validate(html.replace(old,new))


if __name__ == '__main__': unittest.main()
