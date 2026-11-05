"""Version-page rendering paths, without relaxing content or fragment equality."""
import unittest
from pathlib import Path
from build_snapshot import snapshot_html, current_build
from test_guide_integrity import GuideDocument, local_target, ROOT


def validate_snapshot(html, path, expected_html):
    assert html == snapshot_html(expected_html), 'Unexplained snapshot content change'
    document = GuideDocument(html)
    assert not document.has_base, 'Base tags change same-page navigation'
    for name, url, line in document.references:
        target = local_target(url, path)
        if target is None:
            continue
        file, fragment = target
        assert file.is_file(), (line, url)
        if fragment and file == path and fragment.lower() != 'top':
            assert fragment in document.ids, (line, fragment)


class SnapshotPathTests(unittest.TestCase):
    def setUp(self):
        self.index = (ROOT / 'index.html').read_text()
        self.path = ROOT / 'versions' / f'{current_build(self.index)}.html'
        self.snapshot = self.path.read_text()

    def test_current_snapshot_paths_and_same_page_fragments(self):
        validate_snapshot(self.snapshot, self.path, self.index)
        doc = GuideDocument(self.snapshot)
        images = [url for name, url, _ in doc.references if name == 'src']
        self.assertEqual(len(images), 8)
        self.assertTrue(all(url.startswith('../img/') for url in images))
        self.assertIn('href="../heroic-crafting-print.html"', self.snapshot)
        self.assertEqual(self.snapshot.count('href="#pierce-deception-source-note"'), 3)

    def test_generator_changes_only_relative_files(self):
        before = '''<img src="img/a.jpg" data-src="fake.jpg"><a href="print.html#cost">P</a><a href="#local">L</a><a href="https://example.org/x">E</a><a href="//example.org/x">N</a><!-- <img src="fake.jpg"> --><script>const x = '<img src="fake.jpg">';</script>'''
        expected = before.replace('src="img/a.jpg"', 'src="../img/a.jpg"').replace('href="print.html#cost"', 'href="../print.html#cost"')
        self.assertEqual(snapshot_html(before), expected)

    def test_asset_and_content_regressions_are_rejected(self):
        mutations = [
            self.snapshot.replace('src="../img/', 'src="img/'),
            self.snapshot.replace('href="../heroic-crafting-print.html"', 'href="heroic-crafting-print.html"'),
            self.snapshot.replace('href="#pierce-deception-source-note"', 'href="../#pierce-deception-source-note"'),
            self.snapshot.replace('Constitution contribution is <strong>33</strong>', 'Constitution contribution is <strong>32</strong>'),
        ]
        for html in mutations:
            self.assertNotEqual(html, self.snapshot)
            with self.assertRaises(AssertionError):
                validate_snapshot(html, self.path, self.index)

    def test_real_attributes_only_and_supported_attribute_spelling(self):
        before = '''<a data-href="img/a.jpg" title='example href="img/a.jpg"' href = "img/b.jpg">A</a><IMG SRC='img/c.jpg'><img src=img/d.jpg>'''
        expected = before.replace('href = "img/b.jpg"', 'href = "../img/b.jpg"').replace("SRC='img/c.jpg'", "SRC='../img/c.jpg'").replace('src=img/d.jpg', 'src=../img/d.jpg')
        self.assertEqual(snapshot_html(before), expected)

    def test_resolver_uses_document_location_and_blocks_escape(self):
        self.assertEqual(local_target('#sources', self.path), (self.path, 'sources'))
        self.assertEqual(local_target('../img/cover.jpg', self.path)[0], ROOT / 'img/cover.jpg')
        self.assertFalse(local_target('img/cover.jpg', self.path)[0].exists())
        with self.assertRaises(ValueError):
            local_target('../../outside.html', self.path)


if __name__ == '__main__':
    unittest.main()
