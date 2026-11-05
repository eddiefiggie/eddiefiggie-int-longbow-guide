"""Generate the current version page with document-relative local links."""
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTE = re.compile(
    r'''(?P<name>[^\s=/>]+)(?:\s*=\s*(?:"(?P<double>[^"]*)"|'(?P<single>[^']*)'|(?P<bare>[^\s>]+)))?'''
)


def snapshot_html(html):
    """Change only relative file URLs in real start tags, not same-page anchors."""
    line_offsets = [0]
    for line in html.splitlines(keepends=True):
        line_offsets.append(line_offsets[-1] + len(line))
    edits = []

    class Tags(HTMLParser):
        def handle_starttag(self, tag, attrs):
            raw = self.get_starttag_text()
            line, column = self.getpos()
            start = line_offsets[line - 1] + column
            tag_end = re.match(r'<\s*[^\s/>]+', raw).end()
            # Consume complete attributes, including non-URL quoted values, so
            # text like title='example href="x"' is never treated as a link.
            for match in ATTRIBUTE.finditer(raw, tag_end):
                if match.group('name').lower() not in {'src', 'href'}:
                    continue
                value_group = next((key for key in ('double', 'single', 'bare') if match.group(key) is not None), None)
                if value_group is None:
                    continue
                url = match.group(value_group)
                parts = urlsplit(url)
                if not parts.path or parts.scheme or parts.netloc or url.startswith('/'):
                    continue
                a, b = match.span(value_group)
                edits.append((start + a, start + b, '../' + url))

        handle_startendtag = handle_starttag

    parser = Tags()
    parser.feed(html)
    parser.close()
    for start, end, replacement in reversed(edits):
        html = html[:start] + replacement + html[end:]
    return html


def current_build(html):
    match = re.search(r'class="build-date">build (\d{2}-\d{2}-\d{2}\.[1-9]\d*)<', html)
    if not match:
        raise ValueError('Missing current build marker')
    return match.group(1)


def main():
    html = (ROOT / 'index.html').read_text()
    destination = ROOT / 'versions' / f'{current_build(html)}.html'
    destination.write_text(snapshot_html(html))
    print(destination)


if __name__ == '__main__':
    main()
