"""Actual selected report route: recipe constraints, source identity, and nonpromotion."""
import copy
import unittest
import wisdom_loadout
import sinew_rocard


class SinewRocardTests(unittest.TestCase):
    def setUp(self):
        self.data = wisdom_loadout.load()

    def test_report_selection_and_numeric_transcription(self):
        result = wisdom_loadout.validate(self.data)
        self.assertEqual((result['items'],result['artifacts']), (14,1))
        self.assertFalse(result['certified_mechanics'])
        self.assertEqual(len(self.data['reported_ledger']),100)
        self.assertEqual(self.data['augment_sets'],[])

    def test_invalid_recipe_mutants_rejected(self):
        for mutate in [
            lambda d:d['items'].pop(),
            lambda d:d['items'][8].update(id=d['items'][9]['id']),
            lambda d:d['items'][0].update(minor_artifact=True),
            lambda d:d['items'][0].update(filled_ml=35),
            lambda d:d['items'][0]['sockets'][0].update(fill='Quickblade'),
            lambda d:d['items'][0]['sockets'][0].update(color='Blue'),
            lambda d:d['items'][10]['sockets'].pop(),
            lambda d:d['augment_sets'].append({'name':'Quickblade'}),
            lambda d:d['reported_ledger'][9].update(total=50),
            lambda d:d['selection'].update(certified_mechanics=True),
            lambda d:d['provenance'].update(sha256='0'*64),
            lambda d:d['query_summary']['targets'].reverse(),
            lambda d:d['limitations'].__setitem__(0, 'Independently certified'),
            lambda d:d['items'][11]['sockets'][-1].update(color='Green'),
        ]:
            d=copy.deepcopy(self.data);mutate(d)
            with self.assertRaises(ValueError):wisdom_loadout.validate(d)

    def test_generated_text_does_not_transfer_old_proofs(self):
        recipe=wisdom_loadout.render_recipe(self.data)
        summary=wisdom_loadout.render_onepage_rows(self.data)
        audit=sinew_rocard.audit_summary(self.data)
        for text in [recipe,summary,audit]:
            self.assertNotIn('Derived selected-gear',text)
            self.assertNotIn('Quickblade 15 Artifact',text)
        self.assertIn('37 versus 36',recipe)
        self.assertIn('20 versus 19',recipe)
        self.assertIn('one negative level',recipe)
        self.assertIn('permanent',recipe)
        self.assertIn('procurement remains conditional',recipe)
        self.assertIn('not an original solver output',audit)
        detail=sinew_rocard.audit_detail(self.data)
        for anchor in ['components','unverified','rules','sources','gap-survival-whole-build','gap-whole-build-doubleshot']:
            self.assertIn('id="'+anchor+'"',detail)


if __name__=='__main__':unittest.main()
