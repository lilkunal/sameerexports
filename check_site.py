"""Pre-deploy check: inline JS parses (needs node) and internal links resolve. Run after build_site.py."""
import re, os, glob, subprocess, tempfile, sys

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site')
os.chdir(SITE)
errors = []

# every distinct inline script must parse; pages share templates, so dedupe by content
seen = {}
for f in glob.glob('**/*.html', recursive=True):
    for sc in re.findall(r'<script>(.*?)</script>', open(f, encoding='utf-8').read(), re.S):
        seen.setdefault(hash(sc), (f, sc))
for f, sc in seen.values():
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as t:
        t.write(sc)
    r = subprocess.run(['node', '--check', t.name], capture_output=True, text=True)
    os.unlink(t.name)
    if r.returncode:
        errors.append(f'JS syntax in {f}: {r.stderr.strip().splitlines()[-1]}')

# internal links and images resolve
for f in glob.glob('**/*.html', recursive=True):
    if f == '404.html':
        continue
    d = os.path.dirname(f)
    for u in re.findall(r'(?:href|src)="([^"#?]+)', open(f, encoding='utf-8').read()):
        if ':' in u or '${' in u:
            continue
        if not os.path.exists(os.path.normpath(os.path.join(d, u))):
            errors.append(f'broken link in {f}: {u}')

print(f'{len(seen)} distinct scripts checked')
print('\n'.join(errors[:30]) or 'OK')
sys.exit(1 if errors else 0)
