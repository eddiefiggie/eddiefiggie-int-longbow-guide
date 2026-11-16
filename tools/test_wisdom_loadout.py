"""Current Wisdom recipe/dataflow and exact historical preservation regressions.

Model values are not upgraded to source-certified mechanics by these tests.
Historical test modules receive only the exact-restored approved predecessor;
the production recipe, ranking, renderer and ledger are tested here directly.
"""
import copy
import hashlib
import json
from pathlib import Path
import re
import unittest

import stacking_audit as audit
import wisdom_preservation as preservation
import wisdom_corrections as corrections
import wisdom_crafting_integration as crafting
import wisdom_recipe_proof_preservation as recipe_proofs
import wisdom_offense_preservation as offense
from test_lamordia_handling import Document, guide_content, guide_text, norm


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tools/fixtures/wisdom-loadout'
EXPECTED_TARGETS = [
    'Greater Marksmanship', 'Sight Beyond Sight', 'Relentless Fury', 'Bloodrage',
    'Alchemical Fire Attunement', 'Fiery', 'Legendary Salt', 'Improved Deception',
    'Ranged Alacrity', 'Doubleshot', 'Ranged Power', 'Intelligence', 'Seeker',
    'Armor-Piercing', 'Deadly', 'Imbue Dice', 'Sneak Attack Dice',
    'Sneak Attack Damage', 'Constitution', 'Physical Sheltering',
    'Magical Sheltering', 'Fortification', 'False Life', 'Healing Amplification',
    'Dodge', 'Reflex Save', 'Fortitude Save', 'Will Save', 'Wisdom', 'Accuracy',
    'Combustion', 'Damage to helpless enemies',
]
EXPECTED_ITEMS = [
    ('Armor', "Light Armor of the Warblade's Reflection"),
    ('Helmet', 'The Skull of the Horned King'),
    ('Goggles', 'Legendary Goggles of the Archer'),
    ('Necklace', 'Legendary Glabrezu Claw Pendant'),
    ('Trinket', 'Legendary Abyssal Compass'),
    ('Cloak', 'The Queen of Rot'),
    ('Belt', 'Legendary Chains'),
    ('Ring', 'Legendary Celestial Sapphire Ring'),
    ('Ring', 'Legendary Ring of Unnatural Accuracy'),
    ('Gloves', 'Legendary Burrowing Claws'),
    ('Boots', 'Legendary Coldlight Runners'),
    ('Bracers', "Yeenoghu's Reign"),
    ('Quiver', 'Epic Purifying Quiver'),
    ('Main Hand', 'Legendary Calamitous Longbow'),
]


def record_maxima(record):
    """Independently re-add typed maxima from a retained output extraction.

    This deliberately uses neither the guide's ingredient tree nor its
    aggregation function; the result is model arithmetic, not game evidence.
    """
    buckets, totals = {}, {}
    affixes = [a for row in record['chosen'] + record['crafts'] + record['augments']
               for a in row['affixes']]
    affixes.extend(a for row in record['sets'] for a in row['effects'])
    for affix in affixes:
        if affix['type'] == 'Bool':
            continue
        kind = {'Insight Natural': 'Insight', 'Primal Natural': 'Primal',
                'Profane Natural': 'Profane'}.get(affix['type'], affix['type'])
        stats = ('Physical Sheltering', 'Magical Sheltering') if affix['stat'] == 'Sheltering' else (affix['stat'],)
        for stat in stats:
            key = (stat, kind)
            buckets[key] = max(buckets.get(key, float('-inf')), affix['value'])
    for (stat, kind), value in buckets.items():
        totals[stat] = totals.get(stat, 0) + value
    return totals


def current_render_contract(html, data):
    """Bind the actual production renderer; historical callers use the explicit helper."""
    import wisdom_loadout as recipe
    return render_contract(html, data, recipe)


def render_contract(html, data, recipe):
    """Check exact generated blocks and visibility using the supplied pinned renderer."""
    recipe.validate(data)
    renderers = {'recipe': recipe.render_recipe, 'priorities': recipe.render_priorities,
                 'onepage': recipe.render_onepage_rows}
    for kind, (start, end) in recipe.MARKERS.items():
        assert html.count(start) == html.count(end) == 1, ('unique markers', kind)
        left, right = html.index(start) + len(start), html.index(end)
        assert left < right, ('ordered markers', kind)
        assert html[left:right] == '\n' + renderers[kind](data) + '\n', ('generated block drift', kind)
    doc = Document(html).root

    def nodes(node, blocked=False):
        blocked = (blocked or node.tag in {'script', 'style', 'template'}
                   or 'hidden' in node.attrs or 'inert' in node.attrs
                   or node.attrs.get('aria-hidden') == 'true'
                   or node.tag == 'details' and 'open' not in node.attrs
                   or bool(re.search(r'(?:display\s*:\s*none|visibility\s*:\s*hidden)',
                                     node.attrs.get('style', ''), re.I)))
        yield node, not blocked
        for child in node.children:
            if hasattr(child, 'tag'):
                yield from nodes(child, blocked)

    state = list(nodes(doc))
    for identity in ('wisdom-loadout-selection', 'current-affix-priority',
                     'wisdom-recipe-table', 'wisdom-set-table',
                     'wisdom-equipment-changes', 'wisdom-model-comparison',
                     'wisdom-priority-table', 'wisdom-floor-table'):
        found = [(n, visible) for n, visible in state if n.attrs.get('id') == identity]
        assert len(found) == 1 and found[0][1], ('visible unique current content', identity)
    for identity in ('priority', 'kit'):
        found = [(n, visible) for n, visible in state
                 if n.attrs.get('data-loadout-summary') == identity]
        assert len(found) == 1 and found[0][1], ('visible unique onepage row', identity)
    priorities = [(n, visible) for n, visible in state if 'data-priority-rank' in n.attrs]
    assert len(priorities) == 32
    assert all(visible for _, visible in priorities)
    assert [(int(n.attrs['data-priority-rank']), n.attrs['data-stat']) for n, _ in priorities] == list(enumerate(EXPECTED_TARGETS, 1))
    for node, _ in priorities:
        cells = [n for n in node.children if hasattr(n, 'tag') and n.tag in {'th', 'td'}]
        rank = int(node.attrs['data-priority-rank'])
        assert norm(cells[0].text()) == str(rank)
        assert norm(cells[1].text()) == data['query']['targets'][rank - 1]
    return True


def current_bow_context_contract(html, data):
    """Cross-references outside the generated recipe must use its actual fills."""
    doc = Document(html).root
    visible = list(guide_content(doc))
    bow = next(i for i in data['items'] if i['slot'] == 'Main Hand')
    assert bow['id'] == 'Legendary Calamitous Longbow' and bow['filled_ml'] == 34
    assert {s['color']: s['fill']['id'] for s in bow['sockets']} == {
        'Purple': 'Globe of True Imperial Blood', 'Orange': 'A Treatise on Battle',
    }
    choices = [n for n in visible if n.attrs.get('id') == 'endgame-bow-choice']
    ladders = [n for n in visible if n.attrs.get('id') == 'bow-ladder-endgame-choice']
    summaries = [n for n in visible if n.tag == 'tr'
                 and any(a.attrs.get('href') == '#bow-ladder-levels-1-36'
                         and norm(a.text()) == 'Bows' for a in n.nodes('a'))]
    augment_rows = [n for n in visible if n.tag == 'tr'
                    and [norm(c.text()) for c in n.children if hasattr(c, 'tag') and c.tag == 'td'][:2]
                    == ['Augments', 'Orange and Purple slots']]
    assert len(choices) == len(ladders) == len(summaries) == len(augment_rows) == 1
    for node in ladders + summaries + augment_rows:
        text = norm(guide_text(node))
        assert ('Globe/Treatise' in text or
                'Globe of True Imperial Blood' in text and 'A Treatise on Battle' in text)
        assert re.search(r'Calamitous.{0,25}ML\s*34', text), 'current bow minimum level'
        assert re.search(r'(?:outfit|kit).{0,50}(?:level\s*36|ML\s*36)', text), 'full outfit minimum level'
        assert 'Defense +40' not in text
    text = norm(guide_text(choices[0]))
    for clause in ('Purple: Globe of True Imperial Blood', 'Orange: A Treatise on Battle',
                   'Defense +40 is no longer selected', 'not a second solved',
                   'does not widen threat range', 'Neither bow is a universal damage winner'):
        assert clause in text, clause
    assert re.search(r'Calamitous recipe remains filled ML\s*34', text)
    assert 'would leave it ML35' in text or 'would leave it ML 35' in text
    assert 'whole outfit wearable before 36' in text
    assert 'Globe/Treatise' in norm(guide_text(ladders[0]))
    assert re.search(r'Meltscale\s*31', norm(guide_text(summaries[0])))
    return True


class WisdomReleasePreservationTests(unittest.TestCase):
    def test_recorded_startup_identifies_the_approved_base_branch_and_recipe(self):
        data = json.loads((ROOT / 'evidence/wisdom-loadout/startup.json').read_text())
        self.assertEqual(data['repository'], 'eddiefiggie/eddiefiggie-int-longbow-guide')
        self.assertEqual(data['immutable_base_sha'], preservation.BASE_COMMIT)
        self.assertEqual(data['initial_local_head'], preservation.BASE_COMMIT)
        self.assertEqual(data['initial_local_branch'], 'main')
        self.assertTrue(data['initial_worktree_clean'])
        self.assertEqual(data['allowed_working_branch'], 'feat/wisdom-loadout-priorities')
        self.assertEqual(data['selected_loadout'], 'artifact-wisdom-canonical-spot-luck.json')
        self.assertEqual(data['selected_loadout_sha256'],
                         '37e612b60744e9fb104fdfdc39295c88973568ba3affbd0646c8fe1eb6e73a4d')
        self.assertIn('not part of the selected primary recipe', data['optional_ring_dexterity_13'])

    def test_exact_current_files_reverse_to_every_unchanged_predecessor_hash(self):
        self.assertTrue(preservation.validate_full_reversal())

    def test_all_published_prior_snapshots_keep_their_original_bytes(self):
        data = json.loads((FIXTURE / 'preserved-snapshots.json').read_text())
        self.assertEqual(data['baseline_commit'], preservation.BASE_COMMIT)
        self.assertEqual(len(data['files']), 66)
        for path, expected in data['files'].items():
            with self.subTest(path=path):
                self.assertTrue(path.startswith('versions/'))
                raw = (ROOT / path).read_bytes()
                blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
                self.assertEqual(hashlib.sha1(blob).hexdigest(), expected)

    def test_runtime_styles_and_historical_damage_model_are_not_reimplemented(self):
        current, previous = (ROOT / 'index.html').read_text(), preservation.frozen_index()
        for tag in ('script', 'style'):
            pattern = r'<' + tag + r'\b[^>]*>.*?</' + tag + '>'
            self.assertEqual(re.findall(pattern, current, re.S), re.findall(pattern, previous, re.S))
        start, end = '<h3 id="bow-damage-model">', '<h3 id="crafted-endgame-bow">'
        # The .7 release corrects the model's current explanatory prose. Keep
        # this original whole-section equality against its exact .6 view;
        # current score semantics and all 39 tuples have separate live tests.
        point_six = offense.checkpoint_file_text('index.html')
        self.assertEqual(point_six[point_six.index(start):point_six.index(end)],
                         previous[previous.index(start):previous.index(end)])

    def test_reversal_rejects_stale_mixed_duplicate_and_unrelated_edits(self):
        scope = preservation.load_scope()
        for path in preservation.REVIEWED_PATHS:
            current = (corrections.original_file_text(path) if path in corrections.REVIEWED_PATHS
                       else crafting.checkpoint_file_text(path))
            rule = scope['files'][path]
            self.assertTrue(rule['reviewed_replacements'], path)
            change = rule['reviewed_replacements'][0]
            mutations = [current + '\n',
                         current.replace(change['after'], change['before'], 1),
                         current.replace(change['after'], change['after'] * 2, 1)]
            for mutant in mutations:
                self.assertNotEqual(mutant, current)
                with self.subTest(path=path), self.assertRaises(AssertionError):
                    preservation.restore_wisdom_file(path, mutant)

    def test_reversal_hash_and_exact_hunks_are_independent_guards(self):
        # Even a caller that changes the current digest cannot bless an extra
        # edit: exact contexts and the fixed predecessor hash still reject it.
        scope = preservation.load_scope()
        path = 'index.html'
        original = corrections.original_file_text(path)
        for mutant in (original + '<p>Unapproved extra content</p>',
                       original.replace('<h2 id="class-split">', '<h2 id="changed-class-split">')):
            self.assertNotEqual(original, mutant)
            changed = copy.deepcopy(scope)
            changed['files'][path]['current_sha256'] = preservation.sha(mutant)
            changed['files'][path]['current_bytes'] = len(mutant.encode())
            with self.assertRaises(AssertionError):
                preservation.restore_wisdom_file(path, mutant, scope=changed)

    def test_predecessor_views_do_not_accept_a_stale_current_release(self):
        with self.assertRaises(AssertionError):
            preservation.restore_file('index.html', preservation.frozen_index())


class CurrentWisdomManifestTests(unittest.TestCase):
    """The actual chosen recipe, not a frozen historical render or live DDO."""

    def setUp(self):
        import wisdom_loadout
        self.recipe = wisdom_loadout
        self.data = wisdom_loadout.load()

    def test_primary_record_is_bound_to_the_completed_run_and_explicit_derivation(self):
        self.assertTrue(self.recipe.validate(self.data))
        self.assertEqual(self.data['selection']['id'], 'artifact-wisdom-canonical-spot-luck')
        self.assertEqual(self.data['selection']['status'], 'manual-feasible')
        self.assertFalse(self.data['selection']['certified_mechanics'])
        self.assertEqual(self.data['provenance']['guide_commit'], preservation.BASE_COMMIT)
        self.assertEqual(self.data['provenance']['optimizer_commit'],
                         '01e17c1675363458aee46f3765ed6f1b811eb8e3')
        self.assertEqual(self.data['provenance']['dataset_sha256'],
                         'b779480ade9e41de8f0c1eeb554a7bd09060a300c8ceb67f6a80c5abfcad08cf')
        records = {}
        for key in ('selected', 'production'):
            metadata = self.data['provenance'][key]
            raw = (ROOT / metadata['path']).read_bytes()
            self.assertEqual(preservation.sha(raw), metadata['record_sha256'])
            records[key] = json.loads(raw)
            self.assertEqual(records[key]['origin']['sha256'], metadata['sha256'])
        selected, production = records['selected'], records['production']
        self.assertEqual(selected['origin']['sha256'],
                         '37e612b60744e9fb104fdfdc39295c88973568ba3affbd0646c8fe1eb6e73a4d')
        self.assertEqual(production['origin']['sha256'],
                         '6cba0f33765b8c24b19179716e3240147dae98ac047fc53effbecc18470ce6bd')
        self.assertEqual((production['status'], production['passes'], production['elapsed_seconds']),
                         ('optimal', 45, 271.998))
        self.assertEqual(selected['status'], 'manual-feasible')
        self.assertEqual(self.data['query'], production['query'])
        self.assertEqual(self.data['manual_adjustments'], selected['manual_derivation'])
        self.assertFalse(self.data['manual_adjustments']['solverExecuted'])
        self.assertFalse(self.data['optional']['sinew']['selected'])
        self.assertFalse(self.data['optional']['sinew']['studied_by_this_run'])
        self.assertEqual(self.data['model']['raw_production_totals'], record_maxima(production))
        self.assertEqual(self.data['model']['totals'], record_maxima(selected))

    def test_exact_fourteen_items_one_artifact_and_all_actual_socket_placements(self):
        self.assertEqual([(i['slot'], i['id']) for i in self.data['items']], EXPECTED_ITEMS)
        artifacts = [i['id'] for i in self.data['items'] if i['minor_artifact']]
        self.assertEqual(artifacts, ["Yeenoghu's Reign"])
        sockets = [(i['id'], s) for i in self.data['items'] for s in i['sockets']]
        self.assertEqual(len(sockets), 34)
        self.assertTrue(all(s['fill'] for _, s in sockets))
        self.assertEqual(sum(s['color'] in {'Sun', 'Moon'} for _, s in sockets), 9)
        self.assertEqual(sum(s['fill']['kind'] == 'set-augment' for _, s in sockets), 12)
        self.assertEqual(self.data['counts'], {
            'items': 14, 'artifacts': 1, 'sockets': 34, 'occupied': 34,
            'ordinary': 25, 'sun_moon': 9, 'set_placements': 12,
            'ordinary_augment_placements': 22,
        })
        self.assertEqual(self.data['selection']['full_kit_ml'], 36)
        self.assertEqual(max(i['filled_ml'] for i in self.data['items']), 36)
        sets = self.data['augment_sets']
        self.assertEqual([s['name'] for s in sets],
                         ['Dusk Raider', 'Perfect Silence', 'Quickblade', 'Tough Shields'])
        for group in sets:
            with self.subTest(group=group['name']):
                self.assertEqual(group['threshold'], 3)
                self.assertEqual(len(group['placements']), 3)
                self.assertEqual(len({p['host'] for p in group['placements']}), 3)
                for placement in group['placements']:
                    self.assertEqual(sum(host == placement['host']
                                         and s['color'] == placement['color']
                                         and s['fill']['id'] == group['name']
                                         for host, s in sockets), 1)

    def test_wisdom_craft_and_optional_ring_are_not_conflated(self):
        items = {i['id']: i for i in self.data['items']}
        claws = items['Legendary Burrowing Claws']['crafts']
        self.assertEqual(len(claws), 1)
        self.assertEqual(claws[0]['affixes'],
                         [{'stat': 'Wisdom', 'type': 'Enhancement', 'value': 15}])
        ring = items['Legendary Celestial Sapphire Ring']
        self.assertEqual(ring['crafts'], [])
        self.assertEqual(ring['empty_craft_slots'],
                         [{'family': 'Nearly Finished', 'slot': 'Nearly Finished', 'selected': False}])
        branch = self.data['optional']['ring_dexterity_13']
        self.assertFalse(branch['selected'])
        self.assertEqual(branch['evidence_status'], 'model-only')
        self.assertEqual(branch['gear_dexterity_if_selected'], 19)
        totals = self.data['model']['totals']
        for stat, expected in (('Wisdom', 18), ('Dexterity', 6), ('Intelligence', 37),
                               ('Constitution', 32), ('Spot', 27), ('Listen', 7)):
            self.assertEqual(totals[stat], expected, stat)
        self.assertEqual(self.data['model']['raw_production_totals']['Constitution'], 34)

    def test_actual_objective_order_caps_floors_and_exclusions_remain_explicit(self):
        query = self.data['query']
        self.assertEqual(query['targets'], EXPECTED_TARGETS)
        self.assertEqual(list(self.data['model']['ranked']), EXPECTED_TARGETS)
        self.assertNotIn('Dexterity', query['targets'])
        self.assertEqual(query['targets'].index('Wisdom'), 28)
        self.assertTrue(query['includeArtifact'])
        self.assertEqual((query['style'], query['mlCap']), ('ranged', 36))
        self.assertEqual(query['targetCaps']['Doubleshot'], 35)
        self.assertEqual(query['targetCaps']['Ranged Power'], 44)
        self.assertEqual(query['targetFloors']['Physical Sheltering'], 133)
        self.assertEqual(query['targetFloors']['Improved Deception'], 1)
        self.assertIn('Frenzied Berserker', query['excludedSets'])
        self.assertEqual(query['excludedTypes']['Deadly||Insight'],
                         {'stat': 'Deadly', 'bonus_type': 'Insight'})
        blocklist = set(query['blocklist'])
        self.assertIn('Diamond of Spot +22', blocklist)
        chosen = {i['id'] for i in self.data['items']}
        chosen.update(s['fill']['id'] for i in self.data['items'] for s in i['sockets'])
        self.assertFalse(blocklist & chosen)
        festive = [s['fill'] for i in self.data['items'] for s in i['sockets']
                   if s['fill'].get('festive_exception')]
        self.assertTrue(festive)
        self.assertTrue(all(a['id'].startswith('Diamond of Festive ') for a in festive))

    def test_evidence_inventory_records_are_bound_without_promoting_support_grades(self):
        fields = {'claims': 'claim_inventory', 'derivation': 'derivation', 'sources': 'sources'}
        records = {}
        for key, field in fields.items():
            raw = (ROOT / self.data['evidence'][field]).read_bytes()
            self.assertEqual(preservation.sha(raw), self.data['evidence']['record_sha256'][key])
            records[key] = json.loads(raw)
        inventory = records['claims']
        self.assertEqual(len(inventory['claims']), 130)
        self.assertEqual(inventory['coverage']['selectedComponents'], 54)
        self.assertEqual(inventory['coverage']['notFullyCertified'], 30)
        self.assertTrue(any(c['status'] == 'model-only' for c in inventory['claims']))
        self.assertTrue(any(c['status'] == 'unresolved/conflicting' for c in inventory['claims']))
        self.assertEqual(self.data['model']['independent_checks'],
                         {'passed': True, 'count': 373, 'problems': 0, 'warnings': 0})
        self.assertFalse(self.data['selection']['certified_mechanics'])

    def test_invalid_optional_selection_artifact_items_and_rank_data_are_rejected(self):
        cases = {}
        changed = copy.deepcopy(self.data)
        changed['optional']['ring_dexterity_13']['selected'] = True
        cases['optional ring silently selected'] = changed
        changed = copy.deepcopy(self.data)
        ring = next(i for i in changed['items'] if i['id'] == 'Legendary Celestial Sapphire Ring')
        ring['crafts'].append({'host': ring['id'], 'family': 'Nearly Finished',
                               'slot': 'Nearly Finished', 'name': 'Dexterity',
                               'affixes': [{'stat': 'Dexterity', 'type': 'Enhancement', 'value': 13}]})
        cases['optional ring craft inserted into primary'] = changed
        changed = copy.deepcopy(self.data)
        next(i for i in changed['items'] if i['minor_artifact'])['minor_artifact'] = False
        cases['missing mandatory artifact'] = changed
        changed = copy.deepcopy(self.data)
        changed['items'][0]['minor_artifact'] = True
        cases['second artifact'] = changed
        changed = copy.deepcopy(self.data)
        changed['items'][0]['id'] = changed['query']['blocklist'][0]
        cases['blocked item substituted'] = changed
        changed = copy.deepcopy(self.data)
        changed['query']['targets'][9:11] = list(reversed(changed['query']['targets'][9:11]))
        cases['ordered objective reordered'] = changed
        changed = copy.deepcopy(self.data)
        changed['model']['ranked']['Wisdom'] = 3
        cases['stale ranked Wisdom value'] = changed
        changed = copy.deepcopy(self.data)
        changed['model']['totals']['Dexterity'] = 19
        cases['optional DEX leaked into primary total'] = changed
        changed = copy.deepcopy(self.data)
        changed['selection']['certified_mechanics'] = True
        cases['certification promoted'] = changed
        changed = copy.deepcopy(self.data)
        changed['selection']['status'] = 'optimal'
        cases['manual recipe presented as solved optimum'] = changed
        changed = copy.deepcopy(self.data)
        changed['items'][0]['native_affixes'][0]['evidence_status'] = 'verified'
        cases['native inventory grade promoted'] = changed
        changed = copy.deepcopy(self.data)
        changed['items'][0]['native_affixes'][0]['value'] = 999
        cases['rendered native affix value changed'] = changed
        for label, changed in cases.items():
            with self.subTest(case=label), self.assertRaises((AssertionError, ValueError, KeyError)):
                self.recipe.validate(changed)


class CurrentWisdomRenderedGuideTests(unittest.TestCase):
    def setUp(self):
        import wisdom_loadout
        self.recipe = wisdom_loadout
        self.data = wisdom_loadout.load()
        self.html = (ROOT / 'index.html').read_text()

    def test_all_current_blocks_are_generated_from_the_same_selected_data(self):
        self.assertTrue(current_render_contract(self.html, self.data))
        self.assertEqual(self.recipe.replace_blocks(self.html, self.data), self.html)
        recipe = Document(self.recipe.render_recipe(self.data)).root
        table = next(t for t in recipe.nodes('table')
                     if any(c.attrs.get('id') == 'wisdom-recipe-table' for c in t.nodes('caption')))
        body = table.nodes('tbody')[0]
        self.assertEqual(len(body.nodes('tr')), 14)
        actual = []
        for row in body.nodes('tr'):
            cells = [n for n in row.children if hasattr(n, 'tag') and n.tag in {'th', 'td'}]
            actual.append((norm(cells[0].text()), norm(cells[1].nodes('a')[0].text())))
        self.assertEqual(actual, EXPECTED_ITEMS)

    def test_current_tables_keep_labels_and_keyboard_scroll_regions(self):
        for renderer in (self.recipe.render_recipe, self.recipe.render_priorities):
            doc = Document(renderer(self.data)).root
            regions = [n for n in doc.nodes('div') if 'tw' in n.attrs.get('class', '').split()]
            self.assertTrue(regions)
            for region in regions:
                self.assertEqual(region.attrs.get('tabindex'), '0')
                self.assertEqual(region.attrs.get('role'), 'region')
                label = region.attrs.get('aria-labelledby')
                self.assertTrue(label)
                captions = [n for n in region.nodes('caption') if n.attrs.get('id') == label]
                self.assertEqual(len(captions), 1)
                self.assertTrue(norm(captions[0].text()))
                self.assertTrue(all(n.attrs.get('scope') in {'row', 'col'} for n in region.nodes('th')))

    def test_missing_duplicate_hidden_or_inert_current_blocks_are_rejected(self):
        renderers = {'recipe': self.recipe.render_recipe,
                     'priorities': self.recipe.render_priorities,
                     'onepage': self.recipe.render_onepage_rows}
        for kind, renderer in renderers.items():
            block = renderer(self.data)
            start, end = self.recipe.MARKERS[kind]
            whole = start + '\n' + block + '\n' + end
            self.assertIn(whole, self.html)
            mutations = {
                'missing': self.html.replace(block, '', 1),
                'duplicated': self.html.replace(block, block + block, 1),
                'hidden ancestor': self.html.replace(whole, '<div hidden>' + whole + '</div>', 1),
                'inert ancestor': self.html.replace(whole, '<div inert>' + whole + '</div>', 1),
                'template ancestor': self.html.replace(whole, '<template>' + whole + '</template>', 1),
                'closed disclosure': self.html.replace(whole, '<details>' + whole + '</details>', 1),
                'CSS hidden ancestor': self.html.replace(whole, '<div style="display:none">' + whole + '</div>', 1),
            }
            for label, mutant in mutations.items():
                with self.subTest(kind=kind, case=label), self.assertRaises(AssertionError):
                    current_render_contract(mutant, self.data)

    def test_current_priority_reorder_stale_values_and_item_loss_are_rejected(self):
        priorities = self.recipe.render_priorities(self.data)
        rows = re.findall(r'<tr data-priority-rank="\d+".*?</tr>', priorities)
        self.assertEqual(len(rows), 32)
        wrong_order = priorities.replace(rows[9] + rows[10], rows[10] + rows[9])
        self.assertNotEqual(wrong_order, priorities)
        stale_wisdom = rows[28].replace('<td>18</td>', '<td>3</td>')
        self.assertNotEqual(stale_wisdom, rows[28])
        onepage = self.recipe.render_onepage_rows(self.data)
        stale_onepage, changed = re.subn(r'DEX\s*6\b', 'DEX 19', onepage)
        self.assertEqual(changed, 1)
        mutated = [self.html.replace(priorities, wrong_order, 1),
                   self.html.replace(rows[28], stale_wisdom, 1),
                   self.html.replace('data-stat="Wisdom"', 'data-stat="Dexterity"', 1),
                   self.html.replace('<span class="tag">MINOR ARTIFACT</span>', '', 1),
                   self.html.replace(onepage, stale_onepage, 1)]
        for value in mutated:
            self.assertNotEqual(value, self.html)
            with self.assertRaises(AssertionError):
                current_render_contract(value, self.data)

    def test_builder_rejects_missing_duplicate_or_reversed_markers(self):
        for kind, (start, end) in self.recipe.MARKERS.items():
            mutations = [self.html.replace(start, '', 1),
                         self.html.replace(end, end + end, 1),
                         self.html.replace(start, '<!--TEMP-->', 1).replace(end, start, 1).replace('<!--TEMP-->', end, 1)]
            for mutant in mutations:
                with self.subTest(kind=kind), self.assertRaises(ValueError):
                    self.recipe.replace_blocks(mutant, self.data)

    def test_current_nonhistorical_bow_references_match_new_fills_and_levels(self):
        self.assertTrue(current_bow_context_contract(self.html, self.data))

    def test_stale_bow_fill_level_and_unqualified_alternate_are_rejected(self):
        for old, new in (
            ('The new Globe/Treatise fill leaves Calamitous ML34',
             'The retained Defense +40 leaves Calamitous ML36'),
            ('Current Globe/Treatise fills leave Calamitous at ML34',
             'Current Globe/Treatise fills leave Calamitous at ML36'),
            ('Calamitous stays filled ML34', 'Calamitous stays filled ML35'),
            ('not a second solved or fully validated loadout',
             'a second solved and fully validated loadout'),
            ('does not widen threat range', 'widens threat range'),
        ):
            self.assertIn(old, self.html)
            with self.subTest(claim=old), self.assertRaises(AssertionError):
                current_bow_context_contract(self.html.replace(old, new, 1), self.data)


class CurrentWisdomEvidenceGateTests(unittest.TestCase):
    """Exercise the real current calculator inputs, never the restored ledger."""

    def setUp(self):
        self.data = audit.load()
        import build_stacking_audit
        self.renderer = build_stacking_audit

    def test_current_ledger_retains_old_sources_and_exactly_two_scoped_rule_additions(self):
        self.assertTrue(audit.validate(self.data))
        old = json.loads(preservation.frozen_ledger_bytes())
        self.assertEqual(self.data['rules'][:len(old['rules'])], old['rules'])
        self.assertEqual([r['id'] for r in self.data['rules'][len(old['rules']):]],
                         ['int-selected-ten-pairs', 'fort-enh-insight-observed'])
        for sid, source in old['sources'].items():
            with self.subTest(source=sid):
                self.assertEqual(self.data['sources'][sid], source)
        self.assertEqual(self.data['selection_base_commit'], preservation.BASE_COMMIT)
        self.assertEqual(preservation.sha(recipe_proofs.checkpoint_file_bytes('tools/stacking_audit.py')),
                         preservation.BASE_CALCULATOR_SHA)

    def test_current_ability_inputs_match_primary_recipe_without_ring_dexterity13(self):
        rows = {c['id']: (c['stat'], c['amount'], c['bonus_type'])
                for c in self.data['components'] if c['channel'] == 'gear'
                and c['stat'] in {'Wisdom', 'Dexterity'}}
        self.assertEqual(rows, {
            'claws-wisdom': ('Wisdom', 15, 'Enhancement'),
            'celestial-profane-wisdom': ('Wisdom', 2, 'Profane'),
            'globe-wisdom': ('Wisdom', 1, 'Exceptional'),
            'ring-quality-dex': ('Dexterity', 3, 'Quality'),
            'celestial-profane-dexterity': ('Dexterity', 2, 'Profane'),
            'globe-dexterity': ('Dexterity', 1, 'Exceptional'),
        })
        self.assertEqual(sum(v[1] for v in rows.values() if v[0] == 'Wisdom'), 18)
        self.assertEqual(sum(v[1] for v in rows.values() if v[0] == 'Dexterity'), 6)
        # These checks are of modeled ingredient amounts, not certified sums.
        self.assertIsNone(audit.subtotal(self.data, 'Wisdom')['total'])
        self.assertIsNone(audit.subtotal(self.data, 'Dexterity')['total'])

    def test_current_set_components_are_named_unknowns_not_laundered_old_monolith(self):
        rows = {c['id']: c for c in self.data['components']}
        for cid, stat, amount in (
            ('dusk-raider-rp', 'Ranged Power', 15),
            ('tough-shields-prr', 'PRR', 30),
            ('quickblade-ds', 'Doubleshot', 15),
            ('perfect-silence-sneak', 'Sneak dice', 3),
        ):
            with self.subTest(component=cid):
                c = rows[cid]
                self.assertEqual((c['stat'], c['amount'], c['bonus_type']), (stat, amount, 'Artifact'))
                self.assertEqual(c['state'], 'unknown')
                self.assertEqual(c['source'], '')
                self.assertIn(cid, audit.subtotal(self.data, stat, active=['force'])['excluded'])
        self.assertNotIn('monolith-rp', rows)
        self.assertNotIn('monolith-prr', rows)
        self.assertNotIn('pendant-ap', rows)
        self.assertNotIn('pendant-threat', rows)

    def test_current_unproven_whole_combinations_stay_withheld(self):
        for stat in ('Ranged Power', 'Doubleshot', 'Wisdom', 'Dexterity',
                     'Spot', 'Listen', 'PRR', 'MRR', 'Dodge', 'Fortification',
                     'Constitution', 'Seeker', 'Armor-Piercing', 'Deadly', 'Sneak dice'):
            with self.subTest(stat=stat):
                result = audit.subtotal(self.data, stat)
                self.assertIsNone(result['total'])
                self.assertFalse(result['complete'])
                self.assertTrue(result['excluded'] or result['missing_interactions'])
        for stat, expected in (('HP', 108), ('Healing Amplification', 63),
                               ('Ranged threat reduction', 22),
                               ('Greater Marksmanship damage', 2),
                               ('Greater Marksmanship attack', 3), ('Ranged alacrity', 20)):
            with self.subTest(stat=stat):
                result = audit.subtotal(self.data, stat)
                self.assertTrue(result['complete'])
                self.assertEqual(result['total'], expected)

    def test_current_int_gear_subtotal_has_only_the_approved_scoped_completion(self):
        for active in ((), ('force',)):
            with self.subTest(active=active):
                result = audit.subtotal(self.data, 'Intelligence', active=active)
                self.assertEqual((result['stat'], result['channel'], result['total']),
                                 ('Intelligence', 'gear', 37))
                self.assertTrue(result['complete'])
                self.assertEqual(result['counted'], [
                    'boots-int', 'solar-int', 'lunar-int', 'festive-int',
                    'dimlight-int', 'glabrezu-insight-int', 'chains-quality-int'])
                self.assertEqual(result['suppressed'],
                                 ['celestial-profane-intelligence', 'globe-intelligence'])
                self.assertEqual(result['excluded'], [])
                self.assertEqual(result['missing_interactions'], [])
                self.assertEqual(sum(p[2] == 'int-selected-ten-pairs' for p in result['proofs']), 10)
                at35 = audit.subtotal(self.data, 'Intelligence', active=active, level=35)
                self.assertIsNone(at35['total'])
                self.assertFalse(at35['complete'])

    def test_source_less_or_unqualified_current_inputs_cannot_be_promoted(self):
        selected = ('dusk-raider-rp', 'tough-shields-prr', 'quickblade-ds',
                    'perfect-silence-sneak', 'claws-wisdom', 'celestial-dodge',
                    'yeenoghu-quality-deadly',
                    'solar-sneak-damage', 'emerald-imbue')
        # Glabrezu's separately integrated exact source has current missing,
        # forged and wrong-definition negatives in test_wisdom_crafting_integration.
        # Chains Combustion's new recipe-proof path has actual-current negative
        # controls in test_recipe_proofs and test_wisdom_recipe_integration.
        for cid in selected:
            changed = copy.deepcopy(self.data)
            row = next(c for c in changed['components'] if c['id'] == cid)
            self.assertEqual(row['state'], 'unknown')
            row['state'] = 'verified'
            with self.subTest(component=cid), self.assertRaises((AssertionError, KeyError)):
                audit.validate(changed)
        changed = copy.deepcopy(self.data)
        source = changed['sources']['claws-wisdom']
        self.assertIsNone(source['observed'])
        source['observed'] = '2026-11-15T00:00:00Z'
        source['observed_pointer'] = ['capturedAt']
        with self.assertRaises((AssertionError, KeyError)):
            audit.validate(changed)

    def test_actual_current_summary_detail_and_source_packet_follow_current_data(self):
        html = (ROOT / 'index.html').read_text()
        self.assertTrue(self.renderer.validate_guide(html, self.data))
        self.assertEqual((ROOT / 'endgame-stacking-audit.html').read_text(),
                         self.renderer.detail(self.data))
        excerpts = json.loads((ROOT / 'evidence/endgame-stacking/source-excerpts.json').read_text())
        self.assertEqual(excerpts['sources'], self.data['sources'])

    def test_current_summary_visibility_and_data_drift_are_rejected(self):
        html = (ROOT / 'index.html').read_text()
        block = self.renderer.summary(self.data)
        self.assertIn(block, html)
        for mutant in (html.replace(block, '', 1),
                       html.replace(block, block + block, 1),
                       html.replace(block, '<div hidden>' + block + '</div>', 1),
                       html.replace(block, '<template>' + block + '</template>', 1)):
            with self.assertRaises(AssertionError):
                self.renderer.validate_guide(mutant, self.data)
        changed = copy.deepcopy(self.data)
        next(c for c in changed['components'] if c['id'] == 'goggles-ds')['state'] = 'unknown'
        self.assertTrue(audit.validate(changed))
        with self.assertRaises(AssertionError):
            self.renderer.validate_guide(html, changed)


if __name__ == '__main__':
    unittest.main()
