"""Narrow retained-source/actual-Guide guards; not current game certification."""
import copy
import hashlib
import json
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit

from test_lamordia_handling import Document, Node, norm
from test_public_evidence_privacy import validate_public

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / 'evidence/early-xp/claims.json'
SOURCE = ROOT / 'tools/fixtures/endgame-evidence/fresh/wiki-live-audit-2026-11-05.json'
PUBLIC_SHA = 'e8f9285807d932161a72c0dc01f47571b9792e03d3788a25504ca33e1f7becf6'
ORIGINAL_SNAPSHOTS = (
    '10-29-26.10.html',
    '10-29-26.11.html',
    '10-29-26.8.html',
    '10-29-26.9.html',
    '10-30-26.1.html',
    '10-30-26.10.html',
    '10-30-26.2.html',
    '10-30-26.3.html',
    '10-30-26.5.html',
    '10-30-26.6.html',
    '10-30-26.7.html',
    '10-30-26.8.html',
    '10-30-26.9.html',
    '10-31-26.1.html',
    '10-31-26.2.html',
    '10-31-26.3.html',
    '10-31-26.4.html',
    '10-31-26.5.html',
    '10-31-26.6.html',
    '10-31-26.7.html',
    '11-02-26.1.html',
    '11-03-26.1.html',
    '11-03-26.2.html',
    '11-04-26.1.html',
    '11-04-26.10.html',
    '11-04-26.11.html',
    '11-04-26.12.html',
    '11-04-26.13.html',
    '11-04-26.2.html',
    '11-04-26.3.html',
    '11-04-26.4.html',
    '11-04-26.5.html',
    '11-04-26.6.html',
    '11-04-26.7.html',
    '11-04-26.8.html',
    '11-04-26.9.html',
    '11-05-26.1.html',
    '11-05-26.2.html',
    '11-05-26.3.html',
    '11-05-26.4.html',
    '11-05-26.5.html',
    '11-07-26.2.html',
    '11-08-26.1.html',
    'v32.html',
    'v33.html',
    'v34.html',
    'v35.html',
    'v36.html',
    'v37.html',
    'v38.html',
    'v39.html',
    'v40.html',
    'v41.html',
    'v42.html',
    'v43.html',
    'v44.html',
)
PINS = (
    (13, 'wikiDailyDice', 'https://ddowiki.com/page/Daily_Dice',
     'https://ddowiki.com/index.php?title=Daily_Dice&oldid=727165',
     '2026-11-05T12:53:21.155Z', '5db100e9dc28793dfaa8d189091f57d33b70689b7f13f73344ecd58e08136eae'),
    (14, 'wikiMastersGift', 'https://ddowiki.com/page/Item:The_Master%27s_Gift',
     'https://ddowiki.com/index.php?title=Item:The_Master%27s_Gift&oldid=681893',
     '2026-11-05T12:53:29.921Z', 'dcec90da4728483cb944be925a5c0590d8f8c47fc7aeeed3272e959ef1284460'),
)
BLOCK = re.compile(r'\n<div\b(?=[^>]*\bid="early-xp-options")[^>]*>.*?</div>\n', re.S)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source_facts(data, record):
    """Read the original retained page contexts, not a claim-ledger paraphrase."""
    require(len(record['sources']) == 2, 'two scoped observations')
    for receipt, (i, key, url, revision, captured, text_hash) in zip(record['sources'], PINS):
        page = data['pages'][i]
        require((page['evidenceKey'], page['url'], page['permanentLink'], page['capturedAt']) ==
                (key, url, revision, captured), 'source identity and genuine observation')
        require(sha(page['text'].encode()) == text_hash, 'complete captured page context')
        require((receipt['pointer'], receipt['evidence_key'], receipt['url'],
                 receipt['revision_url'], receipt['captured_at'], receipt['text_sha256']) ==
                (f'/pages/{i}', key, url, revision, captured, text_hash), 'excerpt provenance')
        excerpts = ([page['text'].split('\n\n')[3], page['text'].split('\n\n')[8],
                     page['text'].split('Silver[edit]\n', 1)[1].split('Roll\tRewards', 1)[0]]
                    if i == 13 else [page['text']])
        require(receipt['excerpts'] == excerpts, 'exact excerpts from source context')
    dice, gift = (data['pages'][i]['text'] for i in (13, 14))
    # Extract values from the real receipt; the corresponding Guide text below
    # is checked using these values, alongside all qualifying prose.
    silver = re.search(r'Each account gets a free roll on the Silver Chest loot table once per server every (\d+) hours', dice)
    require(silver and 'VIP players get a free roll on the Gold Chest once a week per server.' in dice,
            'account/server and VIP weekly eligibility')
    require('Free rolls can\'t be saved or accumulated;' in dice, 'free-roll accumulation excluded')
    require('The amount of experience depends on how well you roll.' in dice, 'variable yield')
    require('Doubleclick it to consume the token and gain the XP.' in dice and
            'These tokens are not affected by any bonus you may acquire elsewhere on XP gains.' in dice,
            'consumption and no external token XP bonus')
    level = re.search(r'Minimum Level\t(\d+)\t', gift)
    bonus = re.search(r'a \+(\d+)% (\w+) bonus to all earned Experience Points', gift)
    tokens = re.search(r'\((\d+)\) I:Greater Token of the Twelve', gift)
    require(level and bonus and tokens, 'Gift level, bonus and ingredient values')
    require('Augment Type\tColorless' in gift and 'Bind status\tBound to Account\u00a0on Acquire' in gift and
            'This augment can go in any color Augment Slot.' in gift, 'Gift type/binding/slot scope')
    require('Legacy Altar of Epic Rituals, The Twelve\n(5) I:Greater Token of the Twelve\n'
            '(1) I:Mantle of the Worldshaper\n(1) I:Voice of the Master' in gift, 'complete listed recipe')
    return {'hours': silver[1], 'level': level[1], 'percent': bonus[1], 'bonus_type': bonus[2],
            'tokens': tokens[1]}


def expected_paragraphs(facts):
    # Reviewed context is closed: additions cannot negate a correct excerpt.
    require(facts['tokens'] == '5', 'reviewed recipe quantity')
    return {
        'daily-dice-early-xp': (
            'Optional XP help for levels 1–3 build decision. Consider saving XP gems you receive from '
            'Daily Dice and using the ones you have toward levels 1–3; amounts vary by roll, so this does '
            'not promise a level skip. The Wiki lists free Silver rolls per account, per server every '
            f'{facts["hours"]} hours, and free Gold rolls weekly per server for VIPs. Unused free rolls cannot be '
            'saved or accumulated. This advice requires no paid rolls or VIP subscription. Double-click '
            'a token to consume it; XP bonuses, including The Master’s Gift, do not increase its XP.'),
        'masters-gift-optional': (
            'The Master’s Gift is a separate optional goal. If you already own or later earn it, the '
            f'Wiki lists this colorless augment as ML {facts["level"]}, Bound to Account on Acquire, '
            f'with a +{facts["percent"]}% {facts["bonus_type"]} bonus to earned XP, fitting any color '
            'Augment Slot. Use suitable gear you can equip. Newer players need not have it: the listed '
            'Legacy Altar of Epic Rituals recipe requires five Greater Tokens of the Twelve, a Mantle '
            'of the Worldshaper and a Voice of the Master.'),
        'early-xp-source-limits': ('Retained Wiki checks and limits '
                                  '(Wiki pages observed 5 November 2026; no new capture or in-game test).'),
    }


def excluded(node):
    return (node.tag in {'script', 'style', 'template'} or 'hidden' in node.attrs or 'inert' in node.attrs
            or node.attrs.get('aria-hidden', '').lower() == 'true'
            or re.search(r'(?:display\s*:\s*none|visibility\s*:\s*hidden)',
                         node.attrs.get('style', ''), re.I))


def visible_nodes(node):
    if excluded(node):
        return
    yield node
    for child in node.children:
        if isinstance(child, Node):
            yield from visible_nodes(child)


def visible_text(node):
    if excluded(node):
        return ''
    return ''.join(visible_text(c) if isinstance(c, Node) else c for c in node.children)


def guide_contract(html, facts):
    nodes = list(visible_nodes(Document(html).root))
    blocks = [n for n in nodes if n.attrs.get('id') == 'early-xp-options']
    require(len(blocks) == 1 and blocks[0].tag == 'div', 'one actual visible optional block')
    block_nodes = list(visible_nodes(blocks[0]))
    for ident, expected in expected_paragraphs(facts).items():
        matches = [n for n in block_nodes if n.attrs.get('id') == ident]
        require(len(matches) == 1 and matches[0].tag == 'p', 'one actual scoped paragraph: ' + ident)
        require(norm(visible_text(matches[0])) == expected, 'source-bound reviewed context: ' + ident)
    links = [n.attrs.get('href') for n in block_nodes if n.tag == 'a']
    require(links == [PINS[0][3], PINS[1][3], 'evidence/early-xp/index.html'], 'pinned source/limits links')
    require(len([n for n in block_nodes if n.tag == 'p']) == 3, 'no extra unreviewed paragraph')
    require(norm(visible_text(blocks[0])) == ' '.join(expected_paragraphs(facts).values()),
            'no extra unreviewed text outside the paragraphs')
    outside_topic_contract(html)


def outside_topic_contract(html):
    """Guard named XP-gem/Daily-Dice/Master’s Gift prose, including “the Gift”.

    This scans active text for bounded subjects, not general semantic claims. Release
    review separately proves the entire baseline page and protected files.
    """
    matches = list(BLOCK.finditer(html))
    require(len(matches) == 1, 'one complete new block')
    start = html.index('<p id="early-gear-coverage">')
    end = html.index('<div class="tw"><table>', start)
    require(start < matches[0].start() < matches[0].end() <= end, 'beside early coverage before table')
    doc = Document(html).root
    nodes = list(visible_nodes(doc))
    block = next(n for n in nodes if n.attrs.get('id') == 'early-xp-options')
    existing_gift_cell = ("Essence-crafted: Constitution, False Life, Insightful Constitution (ML10+), "
                          "slotted: The Master's Gift (XP); later Topaz of Vitality")
    gift_cells = [n for n in nodes if n.tag == 'td' and norm(visible_text(n)) == existing_gift_cell]
    require(len(gift_cells) == 2, 'two exact reviewed existing Gift selections')
    reviewed = {block, *gift_cells}

    # Default block/line boundaries separate words; inline elements do not.
    # This models document text structure, not CSS display overrides.
    boundaries = {'address', 'article', 'aside', 'blockquote', 'body', 'br', 'dd', 'details',
                  'dialog', 'div', 'dl', 'dt', 'fieldset', 'figcaption', 'figure', 'footer',
                  'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'hgroup', 'hr',
                  'li', 'main', 'nav', 'ol', 'p', 'pre', 'section', 'summary', 'table',
                  'tbody', 'td', 'tfoot', 'th', 'thead', 'tr', 'ul'}

    def outside_text(node):
        if node in reviewed:
            return ' '
        if excluded(node) or node.tag == 'head':
            return ''
        text = ''.join(outside_text(c) if isinstance(c, Node) else c for c in node.children)
        return ' ' + text + ' ' if node.tag in boundaries else text

    topic = re.compile(r"daily\s*dice|xp\s*(?:gems?|tokens?)|master[’']s\s+gift|\bthe\s+gift\b", re.I)
    require(not topic.search(norm(outside_text(doc))),
            'no unreviewed named topic in any active text outside the reviewed contexts')



def manifest(paths):
    return sha(''.join(f'{p.relative_to(ROOT).as_posix()}\t{sha(p.read_bytes())}\n'
                       for p in sorted(paths)).encode())


def notes_contract(html):
    nodes = list(visible_nodes(Document(html).root))
    mains = [n for n in nodes if n.tag == 'main']
    require(len(mains) == 1, 'one readable notes main')
    require(sha(norm(visible_text(mains[0])).encode()) == 'e170f929b5ef97cb0dfbf3ae9d4b5470676c5169ff221e3cea55334bb87773a1',
            'complete reviewed notes context and limitations')
    links = [n.attrs.get('href') for n in nodes if n.tag == 'a']
    require(links == ['../../index.html#early-xp-options', 'claims.json',
                     '../../tools/fixtures/endgame-evidence/fresh/wiki-live-audit-2026-11-05.json',
                     '../../tools/fixtures/endgame-evidence/fresh-provenance.json',
                     '../../tools/fixtures/endgame-evidence/public-redaction.json',
                     PINS[0][3], PINS[1][3], 'https://ddowiki.com/',
                     'https://creativecommons.org/licenses/by-sa/2.5/'], 'clickable notes evidence path')
    for href in links:
        target = urlsplit(href)
        if not target.scheme:
            local = (ROOT / 'evidence/early-xp' / target.path).resolve()
            require(local.is_file(), 'local evidence target exists')
            if target.fragment:
                require(any(n.attrs.get('id') == target.fragment
                            for n in visible_nodes(Document(local.read_text()).root)), 'backlink anchor')
    require(any(n.tag == 'html' and n.attrs.get('lang') == 'en' for n in nodes), 'notes language')
    require(any(n.tag == 'meta' and n.attrs.get('name') == 'viewport' for n in nodes), 'responsive viewport')


class EarlyXPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = SOURCE.read_bytes()
        cls.data = json.loads(cls.raw)
        cls.record = json.loads(RECORD.read_text())
        cls.html = (ROOT / 'index.html').read_text()
        cls.facts = source_facts(cls.data, cls.record)

    def test_original_receipt_identity_and_exact_excerpts(self):
        self.assertEqual(sha(self.raw), PUBLIC_SHA)
        self.assertEqual(len(self.raw), 281940)
        source_facts(self.data, self.record)
        provenance = json.loads((ROOT / self.record['provenance_file']).read_text())
        self.assertEqual(provenance['sha256'], PUBLIC_SHA)
        self.assertEqual(self.record['public_file_sha256'], PUBLIC_SHA)
        self.assertEqual(self.record['public_file_bytes'], provenance['bytes'])
        self.assertEqual(self.record['original_capture_sha256'], provenance['original_sha256'])
        self.assertEqual(self.record['original_capture_bytes'], provenance['original_bytes'])
        self.assertEqual(self.record['source_file'], SOURCE.relative_to(ROOT).as_posix())
        validate_public(self.record)

    def test_actual_guide_is_bound_to_source_and_qualifications(self):
        guide_contract(self.html, self.facts)

    def test_source_factual_and_context_mutations_fail(self):
        mutations = [(13, 'every 16 hours', 'every 24 hours'),
                     (13, 'once a week per server', 'once a day per character'),
                     (13, "Free rolls can't be saved", 'Free rolls can be saved'),
                     (13, 'not affected by any bonus', 'affected by every bonus'),
                     (13, 'depends on how well you roll', 'always reaches level 3'),
                     (14, 'Minimum Level\t1\t', 'Minimum Level\t5\t'),
                     (14, '+5% Enhancement', '+10% Insight'),
                     (14, 'any color Augment Slot', 'a special slot only'),
                     (14, '(5) I:Greater Token', '(1) I:Greater Token'),
                     (14, '(1) I:Voice of the Master', '(0) I:Voice of the Master')]
        for i, old, new in mutations:
            with self.subTest(old=old):
                data = copy.deepcopy(self.data)
                self.assertIn(old, data['pages'][i]['text'])
                data['pages'][i]['text'] = data['pages'][i]['text'].replace(old, new)
                with self.assertRaises(ValueError):
                    source_facts(data, self.record)
        data = copy.deepcopy(self.data)
        data['pages'][13]['text'] += '\nHowever, the Gift does multiply these tokens.'
        with self.assertRaises(ValueError):
            source_facts(data, self.record)

    def test_missing_forged_or_misbound_provenance_fails(self):
        for field, value in [('capturedAt', ''), ('capturedAt', '2026-11-08T00:00:00Z'),
                             ('permanentLink', PINS[1][3]), ('url', PINS[1][2]),
                             ('evidenceKey', 'wikiMastersGift')]:
            with self.subTest(field=field, value=value):
                data = copy.deepcopy(self.data)
                data['pages'][13][field] = value
                with self.assertRaises(ValueError):
                    source_facts(data, self.record)
        record = copy.deepcopy(self.record)
        record['sources'][0]['excerpts'][1] += ' Guaranteed enough for level 3.'
        with self.assertRaises(ValueError):
            source_facts(self.data, record)

    def test_actual_guide_eligibility_yield_and_bonus_mutations_fail(self):
        changes = [('toward levels 1–3', 'past levels 1–2'),
                   ('amounts vary by roll', 'each roll is enough'),
                   ('does not promise a level skip', 'guarantees a level skip'),
                   ('per account, per server', 'per character, per server'),
                   ('every 16 hours', 'every 24 hours'),
                   ('weekly per server for VIPs', 'daily per server for everyone'),
                   ('cannot be saved or accumulated', 'can be saved or accumulated'),
                   ('requires no paid rolls or VIP subscription', 'requires paid rolls and VIP'),
                   ('do not increase its XP', 'increase its XP by 5%'),
                   ('If you already own or later earn it', 'Everyone starts with it'),
                   ('as ML 1', 'as ML 3'), ('+5% Enhancement', '+5% Insight'),
                   ('five Greater Tokens', 'five Tokens'),
                   ('Newer players need not have it', 'Newer players must get it immediately')]
        for old, new in changes:
            with self.subTest(old=old):
                self.assertIn(old, self.html)
                with self.assertRaises(ValueError):
                    guide_contract(self.html.replace(old, new), self.facts)

    def test_missing_hidden_inert_and_duplicate_prose_fails(self):
        para = re.search(r'<p id="daily-dice-early-xp">.*?</p>', self.html)[0]
        block = BLOCK.search(self.html)[0]
        cases = [self.html.replace(para, ''), self.html.replace(para, '<!--' + para + '-->'),
                 self.html.replace(para, '<template>' + para + '</template>'),
                 self.html.replace(para, '<script type="text/plain">' + para + '</script>'),
                 self.html.replace(para, para.replace('<p ', '<p hidden ')),
                 self.html.replace(para, para.replace('<p ', '<p style="display:none" ')),
                 self.html.replace(para, para + para),
                 self.html.replace(block, '\n<div hidden>' + block + '</div>\n'),
                 self.html.replace('amounts vary by roll', '<span hidden>amounts vary by roll</span>')]
        for i, candidate in enumerate(cases):
            with self.subTest(case=i), self.assertRaises(ValueError):
                guide_contract(candidate, self.facts)

    def test_unsupported_additions_inside_and_outside_gate_fail(self):
        unsupported = ('Save XP gems forever across every reincarnation. ',
                       'The Master’s Gift increases Daily Dice token XP. ',
                       'Use the Gift in the Amethyst Loupe at level 1. ',
                       'XP gems guarantee maximum epic and Reaper XP. ')
        for claim in unsupported:
            cases = [self.html.replace('Consider saving', claim + 'Consider saving'),
                     self.html.replace('<div id="early-xp-options">', '<p>' + claim + '</p><div id="early-xp-options">'),
                     self.html.replace('</body>', '<p>' + claim + '</p></body>')]
            for i, candidate in enumerate(cases):
                with self.subTest(claim=claim, location=i), self.assertRaises(ValueError):
                    guide_contract(candidate, self.facts)

    def test_named_claim_cannot_escape_in_other_tags_or_bare_text(self):
        claim = 'The Master’s Gift boosts Daily Dice token XP.'
        for wrapper in ('<div>{}</div>', '<h5>{}</h5>', '<span>{}</span>', '{}'):
            with self.subTest(wrapper=wrapper), self.assertRaises(ValueError):
                guide_contract(self.html.replace('</body>', wrapper.format(claim) + '</body>'), self.facts)

    def test_adjacent_block_alias_and_inline_topic_splits_are_detected(self):
        fragments = (
            '<div>Another note</div><div>The Gift is available immediately to everyone.</div>',
            '<p>Another note</p><h4>The Gift is available immediately to everyone.</h4>',
            '<div>Another note</div>The Gift is available immediately to everyone.',
            '<div>Another note<br>The Gift is available immediately to everyone.</div>',
            '<div>The Gi<span>ft</span> is available immediately to everyone.</div>',
            '<div>The <em>Gift</em> is available immediately to everyone.</div>',
            '<div>XP <span>gems</span> guarantee a level skip.</div>',
            '<div>The Mas<em>ter</em>’s Gift boosts Daily Dice token XP.</div>',
        )
        for fragment in fragments:
            with self.subTest(fragment=fragment), self.assertRaises(ValueError):
                guide_contract(self.html.replace('</body>', fragment + '</body>'), self.facts)
        # Harmless inline splits in supported player prose preserve the words.
        guide_contract(self.html.replace('Daily Dice</a>', 'Da<span>ily</span> Dice</a>'), self.facts)

    def test_inline_markup_and_obsolete_commented_copy_are_allowed(self):
        para = re.search(r'<p id="daily-dice-early-xp">.*?</p>', self.html)[0]
        guide_contract(self.html.replace(para, '<!--' + para + '-->' + para)
                       .replace('amounts vary by roll', '<em>amounts vary by roll</em>'), self.facts)

    def test_preserves_original_56_snapshot_paths_and_bytes(self):
        # Pin named published history; later versions are welcome.
        snapshots = [ROOT / 'versions' / name for name in ORIGINAL_SNAPSHOTS]
        self.assertEqual(len(snapshots), 56)
        self.assertTrue(all(p.is_file() for p in snapshots))
        self.assertEqual(manifest(snapshots), '495fc9ab3d04aa70185f22a436aca6feefa04b185952d3fe35d298a5d8507c49')

    def test_scoped_guard_allows_future_build_stamp_and_unrelated_prose(self):
        candidate = self.html.replace('build 11-08-26.2', 'build 11-09-26.1')
        candidate = candidate.replace('Last updated 8 November 2026', 'Last updated 9 November 2026')
        candidate = candidate.replace('A Levelling Chassis That Can Run R10', 'An Intelligence Longbow Guide')
        candidate = candidate.replace('</body>', '<div>Future unrelated reading note.</div></body>')
        guide_contract(candidate, self.facts)

    def test_readable_notes_context_links_and_attribution(self):
        notes_contract((ROOT / 'evidence/early-xp/index.html').read_text())

    def test_notes_missing_caution_broken_links_and_unsupported_additions_fail(self):
        page = (ROOT / 'evidence/early-xp/index.html').read_text()
        changes = [('no guarantee', 'a guarantee'),
                   ('not evidence of easy or immediate access', 'proof of easy access'),
                   ('<main>', '<main hidden>'),
                   ('href="claims.json"', 'href="missing.json"'),
                   ('</main>', '<p>Gems last forever across lives.</p></main>')]
        for old, new in changes:
            with self.subTest(old=old), self.assertRaises(ValueError):
                notes_contract(page.replace(old, new))


if __name__ == '__main__':
    unittest.main()
