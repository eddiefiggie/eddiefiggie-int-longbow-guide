"""A-018 literal-source, visible-cost and exact-scope guards; no budget certification."""
import hashlib
import json
from pathlib import Path
import re
import unittest

from test_early_xp import visible_nodes, visible_text
from test_lamordia_handling import Document, norm
from test_public_evidence_privacy import validate_public

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'evidence/class-skill-costs'
SCOPE = json.loads((ROOT / 'tools/fixtures/class-skill-costs/scope.json').read_text())
BASELINE_SHA = 'd760d09f95f6c4248f10159327d5829c6e0dc89ef1f6224143c575ab3aad4b48'
SOURCE_SHA = '40321e74f4fa57542cb41b529284a9ae1c326064f4d26f5dc40fd5cb654b8eac'
SKILL_PAGES = {'Search': 'Search', 'Disable Device': 'Disable_Device',
               'Use Magic Device': 'Use_Magic_Device', 'Tumble': 'Tumble_(skill)',
               'Spot': 'Spot', 'Balance': 'Balance'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def restore_cost_prose(html):
    """Reverse only the 14 exact reviewed price edits, including within build slices."""
    assert len(SCOPE['reviewed_replacements']) == 14
    for change in SCOPE['reviewed_replacements']:
        assert html.count(change['after']) == 1, 'exact A-018 correction required'
        html = html.replace(change['after'], change['before'])
    return html


def restore_cost_release(html):
    html = restore_cost_prose(html)
    assert html.count(SCOPE['after_build']) == 1, 'one current build stamp'
    return html.replace(SCOPE['after_build'], SCOPE['before_build'])


def validate_scope(html):
    from test_queen_basic import restore_queen_release
    html = restore_queen_release(html)
    assert SCOPE['baseline_commit'] == '594090c930222ea688e80ca8aec487fb0746cf45'
    assert SCOPE['baseline_index_sha256'] == BASELINE_SHA
    assert sha(restore_cost_release(html).encode()) == BASELINE_SHA, 'content outside A-018 changed'


def class_names(text):
    return {name.strip() for name in re.split(r',\s*(?:and\s+)?|\s+and\s+', text)}


def source_examples(raw):
    assert sha(raw) == SOURCE_SHA, 'exact transmitted ledger identity'
    text = raw.decode()
    assert ('Multiclass characters purchase ranks using the costs for the class currently being advanced, '
            'but maximum ranks is level + 3 if the skill is a class skill for any trained class.') in text
    section = text.split('## Exact own-skill named class lists\n', 1)[1].split('\n## ', 1)[0]
    examples = {}
    for skill, page in SKILL_PAGES.items():
        match = re.search(r'^- ' + re.escape(page) + r': “(?:Balance is a )?Class Skill (?:only )?for (?:an? )?([^”]+)”$', section, re.M)
        assert match, 'literal own-skill statement: ' + page
        examples[skill] = class_names(match[1].rstrip('.'))
    return examples


def skill_nodes(html):
    nodes = list(visible_nodes(Document(html).root))
    start = [i for i, n in enumerate(nodes) if n.tag == 'h2' and n.attrs.get('id') == 'skills']
    end = [i for i, n in enumerate(nodes) if n.tag == 'h2' and n.attrs.get('id') == 'enhancements-80-ap']
    assert len(start) == len(end) == 1 and start[0] < end[0]
    return nodes[start[0]:end[0]]


def table_rows(table):
    return [[norm(visible_text(c)) for c in visible_nodes(row) if c.tag in {'td', 'th'}]
            for row in visible_nodes(table) if row.tag == 'tr']


def validate_costs(html, examples):
    nodes = skill_nodes(html)
    for ident, clauses in {
        'skill-cost-rule': (
            '1 skill point when the skill is a class skill of the class being advanced, or 2 points when it is cross-class and can be trained',
            'it does not make later levels use Rogue prices',
            'Past-life-class levels use the class being advanced',
        ),
        'skill-cost-examples': (
            'named class-skill examples, not an exhaustive list of classes or archetypes',
            'an unlisted class is not automatically cross-class',
            'unresolved Barbarian Balance and Dark Hunter Spot pricing limits',
            'do not verify the existing total budgets or change the selected ranks and priorities',
        ),
    }.items():
        matches = [n for n in nodes if n.attrs.get('id') == ident]
        assert len(matches) == 1 and matches[0].tag == 'p', 'one visible paragraph: ' + ident
        for clause in clauses:
            assert clause in norm(visible_text(matches[0])), clause
    links = {n.attrs.get('href') for n in nodes if n.tag == 'a'}
    assert {'https://ddowiki.com/page/Skill_point', 'https://ddowiki.com/page/Class_skill',
            'evidence/class-skill-costs/README.md'} <= links
    tables = [table_rows(n) for n in nodes if n.tag == 'table']
    assert len(tables) == 2
    assert tables[0][0][0:2] == ['Skill', 'Target'] and tables[0][0][3] == 'Cost'
    rows = {r[0]: r for r in tables[0][1:]}
    assert len(rows) == 9
    for skill, classes in examples.items():
        cost = rows[skill][3]
        match = re.match(r'1 per rank on (.+?) levels; 2 when cross-class', cost)
        assert match and class_names(match[1]) == classes, 'source-bound positive examples: ' + skill
    for skill in ('Disable Device', 'Open Lock'):
        assert 'cross-class and trainable' in rows[skill][3]
    for skill, classes in {'Jump': ('Ranger', 'Rogue', 'Bard', 'Monk', 'Warlock'),
                           'Listen': ('Ranger', 'Bard', 'Monk', 'Rogue')}.items():
        cost = rows[skill][3]
        assert cost.startswith('1 per rank on Ranger levels and other classes that have it, including ')
        assert cost.endswith('; 2 when cross-class')
        assert all(name in cost for name in classes)
    assert rows['Open Lock'][3] == '1 per rank on Rogue levels; other classes use their own price (2 when cross-class and trainable)'
    assert 'stopping here is the build’s priority choice even when a later class also buys it at 1 per rank' in rows['Listen'][2]
    paragraphs = ' '.join(norm(visible_text(n)) for n in nodes if n.tag == 'p')
    assert ('Bluff is a pulling tool, costing 1 point per rank when it is a class skill of the class being advanced, '
            'or 2 when cross-class.') in paragraphs
    life = tables[1]
    assert life[0] == ['Life', 'Level 1', 'Levels 2-10', 'Levels 11-20'] and len(life) == 5
    assert '1 per rank for its class skills, 2 for trainable cross-class skills' in life[1][3]
    assert life[2][3].startswith('On Rogue levels, all skills listed in the first table cost 1 per rank:')
    assert 'are the selected 1-point examples here, not the full Ranger class-skill list;' in life[3][1]
    # Deliberate scope boundary, not validation of these existing A-035 claims.
    assert 'Disable Device, UMD and Tumble cost 2 and have no maximum yet' in life[3][1]
    assert 'raises every Rogue skill’s maximum to 5 for good' in life[3][2]
    text = ' '.join(norm(visible_text(n)) for n in nodes if n.tag in {'p', 'table'})
    for obsolete in ('about 42 points', '10 ranks is 16 points', 'about 10 points over a life',
                     'most past-life classes', 'all other classes pay 2', 'only 1-point buys',
                     'not worth 2 per rank later', 'Eleven Rogue levels make everything'):
        assert obsolete not in text, obsolete


class ClassSkillCostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / 'index.html').read_text()
        cls.raw = (EVIDENCE / 'source-ledger.md').read_bytes()
        cls.examples = source_examples(cls.raw)

    def reject(self, old, new, validator=None):
        self.assertTrue(old in self.html, 'mutation must affect actual Guide: ' + old)
        if validator is None:
            validator = lambda html: validate_costs(html, self.examples)
        with self.assertRaises(AssertionError):
            validator(self.html.replace(old, new))

    def test_actual_costs_match_literal_positive_source_examples(self):
        validate_costs(self.html, self.examples)
        validate_scope(self.html)

    def test_prices_membership_fallthrough_and_repeated_claim_mutations(self):
        for old, new in (
            ('1 skill point when the skill', '2 skill points when the skill'),
            ('class being advanced, or 2 points', 'first class taken, or 2 points'),
            ('it does not make later levels use Rogue prices', 'it makes later levels use Rogue prices'),
            ('not an exhaustive list of classes or archetypes', 'an exhaustive list of classes and archetypes'),
            ('an unlisted class is not automatically cross-class', 'all other classes pay 2'),
            ('Artificer, Bard, Rogue, Warlock and Alchemist levels', 'Artificer, Rogue and Alchemist levels'),
            ('Ranger, Dark Hunter, Alchemist, Rogue and Artificer levels', 'Ranger, Rogue and Artificer levels'),
            ('Artificer, Dark Hunter and Rogue levels', 'Ranger, Dark Hunter and Rogue levels'),
            ('Bard, Monk and Rogue levels; 2 when cross-class', 'Rogue levels; 2 when cross-class'),
            ('Alchemist, Artificer, Druid, Monk, Ranger and Rogue levels', 'Alchemist, Artificer, Druid, Monk, Ranger, Rogue and Dark Hunter levels'),
            ('Alchemist, Bard, Monk and Rogue levels', 'Barbarian, Alchemist, Bard, Monk and Rogue levels'),
            ('cross-class and trainable', 'cross-class'),
            ('1 per rank for its class skills, 2 for trainable cross-class skills', '2 per rank after level 1'),
            ('On Rogue levels, all skills listed in the first table cost 1 per rank:', 'Eleven Rogue levels make everything 1 a rank:'),
            ('are the selected 1-point examples here, not the full Ranger class-skill list;', 'are the only 1-point buys;'),
            ('Bluff is a pulling tool, costing 1 point per rank', 'Bluff is a pulling tool, costing 2 points per rank'),
            ('stopping here is the build’s priority choice', 'buying it on every later level is required'),
        ):
            with self.subTest(old=old):
                self.reject(old, new)

    def test_hidden_inert_commented_or_missing_guidance_rejected(self):
        for ident in ('skill-cost-rule', 'skill-cost-examples'):
            for attr in ('hidden', 'inert', 'aria-hidden="true"', 'style="display:none"'):
                self.reject(f'<p id="{ident}"', f'<p {attr} id="{ident}"')
        self.reject('Artificer, Bard, Rogue, Warlock and Alchemist levels', '<template>Artificer, Bard, Rogue, Warlock and Alchemist levels</template>')
        self.reject('1 per rank on Bard, Monk and Rogue levels', '<!--1 per rank on Bard, Monk and Rogue levels-->')

    def test_scope_rejects_target_budget_a035_and_unrelated_changes(self):
        for old, new in (
            ('<td>Maximum (23)</td>', '<td>Maximum (22)</td>'),
            ('4-5 ranks', '10 ranks'),
            ('A Fighter life has about 266 points', 'A Fighter life has 300 verified points'),
            ('have no maximum yet', 'have a maximum of 2'),
            ('maximum to 5 for good', 'maximum to character level + 3'),
            ('<td>Elemental Arrows (Flaming), Awareness 3</td>', '<td>Awareness 2</td>'),
            ('<td>Legendary Abyssal Compass</td>', '<td>Different gear</td>'),
            ('recommended for lawful lives', 'optional for lawful lives'),
            ('alternate for neutral or chaotic lives', 'alternate for chaotic lives only'),
            ('for <strong>7 AP total</strong>', 'for <strong>6 AP total</strong>'),
            ('</script>', 'throw new Error("mutation");</script>'),
        ):
            with self.subTest(old=old):
                self.reject(old, new, validate_scope)

    def test_transmitted_source_identity_and_provenance_limits(self):
        receipt = json.loads((EVIDENCE / 'receipt.json').read_text())
        self.assertEqual(len(self.raw), 12204)
        self.assertEqual(sha(self.raw), receipt['local_ledger_sha256'])
        self.assertEqual(sha(self.raw + b'\n'), '5d119d732c93a730ffd30f8ccebdbeb72bb579f083c6a7b9be43b96d50b86bf0')
        self.assertEqual(sha(self.raw + b'\n'), receipt['reported_original_ledger_sha256'])
        self.assertTrue(receipt['original_ledger_byte_identity_verified'])
        for key in ('raw_packet_materialized_or_read', 'historical_revisions_opened', 'live_game_test',
                    'a035_training_and_maximum_corrections_included', 'complete_skill_budget_certified'):
            self.assertFalse(receipt[key])
        for exact in ('2026-11-08T22:54:23.304Z | 578481', '2026-11-08T22:55:16.558Z | 532220',
                      '2026-11-08T22:57:38.895Z | 674270 | -2 hours old',
                      'No Dark Hunter Spot price is certified here.', 'No base-class/archetype equivalence inferred.',
                      'the own Balance page names only Alchemist/Bard/Monk/Rogue'):
            self.assertIn(exact, self.raw.decode())
        validate_public(receipt)
        validate_public(self.raw.decode())
        for old, new in ((b'532220', b'532221'), (b'Warlock and Alchemist', b'Fighter and Alchemist'),
                         (b'not an all-archetype matrix', b'an all-archetype matrix')):
            with self.subTest(old=old), self.assertRaises(AssertionError):
                source_examples(self.raw.replace(old, new))

    def test_all_published_snapshots_remain_byte_identical(self):
        for filename, digest in SCOPE['historical_snapshots'].items():
            with self.subTest(filename=filename):
                self.assertEqual(sha((ROOT / filename).read_bytes()), digest)


if __name__ == '__main__':
    unittest.main()
