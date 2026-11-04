"""Retained Wiki category membership only; never feat-slot compatibility."""
import copy
import hashlib
import json
import unittest

from test_editorial_consistency import GuideText
from test_legendary_trick_shot_evidence import (
    ROOT, EVIDENCE, CAPTURE_SHA256, CANONICAL, REVISION, LTS,
    require, table, selected_row,
)

CLAIM = 'Listed as a Legendary feat on the wiki; confirm the slot accepts it'
CATEGORY = 'https://ddowiki.com/page/Category:Legendary_feats'


def validate_classification(html, raw, record):
    require(len(raw) == 13743 and hashlib.sha256(raw).hexdigest() == CAPTURE_SHA256,
            'capture identity changed; source review required')
    capture = json.loads(raw)
    require(capture.get('isError') is False, 'error-flagged capture')
    text = capture['content'][0]['text']
    require(f'Title: "{LTS} - DDO wiki", URL: "{CANONICAL}"' in text
            and '\t\t84 heading Legendary Trick Shot, Value: 1, ID: firstHeading\n' in text
            and f'Value: {REVISION.removeprefix("https://")}\n' in text,
            'subject or revision context changed')
    # Scope membership to the actual page category container, not a stray link.
    context = text[text.index('\t\t\t110 container mw-normal-catlinks'):
                   text.index('\t118 container mw-navigation')]
    require('\t\t\t\t\t117 link Description: Legendary feats, Help: Category:Legendary feats, '
            f'Value: {CATEGORY.removeprefix("https://")}\n' in context,
            'explicit category membership missing')
    require(record['subject'] == LTS and record['canonical_url'] == CANONICAL
            and record['revision'] == 714089 and record['revision_url'] == REVISION,
            'maintained subject or revision changed')
    require(record['capture_file'] == 'Legendary_Trick_Shot.browser.json'
            and record['capture_bytes'] == len(raw)
            and record['capture_sha256'] == CAPTURE_SHA256
            and record['capture_timestamp'] is None, 'capture metadata changed')
    require(record['category_context'] == context, 'maintained category context changed')
    require(record['fact'] == {
        'field': 'wiki_category', 'value': 'Legendary feats',
        'type': 'page category membership', 'url': CATEGORY,
        'qualifiers': ['retained Wiki classification only; not feat-slot eligibility']},
        'maintained classification fact changed')
    require(record['guide_claim'] == {
        'section': 'epic-and-legendary-feats', 'selected_feat': LTS,
        'column': 'What it does (wiki)', 'text': CLAIM}, 'maintained claim context changed')
    rows = table(GuideText(html), 'epic-and-legendary-feats', 'Feat')
    chosen = selected_row(rows, LTS)
    require(chosen[rows[0].index('What it does (wiki)')] == CLAIM,
            'published classification or uncertainty caveat changed')


class LegendaryTrickShotClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / 'index.html').read_text()
        cls.raw = (EVIDENCE / 'Legendary_Trick_Shot.browser.json').read_bytes()
        cls.record = json.loads((EVIDENCE / 'classification.json').read_text())

    def test_published_classification_matches_actual_page_category(self):
        validate_classification(self.html, self.raw, self.record)

    def test_changed_published_classification_is_rejected(self):
        for category in ['Epic Destiny', 'Epic']:
            with self.subTest(category=category):
                html = self.html.replace(CLAIM, CLAIM.replace('Legendary', category))
                self.assertNotEqual(html, self.html)
                with self.assertRaisesRegex(ValueError, 'published classification'):
                    validate_classification(html, self.raw, self.record)

    def test_unsupported_eligibility_assertion_is_rejected(self):
        html = self.html.replace(CLAIM, CLAIM.replace('confirm the slot accepts it',
                                                     'eligible in the level-36 slot'))
        self.assertNotEqual(html, self.html)
        with self.assertRaisesRegex(ValueError, 'uncertainty caveat'):
            validate_classification(html, self.raw, self.record)

    def test_corrupted_capture_subject_revision_or_category_is_rejected(self):
        for old, new in [(b'Legendary Trick Shot - DDO wiki', b'Trick Shot - DDO wiki'),
                         (b'oldid=714089', b'oldid=714090'),
                         (b'Category:Legendary_feats', b'Category:Epic_Destiny_feats'),
                         (b'mw-normal-catlinks', b'unrelated-links')]:
            with self.subTest(context=old):
                raw = self.raw.replace(old, new)
                self.assertNotEqual(raw, self.raw)
                with self.assertRaisesRegex(ValueError, 'capture identity'):
                    validate_classification(self.html, raw, self.record)

    def test_corrupted_maintained_context_is_rejected(self):
        for field, value in [('subject', 'Trick Shot'), ('revision', 714090),
                             ('category_context', 'Legendary feats'),
                             ('guide_claim', {'text': CLAIM})]:
            with self.subTest(field=field):
                record = copy.deepcopy(self.record)
                record[field] = value
                with self.assertRaises(ValueError):
                    validate_classification(self.html, self.raw, record)

    def test_category_cannot_be_promoted_to_slot_eligibility(self):
        for field, value in [('type', 'eligible feat slot'),
                             ('qualifiers', ['eligible in the level-36 slot']),
                             ('value', 'Epic Destiny feats')]:
            with self.subTest(field=field):
                record = copy.deepcopy(self.record)
                record['fact'][field] = value
                with self.assertRaisesRegex(ValueError, 'classification fact'):
                    validate_classification(self.html, self.raw, record)


if __name__ == '__main__':
    unittest.main()
