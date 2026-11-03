"""Offline structural checks for the current guide, not game-mechanics validation."""

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "index.html"
VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}


class GuideDocument(HTMLParser):
    """Collect actual attributes and displayed build text, ignoring comments/scripts."""

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.ids = Counter()
        self.references = []
        self.build_markers = []
        self.has_base = False
        self._stack = []
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids[attributes["id"]] += 1
        for name in ("href", "src"):
            if attributes.get(name) is not None:
                self.references.append((name, attributes[name], self.getpos()[0]))
        if tag == "base":
            self.has_base = True
        marker = None
        if "build-date" in (attributes.get("class") or "").split():
            marker = []
            self.build_markers.append(marker)
        if tag not in VOID_ELEMENTS:
            self._stack.append((tag, marker))

    def handle_endtag(self, tag):
        for position in range(len(self._stack) - 1, -1, -1):
            if self._stack[position][0] == tag:
                del self._stack[position:]
                break

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_ELEMENTS:
            self.handle_endtag(tag)

    def handle_data(self, data):
        if self._stack and self._stack[-1][0] in {"script", "style"}:
            return
        for _, marker in self._stack:
            if marker is not None:
                marker.append(data)


def local_target(url):
    """Return a guide-relative file and fragment; never fetch external URLs."""
    parts = urlsplit(url.strip())
    if parts.scheme or parts.netloc:
        return None
    local_path = unquote(parts.path or "index.html")
    if local_path.startswith("/"):
        raise ValueError(f"Expected a guide-relative URL, got {url!r}")
    target = (ROOT / local_path).resolve()
    # Traversal outside the repo is not a guide-relative asset.
    target.relative_to(ROOT)
    if target.is_dir():
        target /= "index.html"
    return target, unquote(parts.fragment)


class GuideIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guide_bytes = GUIDE.read_bytes()
        cls.document = GuideDocument(cls.guide_bytes.decode("utf-8"))

    def test_current_snapshot_matches_displayed_build(self):
        markers = ["".join(parts).strip() for parts in self.document.build_markers]
        self.assertEqual(len(markers), 1, "Expected one displayed build-date marker")
        match = re.fullmatch(r"build (\d{2}-\d{2}-\d{2}\.[1-9]\d*)", markers[0])
        self.assertIsNotNone(match, f"Invalid displayed build: {markers[0]!r}")
        snapshot = ROOT / "versions" / f"{match.group(1)}.html"
        self.assertTrue(snapshot.is_file(), f"Missing current snapshot: {snapshot.relative_to(ROOT)}")
        self.assertTrue(
            self.guide_bytes == snapshot.read_bytes(),
            f"index.html differs from {snapshot.relative_to(ROOT)}",
        )

    def test_ids_are_unique(self):
        duplicates = {key: count for key, count in self.document.ids.items() if count > 1}
        self.assertFalse(duplicates, f"Duplicate HTML IDs: {duplicates}")

    def test_internal_fragments_resolve(self):
        for name, url, line in self.document.references:
            if name != "href":
                continue
            with self.subTest(line=line, href=url):
                target = local_target(url)
                if target is None:
                    continue
                path, fragment = target
                if path == GUIDE and fragment and fragment.lower() != "top":
                    self.assertIn(fragment, self.document.ids, f"Missing same-page anchor: {fragment!r}")

    def test_local_assets_exist(self):
        self.assertFalse(self.document.has_base, "A base element needs an explicit URL-resolution update")
        for name, url, line in self.document.references:
            with self.subTest(line=line, attribute=name, url=url):
                target = local_target(url)
                if target is not None:
                    self.assertTrue(target[0].is_file(), f"Missing local target: {url!r}")


if __name__ == "__main__":
    unittest.main()
