"""Current rendered gear claims must depend on the bounded Doubleshot result."""
import copy
from pathlib import Path
import unittest
from unittest import mock

import build_stacking_audit
import stacking_audit
import wisdom_loadout
from test_lamordia_handling import Document, norm


class CurrentDoubleshotContentTests(unittest.TestCase):
    def setUp(self):
        self.ledger = stacking_audit.load()
        self.selection = wisdom_loadout.load()

    def test_current_surfaces_show_qualified_gear_scope(self):
        summary = build_stacking_audit.summary(self.ledger)
        doc = Document(summary)
        rows = [n for n in doc.root.nodes('tr')
                if n.attrs.get('data-stat') == 'Doubleshot']
        self.assertEqual(len(rows), 1)
        self.assertIn('35', norm(rows[0].text()))
        self.assertIn('percentage points', norm(rows[0].text()))
        qualifications = [n for n in doc.root.nodes('p')
                          if n.attrs.get('data-doubleshot-qualification') == 'selected-five']
        self.assertEqual(len(qualifications), 1)
        text = norm(qualifications[0].text())
        for required in ('three distinct equipped hosts', 'one Quickblade 15 Artifact',
                         '100 Legendary Staff Splinters', 'full filled kit remains ML36',
                         'Six exact native pairs', 'whole-character'):
            self.assertIn(required, text)
        self.assertIn('35 percentage points', norm(Document(
            wisdom_loadout.render_onepage_rows(self.selection)).root.text()))
        priorities = Document(wisdom_loadout.render_priorities(self.selection))
        ds = [n for n in priorities.root.nodes('tr')
              if n.attrs.get('data-stat') == 'Doubleshot']
        self.assertEqual(len(ds), 1)
        self.assertIn('Selected gear 35 has separate bounded source support at ML36',
                      norm(ds[0].text()))

    def test_renderers_withhold_claim_after_family_or_rule_loss(self):
        mutants = []
        missing_member = copy.deepcopy(self.ledger)
        missing_member['components'] = [c for c in missing_member['components']
                                        if c['id'] != 'quickblade-ds']
        mutants.append(missing_member)
        missing_rule = copy.deepcopy(self.ledger)
        missing_rule['rules'] = [r for r in missing_rule['rules']
                                 if r['id'] != 'doubleshot-selected-six-pairs']
        mutants.append(missing_rule)
        for ledger in mutants:
            for render, expected_error in (
                    (wisdom_loadout.render_doubleshot_qualification, ValueError),
                    (build_stacking_audit.summary, AssertionError),
                    (build_stacking_audit.detail, AssertionError)):
                with self.subTest(renderer=render.__name__, missing=len(ledger['components'])):
                    with self.assertRaises(expected_error):
                        render(ledger)
            with mock.patch.object(stacking_audit, 'load', return_value=ledger):
                # A missing rule profile can fail an earlier required claim
                # guard; either path must withhold the whole rendered output.
                with self.assertRaises(ValueError):
                    wisdom_loadout.render_onepage_rows(self.selection)
                with self.assertRaises(ValueError):
                    wisdom_loadout.render_priorities(self.selection)

    def test_current_guide_and_audit_keep_source_and_whole_build_boundaries(self):
        root = Path(__file__).resolve().parents[1]
        guide = Document((root / 'index.html').read_text())
        current = [n for n in guide.root.nodes('section')
                   if n.attrs.get('id') == 'selected-stacking-summary']
        self.assertEqual(len(current), 1)
        self.assertIn('Derived selected-gear Doubleshot: 35 percentage points at level 36',
                      norm(current[0].text()))
        audit = Document((root / 'endgame-stacking-audit.html').read_text())
        ids = {n.attrs.get('id') for n in audit.root.nodes('h3')}
        self.assertIn('rule-doubleshot-selected-six-pairs', ids)
        self.assertIn('gap-whole-build-doubleshot', ids)
        links = [n.attrs.get('href') for n in current[0].nodes('a')]
        self.assertIn('evidence/wisdom-loadout/doubleshot-sources-2026-11-16.json', links)
        self.assertIn('evidence/wisdom-loadout/doubleshot-integration-2026-11-16.json', links)


if __name__ == '__main__':
    unittest.main()
