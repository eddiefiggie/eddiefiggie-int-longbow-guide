"""Positive, bounded claims from the separately preserved browser supplement."""
import copy
import hashlib
import json
import unittest
from pathlib import Path
from test_lamordia_handling import Document, norm
from test_endgame_evidence import validate_kit, validate_claims

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / 'tools/fixtures/endgame-evidence'
PINS = {
    'wikiEarthSky': ('Ring 2', 'Item:Legendary_The_Earth_and_the_Sky', 633073),
    'wikiCord': ('Belt', 'Item:The_Unbreakable_Cord', 702822),
    'wikiQuiver': ('Quiver', 'Item:Epic_Purifying_Quiver', 630281),
    'wikiBlunted': (None, 'Blunted_Ammunition', 612646),
}
BLUNTED = 'The ammunition fired by this weapon deals bludgeoning damage in addition to its other damage types.'


def validate_supplement(ledger, html):
    assert ledger['pageCount'] == len(ledger['pages']) == 21
    pages = {page['evidenceKey']: page for page in ledger['pages']}
    assert len(pages) == 21
    links = {node.attrs.get('href') for node in Document(html).root.nodes('a')}
    for key, (_, title, revision) in PINS.items():
        page = pages[key]
        expected = f'https://ddowiki.com/index.php?title={title}&oldid={revision}'
        assert page['permanentLink'] == expected
        assert page['capturedAt'].startswith('2026-11-05T')
        assert expected in links
    assert BLUNTED in pages['wikiBlunted']['text']
    assert 'Blunted Ammunition' in pages['wikiQuiver']['text']
    assert 'Burning Ammunition - 1d8' in pages['wikiQuiver']['text']
    assert 'Blue Augment Slot' in norm(pages['wikiEarthSky']['text'])
    for color in ['Green', 'Blue', 'Moon']:
        assert f'{color} Augment Slot' in norm(pages['wikiCord']['text'])
    validate_kit(html)
    validate_claims(html)


class FreshEndgameEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.html = (ROOT / 'index.html').read_text()
        self.path = FIX / 'fresh/wiki-live-audit-2026-11-05.json'
        self.data = self.path.read_bytes()
        self.ledger = json.loads(self.data)

    def test_public_capture_bytes_and_original_provenance_are_distinct(self):
        manifest = json.loads((FIX / 'fresh-provenance.json').read_text())
        digest = hashlib.sha256(self.data).hexdigest()
        self.assertEqual(manifest['original_sha256'], 'a5b0f7b43e9b3aa647417b00fd6e5ccf0925936fc42bcb2711dc0f679c308611')
        self.assertNotEqual(digest, manifest['original_sha256'])
        self.assertEqual(digest, manifest['sha256'])
        self.assertEqual(len(self.data), manifest['bytes'])
        self.assertEqual(manifest['path'], str(self.path.relative_to(FIX)))
        self.assertEqual(manifest['page_count'], 21)
        self.assertEqual(manifest['new_primary_pins'], {
            slot: {'evidence_key': key, 'oldid': revision}
            for key, (slot, _, revision) in PINS.items() if slot is not None
        })

    def test_new_pins_and_positive_effect_have_matching_evidence(self):
        validate_supplement(self.ledger, self.html)
        original = json.loads((FIX / 'inventory.json').read_text())
        pinned = {item['slot'] for item in original if item['pinned_url']}
        self.assertEqual(len(pinned), 8)
        additions = {slot for slot, _, _ in PINS.values() if slot is not None}
        self.assertFalse(pinned & additions)
        self.assertEqual(len(pinned | additions), 11)
        gaps = {item['slot'] for item in original} - pinned - additions
        self.assertEqual(gaps, {'Necklace', 'Trinket', 'Cloak'})

    def test_fabricated_pin_missing_page_or_changed_definition_is_rejected(self):
        for mutate in ['pin', 'page', 'definition']:
            ledger = copy.deepcopy(self.ledger)
            if mutate == 'page':
                ledger['pages'] = ledger['pages'][:-1]
            else:
                page = next(p for p in ledger['pages'] if p['evidenceKey'] == 'wikiBlunted')
                if mutate == 'pin':
                    page['permanentLink'] = page['permanentLink'].replace('612646', '999999')
                else:
                    page['text'] = page['text'].replace(BLUNTED, 'Replaces all other damage types.')
            with self.subTest(mutation=mutate), self.assertRaises(AssertionError):
                validate_supplement(ledger, self.html)

    def test_effect_penalty_and_full_verification_overclaims_are_rejected(self):
        changes = [
            ('deals bludgeoning damage in addition to its other damage types', 'replaces its other damage types with bludgeoning damage'),
            ('weapon-specific interactions remain unverified', 'all weapon interactions are verified'),
            ('eleven of fourteen', 'all fourteen'),
            ('not an in-game check', 'an in-game check'),
        ]
        for old, new in changes:
            self.assertIn(old, self.html)
            with self.subTest(old=old), self.assertRaises(AssertionError):
                validate_supplement(self.ledger, self.html.replace(old, new))


if __name__ == '__main__':
    unittest.main()
