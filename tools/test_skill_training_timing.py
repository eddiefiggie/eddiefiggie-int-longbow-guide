"""A-035: ledger-bound eligibility/heroic ceilings, not raw-source or budget certification."""
import hashlib
import json
from pathlib import Path
import re
import unittest

from test_early_xp import visible_nodes, visible_text
from test_lamordia_handling import Document, norm

ROOT = Path(__file__).resolve().parents[1]
SCOPE = json.loads((ROOT/'tools/fixtures/skill-training-timing/scope.json').read_text())
BASELINE_SHA = 'f43875e9e5ee694cf896314c385192611a018a96333004c767b7cf69b84328b9'
LEDGER_SHA = '40321e74f4fa57542cb41b529284a9ae1c326064f4d26f5dc40fd5cb654b8eac'


def restore_training_prose(html):
    from test_spot_diamond_type import restore_spot_prose
    html = restore_spot_prose(html)
    assert len(SCOPE['reviewed_replacements']) == 5
    for change in reversed(SCOPE['reviewed_replacements'][1:]):
        assert html.count(change['after']) == 1, 'exact A-035 training correction'
        html = html.replace(change['after'],change['before'])
    return html


def restore_training_release(html):
    from test_spot_diamond_type import restore_spot_stamp
    html = restore_spot_stamp(html)
    html = restore_training_prose(html)
    stamp = SCOPE['reviewed_replacements'][0]
    assert html.count(stamp['after']) == 1, 'one current build stamp'
    return html.replace(stamp['after'],stamp['before'])


def validate_ledger(raw):
    assert len(raw) == 12204 and hashlib.sha256(raw).hexdigest() == LEDGER_SHA
    text = raw.decode()
    for claim in (
        'Both Disable_Device and Open_Lock say:',
        "you can only train this skill if it's a class skill for at least one of your classes.",
        'Cross-class maximum at level 1 is 2 ranks under the literal (3 + character level) / 2 rule',
        'maximum ranks is level + 3 if the skill is a class skill for any trained class.',
        'Note that the cost of a rank at each level still depends on whether the skill is class or cross-class for that level-up.',
        'All skill points must be spent during level up. You cannot save them.',
    ):
        assert claim in text,claim
    ranger = re.search(r'^- Ranger: (.+)$',text,re.M)[1]
    rogue = re.search(r'^- Rogue: (.+)$',text,re.M)[1]
    for skill in ('Disable Device','Open Lock','Use Magic Device','Tumble'):
        assert skill not in ranger and skill in rogue,skill
    assert 'No base-class/archetype equivalence inferred.' in text


def validate_training(html):
    validate_ledger((ROOT/'evidence/class-skill-costs/source-ledger.md').read_bytes())
    assert SCOPE['baseline_commit'] == 'cc1fafc0a6fb2ee0a9be215aa61984760871cbe9'
    assert SCOPE['baseline_index_sha256'] == BASELINE_SHA
    assert hashlib.sha256(restore_training_release(html).encode()).hexdigest() == BASELINE_SHA
    nodes = list(visible_nodes(Document(html).root))
    def paragraph(ident):
        found = [n for n in nodes if n.attrs.get('id') == ident]
        assert len(found) == 1 and found[0].tag == 'p'
        return norm(visible_text(found[0]))
    rule = paragraph('skill-training-rule')
    for clause in (
        'Training eligibility, maximum ranks and price are separate.',
        'at least one class already taken has that skill as a class skill',
        'Ordinary Ranger 1 cannot train either',
        'paying a cross-class price does not make it eligible',
        'UMD and Tumble can be trained cross-class',
        'During heroic training (levels 1–20)',
        'maximum of (3 + character level) / 2 ranks',
        'raises the maximum to character level + 3',
        'maximum of 4 ranks',
        'On Scourge, Rogue 1 is taken at character level 2:',
        'ceiling is 5 then, 6 at level 3 and 23 at level 20',
        'These are ceilings, not purchased ranks',
        'each purchase still uses the class being advanced',
        'does not let a later Rogue level supply eligibility at the earlier Ranger-1 training step',
    ):
        assert clause in rule,clause
    partial = paragraph('skill-allocation-limits')
    for clause in ('not a complete skill-point budget','All skill points must be spent during each level-up',
                   'cannot be saved for a later level','No new allocation of the remaining points'):
        assert clause in partial
    rows = [[norm(visible_text(c)) for c in visible_nodes(n) if c.tag=='td']
            for n in nodes if n.tag=='tr']
    scourge = [r for r in rows if r and r[0].startswith('Aasimar Scourge life')]
    assert len(scourge) == 1
    assert 'Disable Device and Open Lock cannot be trained at this step' in scourge[0][1]
    assert 'UMD and Tumble cost 2 points per rank and have a maximum of 2 ranks each at character level 1' in scourge[0][1]
    assert scourge[0][2].startswith('Rogue 1 at character level 2:')
    assert 'a maximum of 5 ranks at character level 2 and character level + 3 thereafter' in scourge[0][2]
    assert 'a price of 1 point per rank while advancing Rogue' in scourge[0][2]
    iconic = [r for r in rows if r and r[0].startswith('Other iconic lives')]
    assert len(iconic) == 1
    assert 'forced class’s points, training eligibility, rank ceilings and prices' in iconic[0][1]
    assert 'Shadar-kai starts as Rogue' in iconic[0][1]
    assert 'Skills already eligible at level 1 remain eligible' in iconic[0][2]
    text = ' '.join(norm(visible_text(n)) for n in nodes if n.tag in ('p','td'))
    assert 'no maximum yet' not in text and 'maximum to 5 for good' not in text


class SkillTrainingTimingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT/'index.html').read_text()

    def test_current_steps_and_exact_prior_release_preserved(self):
        validate_training(self.html)

    def test_ineligible_early_training_caps_prices_visibility_and_budget_overclaims_rejected(self):
        for old,new in (
            ('Ordinary Ranger 1 cannot train either','Ordinary Ranger 1 can train either for 2 points'),
            ('Rogue 1 at character level 2:','Rogue level 2:'),
            ('On Scourge, Rogue 1 is taken at character level 2:','On Scourge, Rogue level 2 is needed:'),
            ('maximum of 2 ranks each at character level 1','no maximum yet'),
            ('a maximum of 5 ranks at character level 2 and character level + 3 thereafter','a maximum of 5 for good'),
            ('a price of 1 point per rank while advancing Rogue','a permanent price of 1 point per rank'),
            ('UMD and Tumble can be trained cross-class','UMD and Tumble require Rogue before training'),
            ('During heroic training (levels 1–20)','At all levels through 36'),
            ('not a complete skill-point budget','a complete certified skill-point budget'),
            ('cannot be saved for a later level','can be saved for Rogue at level 2'),
            ('Shadar-kai starts as Rogue','Shadar-kai starts as Ranger'),
            ('<p id="skill-training-rule"','<p hidden id="skill-training-rule"'),
            ('<p id="skill-allocation-limits"','<p inert id="skill-allocation-limits"'),
            ('<td>Maximum (23)</td>','<td>Maximum (22)</td>'),
            ('<td>Legendary Abyssal Compass</td>','<td>Different gear</td>'),
        ):
            self.assertIn(old,self.html)
            with self.subTest(old=old),self.assertRaises(AssertionError):
                validate_training(self.html.replace(old,new))

    def test_exact_ledger_and_manifest_do_not_become_original_raw_capture(self):
        raw = (ROOT/'evidence/class-skill-costs/source-ledger.md').read_bytes()
        validate_ledger(raw)
        with self.assertRaises(AssertionError):validate_ledger(raw.replace(b'only train',b'always train'))
        receipt = json.loads((ROOT/'evidence/class-skill-costs/receipt.json').read_text())
        self.assertFalse(receipt['raw_packet_materialized_or_read'])
        self.assertFalse(receipt['a035_training_and_maximum_corrections_included'])
        doc = (ROOT/'evidence/skill-training-timing/README.md').read_text()
        for phrase in ('not** the original browser packet','has not been recovered\nor read here',
                       'reported metadata, not local raw-file verification',
                       'a ledger statement, not a locally inspected raw-page quotation',
                       'does not\nextend purchased-rank formulas into epic or legendary levels'):
            self.assertIn(phrase,doc)


if __name__ == '__main__':
    unittest.main()
