"""Validate built production output; exercise a new Markdown post in isolation."""
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
import subprocess
import sys
import shutil

site = 'https://terencez127.github.io'
base = Path('build')
for route in ('index.html', 'archives.html', 'my-super-post.html', 'feeds/python.atom.xml', 'theme/css/journal.css'):
    assert (base / route).is_file(), route
for path in base.rglob('*.html'):
    html = path.read_text()
    assert f'{site}/theme/css/journal.css' in html and f'{site}/feeds/all.atom.xml' in html, path
    assert 'http://terencez127.github.io' not in html, path

def entries(feed):
    return {link.get('href') for link in ET.parse(feed).findall('{*}entry/{*}link')}

assert site + '/my-super-post.html' in entries(base / 'feeds/python.atom.xml')
with TemporaryDirectory() as tmp:
    content = Path(tmp) / 'content'
    out = Path(tmp) / 'output'
    shutil.copytree('content', content)
    slug = 'local-only-publishing-check'
    (content / 'probe.md').write_text(f'Title: Publishing check\nDate: 2099-01-01\nSlug: {slug}\nCategory: Python\n\nTemporary verification paragraph.\n')
    subprocess.run([sys.executable, '-m', 'pelican', str(content), '-s', 'publishconf.py', '-o', str(out), '--fatal', 'warnings', '-e', 'WITH_FUTURE_DATES=true'], check=True)
    assert 'Temporary verification paragraph.' in (out / (slug + '.html')).read_text()
    assert f'{site}/{slug}.html' in (out / 'index.html').read_text()
    assert f'{site}/{slug}.html' in entries(out / 'feeds/all.atom.xml')
print('PASS: HTTPS production links, legacy article and feed, isolated Markdown → article + homepage + Atom.')
