"""Exact +22/ML36 Spot correction; relayed item evidence never qualifies a subtotal."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

import stacking_audit as audit
from build_stacking_audit import detail, summary
from test_lamordia_handling import Document, guide_content, guide_text, norm

ROOT = Path(__file__).resolve().parents[1]
SCOPE = json.loads((ROOT/'tools/fixtures/spot-diamond-type/scope.json').read_text())
BASELINE_SHA = '69baa7faf353d8e3164efb36689b269d8b015ca3065edf1528313080376dedc0'
LEDGER_SHA = 'ec1a1eab6301f39b1ed22c3051d6dc5defff95ed50722d1cbef449510ada99da'
RULE_PATH = ROOT/'tools/fixtures/endgame-evidence/retained/INTiana-DDO-Wiki-bonus-rules-01-evidence.json'
RULE_SHA = 'dfd4c246e04ace0dcf5ddcfad983f4e94fbbdd6192465237fd8ab083c0a90b6b'
ITEM_SHA = '50945611f39c1a9008ab2804fb9ddcb42b677516d0eacc2d25d8d1f9fb3c1a1b'
ITEM_QUOTE = 'Drag this augment into a slot to upgrade an item with a +22 Competence Bonus to the Spot skill. This augment can go in any color Augment Slot.'
SPOT_NOTE = 'Selected ML36 Diamond of Spot +22: Competence per transmitted own-item excerpt (recorded oldid 703902); original bytes and observation context unavailable here. State remains unknown and excluded from certified totals; acquisition unknown. Not a guaranteed final +22 skill change.'


def restore_spot_prose(html):
    assert len(SCOPE['reviewed_replacements']) == 7
    for change in reversed(SCOPE['reviewed_replacements'][1:]):
        assert html.count(change['after']) == 1, 'exact scoped Spot correction'
        html = html.replace(change['after'], change['before'])
    return html


def restore_spot_stamp(html):
    change = SCOPE['reviewed_replacements'][0]
    assert html.count(change['after']) == 1, 'one current build stamp'
    return html.replace(change['after'], change['before'])


def validate_current(html):
    assert SCOPE['baseline_commit'] == '6d98996cd7bab6e2e3e775b56527e1a6e393e0e3'
    assert SCOPE['baseline_index_sha256'] == BASELINE_SHA
    restored = restore_spot_prose(restore_spot_stamp(html))
    assert hashlib.sha256(restored.encode()).hexdigest() == BASELINE_SHA
    nodes = list(guide_content(Document(html).root))
    skills = [n for n in nodes if n.tag == 'p' and norm(guide_text(n)).startswith('Skill augments by level')]
    assert len(skills) == 1
    text = norm(guide_text(skills[0]))
    for clause in ('Diamond of Spot +22 (ML36)', '+22 Competence bonus',
                   'Multiple Competence bonuses to Spot do not add; only the highest applies.',
                   'does not classify other skill diamonds or levels',
                   'establish mixed-type stacking or promise a final +22 skill gain'):
        assert clause in text, clause
    current = norm(guide_text(Document(html).root))
    for clause in ('Spot +22 is a Competence source; it does not promise',
                   'Diamond of Spot +22 adds a Competence source.',
                   'Green (Colorless augment): Diamond of Spot +22 (Competence, ML36; acquisition unknown)',
                   'Spot +22 is a Competence source, not a guaranteed final skill gain.',
                   'the component remains unknown and excluded from subtotals'):
        assert clause in current, clause
    assert 'Spot +22 is an Enhancement source' not in current
    assert 'skill-diamond ladder by minimum level; enhancement bonus' not in current


def validate_sources(relay, raw, doc):
    # This checks the transmitted record, never a local copy of the original item capture.
    assert relay['evidence_kind'] == 'transmitted exact excerpt and reported original-file identity; not original bytes'
    assert relay['url'] == 'https://ddowiki.com/page/Item:Diamond_of_Spot_%2B22'
    assert relay['recorded_permalink'] == 'https://ddowiki.com/index.php?title=Item:Diamond_of_Spot_%2B22&oldid=703902'
    assert relay['reported_original_basename'] == 'wisdom-spot-diamond.browser.json'
    assert relay['reported_original_bytes'] == 674 and relay['reported_original_sha256'] == ITEM_SHA
    assert relay['reported_original_pointer'] == ['content', 0, 'text', '$json', 'text']
    assert relay['original_bytes_materialized_or_read_here'] is False
    assert relay['fresh_wiki_verification'] is False
    assert all(relay[k] is None for k in ('observed_at','observation_method','footer'))
    assert relay['exact_excerpts'] == ['Diamond of Spot +22','Minimum Level 36','Augment Type Colorless',ITEM_QUOTE]
    assert len(raw) == 64245 and hashlib.sha256(raw).hexdigest() == RULE_SHA
    receipt = json.loads(raw)['source_receipts']['artifact_competence_exceptional']
    source = receipt['sources'][1]
    assert source['observed_normal_url'] == 'https://ddowiki.com/page/Competence_bonus'
    paragraph = source['exact_source_sections'][0]['paragraphs'][1]
    assert 'skill checks' in paragraph
    assert "Multiple competence bonuses don't stack, only the highest bonus applies." in paragraph
    assert source['body_observation']['started_at_utc'] == '2026-11-02T05:38:42.604Z'
    assert source['body_observation']['completed_at_utc'] == '2026-11-02T05:38:48.175Z'
    metadata = source['revision_metadata']
    assert metadata['permanent_link'] == 'https://ddowiki.com/index.php?title=Competence_bonus&oldid=682593'
    assert metadata['permanent_link_observation_mark_utc'] == '2026-11-02T05:39:08.191Z'
    assert metadata['historical_endpoint_read'] is False
    assert metadata['earlier_body_bytes_independently_pinned'] is False
    for phrase in (ITEM_QUOTE, ITEM_SHA, RULE_SHA, 'not a local hash verification',
                   'original bytes were not\nmaterialized or read in this executor',
                   'time, observation method and footer/cache context are unavailable',
                   'no fresh Wiki verification or in-game test',
                   'normalized documentary receipt', 'historical endpoint was not\nopened',
                   'not establish Competence/Morale/Luck compatibility',
                   '`state=unknown`, an empty source\nlink'):
        assert phrase in doc, phrase


def validate_ledger(data):
    audit.validate(data)
    rows = [c for c in data['components'] if c['id'] == 'spot-diamond']
    assert len(rows) == 1
    expected = dict(SCOPE['prior_spot_component'], bonus_type='Competence', note=SPOT_NOTE)
    assert rows[0] == expected
    restored = copy.deepcopy(data)
    restored['components'][data['components'].index(rows[0])] = SCOPE['prior_spot_component']
    raw = (json.dumps(restored, ensure_ascii=False, indent=2)+'\n').encode()
    assert SCOPE['baseline_ledger_sha256'] == LEDGER_SHA
    assert hashlib.sha256(raw).hexdigest() == LEDGER_SHA
    for flags in ((), ('force',)):
        result = audit.subtotal(data, 'Spot', active=flags)
        assert result['total'] is None and result['complete'] is False
        assert result['counted'] == [] and result['excluded'] == ['spot-diamond']


class SpotDiamondTypeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT/'index.html').read_text()
        cls.doc = (ROOT/'evidence/spot-diamond-type/README.md').read_text()

    def test_exact_variant_current_claims_and_prior_release_preserved(self):
        validate_current(self.html)

    def test_wrong_type_amount_level_socket_scope_totals_and_hidden_claims_rejected(self):
        for before, after in (
            ('+22 Competence bonus','+22 Enhancement bonus'),
            ('Spot +22 (Competence, ML36','Spot +21 (Competence, ML36'),
            ('Spot +22 (Competence, ML36','Spot +22 (Competence, ML35'),
            ('Green (Colorless augment): Diamond of Spot +22','Colorless: Diamond of Spot +22'),
            ('does not classify other skill diamonds or levels','classifies all skill diamonds at every level'),
            ('only the highest applies.','all of them add together.'),
            ('not a guaranteed final skill gain','a guaranteed final +22 skill gain'),
            ('remains unknown and excluded from subtotals','is verified and yields a Spot subtotal of 29'),
            ('<p><strong>Skill augments by level','<p hidden><strong>Skill augments by level'),
            ('<td>Maximum (23)</td>','<td>Maximum (22)</td>'),
            ('<td>Legendary Abyssal Compass</td>','<td>Different gear</td>'),
        ):
            self.assertIn(before, self.html)
            with self.subTest(before=before), self.assertRaises(AssertionError):
                validate_current(self.html.replace(before, after))

    def test_actual_rule_and_transmitted_item_provenance(self):
        validate_sources(SCOPE['item_relay'], RULE_PATH.read_bytes(), self.doc)

    def test_source_corruption_and_provenance_upgrades_rejected(self):
        raw = RULE_PATH.read_bytes()
        for key, value in (('original_bytes_materialized_or_read_here', True),
                           ('fresh_wiki_verification', True), ('observed_at', '2026-11-09'),
                           ('observation_method', 'fresh browser'), ('footer', 'fresh today'),
                           ('reported_original_bytes', 675), ('reported_original_sha256', '0'*64),
                           ('recorded_permalink', 'https://ddowiki.com/?oldid=1'),
                           ('exact_excerpts', ['All diamonds grant Competence'])):
            relay = dict(SCOPE['item_relay'], **{key:value})
            with self.subTest(key=key), self.assertRaises(AssertionError):
                validate_sources(relay, raw, self.doc)
        with self.assertRaises(AssertionError):
            validate_sources(SCOPE['item_relay'], raw.replace(b"don't stack", b'do stack'), self.doc)
        with self.assertRaises(AssertionError):
            validate_sources(SCOPE['item_relay'], raw, self.doc.replace('not a local hash verification', 'locally verified original bytes'))

    def test_ledger_retains_unknown_gates_and_all_other_data(self):
        data = audit.load()
        validate_ledger(data)
        spot = next(c for c in data['components'] if c['id'] == 'spot-diamond')
        for other_type in ('Morale', 'Luck'):
            other = dict(spot, bonus_type=other_type)
            self.assertIsNone(audit.proof(data, 'Spot', spot, other))
        for field, value in (('bonus_type','Enhancement'), ('amount',23), ('state','verified'),
                             ('source','artifact'), ('kit_min_level',35), ('type_evidence','Competence')):
            changed = copy.deepcopy(data)
            next(c for c in changed['components'] if c['id'] == 'spot-diamond')[field] = value
            with self.subTest(field=field), self.assertRaises((AssertionError,KeyError)):
                validate_ledger(changed)
        changed = copy.deepcopy(data)
        changed['components'][0]['amount'] += 1
        with self.assertRaises(AssertionError):
            validate_ledger(changed)

    def test_generated_current_audit_and_documentation_agree(self):
        data = audit.load()
        rendered = detail(data)
        self.assertEqual((ROOT/'endgame-stacking-audit.html').read_text(), rendered)
        self.assertIn('Spot +22 is a Competence source', summary(data))
        nodes = list(guide_content(Document(rendered).root))
        rows = [n for n in nodes if n.tag == 'tr' and n.attrs.get('id') == 'component-spot-diamond']
        self.assertEqual(len(rows), 1)
        text = norm(guide_text(rows[0]))
        for phrase in ('22 Competence', 'unknown', 'source missing', SPOT_NOTE):
            self.assertIn(phrase, text)
        doc = (ROOT/'docs/knowledge-base/A-074-QUEEN-BASIC.md').read_text()
        self.assertIn('+22 Competence Spot source', doc)
        self.assertIn('add Spot 22 Competence source', doc)
        self.assertIn('reported study and modeled values\nare unchanged', doc)


if __name__ == '__main__':
    unittest.main()
