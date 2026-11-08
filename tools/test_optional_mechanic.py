"""A-016 source/visible guidance/scope checks; not live-game certification."""
import hashlib
import json
from pathlib import Path
import re
import unittest

from test_early_xp import visible_nodes, visible_text
from test_lamordia_handling import Document, norm

ROOT = Path(__file__).resolve().parents[1]
SCOPE = json.loads((ROOT / 'tools/fixtures/optional-mechanic/scope.json').read_text())
EVIDENCE = ROOT / 'evidence/optional-mechanic'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def restore_mechanic_prose(html):
    """Allow exactly A-016 before applying existing build/bow preservation hashes."""
    assert html.count(SCOPE['after']) == 1, 'exact A-016 correction required'
    return html.replace(SCOPE['after'], SCOPE['before'])


def restore_mechanic_release(html):
    html = restore_mechanic_prose(html)
    assert html.count(SCOPE['after_build']) == 1, 'one current build stamp'
    return html.replace(SCOPE['after_build'], SCOPE['before_build'])


def validate_scope(html):
    assert sha(restore_mechanic_release(html).encode()) == SCOPE['baseline_index_sha256'], \
        'content outside A-016 changed'


def validate_note(html):
    nodes = list(visible_nodes(Document(html).root))
    expected = {
        'optional-mechanic-funding': (
            'AP actually available or reallocated at the time of each purchase',
            'preserving all affected prerequisites and gates',
            'at level 4 or 5 therefore requires a contemporaneous reallocation of already-earned AP',
            'Omitting future purchases at levels 17 or 20 does not supply earlier AP',
            'a later reset only returns points at that later time',
            'schedule remains unchanged',
            'does not establish an alternate level-by-level allocation',
        ),
        'optional-mechanic-extension': (
            'only on a life already at Rogue level 2 or higher',
            'After the 4-AP package, buy tier-1 Awareness rank 1 for 1 AP',
            'printed bonus is +1 Listen, Search and Spot',
            'bringing Mechanic to 5 AP spent. Then buy the single rank of tier-2 Skill Boost for 2 AP',
            'activate it to gain a separate +6 Action Boost bonus to all skills for 20 seconds',
            '30-second cooldown',
            'for 7 AP total',
            'Rogue level 2 and 5 AP already spent in Mechanic before purchasing Skill Boost',
            'A character still at Rogue level 1 cannot buy this extension merely by spending more AP',
            'The selected class split is unchanged',
        ),
        'optional-mechanic-awareness': (
            'Only the highest Awareness bonus from the different trees applies',
            'Mechanic Awareness rank 1 does not add to a higher Awareness already owned',
            'does not improve those skills while the selected Arcane Archer Awareness 3 is trained',
            'Skill Boost is the separate active effect',
        ),
    }
    for ident, clauses in expected.items():
        matches = [n for n in nodes if n.attrs.get('id') == ident]
        assert len(matches) == 1 and matches[0].tag == 'p', 'one visible paragraph: ' + ident
        text = norm(visible_text(matches[0]))
        for clause in clauses:
            assert clause in text, clause
    headings = [n.attrs.get('id') for n in nodes if n.tag == 'h3']
    assert headings.count('optional-mechanic') == 1
    section = html.split('<h3 id="optional-mechanic">', 1)[1].split('<h3 ', 1)[0]
    assert all(f'id="{ident}"' in section for ident in expected), 'notes stay with optional package'
    text = norm(visible_text(Document(section).root))
    assert ('Buy Arbalester (core 1) for 1 AP first, then Mechanics ranks 1–3 for 1 AP each: '
            '4 AP total, available from Rogue level 1 when funded') in text
    assert '+3 Search' not in text
    links = {n.attrs.get('href') for n in visible_nodes(Document(section).root) if n.tag == 'a'}
    assert {'https://ddowiki.com/page/Mechanic_enhancements',
            'https://ddowiki.com/page/Enhancements',
            'evidence/optional-mechanic/README.md', '#action-points-by-level'} <= links


class OptionalMechanicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / 'index.html').read_text()

    def reject(self, before, after, validator=validate_note):
        self.assertTrue(before in self.html, 'mutation must affect actual Guide: ' + before)
        with self.assertRaises(AssertionError):
            validator(self.html.replace(before, after))

    def test_actual_note_distinguishes_packages_and_current_gates(self):
        validate_note(self.html)

    def test_rank_cost_bonus_order_and_class_gate_mutations(self):
        for before, after in (
            ('already at Rogue level 2 or higher', 'already at Rogue level 1 or higher'),
            ('Awareness rank 1</strong> for <strong>1 AP', 'Awareness rank 1</strong> for <strong>3 AP'),
            ('+1 Listen, Search and Spot', '+3 Listen, Search and Spot'),
            ('5 AP spent</strong>. Then buy', '4 AP spent</strong>. Then buy'),
            ('single rank of tier-2', 'three ranks of tier-2'),
            ('Skill Boost</strong> for <strong>2 AP', 'Skill Boost</strong> for <strong>1 AP'),
            ('+6 Action Boost bonus', '+3 Action Boost bonus'),
            ('to all skills for 20 seconds', 'to all skills for 30 seconds'),
            ('30-second cooldown', '20-second cooldown'),
            ('and 5 AP already spent', 'or 5 AP already spent'),
            ('before purchasing Skill Boost', 'after purchasing Skill Boost'),
            ('cannot buy this extension', 'can buy this extension'),
        ):
            with self.subTest(before=before):
                self.reject(before, after)

    def test_contemporaneous_funding_and_overlap_mutations(self):
        for before, after in (
            ('at the time of each purchase', 'at level 20'),
            ('while preserving all affected prerequisites and gates', ''),
            ('requires a contemporaneous reallocation of already-earned AP', 'is funded by later refunds'),
            ('does not supply earlier AP', 'supplies earlier AP'),
            ('a later reset only returns points at that later time', 'a later reset funds earlier purchases'),
            ('does not establish an alternate level-by-level allocation', 'establishes a tested alternate allocation'),
            ('Only the highest Awareness bonus', 'The sum of every Awareness bonus'),
            ('does not add to a higher Awareness already owned', 'adds +1 Search to Awareness 3'),
        ):
            with self.subTest(before=before):
                self.reject(before, after)

    def test_hidden_or_inert_correction_cannot_satisfy_guidance(self):
        for ident in ('funding', 'extension', 'awareness'):
            for attribute in ('hidden', 'inert', 'aria-hidden="true"', 'style="display:none"'):
                self.reject(f'<p id="optional-mechanic-{ident}"',
                            f'<p {attribute} id="optional-mechanic-{ident}"')
        self.reject('5 AP already spent', '<template>5 AP already spent</template>')

    def test_four_ap_table_and_other_arcane_archer_awareness_preserved(self):
        section = self.html.split('<h3 id="optional-mechanic">', 1)[1].split('<h3 ', 1)[0]
        self.assertIn('<td>Arbalester (core 1)</td><td>1</td>', section)
        self.assertIn('<td>Mechanics 3 (tier 1)</td><td>3</td>', section)
        self.assertIn('+[1/2/3] Disable Device, Open Lock, and Repair', section)
        self.assertIn('+[1/2/3] to Saving Throws you make against traps', section)
        self.assertIn('Awareness: +3 Listen, Search, Spot and to-hit', self.html)
        self.assertIn('<td>Elemental Arrows (Flaming), Awareness 3</td><td>5</td>', self.html)
        validate_scope(self.html)

    def test_complete_pr38_index_reconstructed_by_exact_scope(self):
        self.assertEqual(SCOPE['baseline_commit'], '2512c0081c047f5a6c50fba23ca3aae3c0f451d4')
        validate_scope(self.html)

    def test_scope_rejects_other_build_gear_bow_model_or_script_changes(self):
        for before, after in (
            ('<td>Elemental Arrows (Flaming), Awareness 3</td>', '<td>Awareness 2</td>'),
            ('<td>Legendary Abyssal Compass</td>', '<td>Different gear</td>'),
            ('recommended for lawful lives', 'optional for lawful lives'),
            ('alternate for neutral or chaotic lives', 'alternate for chaotic lives only'),
            ('<h2 id="class-split">', '<h2 id="different-class-split">'),
            ('<h3 id="action-points-by-level">', '<h3 id="changed-ap-schedule">'),
            ('<strong>Calamitous Longbow</strong>, crafted (100)', '<strong>Calamitous Longbow</strong>, crafted (99)'),
            ('</script>', 'throw new Error("mutation");</script>'),
        ):
            with self.subTest(before=before):
                self.reject(before, after, validate_scope)

    def test_transmitted_source_identity_metadata_and_explicit_limits(self):
        raw = (EVIDENCE / 'source-ledger.md').read_bytes()
        receipt = json.loads((EVIDENCE / 'receipt.json').read_text())
        self.assertEqual(len(raw), 5129)
        self.assertEqual(sha(raw), 'b56ec211719b8940159ed7fc48e77564f2ee6f02af670c77b15e42e05d38bdd0')
        self.assertEqual(sha(raw), receipt['local_ledger_sha256'])
        self.assertEqual(sha(raw + b'\n'), receipt['reported_original_ledger_sha256'])
        self.assertTrue(receipt['original_ledger_byte_identity_verified'])
        self.assertFalse(receipt['raw_packet_materialized_or_read'])
        self.assertFalse(receipt['historical_revisions_opened'])
        self.assertFalse(receipt['live_game_test'])
        text = raw.decode()
        for exact in ('2026-11-08T19:35:21.705Z', '2026-11-08T19:36:21.571Z',
                      'Displayed oldid: 721681', 'Displayed oldid: 704870',
                      'Requires Rogue Level 2, 5 APs spent in tree',
                      'AP Cost: 2”; “Ranks: 1”; “Progression: 5',
                      '+[1/2/3] Listen, Search, and Spot',
                      'only the highest Awareness bonus applies',
                      'meet the progression requirements and any prerequisites, before',
                      'No revalidation of particular main-tree refund choices or new early-AP schedule'):
            self.assertIn(exact, text)
        supplement = (EVIDENCE / 'arcane-archer-supplement.md').read_bytes()
        metadata = receipt['arcane_archer_supplement']
        self.assertEqual(len(supplement), 1386)
        self.assertEqual(sha(supplement), 'c4155aa15b2ab85fc14deccf90879d7fc034ecff2f0fd6c3ed56d090645a618f')
        self.assertEqual(sha(supplement), metadata['local_ledger_sha256'])
        self.assertEqual(sha(supplement + b'\n'), metadata['reported_original_ledger_sha256'])
        self.assertTrue(metadata['original_ledger_byte_identity_verified'])
        self.assertFalse(metadata['raw_packet_materialized_or_read'])
        for exact in ('2026-11-08T19:42:48.072Z', 'oldid: 722900',
                      'Awareness: +[1/2/3] Listen, Search, Spot, and to-hit.',
                      'AP Cost: 1”; “Ranks: 3”; “Progression: 1',
                      'not its mechanics; this fresh AA source supplies the missing mechanics evidence'):
            self.assertIn(exact, supplement.decode())


if __name__ == '__main__':
    unittest.main()
