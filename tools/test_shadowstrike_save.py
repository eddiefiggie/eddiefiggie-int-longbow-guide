"""A-019 retained-source/Guide guards; no current-game or other-effect proof."""
import copy
import hashlib
import json
from pathlib import Path
import re
import unittest

from test_early_xp import visible_nodes, visible_text
from test_lamordia_handling import Document, norm

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / 'evidence/shadowstrike-save/source.json'
SOURCE = ROOT / 'tools/fixtures/endgame-evidence/retained/Shadowdancer.live.json'
CANONICAL = 'https://ddowiki.com/page/Shadowdancer'
REVISION = 'https://ddowiki.com/index.php?title=Shadowdancer&oldid=720964'
PUBLIC_SHA = '0eec83c3445c5f226511773a19e2d742abad87b6b066493f5fdd5d9367d44f7b'
ORIGINAL_SHA = 'ab3c5298ae4058da84421ff0b900b6db4caacc66a39db197bc898335de1c84fe'
TEXT_SHA = 'a282de27aa37629b337ccf0b1330b3eab933c258f37b7662f31b341c8c0ffb70'
DC = 'DC 20 + highest ability score + Assassinate Bonuses'
QUOTE = f'On hit, opponent must make a Fortitude save vs ({DC}) or be cursed with Shadow Loss.'
CONDITION = 'only if the struck opponent fails its Fortitude save'
SCOPE = ('Shadowstrike on-hit Shadow Loss requires the struck opponent to fail '
         'the stated Fortitude save; no other effect adjudicated')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source_contract(raw, record):
    require(sha(raw) == PUBLIC_SHA, 'retained source bytes changed')
    source = json.loads(raw)
    require(source['title'] == 'Shadowdancer - DDO wiki' and
            source['revision'] == REVISION, 'source subject/revision')
    require(sha(source['text'].encode()) == TEXT_SHA, 'original Wiki body identity')
    excerpt = source['text'][4245:4592]
    require(excerpt.startswith(' Shadowstrike (AoE Ranged Attack): Epic Strike:')
            and QUOTE in excerpt, 'complete operative clause under ranged Shadowstrike')
    expected = {
        'finding': 'A-019 / P3-GFE-001', 'source_id': 'Q.E01-shadowstrike',
        'canonical_url': CANONICAL, 'revision_url': REVISION, 'revision': 720964,
        'source_file': str(SOURCE.relative_to(ROOT)), 'source_sha256': PUBLIC_SHA,
        'original_relative_path': 'intiana-audit-2026-11-01/trees/sources/Shadowdancer.live.json',
        'original_sha256': ORIGINAL_SHA, 'text_sha256': TEXT_SHA,
        'pointer': '/text', 'character_range': [4245, 4592],
        'excerpt': excerpt, 'operative_quote': QUOTE,
        'body_observed_start': None, 'body_observed_end': None,
        'current_game_observed': False,
        'canonical_url_status': 'canonical citation; original capture identifies title and revision, not a separate canonical-page observation',
        'scope': SCOPE,
    }
    require(set(record) == set(expected) | {'guide_occurrences'}, 'source record fields')
    for key, value in expected.items():
        require(type(record[key]) is type(value) and record[key] == value,
                'source provenance/operative contract: ' + key)
    return QUOTE


def curse_occurrences(html):
    section = None
    result = []
    for node in visible_nodes(Document(html).root):
        if node.tag in {'h2', 'h3'}:
            section = node.attrs.get('id')
        if node.tag not in {'li', 'tr', 'p'}:
            continue
        text = norm(visible_text(node))
        if 'Shadowstrike' in text and re.search(r'\b(?:curse|cursed|Shadow Loss)\b', text):
            result.append((section, node.tag, text, node))
    return result


def validate(html, raw, record):
    source_contract(raw, record)
    occurrences = curse_occurrences(html)
    expected_locations = [('shadowdancer-27', 'tr', 652),
                          ('abilities-explained', 'li', 1229),
                          ('buttons-and-timers-wiki', 'tr', 1268)]
    require(len(occurrences) == len(record['guide_occurrences']) == 3,
            'three actual Shadowstrike curse occurrences; review additions/omissions')
    for actual, expected, location in zip(occurrences, record['guide_occurrences'], expected_locations):
        section, tag, text, node = actual
        require((section, tag) == location[:2], 'curse subject/location')
        require(expected['section'] == section and expected['tag'] == tag and
                expected['baseline_line'] == location[2], 'occurrence provenance')
        require(text.count(CONDITION) == 1, 'failed Fortitude save condition')
        require(text == expected['reviewed_text'], 'reviewed curse context changed')
        if tag == 'li':
            require(text.count(DC) == 1, 'literal source DC formula')
            links = [n for n in visible_nodes(node) if n.tag == 'a' and
                     norm(visible_text(n)) == 'Shadowdancer page']
            require(len(links) == 1 and links[0].attrs.get('href') == CANONICAL,
                    'direct Shadowdancer citation')
    # The complete selected contexts above are closed. Also reject an added
    # visible named guarantee outside them; this is a bounded wording guard,
    # not an arbitrary natural-language contradiction detector.
    doc = Document(html).root
    for node in visible_nodes(doc):
        if node.tag not in {'li', 'p', 'td', 'figcaption'}:
            continue
        text = norm(visible_text(node))
        require(not re.search(r'(?:Shadowstrike|Shadow Loss)[^.]{0,180}\b(?:always|guaranteed|automatically|without a save|no save)\b', text, re.I),
                'unsupported guaranteed curse claim')
    return True


class ShadowstrikeSaveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / 'index.html').read_text()
        cls.raw = SOURCE.read_bytes()
        cls.record = json.loads(RECORD.read_text())

    def reject_html(self, changed, error):
        self.assertNotEqual(changed, self.html, 'mutation must change actual Guide')
        with self.assertRaisesRegex(ValueError, error):
            validate(changed, self.raw, self.record)

    def test_actual_guide_and_retained_source(self):
        self.assertTrue(validate(self.html, self.raw, self.record))

    def test_harmless_inline_markup_and_inert_old_copy(self):
        changed = self.html.replace('fails its Fortitude save', 'fails its <em>Fortitude save</em>')
        changed += '<!-- Shadowstrike always curses. --><template><p>Shadowstrike always curses.</p></template>'
        self.assertTrue(validate(changed, self.raw, self.record))

    def test_each_occurrence_requires_the_failed_save(self):
        for position in range(3):
            for bad in ['', 'on every hit', CONDITION.replace('fails', 'succeeds'),
                        CONDITION.replace('Fortitude', 'Reflex'),
                        CONDITION.replace('struck opponent', 'attacker')]:
                with self.subTest(position=position, replacement=bad):
                    pieces = self.html.split(CONDITION)
                    changed = CONDITION.join(pieces[:position+1]) + bad + CONDITION.join(pieces[position+1:])
                    self.reject_html(changed, 'failed Fortitude save condition')

    def test_hidden_or_inert_conditions_do_not_satisfy_guard(self):
        for attr in ['hidden', 'inert', 'aria-hidden="true"', 'style="display:none"']:
            with self.subTest(attribute=attr):
                self.reject_html(self.html.replace(CONDITION, f'<span {attr}>{CONDITION}</span>'),
                                 'failed Fortitude save condition')

    def test_literal_dc_cannot_change_or_move_to_inert_text(self):
        for replacement in [DC.replace('score', 'modifier'), DC.replace('20', '10'),
                            DC.replace('Assassinate Bonuses', 'Ranged Power'),
                            f'<template>{DC}</template>']:
            with self.subTest(replacement=replacement):
                self.reject_html(self.html.replace(DC, replacement), 'reviewed curse context|literal source DC')

    def test_direct_link_must_belong_to_shadowdancer(self):
        target = f'href="{CANONICAL}">Shadowdancer page'
        self.reject_html(self.html.replace(target, 'href="https://ddowiki.com/page/Shiradi_Champion">Shadowdancer page'),
                         'direct Shadowdancer citation')

    def test_guaranteed_curse_cannot_be_added_to_each_context(self):
        for position in range(3):
            pieces = self.html.split(CONDITION)
            changed = CONDITION.join(pieces[:position+1]) + CONDITION + '; the curse is guaranteed regardless of the save' + CONDITION.join(pieces[position+1:])
            self.reject_html(changed, 'reviewed curse context')

    def test_new_named_guarantee_outside_context_is_rejected(self):
        for claim in ['Shadowstrike always curses.', 'Shadow Loss is guaranteed.',
                      'Shadow Loss applies automatically without a save.']:
            self.reject_html(self.html.replace('</main>', f'<p>{claim}</p></main>'),
                             'occurrences|guaranteed curse')

    def test_original_build_hash_accepts_only_exact_reviewed_correction(self):
        from test_endgame_evidence import validate_preservation
        validate_preservation(self.html)
        for old, new in [
            ('Dance in the Dark 3, Lithe 2, Epic Strike:',
             'Dance in the Dark 2, Lithe 2, Epic Strike:'),
            ('AoE ranged strike with +30% damage', 'AoE ranged strike with +40% damage')]:
            changed = self.html.replace(old, new)
            self.assertNotEqual(changed, self.html)
            with self.assertRaises(AssertionError):
                validate_preservation(changed)

    def test_preservation_reversal_cannot_mask_missing_save(self):
        from test_endgame_evidence import validate_preservation
        with self.assertRaisesRegex(AssertionError, 'A-019 exact reviewed correction'):
            validate_preservation(self.html.replace(CONDITION, 'on every hit', 1))

    def test_source_mutation_cannot_be_blessed_by_recomputed_receipt_hash(self):
        for old, new in [('Fortitude', 'Reflex'), ('highest ability score', 'highest ability modifier'),
                         ('Shadowdancer', 'Shiradi Champion'), ('720964', '720965')]:
            raw = self.raw.replace(old.encode(), new.encode())
            record = copy.deepcopy(self.record); record['source_sha256'] = sha(raw)
            with self.subTest(mutation=old), self.assertRaisesRegex(ValueError, 'retained source bytes'):
                validate(self.html, raw, record)

    def test_quote_identity_scope_and_clock_mutations_are_rejected(self):
        cases = [('operative_quote', ''), ('operative_quote', QUOTE.replace(' or ', ' and ')),
                 ('excerpt', QUOTE), ('canonical_url', 'https://ddowiki.com/page/Shiradi_Champion'),
                 ('pointer', '/footer'), ('character_range', [0, 10]), ('revision', 720965),
                 ('body_observed_start', '2026-11-08T12:00:00Z'),
                 ('body_observed_end', '2026-11-08T12:00:01Z'),
                 ('current_game_observed', True), ('scope', 'All Shadowstrike mechanics verified')]
        for key, value in cases:
            with self.subTest(field=key):
                record = copy.deepcopy(self.record); record[key] = value
                with self.assertRaisesRegex(ValueError, 'source provenance/operative contract'):
                    validate(self.html, self.raw, record)

    def test_occurrence_inventory_cannot_drop_or_misroute_summary(self):
        record = copy.deepcopy(self.record); record['guide_occurrences'].pop()
        with self.assertRaisesRegex(ValueError, 'three actual'):
            validate(self.html, self.raw, record)
        record = copy.deepcopy(self.record); record['guide_occurrences'][0]['baseline_line'] = 0
        with self.assertRaisesRegex(ValueError, 'occurrence provenance'):
            validate(self.html, self.raw, record)

    def test_record_and_guide_cannot_collude_to_remove_condition(self):
        html = self.html.replace(CONDITION, 'on every hit')
        record = copy.deepcopy(self.record)
        for item in record['guide_occurrences']:
            item['reviewed_text'] = item['reviewed_text'].replace(CONDITION, 'on every hit')
        with self.assertRaisesRegex(ValueError, 'failed Fortitude save condition'):
            validate(html, self.raw, record)


if __name__ == '__main__':
    unittest.main()
