"""Release wording and public provenance checks; not mechanics certification."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = 'evidence/gear-recipes-2026-11-18.json'


class PublishedRecipeSourceNotesTests(unittest.TestCase):
    def test_public_sources_keep_all_six_roles_and_evidence_limits(self):
        raw = (ROOT / EVIDENCE).read_text()
        data = json.loads(raw)
        self.assertNotIn('chatgpt.com/', raw)
        self.assertEqual([s.split(':')[0] for s in data['sources']],
                         ['Level 15', 'Level 15', 'Level 20', 'Level 20',
                          'Level 36', 'Level 36'])
        self.assertFalse(data['certified_mechanics'])
        self.assertFalse(data['reproduced_optimizer'])
        self.assertIn('not independent mechanics observations', data['source_class'])

    def test_current_release_wording_preserves_uncertainty_and_source_links(self):
        guide = (ROOT / 'index.html').read_text()
        self.assertNotIn('chatgpt.com/c/', guide)
        self.assertNotIn('This draft is not released guidance', guide)
        self.assertIn('selected gear recipes published', guide)
        self.assertIn('Publication does not certify the reported mechanics.', guide)
        self.assertIn('not a fresh independent source check', guide)
        for level in (15, 20, 36):
            self.assertIn(f'href="{EVIDENCE}">level-{level} source notes</a>', guide)
