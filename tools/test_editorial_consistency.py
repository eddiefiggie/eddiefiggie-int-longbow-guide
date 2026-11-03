"""Guard repeated selected choices and caveats, without validating game rules."""

from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


def normalized(parts):
    return " ".join("".join(parts).split())


class GuideText(HTMLParser):
    """Read displayed table cells and prose blocks, grouped by heading ID."""

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.tables = defaultdict(list)
        self.blocks = defaultdict(list)
        self._section = None
        self._table = self._row = self._cell = None
        self._blocks = []
        self._ignored = None
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self._ignored = tag
        if tag in {"h2", "h3"}:
            self._section = dict(attrs).get("id")
        if tag == "table":
            self._table = []
            self.tables[self._section].append(self._table)
        elif tag == "tr":
            self._row = []
        elif tag in {"td", "th"}:
            self._cell = []
        if tag in {"p", "li", "tr"}:
            self._blocks.append((self._section, tag, []))

    def handle_endtag(self, tag):
        if tag == self._ignored:
            self._ignored = None
        if tag in {"td", "th"} and self._cell is not None:
            self._row.append(normalized(self._cell))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self._table.append(self._row)
            self._row = None
        elif tag == "table":
            self._table = None
        if self._blocks and self._blocks[-1][1] == tag:
            section, _, parts = self._blocks.pop()
            self.blocks[section].append(normalized(parts))

    def handle_data(self, data):
        if self._ignored:
            return
        if self._cell is not None:
            self._cell.append(data)
        for _, _, parts in self._blocks:
            parts.append(data)


class EditorialConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guide = GuideText((ROOT / "index.html").read_text(encoding="utf-8"))

    def table_with_header(self, section, header):
        matches = [table for table in self.guide.tables[section]
                   if table and header in table[0]]
        self.assertEqual(len(matches), 1, (section, header))
        return matches[0]

    def row(self, table, label):
        matches = [row for row in table[1:] if row and row[0] == label]
        self.assertEqual(len(matches), 1, label)
        return matches[0]

    def roadmap(self):
        return self.table_with_header("levelling-roadmap", "Feat")

    def test_three_quarter_bab_choices_match_roadmap(self):
        detailed = self.table_with_header("heroic-feats", "3/4-BAB past-life class")
        column = detailed[0].index("3/4-BAB past-life class")
        expected = {"12": "Weapon Finesse", "15": "Improved Precise Shot",
                    "18": "Weapon Focus: Ranged"}
        for level, choice in expected.items():
            with self.subTest(level=level):
                selected = self.row(detailed, level)[column]
                self.assertEqual(selected, choice)
                roadmap_level = "16-19" if level == "18" else level
                summary = self.row(self.roadmap(), roadmap_level)[1]
                if level != "18":
                    clauses = [part for part in re.findall(r"\(([^()]*)\)", summary)
                               if "3/4-BAB" in part]
                    self.assertEqual(len(clauses), 1, summary)
                    summary = re.sub(r"\bIPS\b", "Improved Precise Shot", clauses[0])
                self.assertIn(selected, summary)

    def test_scourge_selected_schedule_and_optional_sneak_stay_consistent(self):
        scourge = self.table_with_header("heroic-feats", "Note")
        for level, choice in {"12": "Weapon Finesse", "15": "Weapon Focus: Ranged",
                              "18": "Power Critical"}.items():
            with self.subTest(level=level):
                self.assertEqual(self.row(scourge, level)[1], choice)
        alternatives = [block for block in self.guide.blocks["heroic-feats"]
                        if "Sneak of Shadows" in block]
        self.assertTrue(alternatives)
        for block in alternatives:
            with self.subTest(alternative=block):
                self.assertRegex(block, r"\b18\b")
                self.assertRegex(block, r"\b(?:alternative|optional|candidate)\b")
        purchased = [block for block in self.guide.blocks["heroic-lives"]
                     if "Sneak of Shadows" in block and "Scourge" in block]
        self.assertTrue(purchased)
        for block in purchased:
            self.assertRegex(block, r"\b18\b")

    def test_no_extra_scourge_slot_or_spare_level_twelve_claim(self):
        stale = re.compile(
            r"\beighth\b|\beight (?:picks|slots)\b|"
            r"\bspare (?:level[- ]?)?12 (?:feat )?slot\b|"
            r"\blevel[- ]12 slot is free\b", re.I)
        for section, blocks in self.guide.blocks.items():
            if section in {"audit-log", "sources"}:
                continue
            for block in blocks:
                with self.subTest(section=section, text=block[:100]):
                    self.assertIsNone(stale.search(block), block)

    def test_legendary_trick_shot_caveat_reaches_both_summaries(self):
        detailed = self.table_with_header("epic-and-legendary-feats", "Feat")
        summary = self.table_with_header("the-build-in-one-page", "Area")
        rows = {
            "detailed": self.row(detailed, "36"),
            "one-page": self.row(summary, "Epic and legendary feats"),
            "roadmap": self.row(self.roadmap(), "36"),
        }
        for location, cells in rows.items():
            with self.subTest(location=location):
                text = " ".join(cells)
                self.assertIn("Legendary Trick Shot", text)
                self.assertIn("confirm the slot accepts it", text)

    def test_imbue_summaries_preserve_the_harbinger_condition(self):
        detailed = self.table_with_header("epic-and-legendary-feats", "Feat")
        harbinger = self.row(detailed, "28")
        self.assertEqual(harbinger[1], "Harbinger of Chaos")
        self.assertIn("+2 Imbue dice while Chaotic", " ".join(harbinger))
        summaries = [(section, block) for section, blocks in self.guide.blocks.items()
                     if section not in {"audit-log", "sources"}
                     for block in blocks if "4d6" in block
                     and re.search(r"\bimbue\b|Flaming Arrows", block, re.I)]
        self.assertTrue(summaries)
        for section, block in summaries:
            with self.subTest(section=section):
                self.assertIn("while Chaotic", block)


if __name__ == "__main__":
    unittest.main()
