"""Retained-source and selected-occurrence regressions, with deliberate faults.

Semantic negative controls deliberately bypass the byte hash to prove that field
and context checks work independently of the immutable capture identity check.
"""
import copy
import json
import unittest

from sapphire_evidence import (FIXTURE, ROOT, load_record, validate_guide,
                               validate_source, verify_bytes)


class SapphireEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = load_record()
        cls.raw = (FIXTURE / 'source.json').read_bytes()
        cls.source = json.loads(cls.raw)
        cls.guide = (ROOT / 'index.html').read_text()

    def test_exact_retained_bytes(self):
        verify_bytes(self.raw, self.record)

    def test_full_source_fields_and_context(self):
        validate_source(self.source, self.record)

    def test_selected_published_occurrences(self):
        validate_guide(self.guide, self.source, self.record)

    def test_byte_corruption_is_rejected(self):
        for raw in (self.raw + b' ', self.raw.replace(b'700645', b'700646')):
            with self.subTest(size=len(raw)), self.assertRaises(ValueError):
                verify_bytes(raw, self.record)

    def test_source_field_and_context_faults_are_rejected(self):
        mutations = [
            ('minimum level', '>7\n</td>', '>6\n</td>', 'source field: Minimum Level'),
            ('critical profile', '>19-20 / x3', '>18-20 / x4', 'source field: Critical threat range'),
            ('damage vs enhancement', '[1d8] + 3 Pierce, Magic', '[1d8+3] Pierce, Magic', 'source field: Damage and Type'),
            ('enhancement value', '+3 Enhancement Bonus', '+4 Enhancement Bonus', 'full enchantment list'),
            ('affix value', 'Ranged Alacrity 10%', 'Ranged Alacrity 20%', 'full enchantment list'),
            ('affix type', 'Lesser Human Bane', 'Greater Human Bane', 'full enchantment list'),
            ('slot', 'Purple&nbsp;Augment&nbsp;Slot', 'Red&nbsp;Augment&nbsp;Slot', 'full enchantment list'),
            ('binding', 'Bound to Account&nbsp;on Acquire', 'Bound to Character&nbsp;on Acquire', 'source field: Binding'),
            ('loot', "dragon's hoard chests", 'end chest', 'source field: Location'),
            ('variant', '>Sapphire Sting</span></h1>', '>Epic Sapphire Sting</span></h1>', 'item variant heading'),
            ('revision context', 'revision id 700645.', 'revision id 700646.', 'cache context'),
            ('cached time', 'Cached time: 20261102150341', 'Cached time: 20261103172959', 'cache context'),
            ('wrong table context', 'class="striped"', 'class="unrelated"', 'item table'),
            ('Keen added to full list', '</li></ul>', '</li><li>Keen</li></ul>', 'full enchantment list'),
            ('Mythic uncertainty removed', 'This is a rare enchantment that does not show up on all drops of this item.', 'This appears on every drop.', 'optional Mythic qualifier'),
        ]
        for name, old, new, error in mutations:
            with self.subTest(fault=name):
                source = copy.deepcopy(self.source)
                self.assertIn(old, source['rendered_document_html'])
                source['rendered_document_html'] = source['rendered_document_html'].replace(old, new)
                with self.assertRaisesRegex(ValueError, error):
                    validate_source(source, self.record)

    def test_identity_and_visible_context_faults_are_rejected(self):
        for key, replacement in [('url', 'https://ddowiki.com/page/Item:Epic_Sapphire_Sting'),
                                 ('permanent_link', self.source['permanent_link'].replace('700645', '700646')),
                                 ('capture_format', 'raw-server-html'),
                                 ('captured_at_utc', '2026-11-04T17:29:59.097Z')]:
            with self.subTest(key=key):
                source = dict(self.source, **{key: replacement})
                with self.assertRaisesRegex(ValueError, 'source identity'):
                    validate_source(source, self.record)
        for old, new in [('Minimum Level\t7', 'Minimum Level\t8'),
                         ('Minimum Level\t7', 'Minimum Level\t70'),
                         ('(this is up to 6 hours old)', '(fresh now)')]:
            with self.subTest(visible=old):
                source = dict(self.source)
                self.assertIn(old, source['full_visible_text'])
                source['full_visible_text'] = source['full_visible_text'].replace(old, new)
                with self.assertRaisesRegex(ValueError, 'visible'):
                    validate_source(source, self.record)

    def test_ladder_field_faults_are_rejected(self):
        start = self.guide.index('<tr><td>7</td><td><a href="https://ddowiki.com/page/Item:Sapphire_Sting">')
        end = self.guide.index('</tr>', start) + len('</tr>')
        row = self.guide[start:end]
        for old, new in [('<td>7</td>', '<td>6</td>'), ('19-20/x3', '18-20/x4'),
                         ('[1d8]+3', '[1d8+3]'), ('Ranged Alacrity 10%', 'Ranged Alacrity 20%'),
                         ('Lesser Human Bane', 'Greater Human Bane'), ('Purple slot', 'Red slot'),
                         ('Bound to Account', 'Bound to Character'), ('dragon’s hoard chests', 'end chest'),
                         ('Keen is not listed', 'no Keen'), ('listed 19-20', 'native 19-20')]:
            with self.subTest(fault=old):
                self.assertIn(old, row)
                mutant = self.guide[:start] + row.replace(old, new) + self.guide[end:]
                with self.assertRaisesRegex(ValueError, 'Guide item cells'):
                    validate_guide(mutant, self.source, self.record)

    def test_contradictory_additions_in_selected_context_are_rejected(self):
        for before, addition in [
            ('Keen is not listed among Sapphire Sting’s enchantments.',
             ' Sapphire Sting is a Keen bow.'),
            ('its post-Improved-Critical interaction is not verified here.',
             ' Sapphire Sting stacks with Improved Critical.'),
        ]:
            with self.subTest(unsupported=addition):
                self.assertIn(before, self.guide)
                mutant = self.guide.replace(before, before + addition, 1)
                with self.assertRaisesRegex(ValueError, 'context drift'):
                    validate_guide(mutant, self.source, self.record)

    def test_each_selected_claim_and_uncertainty_is_guarded(self):
        # Use parsed text replacement for every required claim, so inline anchors
        # cannot prevent the deliberate deletion from reaching the validator.
        from sapphire_evidence import Document, norm
        for claim in self.record['guide_claims']:
            for required in claim['required']:
                with self.subTest(claim=claim['name'], required=required):
                    doc = Document(self.guide).root
                    block = next(n for tag in ('tr', 'li', 'p') for n in doc.nodes(tag)
                                 if norm(n.text()).startswith(claim['starts_with']))
                    # Flatten only the chosen actual block, leaving its context
                    # and every other block intact, then delete the required claim.
                    text = norm(block.text())
                    original = self.guide
                    # Replace the entire matching markup block with flattened text.
                    import re
                    candidates = re.findall(r'<'+block.tag+r'\b[^>]*>.*?</'+block.tag+'>', original, re.S)
                    markup = next(b for b in candidates if norm(Document(b).root.text()) == text)
                    mutant = original.replace(markup, '<'+block.tag+'>'+text.replace(required, '[REMOVED]')+'</'+block.tag+'>', 1)
                    with self.assertRaises(ValueError):
                        validate_guide(mutant, self.source, self.record)


if __name__ == '__main__':
    unittest.main()
