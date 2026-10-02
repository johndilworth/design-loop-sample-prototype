#!/usr/bin/env python3
"""Single-page 'evolution' Lucid Standard Import: rows = key screens, columns = review cycles, using the already
hosted annotated shots (journey/cycles/<N>/asset-urls.json). A screen with no capture in a cycle gets a dashed
'Not captured' placeholder. Column headers carry the cycle number and how many harvested feedback items the
PR that produced that cycle's build applied. No shape `note` fields; short ids (evo-*).
Usage: python3 journey/lucid/build_evolution.py --out journey/evolution/lucid-spec.json"""
import argparse, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); J = os.path.dirname(HERE)
ap = argparse.ArgumentParser(); ap.add_argument('--out', default=os.path.join(J, 'evolution', 'lucid-spec.json')); a = ap.parse_args()
ROWS = [('home-00-landing', 'Landing (home)', '/'),
        ('signup-01-create-account', 'Create account', '/signup'),
        ('signup-03-goals', 'Pick your AI goals', '/onboarding/goals'),
        ('vendor-02-detail', 'Vendor detail', '/vendors/:id'),
        ('vendor-03-review', 'Vendor review', '/vendors/:id/review')]
# header text: keep each line <= ~36 chars at 20pt in the 720px box (a 42-char line wrapped and clipped)
# applied = harvested feedback items of the previous cycle resolved by the PR this cycle was captured from
COLS = [(1, 'baseline · main @ 77283a9', 0, 'initial prototype, no feedback yet'),
        (2, 'PR #1 preview @ 5461dff', 11, 'all 11 cycle-1 stickies'),
        (3, 'PR #2 preview @ 2649ac4', 8, '7 changed + 1 already satisfied'),
        (4, 'PR #3 preview @ 20c1782 (final)', 13, 'all 13 stickies, 2 are reversals')]
URLS = {c: json.load(open(os.path.join(J, 'cycles', str(c), 'asset-urls.json'))) for c, *_ in COLS}
IW, IH, GX, GY, LW, X0, Y0, HH = 720, 512, 80, 120, 420, 480, 520, 260
shapes = [
    {'id': 'evo-title', 'type': 'text', 'boundingBox': {'x': 0, 'y': 0, 'w': X0 + 4 * (IW + GX), 'h': 200},
     'text': '<p style="font-size:40pt;text-align:left"><b>Northwind AI Ops · Design loop · Evolution, cycle 1 to cycle 4</b><br>'
             '<span style="font-size:20pt">Same screens, captured at 1440×1024 after each round of Lucid sticky-note feedback. '
             f'{11+8+13} feedback items applied across 3 PRs (#1, #2, #3; all still open).</span></p>'}]
for j, (c, src, n, why) in enumerate(COLS):
    x = X0 + j * (IW + GX)
    shapes.append({'id': f'evo-col-{c}', 'type': 'rectangle', 'boundingBox': {'x': x, 'y': 240, 'w': IW, 'h': HH},
                   'style': {'fill': {'type': 'color', 'color': '#1F2A5A' if c == 4 else '#3A4FD8'}, 'stroke': {'color': '#1F2A5A', 'width': 2, 'style': 'solid'}, 'textColor': '#FFFFFF'},
                   'text': f'<p style="font-size:30pt;text-align:center"><b>Cycle {c}</b><br><span style="font-size:20pt"><b>{n} feedback items applied</b><br>'
                           f'{why}<br>{src}</span></p>'})
for i, (key, label, route) in enumerate(ROWS):
    y = Y0 + i * (IH + GY)
    shapes.append({'id': f'evo-row-{i+1}', 'type': 'text', 'boundingBox': {'x': 0, 'y': y + 120, 'w': LW, 'h': 260},
                   'text': f'<p style="font-size:26pt;text-align:left"><b>{label}</b><br><span style="font-size:16pt">{key}<br>{route}</span></p>'})
    for j, (c, *_rest) in enumerate(COLS):
        x = X0 + j * (IW + GX); sid = f'evo-{i+1}-c{c}'
        url = URLS[c].get(key)
        if url:
            shapes.append({'id': sid, 'type': 'image', 'boundingBox': {'x': x, 'y': y, 'w': IW, 'h': IH},
                           'image': {'type': 'image', 'url': url}, 'stroke': {'color': '#C9CED8', 'width': 2, 'style': 'solid'}})
        else:
            shapes.append({'id': sid, 'type': 'rectangle', 'boundingBox': {'x': x, 'y': y, 'w': IW, 'h': IH},
                           'style': {'fill': {'type': 'color', 'color': '#EEF0F4'}, 'stroke': {'color': '#8A90A0', 'width': 2, 'style': 'dashed'}},
                           'text': f'<p style="font-size:28pt;text-align:center"><b>Not captured</b><br><span style="font-size:18pt">'
                                   f'{key} was not part of the cycle {c} journey</span></p>'})
for sh in shapes:
    sh['text'] = re.sub(r'(\w+)="([^"]*)"', r"\1='\2'", sh['text']) if 'text' in sh else None
    if sh['text'] is None: del sh['text']
doc = {'version': 1, 'pages': [{'id': 'p1', 'title': 'Evolution c1 > c4', 'shapes': shapes, 'lines': []}]}
os.makedirs(os.path.dirname(a.out), exist_ok=True)
s = json.dumps(doc, separators=(',', ':'), ensure_ascii=False); open(a.out, 'w').write(s)
grid = {key: {c: URLS[c].get(key) for c, *_ in COLS} for key, *_ in ROWS}
json.dump({'rows': [r[0] for r in ROWS], 'columns': [{'cycle': c, 'source': s_, 'feedbackApplied': n, 'note': w} for c, s_, n, w in COLS],
           'grid': grid, 'image': {'w': IW, 'h': IH}}, open(os.path.join(os.path.dirname(a.out), 'lucid-layout.json'), 'w'), indent=2)
print(a.out, len(s), 'bytes;', sum(1 for r in grid.values() for u in r.values() if u), 'images,', sum(1 for r in grid.values() for u in r.values() if not u), 'placeholders')
