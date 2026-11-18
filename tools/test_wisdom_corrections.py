# Historical .2 contract: exact approved-checkpoint bytes/modules are explicit.
# New selected-recipe tests exercise production separately; no global imports patched.
"""Current correction semantics plus strict preservation of the prior draft.

These are source-fidelity/structure/regression checks, not browser or live-game
certification. Historical false statements may remain in immutable snapshots.
"""
import selected_recipe_preservation as selected_history
import copy
import json
from pathlib import Path
import re
import unittest

import stacking_audit as audit
audit = selected_history.historical_module('stacking_audit')
import wisdom_corrections as corrections
import wisdom_preservation as preservation
import wisdom_crafting_integration as crafting
from test_lamordia_handling import Document, norm


ROOT = selected_history.HistoricalPath(__file__).resolve().parents[1]
RECEIPT = ROOT / 'evidence/wisdom-loadout/corrections.json'
CLAUSES = {
    'current-doubleshot-explanation': (
        'Multiplies eligible hit damage', 'not independent extra arrows',
        'does not imply additional proc rolls',
        'Scaling is reduced above 200%', 'not a standalone DPS percentage'),
    'current-quicken-choice': (
        'Quicken Spell remains unselected', 'starting Wisdom 8',
        'actual Ranger level, total equipped Wisdom and prepared spells',
        'does not itself certify', 'No feat or spell selection changes'),
    'current-healing-context': (
        'Starting Wisdom 8 is not the final equipped score',
        'actual Ranger level, total equipped Wisdom and prepared spells',
        'not proof of usable or sufficient healing', 'No spell, feat or healing rotation'),
    'current-wisdom-will': (
        'not a permanently equipped −1 modifier', 'same-type overlaps',
        'only part of a multiclass character’s save', 'final Will remain unverified'),
    'current-will-response': (
        'complete class progressions, total equipped Wisdom modifier',
        'do not reuse a fixed −1 Wisdom modifier', 'does not certify the final Will save',
        'adds no new augment or selected ability'),
    'current-critical-assumptions': (
        'standard 20/x3 longbow', 'conditional arithmetic',
        'Every prerequisite, rank and weapon condition must apply',
        'not a measured character profile or an optimizer result'),
    'current-critical-profile': (
        'Conditional build arithmetic', 'applicable bow, selected feats',
        '16–18/x6 and 19–20/x8', 'not an observed character profile',
        'not an observed character profile or a critical-range gain from the new artifact'),
    'current-elasticity': (
        'natural 19 or 20', 'confirmed critical', 'not negated by fortification',
        'not guaranteed extra damage on one tenth',
        'does not add Elasticity to the selected Calamitous recipe'),
    'current-alacrity-summary': (
        'historical Haste-always-up model', 'assumed 15% baseline',
        '1.20/1.15 ≈ 1.0435', 'model arithmetic, not a measured attack-rate or sustained-DPS gain'),
}


def hidden(node):
    return (node.tag in {'script', 'style', 'template'} or 'hidden' in node.attrs
            or 'inert' in node.attrs or node.attrs.get('aria-hidden') == 'true'
            or bool(re.search(r'(?:display\s*:\s*none|visibility\s*:\s*hidden)',
                              node.attrs.get('style', ''), re.I)))


def visible_text(node):
    if hidden(node):
        return ''
    return ''.join(visible_text(c) if hasattr(c, 'tag') else c for c in node.children)


def prose_contract(html):
    def walk(node, blocked=False):
        blocked = blocked or hidden(node)
        yield node, not blocked
        for child in node.children:
            if hasattr(child, 'tag'):
                yield from walk(child, blocked)

    state = list(walk(Document(html).root))
    for identity, clauses in CLAUSES.items():
        found = [(n, live) for n, live in state if n.attrs.get('id') == identity]
        assert len(found) == 1 and found[0][1], ('unique non-hidden current explanation', identity)
        text = norm(visible_text(found[0][0]))
        for clause in clauses:
            assert clause in text, (identity, clause)
    return True


def annotation_contract(data):
    rows = {e['id']: e for e in data['non_total_effects']}
    required = {
        'yeenoghu-actions': ('Rage uses after resting', 'not Action Boost uses'),
        'yeenoghu-procs': ('Bloodrage — conditional proc', 'not permanent Ranged Power'),
        'yeenoghu-rams-might': ('Ram’s Might — permanent while equipped', 'overlap', 'none is added'),
        'glabrezu-actions': ('Action Boost', 'different resource', 'Rage uses'),
    }
    for identity, clauses in required.items():
        row = rows[identity]
        assert row['state'] == 'unknown' and row['sources'] == [], identity
        text = row['claim'] + ' ' + row['note']
        for clause in clauses:
            assert clause in text, (identity, clause)
    assert 'Action Boost' not in rows['yeenoghu-actions']['claim']
    assert 'Ram’s Might' not in rows['yeenoghu-procs']['claim']
    return True


class CurrentMechanicsCorrectionTests(unittest.TestCase):
    def setUp(self):
        self.html = (ROOT / 'index.html').read_text()

    def test_current_explanations_include_all_required_conditions(self):
        self.assertTrue(prose_contract(self.html))

    def test_each_missing_reverted_or_overclaimed_condition_is_rejected(self):
        for identity, clauses in CLAUSES.items():
            clause = clauses[-1]
            match = re.search(r'<(?P<tag>\w+)\b[^>]*id="' + identity
                              + r'"[^>]*>.*?</(?P=tag)>', self.html, re.S)
            self.assertIsNotNone(match, identity)
            block = match.group()
            self.assertIn(clause, norm(visible_text(Document(block).root)))
            # Clauses used here deliberately have no intervening HTML markup.
            self.assertIn(clause, block)
            mutant = self.html.replace(block, block.replace(clause, 'UNSUPPORTED UNCONDITIONAL CLAIM', 1), 1)
            self.assertNotEqual(mutant, self.html)
            with self.subTest(identity=identity), self.assertRaises(AssertionError):
                prose_contract(mutant)

    def test_hidden_missing_duplicate_or_inert_explanations_do_not_pass(self):
        for identity in CLAUSES:
            block = re.search(r'<(?P<tag>\w+)\b[^>]*id="' + identity
                              + r'"[^>]*>.*?</(?P=tag)>', self.html, re.S).group()
            replacements = ['', block + block, '<!--' + block + '-->']
            replacements += ['<' + wrapper + '>' + block + '</' + wrapper.split()[0] + '>'
                             for wrapper in ('div hidden', 'div inert', 'template',
                                             'div style="display:none"', 'div aria-hidden="true"')]
            for replacement in replacements:
                with self.subTest(identity=identity, replacement=replacement[:40]), self.assertRaises(AssertionError):
                    prose_contract(self.html.replace(block, replacement, 1))

    def test_unchanged_historical_errors_do_not_satisfy_current_explanations(self):
        original = corrections.original_file_text('index.html')
        with self.assertRaises(AssertionError):
            prose_contract(original)
        self.assertIn('Whole extra arrows', original)
        self.assertTrue(prose_contract(self.html))

    def test_current_resource_annotations_and_generated_audit_agree(self):
        import build_stacking_audit
        build_stacking_audit = selected_history.historical_module('build_stacking_audit')
        data = audit.load()
        self.assertTrue(annotation_contract(data))
        actual = (ROOT / 'endgame-stacking-audit.html').read_text()
        self.assertEqual(actual, build_stacking_audit.detail(data))
        for text in ('Major Anger +5 Rage uses after resting',
                     'Ram’s Might — permanent while equipped', 'Bloodrage — conditional proc'):
            self.assertIn(text, actual)
        self.assertNotIn('Major Anger +5 Action Boost uses', actual)

    def test_wrong_resource_permanence_or_evidence_promotion_is_rejected(self):
        for identity, field, replacement in (
            ('yeenoghu-actions', 'claim', 'Major Anger +5 Action Boost uses after resting'),
            ('yeenoghu-procs', 'claim', 'Bloodrage and Ram’s Might — permanent'),
            ('yeenoghu-rams-might', 'claim', 'Ram’s Might — conditional damage proc'),
            ('glabrezu-actions', 'note', 'Stacks with Major Anger for eight Action Boosts'),
            ('yeenoghu-actions', 'state', 'verified'),
        ):
            data = copy.deepcopy(audit.load())
            next(e for e in data['non_total_effects'] if e['id'] == identity)[field] = replacement
            with self.subTest(identity=identity, field=field), self.assertRaises(AssertionError):
                annotation_contract(data)

    def test_generated_affix_text_and_procurement_limits_are_not_stale(self):
        import wisdom_loadout
        wisdom_loadout = selected_history.historical_module('wisdom_loadout')
        data = wisdom_loadout.load()
        recipe = wisdom_loadout.render_recipe(data)
        onepage = wisdom_loadout.render_onepage_rows(data)
        self.assertIn('permanent while equipped; incremental ranged damage not credited', recipe)
        self.assertIn('Rage uses after resting, not Action Boost uses', recipe)
        self.assertNotIn('Ram&#x27;s Might — present; conditions apply', recipe)
        self.assertIn('Search policy excludes event/limited gear', onepage)
        self.assertIn('exact non-event procurement of Healing Amplification +63 remains unverified', onepage)
        self.assertIn('Optional ring DEX 13 is separate and provisional', onepage)
        self.assertEqual(wisdom_loadout.replace_blocks(self.html, data), self.html)


class CorrectionPreservationTests(unittest.TestCase):
    def test_exact_outer_and_inner_reversals_pass_independently_and_together(self):
        self.assertTrue(corrections.validate_full_reversal())
        self.assertTrue(preservation.validate_full_reversal())
        for path in preservation.REVIEWED_PATHS:
            original = (corrections.original_file_text(path) if path in corrections.REVIEWED_PATHS
                        else crafting.checkpoint_file_text(path))
            self.assertEqual(preservation.restore_wisdom_file(path, original),
                             preservation.predecessor_file_text(path))

    def test_outer_reversal_rejects_stale_mixed_duplicate_and_unrelated_content(self):
        scope = corrections.load_scope()
        for path in corrections.REVIEWED_PATHS:
            current = crafting.checkpoint_file_text(path)
            change = scope['files'][path]['reviewed_replacements'][0]
            mutants = [current + '\n', corrections.original_file_text(path),
                       current.replace(change['after'], change['before'], 1),
                       current.replace(change['after'], change['after'] * 2, 1)]
            for mutant in mutants:
                self.assertNotEqual(mutant, current)
                with self.subTest(path=path), self.assertRaises(AssertionError):
                    corrections.restore_file(path, mutant)

    def test_outer_fixed_predecessor_still_rejects_rehashed_extra_edit(self):
        path = 'index.html'
        current = crafting.checkpoint_file_text(path)
        mutant = current + '<p>Unapproved build change</p>'
        scope = copy.deepcopy(corrections.load_scope())
        scope['files'][path]['current_bytes'] = len(mutant.encode())
        scope['files'][path]['current_sha256'] = corrections.sha(mutant)
        with self.assertRaises(AssertionError):
            corrections.restore_file(path, mutant, scope=scope)

    def test_no_numeric_component_source_rule_or_other_annotation_changed(self):
        old = json.loads(corrections.original_file_text('tools/fixtures/endgame-stacking/ledger.json'))
        current = json.loads(crafting.checkpoint_file_text('tools/fixtures/endgame-stacking/ledger.json'))
        self.assertEqual({k: v for k, v in current.items() if k != 'non_total_effects'},
                         {k: v for k, v in old.items() if k != 'non_total_effects'})
        allowed = {'yeenoghu-actions', 'yeenoghu-procs', 'glabrezu-actions', 'yeenoghu-rams-might'}
        self.assertEqual([x for x in current['non_total_effects'] if x['id'] not in allowed],
                         [x for x in old['non_total_effects'] if x['id'] not in allowed])
        self.assertEqual(len(current['non_total_effects']), len(old['non_total_effects']) + 1)
        for before in old['non_total_effects']:
            after = next(e for e in current['non_total_effects'] if e['id'] == before['id'])
            self.assertEqual({k: v for k, v in before.items() if k not in {'claim', 'note'}},
                             {k: v for k, v in after.items() if k not in {'claim', 'note'}})

    def test_complete_calculator_results_are_identical_not_just_totals(self):
        old = json.loads(corrections.original_file_text('tools/fixtures/endgame-stacking/ledger.json'))
        current = json.loads(crafting.checkpoint_file_text('tools/fixtures/endgame-stacking/ledger.json'))
        families = sorted({(c['channel'], c['stat']) for c in old['components']})
        self.assertEqual(len(families), 38)
        for channel, stat in families:
            for active in ((), ('force',)):
                with self.subTest(channel=channel, stat=stat, active=active):
                    self.assertEqual(audit.subtotal(current, stat, channel=channel, active=active),
                                     audit.subtotal(old, stat, channel=channel, active=active))

    def test_original_manifest_sources_model_and_prior_draft_snapshot_are_unchanged(self):
        receipt = json.loads(RECEIPT.read_text())
        for path, expected in receipt['original_records_preserved'].items():
            # Only the approved later calculator extension is reversed here;
            # original receipts, models and snapshots remain literal bytes.
            raw = crafting.checkpoint_file_bytes(path)
            with self.subTest(path=path):
                self.assertEqual((len(raw), corrections.sha(raw)), (expected['bytes'], expected['sha256']))
        for path, digest in receipt['retained_sources_sha256'].items():
            with self.subTest(path=path):
                self.assertEqual(corrections.sha((ROOT / path).read_bytes()), digest)
        self.assertEqual(corrections.sha((ROOT / 'tools/fixtures/wisdom-loadout/selection.json').read_bytes()),
                         '8223bd8e25ed9dc4ad9454439ead42dfb693cc008d18d0ddfeb270d33863c37d')
        self.assertEqual(corrections.sha((ROOT / 'versions/11-15-26.1.html').read_bytes()),
                         '9dcc34e46b405d9917a713d14fb3b63f4b5b10c72284a9d516a95486df4cd17f')

    def test_correction_checkpoint_snapshot_is_generated_without_overwriting_prior_draft(self):
        import build_snapshot
        current = crafting.checkpoint_file_text('index.html')
        self.assertEqual(build_snapshot.current_build(current), '11-15-26.2')
        self.assertEqual((ROOT / 'versions/11-15-26.2.html').read_text(),
                         build_snapshot.snapshot_html(current))


class CorrectionEvidenceBoundaryTests(unittest.TestCase):
    def test_receipt_distinguishes_actual_initial_head_from_staged_pr_tree(self):
        receipt = json.loads(RECEIPT.read_text())
        startup = receipt['startup']
        self.assertEqual(startup['immutable_remote_parent_sha'], corrections.BASE_COMMIT)
        self.assertEqual(startup['actual_initial_staged_tree'], corrections.BASE_TREE)
        self.assertEqual(startup['actual_initial_local_head'], preservation.BASE_COMMIT)
        self.assertNotEqual(startup['actual_initial_local_head'], startup['immutable_remote_parent_sha'])
        self.assertEqual(startup['initial_staged_files'], 49)
        self.assertFalse(startup['initial_unstaged_changes'])
        self.assertEqual(receipt['baseline_tests']['tests'], 258)
        self.assertFalse(receipt['release_limits']['merge_authorized'])
        self.assertFalse(receipt['release_limits']['publication_authorized'])

    def test_retained_tooltips_support_distinctions_without_inventing_observations(self):
        receipt = json.loads(RECEIPT.read_text())
        claims = {c['id']: c for c in receipt['claims']}
        self.assertEqual(len(claims), 9)
        for identity, needed in (('major-anger', 'Rages'), ('rams-might', 'permanently')):
            source = claims[identity]['retained'][0]
            self.assertIsNone(source['original_observation'])
            self.assertEqual(source['revision'], '700306')
            value = json.loads((ROOT / source['path']).read_text())
            for part in source['pointer']:
                value = value[part]
            self.assertIn(needed, value)
        double = json.loads((ROOT / 'tools/fixtures/endgame-evidence/retained/Doubleshot.json').read_text())
        self.assertIn('719351', str(double['revision']))
        self.assertIn('extra damage with a single attack', double['text'])
        self.assertIn('50% past a soft cap of 200%', double['text'])

    def test_missing_casting_and_live_dps_evidence_stays_missing(self):
        receipt = json.loads(RECEIPT.read_text())
        casting = next(c for c in receipt['claims'] if c['id'] == 'wisdom-casting')
        self.assertEqual(casting['retained'], [])
        self.assertIn('unsupported absolute', casting['classification'])
        self.assertIn('No independently retained Ranger casting-threshold', casting['classification'])
        for key in ('new_optimizer_run', 'gear_or_priority_change', 'source_grade_promotion'):
            self.assertFalse(receipt['release_limits'][key])
        self.assertIn('no retry', receipt['release_limits']['browser_qa'].lower())


if __name__ == '__main__':
    unittest.main()
