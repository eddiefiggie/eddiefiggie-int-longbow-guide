"""Bind advice to the selected plan, not to a universal unlock or game rule."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


def validate(html):
    html = re.sub(r'<!--.*?-->', '', html, flags=re.S)
    rows = re.findall(r'<tr>.*?</tr>', html, re.S)
    purchases = [r for r in rows if 'Walker’s Guidance' in r and
                 ('Horizon:' in r or 'Horizon Walker:' in r)]
    assert len(purchases) == 2, 'both selected purchase rows'
    assert all(r.startswith('<tr><td>14</td>') for r in purchases), 'selected character level 14'
    tier = next(r for r in rows if 'Walker Training II' in r and '<td>4</td>' in r)
    assert '(purchased at character level 14 in this Guide’s plan)' in tier
    explanation = next(x for x in re.findall(r'<li>.*?</li>', html, re.S)
                       if x.startswith('<li><strong>Walker’s Guidance</strong>'))
    assert 'This Guide buys Walker’s Guidance at character level 14; it is not available earlier in the selected purchase order.' in explanation
    assert '<strong>From character level 14 in this Guide’s plan, use Walker’s Guidance</strong>' in html
    assert 'do not count on this button before its planned purchase.' in html
    assert 'Walker’s Guidance is purchased at character level 14 in this plan, not a claim about its earliest possible unlock.' in html
    for obsolete in ['covers lives before Ranger 9', 'it is your Evasion outright',
                     'Use Walker’s Guidance as your Evasion']:
        assert obsolete not in html, 'obsolete early-use instruction'


class WalkersGuidanceTimingTests(unittest.TestCase):
    def test_selected_plan_and_repeated_advice(self):
        validate((ROOT / 'index.html').read_text())

    def test_negative_controls(self):
        html = (ROOT / 'index.html').read_text()
        for old, new in [
            ('<tr><td>14</td><td></td><td>Horizon:', '<tr><td>9</td><td></td><td>Horizon:'),
            ('<tr><td>14</td><td>56</td>', '<tr><td>10</td><td>56</td>'),
            ('(purchased at character level 14 in this Guide’s plan)', '(covers lives before Ranger 9)'),
            ('This Guide buys Walker’s Guidance at character level 14;', 'This Guide buys Walker’s Guidance at character level 9;'),
            ('From character level 14 in this Guide’s plan, use Walker’s Guidance', 'Use Walker’s Guidance as your Evasion'),
            ('do not count on this button before its planned purchase.', 'use it before Ranger 9.'),
            ('not a claim about its earliest possible unlock.', 'its earliest possible unlock.'),
        ]:
            with self.subTest(old=old):
                self.assertIn(old, html)
                with self.assertRaises(AssertionError):
                    validate(html.replace(old,new))


if __name__ == '__main__':
    unittest.main()
