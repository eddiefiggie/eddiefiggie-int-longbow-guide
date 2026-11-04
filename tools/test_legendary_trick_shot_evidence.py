"""Two necessary prerequisites from retained wiki revision 714089, not legality."""

import copy
import hashlib
import json
from pathlib import Path
import re
import unittest

from test_editorial_consistency import GuideText

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'evidence' / 'legendary-trick-shot'
CAPTURE_SHA256 = '3787c98e40d2be79e2efb6096c0db3362c2c95a5269f0d192ef071f0da9c84cf'
CANONICAL = 'https://ddowiki.com/page/Legendary_Trick_Shot'
REVISION = 'https://ddowiki.com/index.php?title=Legendary_Trick_Shot&oldid=714089'
LTS = 'Legendary Trick Shot'
TS = 'Trick Shot'
CAVEAT = 'confirm the slot accepts it'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_facts(raw, record):
    """Fail closed if retained bytes, source context or maintained facts change."""
    require(len(raw) == 13743 and hashlib.sha256(raw).hexdigest() == CAPTURE_SHA256,
            'retained capture identity changed; source review required')
    capture = json.loads(raw)
    require(capture.get('isError') is False, 'source is error-flagged')
    text = capture['content'][0]['text']
    require(f'URL: "{CANONICAL}"' in text and REVISION.removeprefix('https://') in text,
            'source page/revision context missing')
    context = text[text.index('\t\t\t\t90 heading'):text.index('\t\t\t\t100 heading')]
    # Read the prerequisite and its linked feat together under the subject heading.
    match = re.search(r'98 text Prerequisite:  Level (\d+), \n\t+99 link Description: (.*?), Value: ddowiki.com/page/Trick_Shot\n', context)
    require(match is not None, 'explicit prerequisite context missing')
    level, feat = int(match[1]), match[2]
    require(record['subject'] == LTS and record['kind'] == 'wiki-stated prerequisite'
            and record['canonical_url'] == CANONICAL and record['revision'] == 714089
            and record['revision_url'] == REVISION and record['context'] == context,
            'maintained source context differs from retained passage')
    require(record['capture_file'] == 'Legendary_Trick_Shot.browser.json'
            and record['capture_bytes'] == len(raw) and record['capture_sha256'] == CAPTURE_SHA256
            and record['capture_timestamp'] is None, 'capture metadata changed')
    require(record['facts'] == [
        {'field': 'minimum_level', 'value': level, 'type': 'integer',
         'qualifiers': ['necessary prerequisite, not sufficient legality']},
        {'field': 'required_feat', 'value': feat, 'type': 'feat reference',
         'qualifiers': ['must already be selected in this guide schedule',
                        'no same-level ordering adjudicated']}], 'maintained facts differ from source')
    require(record['guide_claim'] == {'section': 'epic-and-legendary-feats',
            'column': 'Prerequisite', 'text': f'Level {level}, {feat}'},
            'maintained claim context changed')
    return level, feat


def one(items, description):
    require(len(items) == 1, f'expected one {description}; found {len(items)}')
    return items[0]


def table(guide, section, header):
    return one([t for t in guide.tables[section] if t and header in t[0]], section)


def selected_row(rows, feat):
    # Only the Feat column counts, not a prerequisite or an incidental mention.
    return one([r for r in rows[1:] if len(r) > 1 and
                (r[1] == feat or r[1] == f'{feat} ({CAVEAT})')], feat)


def check_schedule(level, prior_level, minimum, location):
    require(level >= minimum, f'{location}: Legendary Trick Shot below source minimum')
    require(prior_level < level, f'{location}: missing prior Trick Shot')


def validate(html, raw, record):
    minimum, prerequisite = source_facts(raw, record)
    guide = GuideText(html)
    for section in ['epic-and-legendary-feats', 'levelling-roadmap']:
        rows = table(guide, section, 'Feat')
        chosen = selected_row(rows, LTS)
        prior = selected_row(rows, prerequisite)
        require(chosen[0].isdigit() and prior[0].isdigit(), 'ambiguous selection level')
        check_schedule(int(chosen[0]), int(prior[0]), minimum, section)
        require(CAVEAT in ' '.join(chosen), f'{section}: slot uncertainty removed')
        if section == 'epic-and-legendary-feats':
            require(chosen[rows[0].index('Prerequisite')] == record['guide_claim']['text'],
                    'published prerequisite claim differs from source')
    summary = table(guide, 'the-build-in-one-page', 'Area')
    row = one([r for r in summary[1:] if r[0] == 'Epic and legendary feats'], 'feat summary')
    # Anchor whole comma-separated selections, so Legendary Trick Shot cannot
    # accidentally supply the prerequisite Trick Shot selection.
    clauses = row[1].split(', ')
    prior = one([m for c in clauses if (m := re.fullmatch(r'Trick Shot (\d+)', c))],
                'summary Trick Shot selection')
    chosen = one([m for c in clauses if (m := re.fullmatch(
        r'Legendary Trick Shot (\d+) \(confirm the slot accepts it\)\.', c))],
        'summary Legendary Trick Shot selection with slot caveat')
    check_schedule(int(chosen[1]), int(prior[1]), minimum, 'one-page summary')


class LegendaryTrickShotEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / 'index.html').read_text()
        cls.raw = (EVIDENCE / 'Legendary_Trick_Shot.browser.json').read_bytes()
        cls.record = json.loads((EVIDENCE / 'source.json').read_text())

    def test_published_claim_and_three_schedules_match_retained_prerequisites(self):
        validate(self.html, self.raw, self.record)

    def reject_html(self, changed, message=None):
        self.assertNotEqual(changed, self.html, 'negative control did not mutate guide')
        with self.assertRaisesRegex(ValueError, message or '.'):
            validate(changed, self.raw, self.record)

    def test_each_schedule_rejects_too_low_level(self):
        for old, new in [
            ('<td>36</td><td>Legendary Trick Shot</td>', '<td>29</td><td>Legendary Trick Shot</td>'),
            ('<td>36</td><td>Legendary Trick Shot (', '<td>29</td><td>Legendary Trick Shot ('),
            ('Legendary Trick Shot 36 (', 'Legendary Trick Shot 29 (')]:
            with self.subTest(location=old):
                self.reject_html(self.html.replace(old, new), 'below source minimum')

    def test_each_schedule_requires_actual_prior_selection(self):
        for old, new in [
            ('<td>Trick Shot</td><td>Level 21</td>', '<td>Other feat</td><td>Level 21</td>'),
            ('<td>Trick Shot</td><td>Shadowdancer:', '<td>Other feat</td><td>Shadowdancer:'),
            (', Trick Shot 33,', ', Other feat 33,')]:
            with self.subTest(location=old):
                self.reject_html(self.html.replace(old, new))

    def test_same_or_later_level_does_not_establish_prior_selection(self):
        for level in [36, 37]:
            for old, new in [
                ('<td>33</td><td>Trick Shot</td><td>Level 21</td>',
                 f'<td>{level}</td><td>Trick Shot</td><td>Level 21</td>'),
                ('<td>33</td><td>Trick Shot</td><td>Shadowdancer:',
                 f'<td>{level}</td><td>Trick Shot</td><td>Shadowdancer:'),
                (', Trick Shot 33,', f', Trick Shot {level},')]:
                with self.subTest(level=level, location=old):
                    self.reject_html(self.html.replace(old, new), 'missing prior Trick Shot')

    def test_minimum_boundary_accepts_only_the_two_necessary_conditions(self):
        # Synthetic schedule only: this does NOT assert an eligible feat slot.
        html = self.html.replace('<td>33</td><td>Trick Shot</td>',
                                 '<td>29</td><td>Trick Shot</td>')
        html = html.replace('<td>36</td><td>Legendary Trick Shot',
                            '<td>30</td><td>Legendary Trick Shot')
        html = html.replace(', Trick Shot 33,', ', Trick Shot 29,')
        html = html.replace('Legendary Trick Shot 36 (', 'Legendary Trick Shot 30 (')
        validate(html, self.raw, self.record)

    def test_corrupted_capture_is_rejected(self):
        for raw in [self.raw.replace(b'Level 30', b'Level 20'),
                    self.raw.replace(b'"isError":false', b'"isError":true')]:
            self.assertNotEqual(raw, self.raw)
            with self.assertRaisesRegex(ValueError, 'capture identity'):
                validate(self.html, raw, self.record)

    def test_corrupted_maintained_source_and_claim_context_are_rejected(self):
        for key, value in [('context', 'Level 30, Trick Shot'), ('revision', 714090),
                           ('canonical_url', 'https://ddowiki.com/page/Trick_Shot'),
                           ('guide_claim', {'text': 'Level 20'}),
                           ('capture_timestamp', '2026-11-03')]:
            with self.subTest(field=key):
                changed = copy.deepcopy(self.record)
                changed[key] = value
                with self.assertRaises(ValueError):
                    validate(self.html, self.raw, changed)
        changed = copy.deepcopy(self.record)
        changed['facts'][0]['value'] = 20
        with self.assertRaisesRegex(ValueError, 'facts differ'):
            validate(self.html, self.raw, changed)

    def test_citation_and_matching_selections_cannot_mask_wrong_claim(self):
        self.reject_html(self.html.replace('Level 30, Trick Shot</td>',
                                          'Level 20, Trick Shot</td>'), 'claim differs')

    def test_slot_caveat_is_required_but_slot_legality_is_not_asserted(self):
        self.reject_html(self.html.replace(CAVEAT, 'slot verified'))


if __name__ == '__main__':
    unittest.main()
