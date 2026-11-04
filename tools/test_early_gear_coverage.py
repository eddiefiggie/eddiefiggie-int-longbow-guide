"""Internal Guide consistency only; no independent item or starter-kit certification."""
import hashlib
from pathlib import Path
import re
import unittest
from test_editorial_consistency import GuideText
from test_lamordia_handling import Document, guide_content, guide_text

ROOT = Path(__file__).resolve().parents[1]
NOTE = ('The ten armor and accessory entries below are labelled ML 3 in this Guide, including '
        'the Saltmarsh Explorer pieces. On those listed minimum levels, they are not a level-1 '
        'or level-2 loadout. This Guide does not yet establish a complete level 1–2 kit; '
        'the weapon and quiver entries remain separate. This clarifies the existing labels, '
        'not a fresh verification of item eligibility.')
SUMMARY = ('Selected Saltmarsh pieces from 3, according to the ML 3 labels below; '
           'a complete level 1–2 kit is not established here.')
INTRO = ('The bands group the selected loadouts; use the minimum level listed for each item, '
         'not the start of the band.')


def validate(html):
    nodes = list(guide_content(Document(html).root))
    notes = [n for n in nodes if n.attrs.get('id') == 'early-gear-coverage']
    assert len(notes) == 1 and notes[0].tag == 'p', 'one actual coverage paragraph'
    assert guide_text(notes[0]) == NOTE, 'scoped unresolved-kit explanation'
    parsed = GuideText(html)
    rows = [r for t in parsed.tables['gear-milestones'] for r in t if r and r[0] == '1-7']
    assert len(rows) == 1 and rows[0][2] == SUMMARY, 'milestone timing matches printed ML labels'
    assert any(INTRO in p for p in parsed.blocks['levelling-gear']), 'band introduction'
    sets = [p for p in parsed.blocks['levelling-gear'] if p.startswith('Sets inside the levelling set.')]
    assert len(sets) == 1, 'one set summary'
    assert 'Saltmarsh Explorer from 3 through 4, according to the selected pieces’ ML 3 labels above' in sets[0], 'set timing follows existing item labels'
    assert 'Saltmarsh Explorer at 1-4' not in sets[0], 'no repeated level-1 set implication'
    skills = ' '.join(parsed.blocks['skills'])
    assert 'the Loupe’s +6 from its listed ML 3 through level 9' in skills, 'Loupe timing matches own row'
    assert 'the Loupe’s +6 at 1-9' not in skills, 'no contradictory repeated timing'
    band = html[html.index('<h4 id="gear-band-1-4">Levels 1-4</h4>'):html.index('<h4 id="gear-band-5-9">Levels 5-9</h4>')]
    assert 'id="early-gear-coverage"' in band and band.index('id="early-gear-coverage"') < band.index('<table>'), 'note beside early kit'
    table = re.search(r'<table>.*?</table>', band, re.S)[0]
    assert hashlib.sha256(table.encode()).hexdigest() == '82849b89490dc243c05eb239a9841586e3c7215b0598ca6316aad3ba6e7870e7', 'all original early item rows preserved'
    assert table.count('(ML 3)') == 10, 'ten printed ML3 labels, not external certification'


class EarlyGearCoverageTests(unittest.TestCase):
    def test_repeated_instructions_and_preserved_rows(self):
        validate((ROOT / 'index.html').read_text())

    def test_contradictions_and_overclaim_are_rejected(self):
        html = (ROOT / 'index.html').read_text()
        changes = [('Saltmarsh Explorer from 3 through 4, according to the selected pieces’ ML 3 labels above', 'Saltmarsh Explorer at 1-4'),
                   (SUMMARY, 'The levelling set, levels 1-4 (Saltmarsh Explorer pieces)'),
                   (INTRO, 'The bands are the levels at which the loadout changes.'),
                   ('the Loupe’s +6 from its listed ML 3 through level 9', 'the Loupe’s +6 at 1-9'),
                   ('does not yet establish a complete level 1–2 kit', 'establishes a complete level 1–2 kit'),
                   ('not a fresh verification of item eligibility', 'freshly verified item eligibility'),
                   ('are labelled ML 3 in this Guide', 'are officially certified ML 3'),
                   ('Smuggler\'s Gear</a> (ML 3)', 'Smuggler\'s Gear</a> (ML 1)')]
        for old, new in changes:
            with self.subTest(old=old):
                self.assertIn(old, html)
                with self.assertRaises(AssertionError):
                    validate(html.replace(old, new))
        note = re.search(r'<p id="early-gear-coverage">.*?</p>', html)[0]
        for mutated in (html.replace(note, ''), html.replace(note, '<!--' + note + '-->'),
                        html.replace(note, '') + note):
            with self.assertRaises(AssertionError):
                validate(mutated)


if __name__ == '__main__':
    unittest.main()
