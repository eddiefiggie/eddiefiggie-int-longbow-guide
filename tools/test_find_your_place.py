"""Native entry-point routing contracts, not rendered or mechanics certification."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
LINKS = {
'Full-BAB schedule':'heroic-feats', '3/4-BAB schedule':'heroic-feats',
'Aasimar Scourge selections and separate class grant':'aasimar-scourge-feats',
'class split and life-specific exceptions':'class-split',
'level-by-level roadmap':'levelling-roadmap', 'AP purchase order':'action-points-by-level',
'DP purchase order':'destiny-points-by-level', 'Scourge Harper substitution':'harper-agent-14-ap',
'epic and legendary feat schedule':'epic-and-legendary-feats',
'30–36 transition and endgame kit':'endgame-kit-ml35-36',
'level 1–2 kit remains unresolved':'early-gear-coverage', 'bow ladder':'bow-ladder-levels-1-36',
**{band.replace('-', '–'):'gear-band-'+band for band in ['1-4','5-9','10-14','15-19','20-29']}}


def validate(html):
    html=re.sub(r'<!--.*?-->', '', html, flags=re.S)
    blocks=re.findall(r'<details id="find-your-place">(.*?)</details>',html,re.S)
    assert len(blocks)==1, 'one native disclosure'
    block=blocks[0]
    assert block.startswith('\n<summary><strong>Find your place: life schedule and current level</strong></summary>')
    assert html.index('<details id="find-your-place">') < html.index('<h2 id="start-here">')
    assert dict((label,target) for target,label in re.findall(r'<a href="#([^"]+)">([^<]+)</a>',block))==LINKS
    for target in LINKS.values(): assert html.count('id="'+target+'"')==1, target
    for band in ['1-4','5-9','10-14','15-19','20-29']:
        assert '<h4 id="gear-band-'+band+'">Levels '+band+'</h4>' in html
    for text in ['do not calculate or replace your build',
                 'not a separate schedule for every life',
                 'retain their timing exceptions',
                 'Follow each item’s minimum level, not the band’s first level']:
        assert text in block, text


class FindYourPlaceTests(unittest.TestCase):
    def test_routes_and_qualifiers(self): validate((ROOT/'index.html').read_text())

    def test_negative_controls(self):
        html=(ROOT/'index.html').read_text()
        for old,new in [
            ('<summary>','<div>'),
            ('<details id="find-your-place">','<details id="find-your-place" hidden>'),
            ('href="#aasimar-scourge-feats">Aasimar','href="#heroic-feats">Aasimar'),
            ('href="#destiny-points-by-level">DP','href="#action-points-by-level">DP'),
            ('href="#gear-band-5-9">5–9','href="#gear-band-1-4">5–9'),
            ('id="gear-band-10-14"','id="missing-band"'),
            ('selections and separate class grant','selections'),
            ('not a separate schedule for every life','a schedule for every life'),
            ('Scourge Harper substitution','Harper'),
            ('level 1–2 kit remains unresolved','complete starter kit'),
            ('Follow each item’s minimum level, not the band’s first level','Equip at the band’s first level'),
        ]:
            with self.subTest(old=old):
                self.assertIn(old,html)
                with self.assertRaises(AssertionError):validate(html.replace(old,new))


if __name__=='__main__':unittest.main()
