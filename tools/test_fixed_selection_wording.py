"""Six current-recipe wording fixes; selected choices and source limits stay fixed."""
import hashlib
import json
from pathlib import Path
import unittest

from test_lamordia_handling import Document, guide_content, guide_text, norm

ROOT = Path(__file__).resolve().parents[1]
SCOPE = json.loads((ROOT/'tools/fixtures/fixed-selection-wording/scope.json').read_text())
BASELINE_SHA = '12ebc937d98181346300150df3f98d275d801db77e227996bf368c464b5552f1'


def restore_fixed_selection_prose(html):
    assert len(SCOPE['reviewed_replacements']) == 7
    for change in SCOPE['reviewed_replacements'][1:]:
        assert html.count(change['after']) == 1, 'exact current-selection correction'
        html = html.replace(change['after'],change['before'])
    return html


def restore_fixed_selection_release(html):
    html = restore_fixed_selection_prose(html)
    stamp = SCOPE['reviewed_replacements'][0]
    assert html.count(stamp['after']) == 1, 'one current build stamp'
    return html.replace(stamp['after'],stamp['before'])


def validate_selection(html):
    assert SCOPE['baseline_commit'] == '1a74f38a204123c9d63532071838979522230ba2'
    assert SCOPE['baseline_index_sha256'] == BASELINE_SHA
    assert hashlib.sha256(restore_fixed_selection_release(html).encode()).hexdigest() == BASELINE_SHA
    nodes = list(guide_content(Document(html).root))
    tables = [n for n in nodes if n.tag == 'table'
              and [norm(t.text()) for t in n.nodes('th')][:3] == ['Slot','Item','ML']]
    assert len(tables) == 1, 'one visible selected kit table'
    text = guide_text(tables[0])
    assert 'solver' not in text.lower(), 'current fixed selections are not empty solver slots'
    for claim in (
        'Nearly Complete: Constitution +16 (selected craft; item-page value, with the generic +15 conflict still unresolved)',
        'Nearly Complete: Dexterity +15 (selected craft; Intelligence Enhancement is already carried by the boots’ craft)',
        'Epic Purifying Quiver', 'selected quiver in BASIC', 'No sockets',
        'weapon-specific interactions remain unverified',
    ):
        assert claim in text,claim
    current_text = guide_text(Document(html).root)
    assert 'Exceptional Intelligence +2 (selected Calamitous craft)' in current_text
    assert 'Use the BASIC kit’s Defense +40 and A Treatise on Battle; either selected filled bow requires level 36' in current_text
    assert 'Earlier optimizer runs are in the Appendix.' in current_text
    assert 'its actual grant and the mixed-type recipe total remain unverified' in html
    assert 'relayed metadata, not retained original solver output or a local rerun' in html


class FixedSelectionWordingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT/'index.html').read_text()

    def test_current_selection_and_exact_published_baseline(self):
        validate_selection(self.html)

    def test_stale_solver_wording_source_overclaims_and_choice_changes_are_rejected(self):
        for old,new in (
            ('selected craft; item-page value, with the generic +15 conflict still unresolved',
             'build decision; the solver leaves it empty'),
            ('selected quiver in BASIC','the solver leaves this slot empty'),
            ('selected craft; Intelligence Enhancement','the solver’s pick; Intelligence Enhancement'),
            ('selected Calamitous craft','the kit’s solve'),
            ('Use the BASIC kit’s Defense +40 and A Treatise on Battle; either selected filled bow requires level 36',
             'Not scored by the optimizer; a build decision by the kit’s gaps'),
            ('Earlier optimizer runs are in the Appendix.',
             'The optimizer runs that produced the kit are in the Appendix.'),
            ('generic +15 conflict still unresolved','generic +15 conflict resolved'),
            ('Nearly Complete: Constitution +16','Nearly Complete: Intelligence +16'),
            ('Epic Purifying Quiver','Epic Quiver of Alacrity'),
            ('Diamond of Spot +22','Diamond of Spot +21'),
            ('relayed metadata, not retained original solver output or a local rerun',
             'newly recovered original solver output'),
            ('<h2 id="class-split">','<h2 id="changed-class-split">'),
        ):
            self.assertIn(old,self.html)
            with self.subTest(old=old),self.assertRaises(AssertionError):
                validate_selection(self.html.replace(old,new))

    def test_prior_published_snapshot_keeps_its_original_wording(self):
        old = (ROOT/'versions/11-09-26.1.html').read_text()
        self.assertIn('build decision; the solver leaves it empty',old)
        self.assertIn('the solver leaves this slot empty because nothing in it moves the ranked stats',old)
        self.assertIn('the solver’s pick',old)
        self.assertIn('the kit’s solve',old)
        self.assertIn('Not scored by the optimizer; a build decision by the kit’s gaps',old)
        self.assertIn('The optimizer runs that produced the kit are in the Appendix.',old)
        self.assertIn('build 11-09-26.1</span>',old)


if __name__ == '__main__':
    unittest.main()
