"""Behavioral regressions for source-bound arithmetic and evidence boundaries.

These checks test what the supplied evidence is allowed to establish, not live DDO.
"""
import copy
import json
import unittest
from pathlib import Path
import stacking_audit as audit
from build_stacking_audit import detail, summary, validate_guide


class StackingAuditTests(unittest.TestCase):
    def setUp(self):
        self.data=audit.load()

    def component(self,data,cid):
        return next(c for c in data['components'] if c['id']==cid)

    def test_real_source_contexts_values_types_and_identities_validate(self):
        self.assertTrue(audit.validate(self.data))

    def test_supported_gear_arithmetic_is_not_a_character_total(self):
        for stat,expected in [('PRR',132),('MRR',72),('HP',108),('Healing Amplification',63),
                              ('Greater Marksmanship damage',2),('Greater Marksmanship attack',3),
                              ('Ranged threat reduction',22),('Sneak dice',3)]:
            with self.subTest(stat=stat):
                result=audit.subtotal(self.data,stat)
                self.assertTrue(result['complete'])
                self.assertEqual(result['total'],expected)

    def test_same_type_duplicates_choose_maximum_once(self):
        expected={'PRR':{'earth-sky-prr'},'Doubleshot':{'goggles-ds'},
                  'Armor-Piercing':{'pendant-ap'},'Intelligence':set(),
                  'Constitution':set(), 'Fortitude':set()}
        for stat,suppressed in expected.items():
            with self.subTest(stat=stat):self.assertEqual(set(audit.subtotal(self.data,stat)['suppressed']),suppressed)

    def test_artifact_does_not_transitively_prove_other_types_stack(self):
        result=audit.subtotal(self.data,'Ranged Power')
        self.assertIsNone(result['total'])
        topaz=self.component(self.data,'topaz-rp');lunar=self.component(self.data,'lunar-rp')
        artifact=self.component(self.data,'monolith-rp')
        self.assertIsNone(audit.proof(self.data,'Ranged Power',topaz,lunar))
        self.assertEqual(audit.proof(self.data,'Ranged Power',topaz,artifact),'artifact-other-types')
        self.assertEqual(audit.proof(self.data,'Ranged Power',lunar,artifact),'artifact-other-types')
        self.assertIn('topaz-rp',result['excluded']);self.assertIn('lunar-rp',result['excluded'])

    def test_unproven_mixed_type_totals_are_withheld(self):
        for stat in ['Doubleshot','Seeker','Intelligence','Armor-Piercing','Constitution','Fortification','Accuracy','Fortitude','Reflex','Will']:
            with self.subTest(stat=stat):
                result=audit.subtotal(self.data,stat)
                self.assertIsNone(result['total']);self.assertFalse(result['complete'])
                self.assertTrue(result['missing_interactions'] or result['excluded'])

    def test_removing_positive_rules_withholds_previously_supported_results(self):
        for rid,stat in [('prr-combination','PRR'),('mrr-combination','MRR'),('vitality-combination','HP')]:
            data=copy.deepcopy(self.data)
            data['rules']=[r for r in data['rules'] if r['id']!=rid]
            with self.subTest(rule=rid):
                self.assertIsNone(audit.subtotal(data,stat)['total'])

    def test_missing_same_type_rule_does_not_silently_suppress_duplicates(self):
        data=copy.deepcopy(self.data)
        data['rules']=[r for r in data['rules'] if r['kind']!='same_type_max']
        result=audit.subtotal(data,'Greater Marksmanship damage')
        self.assertIsNone(result['total']);self.assertTrue(result['missing_interactions'])

    def test_forged_rule_scope_is_rejected_even_when_quote_is_real(self):
        for field,value in [('stats',['*']),('types',['Exceptional']),('kind','pair')]:
            data=copy.deepcopy(self.data)
            rule=next(r for r in data['rules'] if r['id']=='prr-combination')
            rule[field]=value
            with self.subTest(field=field),self.assertRaises((AssertionError,KeyError)):audit.validate(data)

    def test_invented_positive_rule_cannot_admit_ranged_power_total(self):
        data=copy.deepcopy(self.data)
        data['rules'].append(dict(id='invented',source='stack',quote='Bonuses of the same type do not stack:',
                                 kind='different_types',types=['Enhancement'],stats=['Ranged Power']))
        with self.assertRaises((AssertionError,KeyError)):audit.validate(data)

    def test_value_type_stat_and_channel_mutations_are_rejected(self):
        mutations=[('amount',41),('bonus_type','Exceptional'),('stat','Constitution'),('channel','build')]
        for field,value in mutations:
            data=copy.deepcopy(self.data);self.component(data,'defense-prr')[field]=value
            with self.subTest(field=field),self.assertRaises(AssertionError):audit.validate(data)

    def test_source_url_revision_pointer_quote_and_hash_mutations_are_rejected(self):
        mutations=[('url','https://ddowiki.com/page/Fortification'),('revision','https://ddowiki.com/index.php?title=Stack&oldid=999'),
                   ('pointer',['receipts',2,'text']),('quote','Invented +999 Ranged Power'),('sha256','0'*64)]
        for field,value in mutations:
            data=copy.deepcopy(self.data);data['sources']['prr-rule'][field]=value
            with self.subTest(field=field),self.assertRaises((AssertionError,KeyError,IndexError)):audit.validate(data)

    def test_component_provenance_is_required_even_when_quote_and_amount_exist(self):
        for field, pointer in [('revision', 'revision_pointer'), ('observed', 'observed_pointer')]:
            data=copy.deepcopy(self.data)
            source=data['sources']['defense']
            source[field]=None;source[pointer]=None
            with self.subTest(field=field):
                with self.assertRaises(AssertionError):audit.validate(data)
                result=audit.subtotal(data,'MRR')
                self.assertIn('defense-mrr',result['excluded'])
                self.assertFalse(result['complete'])
                with self.assertRaises(AssertionError):validate_guide((audit.ROOT/'index.html').read_text(),data)

    def test_interaction_rule_provenance_is_required_even_when_quote_is_real(self):
        for field, pointer in [('revision', 'revision_pointer'), ('observed', 'observed_pointer')]:
            data=copy.deepcopy(self.data)
            source=data['sources']['mrr-rule']
            source[field]=None;source[pointer]=None
            # The unqualified retained rule stays visible, but cannot prove an edge.
            audit.validate(data)
            with self.subTest(field=field):
                result=audit.subtotal(data,'MRR')
                self.assertIsNone(result['total'])
                self.assertTrue(result['missing_interactions'])
                self.assertIn('Unverified provenance: excluded from calculations',detail(data))
                with self.assertRaises(AssertionError):validate_guide((audit.ROOT/'index.html').read_text(),data)

    def test_fixed_factual_clauses_require_source_provenance(self):
        for sid in ['augment-min-level','augment-values','skull-con','nearly-complete','cut-to-soul-fresh','marksmanship-rule']:
            data=copy.deepcopy(self.data)
            data['sources'][sid]['observed']=None
            data['sources'][sid]['observed_pointer']=None
            with self.subTest(source=sid):
                for render in (summary,detail):
                    with self.assertRaises(AssertionError):render(data)

    def test_body_text_and_receipt_creation_are_not_observation_context(self):
        data=copy.deepcopy(self.data)
        source=data['sources']['mrr-rule']
        source['observed']=source['quote'];source['observed_pointer']=['text']
        self.assertFalse(audit.source_provenance(source))
        with self.assertRaises(AssertionError):audit.validate(data)
        source['observed']='2026-11-07T20:00:00Z';source['observed_pointer']=['created_at_utc']
        self.assertFalse(audit.source_provenance(source))

    def test_public_renderers_reject_forged_nonnull_source_metadata(self):
        for field,value in [('observed','2099-01-01T00:00:00Z'),('revision','https://ddowiki.com/index.php?title=Magical_Resistance_Rating&oldid=1')]:
            data=copy.deepcopy(self.data);data['sources']['mrr-rule'][field]=value
            with self.subTest(field=field):
                for render in (summary,detail):
                    with self.assertRaises(AssertionError):render(data)

    def test_verified_and_conditional_other_effects_require_provenance(self):
        for eid in ['light-absorption','demonic-shield']:
            data=copy.deepcopy(self.data)
            effect=next(e for e in data['non_total_effects'] if e['id']==eid)
            source=data['sources'][effect['sources'][0]]
            source['observed']=None;source['observed_pointer']=None
            with self.subTest(effect=eid):
                with self.assertRaises(AssertionError):audit.validate(data)
                with self.assertRaises(AssertionError):detail(data)

    def test_live_body_contributions_match_derived_totals_and_do_not_restore_fortification(self):
        html=(audit.ROOT/'index.html').read_text()
        for old,new in [('132 gear PRR','133 gear PRR'),('72 gear MRR','32 gear MRR'),('Combined Fortification remains unverified','Fortification is 100% from one augment'),('Your own comes from items.','Item fortification is an enhancement bonus that stacks with Insightful Fortification. Your own comes from items.')]:
            with self.subTest(claim=old),self.assertRaises(AssertionError):
                validate_guide(html.replace(old,new),self.data)

    def test_item_craft_source_conflict_stays_excluded_without_swap(self):
        c=self.component(self.data,'skull-con')
        self.assertEqual(c['state'],'conflicting')
        self.assertEqual(c['amount'],16)
        self.assertIn('skull-con',audit.subtotal(self.data,'Constitution')['excluded'])
        self.assertIn('nearly-complete',c['related_sources'])
        self.assertIn('Constitution +15',self.data['sources']['nearly-complete']['quote'])

    def test_multi_effect_page_cannot_launder_value_into_another_stat(self):
        for cid,stat in [('armor-ds','Armor-Piercing'),('armor-accuracy','Deadly'),('armor-ds','Ranged alacrity'),('marksmanship-goggles-damage','Greater Marksmanship attack'),('marksmanship-goggles-attack','Greater Marksmanship damage')]:
            data=copy.deepcopy(self.data);self.component(data,cid)['stat']=stat
            with self.subTest(component=cid),self.assertRaises(AssertionError):audit.validate(data)

    def test_capture_timestamp_cannot_be_relabelled_as_newer(self):
        data=copy.deepcopy(self.data);data['sources']['prr-rule']['observed']='2099-01-01T00:00:00Z'
        with self.assertRaises(AssertionError):audit.validate(data)

    def test_summary_changes_when_component_qualification_is_downgraded(self):
        html=(audit.ROOT/'index.html').read_text()
        for cid in ['cloak-ds','solar-sneak','ring-threat','healing-amp']:
            data=copy.deepcopy(self.data);self.component(data,cid)['state']='unknown'
            audit.validate(data)
            with self.subTest(component=cid),self.assertRaises(AssertionError):validate_guide(html,data)

    def test_summary_hidden_ancestor_is_rejected(self):
        html=(audit.ROOT/'index.html').read_text();block=summary(self.data)
        for wrapper in ['div hidden','template','details']:
            mutated=html.replace(block,'<'+wrapper+'>'+block+'</'+wrapper.split()[0]+'>')
            with self.subTest(wrapper=wrapper),self.assertRaises(AssertionError):validate_guide(mutated,self.data)

    def test_duplicate_component_identity_is_rejected(self):
        data=copy.deepcopy(self.data);data['components'].append(copy.deepcopy(data['components'][0]))
        with self.assertRaises(AssertionError):audit.validate(data)

    def test_unknown_and_conflicting_cannot_be_activated_by_caller(self):
        for state in ['unknown','conflicting']:
            data=copy.deepcopy(self.data);c=self.component(data,'defense-prr')
            c['state']=state;c['requires']=['force-verified']
            result=audit.subtotal(data,'PRR',active=['force-verified'])
            self.assertIn(c['id'],result['excluded']);self.assertNotIn(c['id'],result['counted'])
            self.assertFalse(result['complete'])

    def test_condition_requires_all_terms_and_never_enters_standing_sum(self):
        data=copy.deepcopy(self.data);c=self.component(data,'defense-prr')
        c['state']='conditional';c['requires']=['equipped','condition-met']
        audit.validate(data)
        self.assertIn(c['id'],audit.subtotal(data,'PRR')['excluded'])
        self.assertIn(c['id'],audit.subtotal(data,'PRR',active=['equipped'])['excluded'])
        self.assertEqual(audit.subtotal(data,'PRR',active=['equipped','condition-met'])['total'],132)

    def test_full_kit_cannot_be_certified_at_level35(self):
        for stat in ['PRR','MRR','Doubleshot','HP']:
            result=audit.subtotal(self.data,stat,level=35)
            self.assertIsNone(result['total']);self.assertFalse(result['complete'])
        source=self.data['sources']['augment-min-level']['quote']
        self.assertIn('increases the slotted item’s minimum level',source)
        for sid in ['defense-min-level','false-life-min-level']:
            self.assertRegex(self.data['sources'][sid]['quote'],r'Minimum Level\s+36')

    def test_fortification_quality_needs_its_own_positive_edges(self):
        result=audit.subtotal(self.data,'Fortification')
        self.assertEqual(set(result['excluded']),{'fort-enh','fort-insight','fort-quality'})
        self.assertFalse(audit.source_provenance(self.data['sources']['fortification-rule']))
        self.assertIsNone(audit.proof(self.data,'Fortification',self.component(self.data,'fort-enh'),self.component(self.data,'fort-insight')))
        self.assertIsNone(result['total'])

    def test_same_type_untype_or_feat_is_not_automatically_maximized(self):
        for typ in ['Untyped','Feat']:
            a={'channel':'build','bonus_type':typ};b=a.copy()
            self.assertIsNone(audit.proof(self.data,'Doubleshot',a,b))

    def test_cross_channel_proof_does_not_leak(self):
        a=self.component(self.data,'defense-prr');b=copy.deepcopy(self.component(self.data,'lunar-prr'))
        b['channel']='enemy'
        self.assertIsNone(audit.proof(self.data,'PRR',a,b))

    def test_dodge_bypass_cannot_be_reclassified_as_avoidance(self):
        data=copy.deepcopy(self.data);self.component(data,'sight-beyond-sight')['stat']='Dodge'
        with self.assertRaises(AssertionError):audit.validate(data)

    def test_optional_second_set_and_mythic_do_not_enter_selected_totals(self):
        counted=audit.subtotal(self.data,'MRR')['counted']
        self.assertEqual(set(counted),{'defense-mrr','compass-insight-mrr','compass-quality-mrr'})
        self.assertFalse(any(c['bonus_type']=='Mythic' for c in self.data['components']))

    def test_doubleshot_softcap_boundary_and_above_200(self):
        for raw,expected in [(0,0),(199,199),(200,200),(201,200.5),(230,215),(400,300)]:
            self.assertEqual(audit.doubleshot_effective(raw),expected)
        with self.assertRaises(AssertionError):audit.doubleshot_effective(-1)

    def test_rendered_guide_and_detail_are_current_calculated_results(self):
        html=(audit.ROOT/'index.html').read_text()
        self.assertTrue(validate_guide(html,self.data))
        self.assertEqual((audit.ROOT/'endgame-stacking-audit.html').read_text(),detail(self.data))

    def test_summary_hidden_removed_stale_or_duplicate_is_rejected(self):
        html=(audit.ROOT/'index.html').read_text();block=summary(self.data)
        mutants=[html.replace(block,''),html.replace(block,block+block),
                 html.replace('id="selected-stacking-summary"','hidden id="selected-stacking-summary"'),
                 html.replace('<td>132</td>','<td>133</td>')]
        for mutated in mutants:
            with self.assertRaises(AssertionError):validate_guide(mutated,self.data)

    def test_unsupported_historical_claims_remain_in_qualified_log(self):
        html=(audit.ROOT/'index.html').read_text()
        self.assertTrue(validate_guide(html,self.data))
        from test_lamordia_handling import Document
        old=[n for n in Document(html).root.nodes('details') if n.attrs.get('id')=='endgame-historical-notes'][0]
        self.assertIn('Historical log, not asserted current totals.',old.text())
        self.assertIn('92 from the build',old.text())
        self.assertIn('historical solver Constitution 32',summary(self.data))

if __name__=='__main__':unittest.main()
