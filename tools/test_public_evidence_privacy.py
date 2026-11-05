"""Public source fixtures exclude unnecessary editor identity metadata."""
import hashlib
import ipaddress
import json
import re
import unittest
from pathlib import Path

FIX = Path(__file__).resolve().parent / 'fixtures/endgame-evidence'
IPV4 = re.compile(r'(?<![\w])(?:\d{1,3}\.){3}\d{1,3}\b')
IPV6 = re.compile(r'(?<![0-9A-Za-z:])(?:[0-9A-Fa-f]{0,4}:){2,}[0-9A-Fa-f:.]*')
EDITOR_KEYS = {'author', 'author_user', 'based_on_work_by', 'editor_label', 'editor_help',
               'editor_normal_url', 'footer_user_label', 'footer_user_help',
               'footer_user_normal_url', 'primary_author_label', 'primary_author_help',
               'primary_author_normal_url'}

def validate_public(value):
    if isinstance(value, dict):
        assert not (value.keys() & EDITOR_KEYS)
        for child in value.values(): validate_public(child)
    elif isinstance(value, list):
        for child in value: validate_public(child)
    elif isinstance(value, str):
        for match in list(IPV4.finditer(value)) + list(IPV6.finditer(value)):
            try: ipaddress.ip_address(match.group().rstrip('.'))
            except ValueError: continue
            raise AssertionError('IP address in public source fixture')
        assert not re.search(r'(?<![:/\w])/(?:home|Users|workspace|tmp|root)(?:/|\b)', value)
        assert 'User:' not in value and 'Special:Contributions' not in value
        for line in value.splitlines():
            if 'This page was last modified' in line:
                assert ' by ' not in line
        try: embedded = json.loads(value)
        except ValueError: return
        if isinstance(embedded, (dict, list)): validate_public(embedded)

class PublicEvidencePrivacyTests(unittest.TestCase):
    def test_all_public_evidence_excludes_editor_identifiers(self):
        for path in FIX.rglob('*.json'):
            with self.subTest(path=path.name): validate_public(json.loads(path.read_text()))

    def test_ip_in_nested_or_stringified_capture_is_rejected(self):
        for value in [{'modified': 'Anonymous user 192.0.2.7.'},
                      {'text': json.dumps({'modified': 'Anonymous user 2001:db8::7'})},
                      {'content': [{'author_user': 'ExampleEditor'}]},
                      {'context': '/home/example/private-capture'}]:
            with self.subTest(value=value), self.assertRaises(AssertionError): validate_public(value)

    def test_redaction_manifest_identifies_public_derivatives(self):
        ledger = json.loads((FIX / 'public-redaction.json').read_text())
        self.assertGreater(len(ledger['files']), 0)
        for record in ledger['files']:
            data = (FIX / record['path']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), record['public_sha256'])
            self.assertEqual(len(data), record['public_bytes'])
            self.assertNotEqual(record['original_sha256'], record['public_sha256'])

    def test_source_mapping_hashes_refer_to_public_bytes(self):
        for source in json.loads((FIX / 'sources.json').read_text()):
            if source.get('public_file_sha256'):
                self.assertEqual(hashlib.sha256((FIX / source['retained_file']).read_bytes()).hexdigest(), source['public_file_sha256'])

    def test_source_credit_and_license_are_retained(self):
        readme = (FIX / 'README.md').read_text()
        self.assertIn('https://ddowiki.com/', readme)
        self.assertIn('https://creativecommons.org/licenses/by-sa/2.5/', readme)
        self.assertIn('complete original captures are retained privately', readme)

if __name__ == '__main__': unittest.main()
