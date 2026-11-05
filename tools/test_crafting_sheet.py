"""Exact extraction/freshness checks; pagination requires rendered print QA."""
from pathlib import Path
import unittest
from build_crafting_sheet import BLOCKS, Extractor, render
from test_lamordia_handling import Document
ROOT=Path(__file__).resolve().parents[1]

def validate(source,sheet):
    assert sheet == render(source), 'stale generated reference'
    blocks=Extractor(source).blocks
    for block in blocks.values(): assert sheet.count(block)==1, 'complete verbatim block'
    assert 'heroic-purchase-checkoff' not in sheet and '<input' not in sheet and '<script' not in sheet
    doc=Document(sheet).root
    ids=[n.attrs['id'] for tag in ['p','div','section'] for n in doc.nodes(tag) if 'id' in n.attrs]
    assert len(ids)==len(set(ids))
    for a in doc.nodes('a'):
        href=a.attrs['href']
        if href.startswith('#'): assert href[1:] in ids
        elif href.startswith('https:'): assert href.startswith('https://ddowiki.com/index.php?title=') and '&oldid=' in href
    urls=[a for a in doc.nodes('a') if a.text().startswith('https:')]
    assert len(urls)==2 and all(a.text()==a.attrs['href'] for a in urls)
    assert 'oldid=720728' in sheet and 'oldid=702384' in sheet

class CraftingSheetTests(unittest.TestCase):
    def test_current_sheet_and_complete_citations(self):
        validate((ROOT/'index.html').read_text(),(ROOT/'heroic-crafting-print.html').read_text())
    def test_faults_and_source_edits(self):
        source=(ROOT/'index.html').read_text();sheet=(ROOT/'heroic-crafting-print.html').read_text()
        for old,new in [('10 of each part','5 of each part'),('not all possible costs','all costs'),
                        ('Heroic - Dreadful','Heroic'),('minimum level to 34','minimum level to 8'),
                        ('a Jeweler’s Tool Kit does not work.',''),('oldid=702384','oldid=1'),
                        ('build 11-05-26.2','build stale')]:
            with self.subTest(old=old):
                assert old in sheet
                with self.assertRaises(AssertionError):validate(source,sheet.replace(old,new))
        for ident in BLOCKS:
            with self.subTest(ident=ident):
                block=Extractor(source).blocks[ident]
                with self.assertRaises(AssertionError):validate(source,sheet.replace(block,''))
                with self.assertRaises(ValueError):render(source.replace(block,''))
        # A later source edit must regenerate, rather than preserve yesterday's extract.
        changed=source.replace('no Bleak Wires listed.','no Bleak Wires listed in this row.',1)
        assert render(changed)!=sheet
        with self.assertRaises(AssertionError):validate(changed,sheet)
