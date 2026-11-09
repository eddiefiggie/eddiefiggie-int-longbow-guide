"""Bound the local editorial cleanup without weakening older release contracts."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

import stacking_audit as audit
from build_stacking_audit import summary

ROOT = Path(__file__).resolve().parents[1]
SCOPE = json.loads((ROOT/'tools/fixtures/editorial-comparison-cleanup/scope.json').read_text())
BASELINE_SHA = '2aef272d53307beab05f63a557397be744b360f3fcb91ca5261274a0037f5aa3'


def restore_exact(text, changes):
    for change in reversed(changes):
        assert text.count(change['after']) == 1, 'exact editorial replacement'
        text = text.replace(change['after'], change['before'])
    return text


def restore_editorial_prose(html):
    assert len(SCOPE['reviewed_replacements']) == 7
    return restore_exact(html, SCOPE['reviewed_replacements'][1:])


def restore_editorial_stamp(html):
    return restore_exact(html, SCOPE['reviewed_replacements'][:1])


def validate_current(html):
    assert SCOPE['baseline_commit'] == 'd426d2d9b2bbc63a255e5695faa0663df0f929b7'
    assert SCOPE['baseline_index_sha256'] == BASELINE_SHA
    restored = restore_editorial_prose(restore_editorial_stamp(html))
    assert hashlib.sha256(restored.encode()).hexdigest() == BASELINE_SHA


class EditorialComparisonCleanupTests(unittest.TestCase):
    def test_exact_editorial_scope_preserves_history_choices_numbers_and_links(self):
        validate_current((ROOT/'index.html').read_text())
        for path, expected in SCOPE['unchanged_inputs'].items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(), expected)

    def test_restored_stale_claim_and_unrelated_changes_are_rejected(self):
        html = (ROOT/'index.html').read_text()
        rule = SCOPE['reviewed_replacements'][4]
        for before, after in (
            (rule['after'], rule['before']),
            ('<td>Legendary Abyssal Compass</td>', '<td>Different gear</td>'),
            ('<td>36 → 35</td>', '<td>36 → 36</td>'),
            ('<td>Maximum (23)</td>', '<td>Maximum (22)</td>'),
            ('Spot +22 is a Competence source, not a guaranteed final skill gain.',
             'Spot +22 guarantees a final +22 skill gain.'),
            ('https://ddowiki.com/page/Item:The_Queen_of_Rot', 'https://example.invalid/queen'),
        ):
            self.assertIn(before, html)
            with self.subTest(before=before), self.assertRaises(AssertionError):
                validate_current(html.replace(before, after))

    def test_generator_changes_are_only_the_reviewed_wording(self):
        text = (ROOT/'tools/build_stacking_audit.py').read_text()
        self.assertEqual(len(SCOPE['generator_replacements']), 3)
        restored = restore_exact(text, SCOPE['generator_replacements'])
        self.assertEqual(hashlib.sha256(restored.encode()).hexdigest(), SCOPE['baseline_generator_sha256'])

    def test_goggles_summary_keeps_evidence_gate_without_old_cloak_comparison(self):
        data = audit.load()
        rendered = summary(data)
        self.assertIn('Goggles provide the selected 9% Enhancement Doubleshot.', rendered)
        # Losing provenance must select the existing unknown-input branch, not certify a source.
        unknown = copy.deepcopy(data)
        next(c for c in unknown['components'] if c['id'] == 'goggles-ds')['state'] = 'unknown'
        fallback = summary(unknown)
        self.assertIn('The goggles Doubleshot input remains unverified.', fallback)
        self.assertNotIn('Goggles provide the selected 9%', fallback)
        for output in (rendered, fallback):
            self.assertNotIn('former cloak', output)
            self.assertNotIn('former Light Absorption', output)
            self.assertIn('The selected Queen’s Freedom of Movement is a relayed item effect.', output)
            self.assertIn('the component remains unknown and excluded from subtotals', output)


if __name__ == '__main__':
    unittest.main()
