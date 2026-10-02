#!/usr/bin/env python3
"""Composite the 3x cursor (hotspot = pointer tip) onto each manifest screenshot at the click point.
Clamps so the whole cursor stays in frame. Writes annotated/ PNGs and updates manifest entries
with `annotated` path + cursor placement. Usage: python3 journey/annotate.py [--cycle N]"""
import json, os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CURSOR = Image.open(os.path.join(HERE, 'assets', 'cursor-3x.png')).convert('RGBA')  # 141x198
HOT = (27, 30)  # tip in 3x space (SVG tip 9,10 * 3)
cycle = int(sys.argv[sys.argv.index('--cycle') + 1]) if '--cycle' in sys.argv else None
mpath = os.path.join(HERE, 'manifest.json')
m = json.load(open(mpath))
for e in m['entries']:
    if cycle is not None and e['cycle'] != cycle:
        continue
    src = os.path.join(HERE, e['screenshot'])
    out_dir = os.path.join(os.path.dirname(os.path.dirname(src)), 'annotated')
    os.makedirs(out_dir, exist_ok=True)
    im = Image.open(src).convert('RGBA')
    info = None
    if e.get('clicked'):
        tx, ty = e['clicked']['click']['x'], e['clicked']['click']['y']
        px, py = tx - HOT[0], ty - HOT[1]
        cpx = max(0, min(px, im.width - CURSOR.width)); cpy = max(0, min(py, im.height - CURSOR.height))
        im.alpha_composite(CURSOR, (cpx, cpy))
        info = {'tip': [tx, ty], 'paste': [cpx, cpy], 'scale': '3x', 'clamped': (cpx, cpy) != (px, py)}
    dst = os.path.join(out_dir, os.path.basename(src))
    im.convert('RGB').save(dst, optimize=True)
    e['annotated'] = os.path.relpath(dst, HERE)
    e['cursor'] = info
json.dump(m, open(mpath, 'w'), indent=2)
print('annotated', sum(1 for e in m['entries'] if cycle is None or e['cycle'] == cycle))
