"""Bow-only release scope and reader safeguards; not live-game certification."""
import hashlib
import json
from pathlib import Path
import re
import unittest

from test_lamordia_handling import Document, guide_content, guide_text

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / 'tools/fixtures/endgame-bow-options/scope.json').read_text())
NOTE_ID = 'endgame-bow-choice'
LINK = '#' + NOTE_ID
SINEW = "https://ddowiki.com/page/Item:Legendary_Demogorgon's_Sinew"


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def visible_note(html):
    nodes = list(guide_content(Document(html).root))
    notes = [n for n in nodes if n.attrs.get('id') == NOTE_ID]
    assert len(notes) == 1 and notes[0].tag == 'section', 'one visible bow-choice section'
    note = notes[0]
    assert note.attrs.get('aria-labelledby') == 'endgame-bow-choice-title'
    assert any(n.tag == 'h4' and n.attrs.get('id') == 'endgame-bow-choice-title'
               for n in guide_content(note)), 'visible heading'
    return note


def validate_choice(html):
    note = visible_note(html)
    text = guide_text(note)
    for claim in (
        'Calamitous (base ML34): recommended for lawful lives, including Paladin.',
        'Paladins require Lawful Good alignment',
        'a negative level on lawful wielders',
        'penalty, not a prohibition',
        'do not assume two negative levels',
        'Legendary Demogorgon’s Sinew (base ML35): an alternate for neutral or chaotic lives.',
        '6[1d8+3]+16, 20/x3, with Anarchic 7, Anarchic Burst 7, Paralyzing 117 and Elasticity',
        'Melancholic Flames (16d6 fire and Adamantine)',
        'Dolorous Flames (Good bypass and a fire proc)',
        'Miserable Dimlight (Exceptional INT +2) and Woeful Salt',
        'Sinew has no Lamordia weapon slots',
        'lost bow-supplied effects; other build sources of bypass remain unchanged',
        'Globe of True Imperial Blood supplies Exceptional +1 instead',
        'a derived net loss of 1 INT',
        'not a claim about the INT modifier, Know the Angles or DPS',
        'Elasticity adds +1 critical multiplier on confirmed natural 19/20 criticals',
        'does not widen threat range',
        'Paralyzing 117 allows a Will save and has immunities',
        'no helpless-damage benefit is assumed',
        'Anarchic excludes chaos-aligned creatures; Anarchic Burst lists damage against lawful enemies',
        'different target conditions; their joint damage is not established here',
        'Neither bow is a universal damage winner',
        'both bows have Purple and Orange sockets',
        'Purple: Sapphire of Defense +40 (Blue augment, ML36)',
        'Orange: A Treatise on Battle (ML32; Combat Mastery +11 and Fear Immunity)',
        'allow Blue in Purple',
        'raise the host’s minimum level to the highest slotted augment’s level',
        'filled bow ML36',
        'extract it with a Jeweler’s Tool Kit before re-slotting; overwriting destroys it',
        'not an automatic or free transfer',
        'does not transfer weapon crafts, sentient gems, XP or filigrees',
        'Calamitous remains the reference loadout for its existing audit',
        'historical model and stacking audit have not been recalculated for Sinew',
    ):
        assert claim in text, claim
    for prohibited in ('Heart Shard', 'Bloody Boulder', 'Piwafwi', 'Burrower',
                       'Demon’s Arc', 'chaotic only', 'guaranteed paralysis',
                       'helpless DPS', 'illegal', 'unusable'):
        assert prohibited.lower() not in text.lower(), prohibited
    links = {n.attrs.get('href') for n in guide_content(note) if n.tag == 'a'}
    assert {SINEW, 'https://ddowiki.com/page/Item:Legendary_Calamitous_Longbow',
            'https://ddowiki.com/page/Paladin',
            'https://ddowiki.com/page/Viktranium_Experiment_crafting',
            'https://ddowiki.com/page/Augment_Slot',
            'evidence/endgame-bow-options/README.md'} <= links
    start = html.index('<h3 id="endgame-kit-ml35-36">')
    table = re.search(r'<table>.*?</table>', html[start:], re.S)[0]
    assert digest(table) == CONTRACT['baseline_endgame_table_sha256'], 'all 14 kit rows and fills unchanged'


def validate_scope(html):
    """Reverse only the reviewed bow prose; every remaining byte equals main."""
    validate_choice(html)
    for pattern in (r'<section id="endgame-bow-choice".*?</section>\n',
                    r'<p id="bow-ladder-endgame-choice">.*?</p>\n'):
        html, count = re.subn(pattern, '', html, flags=re.S)
        assert count == 1, 'one authorized addition'
    for change in CONTRACT['reviewed_replacements']:
        assert html.count(change['after']) == 1, 'exact reviewed bow prose/stamp'
        html = html.replace(change['after'], change['before'])
    assert digest(html) == CONTRACT['baseline_index_sha256'], 'content outside bow scope changed'


class EndgameBowOptionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / 'index.html').read_text()

    def test_both_options_conditions_and_socket_handling(self):
        validate_choice(self.html)

    def test_all_non_bow_content_and_complete_original_kit_preserved(self):
        validate_scope(self.html)

    def test_repeated_progression_advice_routes_to_current_choice(self):
        nodes = list(guide_content(Document(self.html).root))
        links = [n for n in nodes if n.tag == 'a' and n.attrs.get('href') == LINK]
        self.assertEqual(len(links), 5)
        for section in ('the-build-in-one-page', 'gear-milestones', 'bow-ladder-levels-1-36',
                        'bow-damage-model', 'crafted-endgame-bow'):
            block = self.html.split(f'id="{section}"', 1)[1]
            block = re.split(r'<h[23] ', block, maxsplit=1)[0]
            self.assertIn(f'href="{LINK}"', block, section)

    def test_claim_and_visibility_negative_controls(self):
        for before, after in (
            ('recommended for lawful lives', 'unusable on lawful lives'),
            ('Paladins require Lawful Good', 'Paladins allow any'),
            ('alternate for neutral or chaotic lives', 'alternate for chaotic lives only'),
            ('a negative level on lawful wielders', 'two negative levels on lawful wielders'),
            ('net loss of 1 INT', 'net loss of 2 INT'),
            ('confirmed natural 19/20 criticals', 'all natural 19/20 rolls'),
            ('allows a Will save and has immunities', 'guarantees helpless DPS'),
            ('Purple: Sapphire of Defense +40', 'Purple: Heart Shard'),
            ('Blue augment, ML36', 'Blue augment, ML35'),
            ('filled bow ML36', 'filled bow ML35'),
            ('extract it with a Jeweler’s Tool Kit', 'transfer it for free'),
            ('https://ddowiki.com/page/Paladin', 'https://ddowiki.com/page/Ranger'),
            ('<section id="endgame-bow-choice"', '<section hidden id="endgame-bow-choice"'),
        ):
            with self.subTest(before=before):
                self.assertIn(before, self.html)
                with self.assertRaises(AssertionError):
                    validate_choice(self.html.replace(before, after))
        block = re.search(r'<section id="endgame-bow-choice".*?</section>', self.html, re.S)[0]
        for replacement in ('', '<!--' + block + '-->', '<template>' + block + '</template>', block + block):
            with self.assertRaises(AssertionError):
                validate_choice(self.html.replace(block, replacement))

    def test_transmitted_source_ledger_and_explicit_provenance_limits(self):
        directory = ROOT / 'evidence/endgame-bow-options'
        source = (directory / 'source-ledger.md').read_text()
        self.assertEqual(digest(source), '98df0bd8dc0a73a242eda20b88bc96e459d81d13dee501283d573b86c3da2ecd')
        self.assertEqual(len(re.findall(r'^## \d+\.', source, re.M)), 14)
        self.assertEqual(len(re.findall(r'^Captured 2026-11-08T', source, re.M)), 14)
        for quote in ('Alignment: Lawful Good', 'Minimum Level36',
                      'Blue, Green, or Purple Augment Slot',
                      'unslot an augment and claim the old augment back',
                      'not with other exceptional bonuses',
                      'does not render a creature helpless',
                      'This exact item does not quantify proc rate or damage'):
            self.assertIn(quote, source)
        receipt = json.loads((directory / 'receipt.json').read_text())
        self.assertEqual(receipt['local_ledger_sha256'], digest(source))
        self.assertFalse(receipt['raw_packet_materialized_or_read'])
        self.assertTrue(receipt['original_ledger_byte_identity_verified'])
        self.assertEqual(digest(source + '\n\n'), receipt['reported_original_ledger_sha256'])

    def test_scope_rejects_gear_craft_augment_and_chassis_changes(self):
        for before, after in (
            ('<td>Legendary Abyssal Compass</td>', '<td>Legendary The Bloody Boulder</td>'),
            ('<td>Cloak of Summer’s End (level 36)</td>', '<td>Legendary Piwafwi</td>'),
            ('<td>Legendary Burrowing Claws</td>', '<td>Legendary Burrower</td>'),
            ('Quality Constitution +3, Quality Seeker +3', 'Quality Deadly +3, Quality Seeker +3'),
            ('Sapphire of Resistance +12 (all saves)', 'Sapphire of Resistance +13 (all saves)'),
            ('Miserable: Legendary Miserable Dimlight (Weapon), Exceptional Intelligence +2.', 'Miserable: none.'),
            ('<h2 id="class-split">', '<h2 id="changed-class-split">'),
            ('<strong>Calamitous Longbow</strong>, crafted (100)', '<strong>Calamitous Longbow</strong>, crafted (99)'),
        ):
            with self.subTest(before=before):
                self.assertIn(before, self.html)
                with self.assertRaises(AssertionError):
                    validate_scope(self.html.replace(before, after))


if __name__ == '__main__':
    unittest.main()
