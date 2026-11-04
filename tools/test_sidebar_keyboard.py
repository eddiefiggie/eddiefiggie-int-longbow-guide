"""Source-contract checks; actual focus/scroll behavior needs browser QA."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


def validate(html):
    # Ignore commented-out rules and script text masquerading as CSS.
    css = re.search(r'<style>(.*?)</style>', html, re.S)[1]
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    assert re.search(r'#sidenav li\.open > ol,\s*#sidenav li:focus-within > ol\s*\{display:block\}', css), 'focused descendants keep their group visible'
    assert '#sidenav ol ol{margin:.1rem 0 .3rem .6rem;display:none}' in css, 'inactive groups remain compact'
    assert '@media(min-width:1180px)' in css.replace(' ', ''), 'desktop-only sidebar retained'
    script = re.search(r'<script>(.*?)</script>', html, re.S)[1]
    script = re.sub(r'/\*.*?\*/|//[^\n]*', '', script, flags=re.S)
    assert script.count('scrollIntoView(') == 1, 'one sidebar recenter operation'
    assert "if(!nav.contains(document.activeElement) && (r.top<40||r.bottom>window.innerHeight-40)) cur.a.scrollIntoView({block:'center'});" in script, 'recenter cannot override keyboard exploration'
    assert ':focus-visible{outline:2px solid var(--accent);outline-offset:2px}' in css, 'visible focus retained'


class SidebarKeyboardTests(unittest.TestCase):
    def test_keyboard_contract(self):
        validate((ROOT / 'index.html').read_text())

    def test_negative_controls(self):
        html = (ROOT / 'index.html').read_text()
        for old, new in [
            (', #sidenav li:focus-within > ol', ''),
            (':focus-within', ':focus'),
            (':focus-within', ':hover'),
            ('!nav.contains(document.activeElement) && ', ''),
            ('!nav.contains(document.activeElement)', 'nav.contains(document.activeElement)'),
            ('!nav.contains(document.activeElement)', 'nav === document.activeElement'),
            ("cur.a.scrollIntoView({block:'center'});", "cur.a.scrollIntoView({block:'center'}); cur.a.scrollIntoView();"),
        ]:
            with self.subTest(old=old, new=new):
                self.assertIn(old, html)
                with self.assertRaises(AssertionError):
                    validate(html.replace(old, new))


if __name__ == '__main__':
    unittest.main()
