"""Generate a static print reference from three authoritative Guide blocks."""
from html import escape, unescape
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BLOCKS = ('heroic-calamitous-subtotal', 'heroic-calamitous-recipe', 'lamordia-augment-handling')

class Extractor(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.offsets = [0]
        for line in text.splitlines(keepends=True): self.offsets.append(self.offsets[-1]+len(line))
        self.active = None
        self.depth = 0
        self.blocks = {}
        self.feed(text)
        if self.active or set(self.blocks) != set(BLOCKS): raise ValueError('Missing or incomplete source block')
    def source_offset(self):
        line,col = self.getpos()
        return self.offsets[line-1]+col
    def handle_starttag(self, tag, attrs):
        ident = dict(attrs).get('id')
        if ident in BLOCKS:
            if self.active or ident in self.blocks: raise ValueError('Duplicate/nested source block')
            self.active = (ident,tag,self.source_offset())
            self.depth = 0
        if self.active and tag == self.active[1]: self.depth += 1
    def handle_endtag(self, tag):
        if self.active and tag == self.active[1]:
            self.depth -= 1
            if not self.depth:
                ident,_,start = self.active
                end = self.text.index('>',self.source_offset())+1
                self.blocks[ident] = self.text[start:end]
                self.active = None

STYLE = '''body{font:18px/1.5 Georgia,serif;color:#111;background:white;max-width:46rem;margin:2rem auto;padding:0 1rem}
h1{font-size:1.6rem}h2,h4{font-size:1.15rem;break-after:avoid}a{color:#173f73;overflow-wrap:anywhere}
li{margin:.4rem 0}p{margin:.8rem 0}.sources{font-size:.85rem} .sources a{word-break:break-word}
@page{size:auto;margin:16mm}
@media print{body{font-size:11pt;max-width:none;margin:0;padding:0}a{color:inherit}p,li{orphans:3;widows:3}h1,h2,h4{break-after:avoid} .screen-only{display:none}}
'''

def render(source):
    blocks = Extractor(source).blocks
    build = re.findall(r'<span class="build-date">build ([^<]+)</span>', source)
    if len(build) != 1: raise ValueError('One build identity required')
    content = '\n'.join(blocks[k] for k in BLOCKS)
    urls = list(dict.fromkeys(unescape(u) for u in re.findall(r'href="(https://ddowiki.com/[^" ]+)"',content)))
    if len(urls) != 2 or any('oldid=' not in u for u in urls): raise ValueError('Expected two pinned source URLs')
    links = '\n'.join('<li><a href="'+escape(u,quote=True)+'">'+escape(u)+'</a></li>' for u in urls)
    return '''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Heroic Calamitous crafting reference</title><style>'''+STYLE+'''</style></head><body>
<h1>Heroic Calamitous crafting reference</h1>
<p>INT Longbow Guide · build '''+escape(build[0])+''' · Reference extract</p>
<p class="screen-only"><a href="index.html#heroic-calamitous-subtotal">Back to the Guide</a>. Use your browser’s Print command.</p>
'''+content+'''
<h2>Retained source URLs</h2><ol class="sources">
'''+links+'''
</ol></body></html>
'''

if __name__ == '__main__':
    (ROOT/'heroic-crafting-print.html').write_text(render((ROOT/'index.html').read_text()),encoding='utf-8')
