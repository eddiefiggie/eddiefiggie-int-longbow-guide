# Historical .2 contract: exact approved-checkpoint bytes/modules are explicit.
# New selected-recipe tests exercise production separately; no global imports patched.
"""Current offensive claim boundaries on actual production files.

These tests distinguish source-supported conditions and safe arithmetic from
the preserved historical model. They do not certify live-game timing or DPS.
"""
import selected_recipe_preservation as selected_history
import copy
import json
from pathlib import Path
import re
import unittest

import bowmodel
import build_stacking_audit
build_stacking_audit = selected_history.historical_module('build_stacking_audit')
import stacking_audit as audit
audit = selected_history.historical_module('stacking_audit')
import wisdom_loadout
wisdom_loadout = selected_history.historical_module('wisdom_loadout')
import wisdom_offense_preservation as preservation
import wisdom_chains_type_preservation as chains_type
from build_snapshot import current_build, snapshot_html
from test_editorial_consistency import GuideText
from test_lamordia_handling import Document, norm
from test_score_explanation import ScoreNoteDocument
from test_wisdom_corrections import hidden, visible_text
from test_wisdom_loadout import current_render_contract


ROOT = selected_history.HistoricalPath(__file__).resolve().parents[1]
SOURCE_PACKET = 'evidence/wisdom-loadout/offensive-sources-2026-11-15.json'
MECHANICS_PACKET = 'evidence/wisdom-loadout/offensive-mechanics-2026-11-15.json'
SOURCE_SHA = '58479bff309e52e0227f92631a9ce178cfd23a38659ddbcf466b804dc77a7dcd'
MECHANICS_SHA = '3b0159c1d989d4f73b3902149f1361b7b91d7c0bb396519625dfc9a05234d4e1'
CURRENT_SCORE_TEXT = (
    'Reading the scores: each comparison sets its highest modeled result to 100. '
    'Other scores are relative to that same row: 75 means approximately three quarters '
    'of its highest historical speed-adjusted comparison score under the assumptions above. '
    'The table summarizes with approximate whole-number scores; the model script '
    'prints percentages to one decimal place. Rounding can make unequal results look tied. '
    'These are not DPS figures, and scores in different level rows are not comparable.')


def states(html):
    def walk(node, blocked=False):
        blocked = (blocked or hidden(node) or node.tag == 'details' and 'open' not in node.attrs
                   or 'tooltip' in node.attrs.get('class', '').split())
        yield node, not blocked
        for child in node.children:
            if hasattr(child, 'tag'):
                yield from walk(child, blocked)

    return list(walk(Document(html).root))


def unique_live(html, predicate, label):
    matches = [(node, live) for node, live in states(html) if predicate(node)]
    assert len(matches) == 1 and matches[0][1], ('one visible current claim', label)
    return matches[0][0]


def claim(html, identity):
    node = unique_live(html, lambda n: n.attrs.get('id') == identity, identity)
    return norm(visible_text(node)), node


def cells(node):
    return [norm(visible_text(c)) for c in node.children
            if hasattr(c, 'tag') and c.tag in {'td', 'th'}]


def require_clauses(text, clauses):
    for clause in clauses:
        assert clause in text, clause


def score_contract(html):
    text, _ = claim(html, 'bow-model-score-scale')
    assert text == CURRENT_SCORE_TEXT, 'current score units, normalization and limits'
    notes = ScoreNoteDocument(html).notes
    assert len(notes) == 1 and notes[0]['closed'], 'one closed score paragraph'
    assert notes[0]['section'] == 'bow-damage-model' and notes[0]['before_table'], 'score note before model table'
    scope, _ = claim(html, 'historical-bow-score-scope')
    require_clauses(scope, ('historical speed-adjusted comparison score', 'representative evaluated levels',
                            'neither a complete expected-damage-per-attack calculation nor calibrated DPS',
                            'does not simulate the current Wisdom loadout', 'minimum level separately'))
    omissions, node = claim(html, 'historical-bow-model-omissions')
    require_clauses(omissions, ('no explicit Seeker input or Combat Archery +1[W] term',
                                'different dice', 'no complete hit/AC, confirmation, fortification, dodge or concealment',
                                'full normal damage to every nonthreat d20 outcome',
                                'imbue, rider, sneak, proc and active-rotation channels',
                                'engine and stored results have not been changed'))
    assert MECHANICS_PACKET in {a.attrs.get('href') for a in node.nodes('a')}


def ability_contract(html):
    node = unique_live(html, lambda n: n.tag == 'p' and norm(visible_text(n)).startswith('Why the plan looks like this.'),
                       'selected past-life rationale')
    text = norm(visible_text(node))
    require_clauses(text, ('+1 INT modifier contributes +1 to hit and +2 ability-based bow damage',
                           'once both Precise Shot and Improved Precise Shot are acquired',
                           'separate +50% passive contributions stack',
                           'Know the Angles supplies its own conditional Insight bonus and is not doubled'))
    links = {a.attrs.get('href') for a in node.nodes('a')}
    assert {'https://ddowiki.com/page/Precise_Shot', 'https://ddowiki.com/page/Improved_Precise_Shot',
            'https://ddowiki.com/page/Harper_Agent_enhancements'} <= links
    row = unique_live(html, lambda n: n.tag == 'tr' and cells(n)[:1] == ['Selected damage inputs'],
                      'selected damage arithmetic')
    parts = cells(row)
    assert len(parts) == 3
    values = re.search(r'Ranger \+(\d+) ranged, Monk \+(\d+), Enchant Weapon \+(\d+), '
                       r'\+(\d+) Intelligence modifier at x(\d+) \(\+(\d+)', parts[1])
    assert values, 'named ordinary weapon contributions'
    ranger, monk, enchantment, intelligence, multiplier, ability = map(int, values.groups())
    assert (ranger, monk, enchantment, intelligence, multiplier) == (6, 3, 3, 2, 2)
    assert ability == intelligence * multiplier
    sneak = re.search(r'Dark Hunter \+(\d+) and Rogue \+(\d+) on eligible sneak attacks', parts[1])
    assert sneak, 'conditional sneak contributions'
    derived = re.search(r'Derived \+(\d+) eligible weapon damage, or \+(\d+) including the listed sneak additions', parts[2])
    assert derived, 'derived current illustration'
    ordinary = ranger + monk + enchantment + ability
    assert tuple(map(int, derived.groups())) == (ordinary, ordinary + sum(map(int, sneak.groups()))) == (16, 22)
    require_clauses(' '.join(parts), ('once Precise Shot and Improved Precise Shot are both acquired',
                                     'before other scaling and target defenses',
                                     'Know the Angles is a separate active Insight bonus'))


def flaming_contract(html):
    text, node = claim(html, 'flaming-dice-progression')
    require_clauses(text, ('at level 30', '4d6 Fire while Chaotic or 2d6 otherwise',
                           'one base die, one from Scion, and two from Harbinger only while Chaotic',
                           'Emerald of Arcane Empowerment', 'ML34 Coldlight Runners host is equipped',
                           '5d6 / 3d6', 'complete filled outfit still requires level 36',
                           '100% Fire Spell Power', 'eligible damage is multiplied by Doubleshot',
                           'active toggle, a qualifying hit, alignment, equipped bonuses and the target’s defenses',
                           'not a current-kit damage result'))
    assert {'https://ddowiki.com/page/Arcane_Archer_enhancements',
            'https://ddowiki.com/page/Item:Emerald_of_Arcane_Empowerment', MECHANICS_PACKET} <= {
                a.attrs.get('href') for a in node.nodes('a')}
    rows = [(cells(n), live) for n, live in states(html) if n.tag == 'tr'
            and cells(n)[:1] == ['Flaming Arrows and Morphic Arrows']]
    assert len(rows) == 1 and rows[0][1], 'one current toggle recap'
    require_clauses(' '.join(rows[0][0]), ('5d6 Fire while Chaotic / 3d6 otherwise',
                                         'selected Emerald-bearing ML34 boots equipped',
                                         'baseline at 30 is 4d6 / 2d6', 'Full outfit ML36',
                                         'subject to hit and target conditions'))


def speed_contract(html):
    text, node = claim(html, 'current-alacrity-baseline')
    require_clauses(text, ('Enhancement speed bonus', '15% Enhancement attack-speed bonus',
                           'Shadow Striker’s 20% Enhancement Ranged Alacrity',
                           'Another 20% bonus of that type on a bow adds no speed while that armor is equipped',
                           'historical model assumes a 15% Haste baseline', '1.20/1.15 ≈ 1.0435',
                           'about +4.35%', 'not a measured current-kit attack-rate gain',
                           'BAB, animations, boosts and Patience'))
    assert {'https://ddowiki.com/page/Ranged_Alacrity', 'https://ddowiki.com/page/Haste',
            'https://ddowiki.com/page/Shadow_Striker'} <= {a.attrs.get('href') for a in node.nodes('a')}
    doubled, _ = claim(html, 'current-doubleshot-explanation')
    require_clauses(doubled, ('Multiplies eligible hit damage', 'not independent extra arrows',
                             'does not imply additional proc rolls', 'Scaling is reduced above 200%',
                             'not a standalone DPS percentage'))
    row = unique_live(html, lambda n: n.tag == 'tr' and '2.15/2.09' in ' '.join(cells(n)),
                      'historical six-point Doubleshot example')
    require_clauses(' '.join(cells(row)), ('historical assumed 109% to 115% pool', 'about 2.87%',
                                         'expected Doubleshot-eligible damage', 'below the 200% threshold',
                                         'not extra independent shots or a certified current total'))


def current_flat_damage_reasoning(html):
    def walk(node, archived=False):
        archived = archived or node.attrs.get('id') in {'endgame-historical-notes', 'optimizer-historical-notes'}
        if hidden(node) or archived:
            return
        if node.tag in {'p', 'li', 'td'}:
            text = norm(visible_text(node)).lower()
            assert 'flat damage is near zero' not in text, 'obsolete current R10 rationale'
        for child in node.children:
            if hasattr(child, 'tag'):
                yield from walk(child, archived)
        yield node

    list(walk(Document(html).root))


def evidence_contract(source, mechanics):
    assert source['record_type'] == 'scoped-offensive-source-observation-register'
    assert mechanics['record_type'] == 'scoped-offensive-mechanics-claim-inventory'
    assert source['schema_version'] == mechanics['schema_version'] == 1
    assert source['review_boundary'] == mechanics['review_boundary']
    boundary = source['review_boundary']
    assert boundary['reviewed_remote_head'] == preservation.BASE_COMMIT
    assert boundary['reviewed_tree'] == preservation.BASE_TREE
    assert boundary['branch'] == 'feat/wisdom-loadout-priorities' and boundary['pull_request'] == 47
    provenance = source['provenance']
    assert provenance['record_kind'] == 'transcribed observation summaries and paraphrases'
    for key in ('raw_dom_capture_included', 'exact_quotation_claimed', 'cryptographic_browser_capture_binding',
                'independently_reopened_revision_urls', 'retained_source_metadata_repaired', 'new_component_qualification'):
        assert provenance[key] is False, key
    require_clauses(provenance['publisher_limit'], ('no per-page capture timestamps or raw text', 'none are invented'))
    assert mechanics['source_packet']['path'] == SOURCE_PACKET
    assert mechanics['source_packet']['sha256'] == SOURCE_SHA
    assert 'not raw browser-capture authentication' in mechanics['source_packet']['hash_scope']
    wiki, publisher, repository = source['wiki_observations'], source['publisher_sources'], source['repository_sources']
    assert (len(wiki), len(publisher), len(repository)) == (27, 8, 11)
    identities = [row['id'] for row in wiki + publisher + repository]
    assert len(identities) == len(set(identities)) == 46
    assert all(set(row) == {'id', 'title', 'url'} for row in publisher), 'no invented publisher capture metadata'
    assert all(row['new_external_observation'] is False for row in repository)
    assert all((ROOT / row['path']).is_file() for row in repository)
    claims = mechanics['claims']
    expected = {f'{prefix}-{number:02}' for prefix, count in (('CRIT', 13), ('SPD', 12), ('DMG', 12))
                for number in range(1, count + 1)}
    assert len(claims) == 37 and {row['id'] for row in claims} == expected
    assert mechanics['coverage']['review_groups'] == {'critical': 13, 'speed': 12, 'damage': 12}
    for key in ('records_are_unique_proven_errors', 'full_guide_mechanics_inventory_complete',
                'full_dps_validated', 'whole_character_totals_certified'):
        assert mechanics['coverage'][key] is False, key
    for row in claims:
        assert row['source_ids'] and set(row['source_ids']) <= set(identities), row['id']
        assert row['applicability'] and row['limitations'] and row['repository_locations'], row['id']
        assert row['new_formal_ledger_qualification'] is False, row['id']
    current = mechanics['current_text_contract']
    ability = current['ability_damage']
    assert set(ability['source_ids']) == {'harper', 'precise-shot', 'improved-precise-shot', 'u734', 'u76', 'u45'}
    assert ability['ordinary_ability_modifier_factor_after_both_feats'] == sum(ability['arithmetic_terms']) == 2
    assert ability['arithmetic_terms'] == [1, .5, .5]
    assert ability['required_feats'] == ['Precise Shot', 'Improved Precise Shot']
    assert ability['active_ips_stance_required_for_passive_increment'] is False
    assert ability['know_the_angles_is_separate'] is True
    assert ability['whole_character_damage_certified'] is False
    imbue = current['imbue']
    assert (imbue['base_die'], imbue['power'], imbue['power_scaling_percent']) == ('1d6', 'Fire Spell Power', 100)
    assert {'u62', 'u63', 'repo-coldlight-host'} <= set(imbue['source_ids'])
    assert imbue['unconditional_fixed_damage_per_arrow_supported'] is False
    scenarios = mechanics['named_imbue_scenarios']
    rows = {row['id']: row for row in scenarios['scenarios']}
    first, equipped = rows['level-30-feat-and-tree'], rows['selected-emerald-equipped']
    assert (first['level'], first['emerald_equipped'], first['chaotic_dice'], first['nonchaotic_dice']) == (30, False, 4, 2)
    assert (equipped['minimum_host_level'], equipped['emerald_equipped'], equipped['chaotic_dice'],
            equipped['nonchaotic_dice']) == (34, True, 5, 3)
    emerald = next(row for row in scenarios['contributions'] if row['id'] == 'emerald-equipped')
    assert (emerald['dice'], emerald['augment_minimum_level'], emerald['host_minimum_level'],
            emerald['host']) == (1, 28, 34, 'Legendary Coldlight Runners')
    assert 'same-type Emerald variants do not add' in emerald['condition']
    assert scenarios['full_selected_outfit_minimum_level'] == 36
    assert scenarios['selected_crooked_touch'] == 'Whirling Wrists 3'
    assert scenarios['unselected_alternative_not_counted'] == 'Flickering Fingers'
    combustion = current['combustion_applicability']
    assert (combustion['selected_gear_amount'], combustion['bonus_type'], combustion['power']) == (142, 'Equipment', 'Fire Spell Power')
    assert combustion['applies_to_selected_flaming'] is True
    assert combustion['full_character_spell_power_or_dps_certified'] is False
    assert combustion['formal_ledger_qualification_changed'] is False
    for key in ('calibrated_dps', 'current_loadout_simulation', 'item_level_eligibility_certified', 'replacement_ranking_derived'):
        assert current['historical_model'][key] is False
    assert current['historical_model']['label'] == 'historical speed-adjusted comparison score'
    for key, value in mechanics['preservation_boundary'].items():
        if isinstance(value, bool):
            assert value is False, key


class CurrentOffensiveClaimsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / 'index.html').read_text()

    def test_actual_outputs_match_current_generators_and_new_snapshot(self):
        self.assertEqual(current_build(self.html), '11-16-26.2')
        self.assertEqual(Path(wisdom_loadout.__file__).resolve(), ROOT / 'tools/wisdom_loadout.py')
        self.assertEqual(Path(build_stacking_audit.__file__).resolve(), ROOT / 'tools/build_stacking_audit.py')
        data = wisdom_loadout.load()
        self.assertTrue(current_render_contract(self.html, data))
        self.assertTrue(build_stacking_audit.validate_guide(self.html, audit.load()))
        self.assertEqual((ROOT / 'endgame-stacking-audit.html').read_text(), build_stacking_audit.detail(audit.load()))
        self.assertEqual((ROOT / 'versions/11-16-26.2.html').read_text(), snapshot_html(self.html))
        self.assertEqual(wisdom_loadout.validate(data)['claim_count'], 130)
        self.assertEqual(len(data['query']['targets']), 32)

    def test_current_score_units_limits_and_displayed_scores_are_preserved(self):
        score_contract(self.html)
        current = GuideText(self.html).tables['bow-damage-model']
        previous = GuideText(preservation.checkpoint_file_text('index.html')).tables['bow-damage-model']
        self.assertEqual(len(current), 1)
        self.assertEqual(len(current[0]), 9)
        # Labels and explanations change, but all displayed result/name cells
        # retain their complete historical values.
        self.assertEqual([row[1:3] for row in current[0][1:]], [row[1:3] for row in previous[0][1:]])

    def test_score_note_rejects_wrong_units_normalization_and_false_certainty(self):
        for old, new in (
                ('to 100', 'to 1000'), ('same row', 'all rows'), ('three quarters', 'one quarter'),
                ('one decimal place', 'two decimal places'), ('not DPS figures', 'DPS figures'),
                ('are not comparable', 'are comparable'),
                ('can make unequal results look tied', 'proves equal results'),
                ('highest historical speed-adjusted comparison score', 'highest expected per-attack damage')):
            with self.subTest(old=old):
                self.assertIn(old, self.html)
                with self.assertRaises(AssertionError):
                    score_contract(self.html.replace(old, new))

    def test_current_score_note_cannot_be_hidden_duplicated_or_moved(self):
        note = re.search(r'<p id="bow-model-score-scale">.*?</p>', self.html, re.S)[0]
        without = self.html.replace(note, '')
        table_end = without.index('</table>', without.index('<h3 id="bow-damage-model">')) + len('</table>')
        cases = {
            'comment': self.html.replace(note, '<!--' + note + '-->'),
            'script': self.html.replace(note, '<script type="text/plain">' + note + '</script>'),
            'template': self.html.replace(note, '<template>' + note + '</template>'),
            'hidden': self.html.replace(note, '<div hidden>' + note + '</div>'),
            'style': self.html.replace(note, '<div style="display:none">' + note + '</div>'),
            'duplicate': self.html.replace(note, note + note),
            'wrong section': without.replace('<h3 id="bow-damage-model">', note + '<h3 id="bow-damage-model">'),
            'after table': without[:table_end] + note + without[table_end:],
        }
        for label, mutant in cases.items():
            with self.subTest(case=label), self.assertRaises(AssertionError):
                score_contract(mutant)
        score_contract(self.html.replace(note, '<!--' + note + '-->' + note))
        score_contract(self.html.replace('id="bow-model-score-scale"', 'class="note" id="bow-model-score-scale"')
                       .replace('Other scores', '<em>Other</em> scores'))

    def test_current_ability_rationale_and_16_22_arithmetic(self):
        ability_contract(self.html)
        for old, new in (('+2 ability-based bow damage', '+1.5 ability-based bow damage'),
                         ('once both Precise Shot and Improved Precise Shot are acquired', 'at every level'),
                         ('Derived +16 eligible weapon damage', 'Derived +15 eligible weapon damage'),
                         ('or +22 including the listed sneak additions', 'or +21 including the listed sneak additions'),
                         ('and is not doubled', 'and is doubled')):
            with self.subTest(old=old):
                self.assertIn(old, self.html)
                with self.assertRaises(AssertionError):
                    ability_contract(self.html.replace(old, new))

    def test_current_flaming_counts_keep_the_feat_alignment_and_host_boundaries(self):
        flaming_contract(self.html)
        selected = wisdom_loadout.load()
        boots = next(i for i in selected['items'] if i['id'] == 'Legendary Coldlight Runners')
        emeralds = [(i['id'], socket['fill']) for i in selected['items'] for socket in i['sockets']
                    if socket.get('fill', {}).get('id') == 'Emerald of Arcane Empowerment']
        self.assertEqual(len(emeralds), 1)
        self.assertEqual(emeralds[0][0], boots['id'])
        self.assertEqual(boots['filled_ml'], 34)
        self.assertNotIn('Flickering Fingers', json.dumps(selected['items']))
        for old, new in (('ML34 Coldlight Runners host is equipped', 'ML28 augment is owned'),
                         ('5d6 / 3d6', '4d6 / 2d6'), ('only while Chaotic', 'for every alignment'),
                         ('100% Fire Spell Power', '75% Fire Spell Power')):
            with self.subTest(old=old), self.assertRaises(AssertionError):
                flaming_contract(self.html.replace(old, new))

    def test_current_speed_and_doubleshot_semantics_do_not_create_extra_rolls(self):
        speed_contract(self.html)
        self.assertAlmostEqual((1.20 / 1.15 - 1) * 100, 4.34782608695652)
        self.assertAlmostEqual((2.15 / 2.09 - 1) * 100, 2.87081339712919)
        # Check the relevant soft-cap seam without changing the retained model.
        self.assertEqual([audit.doubleshot_effective(value) for value in (109, 115, 200, 201, 300)],
                         [109, 115, 200, 200.5, 250])
        self.assertTrue(all(bowmodel.DSPOOL[level] + bow[8] < 2
                            for level, bows in bowmodel.BANDS.items() for _, bow in bows))
        for old, new in (('adds no speed while that armor is equipped', 'adds 4.35% speed while that armor is equipped'),
                         ('does not imply additional proc rolls', 'grants additional proc rolls'),
                         ('expected Doubleshot-eligible damage', 'independent shots')):
            with self.subTest(old=old), self.assertRaises(AssertionError):
                speed_contract(self.html.replace(old, new))

    def test_feywild_and_representative_levels_do_not_imply_early_acquisition(self):
        profile, _ = claim(self.html, 'current-critical-profile')
        require_clauses(profile, ('Conditional build arithmetic', '16–18/x6 and 19–20/x8',
                                  'not an observed character profile', 'Feywild Attunement at 15',
                                  'Combat Archery at 21', 'Patience at 27', 'Lore of the Hunt at 30'))
        guide = GuideText(self.html)
        table = guide.tables['bow-damage-model'][0]
        labels = [row[0] for row in table[1:]]
        self.assertTrue(all('evaluated at' in label for label in labels))
        self.assertIn('selected Feywild arrives at 15', labels[2])
        self.assertIn('Combat Archery arrives at 21', labels[3])
        self.assertIn('Patience changes the profile at 27', labels[4])
        self.assertIn('Lore of the Hunt arrives at 30', labels[5])
        self.assertIn('enforce each item’s minimum level separately', labels[-1])
        historical = ' '.join(guide.blocks['bow-damage-model'])
        require_clauses(historical, ('level-8 case therefore requires an outside Haste source',
                                     'selected SLA arrives at 10'))

    def test_point_eight_combustion_language_keeps_the_separate_damage_channels(self):
        calculator = selected_history.checkpoint_module(chains_type, 'stacking_audit')
        recipe = selected_history.checkpoint_module(chains_type, 'wisdom_loadout')
        renderer = selected_history.checkpoint_module(chains_type, 'build_stacking_audit')
        ledger = calculator.load()
        for html in (chains_type.checkpoint_file_text('index.html'),
                     chains_type.checkpoint_file_text('endgame-stacking-audit.html'),
                     recipe.render_crafting_qualification(ledger), renderer.summary(ledger)):
            text = norm(Document(html).root.text())
            require_clauses(text, ('142 is a selected-gear Fire Spell Power contribution',
                                   'applicability to the selected Arcane Archer Flaming imbue while active',
                                   'overlapping Equipment Spell Power can reduce its marginal benefit',
                                   'not weapon damage, full-character Spell Power or DPS',
                                   'does not establish scaling for Melancholic or Dolorous weapon effects',
                                   'Chains Fortification and Spot remain excluded'))
        self.assertEqual(calculator.subtotal(ledger, 'Combustion')['total'], 142)
        self.assertEqual(calculator.subtotal(ledger, 'Intelligence')['total'], 37)
        self.assertEqual(calculator.subtotal(ledger, 'Doubleshot')['total'], None)

    def test_current_combustion_keeps_the_unchanged_damage_channel_limits(self):
        ledger = audit.load()
        for html in (self.html, (ROOT / 'endgame-stacking-audit.html').read_text(),
                     wisdom_loadout.render_crafting_qualification(ledger),
                     build_stacking_audit.summary(ledger)):
            require_clauses(norm(Document(html).root.text()), (
                '142 is a selected-gear Fire Spell Power contribution',
                'applicability to the selected Arcane Archer Flaming imbue while active',
                'overlapping Equipment Spell Power can reduce its marginal benefit',
                'not weapon damage, full-character Spell Power or DPS',
                'does not establish scaling for Melancholic or Dolorous weapon effects'))
        self.assertEqual(audit.subtotal(ledger, 'Combustion')['total'], 142)
        self.assertEqual(audit.subtotal(ledger, 'Intelligence')['total'], 37)
        doubleshot = audit.subtotal(ledger, 'Doubleshot')
        self.assertEqual((doubleshot['total'], doubleshot['complete']), (35, True))

    def test_reaper_reasoning_preserves_relative_gain_without_changing_priorities(self):
        current_flat_damage_reasoning(self.html)
        guide = GuideText(self.html)
        text = ' '.join(guide.blocks['reaper-10'])
        require_clauses(text, ('reducing 100 and 110 to 10 and 11 still leaves a 10% relative gain',
                               'selected priorities remain unchanged',
                               'does not newly validate that table’s exact mitigation values'))
        for baseline, addition, factor in ((100, 10, .1), (50, 2, .25), (200, 3, .75)):
            self.assertAlmostEqual(factor * (baseline + addition) / (factor * baseline),
                                   (baseline + addition) / baseline)
        self.assertEqual(preservation.checkpoint_file_bytes('tools/fixtures/wisdom-loadout/selection.json'),
                         (ROOT / 'tools/fixtures/wisdom-loadout/selection.json').read_bytes())
        with self.assertRaises(AssertionError):
            current_flat_damage_reasoning(self.html.replace('reducing 100 and 110 to 10 and 11',
                                                            'flat damage is near zero; reducing 100 and 110 to 10 and 11', 1))
        # The explicitly retained experiments remain historical evidence.
        archived = re.sub(r'(<details\b[^>]*id="endgame-historical-notes"[^>]*>)',
                          r'\1<p>flat damage is near zero</p>', self.html, count=1)
        self.assertNotEqual(archived, self.html)
        current_flat_damage_reasoning(archived)


class OffensiveSourceBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source, mechanics = (ROOT / SOURCE_PACKET).read_bytes(), (ROOT / MECHANICS_PACKET).read_bytes()
        assert preservation.sha(source) == SOURCE_SHA
        assert preservation.sha(mechanics) == MECHANICS_SHA
        cls.source, cls.mechanics = json.loads(source), json.loads(mechanics)

    def test_additive_register_retains_scope_provenance_and_source_bindings(self):
        evidence_contract(self.source, self.mechanics)

    def test_summaries_cannot_be_promoted_to_raw_captures_or_full_certification(self):
        cases = (
            ('raw DOM', 'source', ('provenance', 'raw_dom_capture_included'), True),
            ('authenticated browser capture', 'source', ('provenance', 'cryptographic_browser_capture_binding'), True),
            ('DPS certification', 'mechanics', ('coverage', 'full_dps_validated'), True),
            ('first passive only', 'mechanics', ('current_text_contract', 'ability_damage',
                                              'ordinary_ability_modifier_factor_after_both_feats'), 1.5),
            ('new ledger gate', 'mechanics', ('current_text_contract', 'combustion_applicability',
                                            'formal_ledger_qualification_changed'), True),
        )
        for label, target, keys, value in cases:
            source, mechanics = copy.deepcopy(self.source), copy.deepcopy(self.mechanics)
            node = source if target == 'source' else mechanics
            for key in keys[:-1]:
                node = node[key]
            node[keys[-1]] = value
            with self.subTest(mutation=label), self.assertRaises(AssertionError):
                evidence_contract(source, mechanics)
        changed = copy.deepcopy(self.mechanics)
        changed['named_imbue_scenarios']['scenarios'][1]['minimum_host_level'] = 28
        with self.assertRaises(AssertionError):
            evidence_contract(self.source, changed)
        changed = copy.deepcopy(self.mechanics)
        changed['claims'][0]['source_ids'] = ['invented-source']
        with self.assertRaises(AssertionError):
            evidence_contract(self.source, changed)


if __name__ == '__main__':
    unittest.main()
