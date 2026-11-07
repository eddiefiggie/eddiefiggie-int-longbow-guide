"""A-004: summaries follow this Guide's purchases, not live-game eligibility."""
from pathlib import Path
import re
import unittest

from test_lamordia_handling import Document, Node, norm
from test_endgame_evidence import validate_preservation

ROOT = Path(__file__).resolve().parents[1]
COMPARISON = 'third-tree-fatesinger-or-legendary-dreadnought-build-decision'
MILESTONES = {'Fate’s Repertoire': 22, 'Pluck of a String': 22,
              'Harmonic Resonance': 24, 'Intoxicating Presence': 24,
              'Arrow of Discord': 25, 'Pianissimo 2': 25,
              'Glitter of Fame': 27, 'Master the Acoustics 3': 28}
CUMULATIVE = {20: 0, 21: 0, 22: 3, 23: 3, 24: 6, 25: 10,
              26: 10, 27: 11, **{level: 14 for level in range(28, 37)}}


def active_nodes(node):
    """Exclude comments (parser behavior), hidden ancestors and inert subtrees.

    This is a document-structure check, not CSS or browser visibility QA.
    """
    if node.tag in {'script', 'style', 'template'} or 'hidden' in node.attrs or 'inert' in node.attrs:
        return []
    return [node] + [descendant for child in node.children if isinstance(child, Node)
                     for descendant in active_nodes(child)]


def active_text(node):
    if node.tag in {'script', 'style', 'template'} or 'hidden' in node.attrs or 'inert' in node.attrs:
        return ''
    return ''.join(active_text(child) if isinstance(child, Node) else child for child in node.children)


def section(html, heading_id):
    nodes = active_nodes(Document(html).root)
    starts = [i for i, n in enumerate(nodes)
              if n.tag in {'h2', 'h3'} and n.attrs.get('id') == heading_id]
    assert len(starts) == 1, 'one actual section: ' + heading_id
    start = starts[0] + 1
    end = next((i for i in range(start, len(nodes)) if nodes[i].tag in {'h2', 'h3'}), len(nodes))
    return nodes[start:end]


def table_rows(nodes):
    tables = [n for n in nodes if n.tag == 'table']
    assert len(tables) == 1, 'one actual table'
    return [[norm(active_text(c)) for c in active_nodes(row) if c.tag == 'td']
            for row in active_nodes(tables[0]) if row.tag == 'tr' and row.nodes('td')]


def by_level(rows, width):
    result = {}
    for row in rows:
        assert len(row) == width, 'expected source columns'
        if row[0].isdigit() and int(row[0]) >= 20:
            level = int(row[0])
            assert level not in result, 'unique source level'
            result[level] = row
    assert set(result) == set(range(20, 37)), 'all epic and legendary rows'
    return result


def plan(html):
    roadmap = by_level(table_rows(section(html, 'levelling-roadmap')), 5)
    dp = by_level(table_rows(section(html, 'destiny-points-by-level')), 4)
    levels = {}
    for ability, expected in MILESTONES.items():
        road_levels = [level for level, row in roadmap.items() if ability in row[2]]
        dp_levels = [level for level, row in dp.items() if ability in row[2]]
        assert road_levels == dp_levels == [expected], 'purchase milestone: ' + ability
        levels[ability] = road_levels[0]
    for rows in (roadmap, dp):
        assert [level for level, row in rows.items() if 'Fatesinger:' in row[2]] == [22, 24, 25, 27, 28]
        assert all('Shiradi:' in rows[level][2] and 'Fatesinger' not in rows[level][2] for level in (20, 21))
    assert [dp[level][3] for level in (20, 21)] == ['Shiradi 12', 'Shiradi 16']
    cumulative, total = {}, 0
    for level, row in dp.items():
        updated = re.findall(r'Fatesinger (\d+)', row[3])
        assert len(updated) <= 1, 'one Fatesinger subtotal per row'
        if updated:
            total = int(updated[0])
        cumulative[level] = total
    assert cumulative == CUMULATIVE, 'actual cumulative Fatesinger DP'
    assert 'Harmonic Resonance (2 points)' in dp[levels['Harmonic Resonance']][2]
    return levels, cumulative


def validate(html):
    levels, cumulative = plan(html)
    first = min(level for level, points in cumulative.items() if points)
    complete = min(level for level, points in cumulative.items() if points == 14)
    nodes = section(html, COMPARISON)
    rows = table_rows(nodes)
    timing = [row for row in rows if row[0] == 'Online while levelling']
    assert len(timing) == 1 and len(timing[0]) == 3, 'actual comparison timing cell'
    assert timing[0][1] == (
        f'In this Guide’s roadmap: Pluck at {levels["Pluck of a String"]}, '
        f'Harmonic Resonance at {levels["Harmonic Resonance"]}, '
        f'Pianissimo at {levels["Pianissimo 2"]}; all 14 points bought by {complete} (see DP order)'
    ), 'comparison follows actual plan'
    verdicts = [n for n in nodes if n.tag == 'p' and norm(active_text(n)).startswith('Verdict:')]
    assert len(verdicts) == 1, 'one actual verdict'
    sentence = (f'In this Guide’s roadmap, Fatesinger purchases start at {first} '
                f'and all 14 points are bought by {complete}.')
    assert sentence in norm(active_text(verdicts[0])), 'verdict follows actual plan'
    assert 'online at 20' not in norm(active_text(verdicts[0])), 'obsolete early timing'
    timing_cell = next(n for n in nodes if n.tag == 'td' and norm(active_text(n)) == timing[0][1])
    assert {a.attrs.get('href') for a in timing_cell.nodes('a')} == {'#levelling-roadmap', '#destiny-points-by-level'}
    assert '#levelling-roadmap' in {a.attrs.get('href') for a in verdicts[0].nodes('a')}


class FatesingerTimingTests(unittest.TestCase):
    def setUp(self):
        self.html = (ROOT / 'index.html').read_text()

    def test_actual_roadmap_dp_and_both_summaries_agree(self):
        validate(self.html)
        validate_preservation(self.html)  # Original full-build hash, exact prose reversals only.

    def test_early_or_wrong_summary_milestones_fail(self):
        for old, new in [('Pluck at 22', 'Pluck at 20'),
                         ('Harmonic Resonance at 24', 'Harmonic Resonance at 22'),
                         ('Pianissimo at 25', 'Pianissimo at 24'),
                         ('all 14 points bought by 28', 'all 14 points bought by 22'),
                         ('purchases start at 22', 'purchases start at 20'),
                         ('all 14 points are bought by 28', 'all 14 points are bought by 27'),
                         ('In this Guide’s <a href="#levelling-roadmap">roadmap</a>', 'At the earliest possible unlock')]:
            with self.subTest(old=old):
                self.assertIn(old, self.html)
                with self.assertRaises(AssertionError):
                    validate(self.html.replace(old, new))

    def test_roadmap_and_dp_purchase_mutations_fail(self):
        for heading in ('levelling-roadmap', 'destiny-points-by-level'):
            for ability in ('Pluck of a String', 'Harmonic Resonance', 'Pianissimo 2', 'Master the Acoustics 3'):
                start = self.html.index('id="' + heading + '"')
                at = self.html.index(ability, start)
                mutated = self.html[:at] + self.html[at:].replace(ability, 'Omitted purchase', 1)
                with self.subTest(heading=heading, ability=ability), self.assertRaises(AssertionError):
                    validate(mutated)

    def test_wrong_cumulative_dp_or_early_points_fail(self):
        for old, new in [('Shiradi 12</td>', 'Shiradi 9, Fatesinger 3</td>'),
                         ('Shiradi 16</td>', 'Shiradi 13, Fatesinger 3</td>'),
                         ('Fatesinger 3</td>', 'Fatesinger 4</td>'),
                         ('Fatesinger 6</td>', 'Fatesinger 5</td>'),
                         ('Fatesinger 10</td>', 'Fatesinger 14</td>'),
                         ('Fatesinger 11</td>', 'Fatesinger 14</td>'),
                         ('Fatesinger 14, Shadowdancer 1</td>', 'Fatesinger 13, Shadowdancer 1</td>')]:
            with self.subTest(old=old):
                self.assertIn(old, self.html)
                with self.assertRaises(AssertionError):
                    validate(self.html.replace(old, new))

    def test_hidden_or_commented_summaries_fail(self):
        cell = re.search(r'<td>In this Guide’s .*?</td>', self.html)[0]
        verdict = re.search(r'<p><strong>Verdict:</strong>.*?</p>', self.html)[0]
        for part in (cell, verdict):
            for wrapper in ('<!--{}-->', '<template>{}</template>', '<div hidden>{}</div>'):
                with self.subTest(part=part[:30], wrapper=wrapper), self.assertRaises(AssertionError):
                    validate(self.html.replace(part, wrapper.format(part)))

    def test_inline_hidden_text_fails_and_visible_markup_is_accepted(self):
        for text in ('Pluck at 22', 'Fatesinger purchases start at 22'):
            for wrapper in ('<span hidden>{}</span>', '<span inert>{}</span>', '<template>{}</template>'):
                with self.subTest(text=text, wrapper=wrapper), self.assertRaises(AssertionError):
                    validate(self.html.replace(text, wrapper.format(text)))
            validate(self.html.replace(text, '<strong>' + text + '</strong>'))

    def test_full_build_guard_rejects_purchase_and_comparison_changes(self):
        for old, new in [('Master the Acoustics 3', 'Master the Acoustics 2'),
                         ('Fatesinger 10</td>', 'Fatesinger 9</td>'),
                         ('<td>+15 (damage taken is', '<td>+16 (damage taken is')]:
            with self.subTest(old=old):
                self.assertIn(old, self.html)
                with self.assertRaises(AssertionError):
                    validate_preservation(self.html.replace(old, new))


if __name__ == '__main__':
    unittest.main()
