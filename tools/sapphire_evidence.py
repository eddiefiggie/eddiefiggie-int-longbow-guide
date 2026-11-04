"""Offline checks of one retained item page and selected Guide occurrences.

Never fetches URLs or executes source scripts. This is a fixed-capture regression
contract, not a generic Wiki parser or certification of modeled game mechanics.
"""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tools/fixtures/sapphire-sting'


def norm(text):
    return ' '.join(text.split())


class Node:
    def __init__(self, tag='', attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []

    def nodes(self, tag):
        return [node for child in self.children if isinstance(child, Node)
                for node in ([child] if child.tag == tag else []) + child.nodes(tag)]

    def text(self, tooltips=False):
        if self.tag in {'script', 'style'}:
            return ''
        if not tooltips and ('tooltip' in self.attrs.get('class', '').split()
                             or 'display: none' in self.attrs.get('style', '')):
            return ''
        return ''.join(c.text(tooltips) if isinstance(c, Node) else c for c in self.children)


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack = [self.root]
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                       'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def one(nodes, label):
    require(len(nodes) == 1, f'{label}: expected one, found {len(nodes)}')
    return nodes[0]


def load_record():
    return json.loads((FIXTURE / 'record.json').read_text())


def verify_bytes(raw, record):
    require(len(raw) == record['size_bytes'], 'source size')
    require(hashlib.sha256(raw).hexdigest() == record['sha256'], 'source SHA-256')


def validate_source(source, record):
    for key, value in record['identity'].items():
        require(source.get(key) == value, f'source identity: {key}')
    html = source['rendered_document_html']
    doc = Document(html).root
    heading = one([n for n in doc.nodes('h1') if n.attrs.get('id') == 'firstHeading'], 'item heading')
    require(norm(heading.text()) == 'Item:Sapphire Sting', 'item variant heading')
    require(any(n.attrs.get('href') == source['permanent_link'] and
                norm(n.text()) == 'Permanent link' for n in doc.nodes('a')), 'DOM revision permalink')
    for marker in record['cache_markers']:
        require(marker in html, f'cache context: {marker}')
    require(record['freshness_warning'] in source['full_visible_text'], 'visible freshness warning')
    require(record['freshness_warning'] in norm(doc.text()), 'DOM freshness warning')
    table = one([n for n in doc.nodes('table') if 'striped' in n.attrs.get('class', '').split()], 'item table')
    fields = {}
    for row in table.nodes('tr'):
        cells = [n for n in row.children if isinstance(n, Node) and n.tag in {'th', 'td'}]
        require(len(cells) >= 2, 'item row context')
        key = norm(cells[0].text())
        require(key not in fields, f'duplicate source field: {key}')
        fields[key] = cells[1]
    for key, value in record['fields'].items():
        require(key in fields and norm(fields[key].text()) == value, f'source field: {key}')
        require(norm_visible(source['full_visible_text']).splitlines().count(f'{key}\t{value}') == 1,
                f'visible field: {key}')
    enchantments = fields['Enchantments']
    entries = [norm(n.text()) for n in enchantments.nodes('li')]
    require(entries == record['enchantments'], 'full enchantment list')
    require('Keen' not in entries, 'Keen must only be described as not listed')
    mythic = one([n for n in enchantments.nodes('li') if norm(n.text()).startswith('Mythic Weapon Boost')], 'Mythic entry')
    require(record['mythic_qualifier'] in norm(mythic.text(tooltips=True)), 'optional Mythic qualifier')
    # +3 is supported independently by both the damage row and enhancement entry.
    require(entries[0] == '+3 Enhancement Bonus', 'enhancement separate from die')
    return {key: norm(node.text()) for key, node in fields.items()}


def norm_visible(text):
    # Preserve field/value separators while normalizing NBSP and whitespace in each field.
    return '\n'.join('\t'.join(norm(part) for part in line.split('\t')) for line in text.splitlines())


def validate_guide(html, source, record):
    fields = validate_source(source, record)
    doc = Document(html).root
    row = one([n for n in doc.nodes('tr') if any(
        a.attrs.get('href') == source['url'] and norm(a.text()) == 'Sapphire Sting'
        for a in n.nodes('a'))], 'Guide ladder row')
    cells = [norm(n.text()) for n in row.children if isinstance(n, Node) and n.tag == 'td']
    profile = fields['Critical threat range'].replace(' / ', '/')
    damage = fields['Damage and Type'].split(' Pierce, Magic')[0].replace(' ', '')
    require(cells == [fields['Minimum Level'], 'Sapphire Sting', fields['Minimum Level'],
        f'listed {profile} (Keen is not listed)',
        damage + ', Ranged Alacrity 10%, Destruction, Maiming, Lesser Human Bane, Purple slot. Bound to Account',
        fields['Location'].replace("'", '’')], 'Guide item cells')
    # These selected blocks are context-bound; unrelated appearances are not certified.
    blocks = [norm(n.text()) for tag in ('tr', 'li', 'p') for n in doc.nodes(tag)]
    for claim in record['guide_claims']:
        block = one([b for b in blocks if b.startswith(claim['starts_with'])], claim['name'])
        # Freeze the full selected context as a drift guard, not a claim that
        # its unrelated mechanics are validated by this item source. This also
        # rejects contradictory additions that preserve the required caveats.
        require(block == claim['context_text'], f"{claim['name']}: context drift")
        for text in claim['required']:
            require(text in block, f"{claim['name']}: {text}")
        for text in ('no Keen', 'not Keen', 'not a Keen bow', 'native 19-20'):
            require(text not in block.removeprefix('Native expanded range is not Keen.'),
                    f"{claim['name']}: unconditional {text}")
