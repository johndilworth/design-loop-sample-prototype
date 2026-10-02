#!/usr/bin/env python3
"""Build Lucid Standard Import JSON for a review cycle: one Lucid frame per step, screenshot inside with
~400px margin for stickies, visible frame title 'stepKey · route · title', arrows between frames, and a
legend/instructions block at the top of each page. Shape `note` fields are never set.

Usage:
  python3 journey/lucid/build_spec.py --cycle 1 --asset-prefix design-loop-c1r [--flows signup,vendor-approval]
        [--layout pages|rows] [--out /tmp/spec-cycle-1.json]
  Images: https://journey-assets-ai-xform.netlify.app/<asset-prefix>-<flow>/<annotated filename>
  layout=pages -> one Lucid page per flow (default); layout=rows -> flows stacked as rows on one page.
"""
import argparse, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('--cycle', type=int, default=1)
ap.add_argument('--flows', default='')
ap.add_argument('--asset-prefix', default=None, help='default design-loop-c<cycle>')
ap.add_argument('--asset-host', default='https://journey-assets-ai-xform.netlify.app')
ap.add_argument('--layout', choices=['pages', 'rows'], default='pages')
ap.add_argument('--frame-type', default='sparkFrame')
ap.add_argument('--manifest', default=os.path.join(HERE, '..', 'manifest.json'))
ap.add_argument('--out', default=os.path.join(os.environ.get('LUCID_OUT', '/tmp'), 'spec-cycle.json'))
a = ap.parse_args()
CYCLE = a.cycle
PREFIX = a.asset_prefix or f'design-loop-c{CYCLE}'
M = json.load(open(a.manifest))
entries = [e for e in M['entries'] if e['cycle'] == CYCLE]
flow_keys = [f for f in a.flows.split(',') if f] or list(dict.fromkeys(e['flow'] for e in entries))

IW, IH = 1440, 1024
MX, MTOP, MBOT = 400, 260, 400
FW, FH = MX * 2 + IW, MTOP + IH + MBOT          # 2240 x 1684
GAP = 480                                        # horizontal gap between frames
ROW_GAP = 1600                                   # vertical gap between flow rows (layout=rows)
LEGEND_TEXT = ('Leave feedback as sticky notes INSIDE the screen\'s frame. '
               '<span style="color:#C62828"><b>Red = must</b></span>, '
               '<span style="color:#9A7B00"><b>Yellow = try</b></span>, '
               '<span style="color:#1565C0"><b>Blue = maybe</b></span>. '
               'Comments are read as general feedback.')
esc = lambda s: (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def header_shapes(pid, y0, subtitle):
    """Doc title + legend block placed above y0 (top of first frame row)."""
    return [
        {'id': f'doc-title-{pid}', 'type': 'text', 'boundingBox': {'x': 0, 'y': y0 - 860, 'w': 4400, 'h': 200},
         'text': f'<p style="font-size:40pt"><b>Northwind AI Ops · Design loop · Cycle {CYCLE} review</b><br>'
                 f'<span style="font-size:20pt">{esc(subtitle)}</span></p>'},
        {'id': f'legend-box-{pid}', 'type': 'rectangle', 'boundingBox': {'x': 0, 'y': y0 - 560, 'w': 2600, 'h': 360},
         'style': {'fill': {'type': 'color', 'color': '#F4F6FB'}, 'stroke': {'color': '#3A4FD8', 'width': 3, 'style': 'solid'}},
         'text': f'<p style="font-size:22pt;text-align:left"><b>How to review</b><br>{LEGEND_TEXT}</p>'},
        {'id': f'legend-must-{pid}', 'type': 'rectangle', 'boundingBox': {'x': 2700, 'y': y0 - 530, 'w': 260, 'h': 300},
         'style': {'fill': {'type': 'color', 'color': '#FF8A80'}, 'stroke': {'color': '#C62828', 'width': 2, 'style': 'solid'}},
         'text': '<p style="font-size:24pt;text-align:center"><b>Red</b><br>must</p>'},
        {'id': f'legend-try-{pid}', 'type': 'rectangle', 'boundingBox': {'x': 3020, 'y': y0 - 530, 'w': 260, 'h': 300},
         'style': {'fill': {'type': 'color', 'color': '#FFE066'}, 'stroke': {'color': '#9A7B00', 'width': 2, 'style': 'solid'}},
         'text': '<p style="font-size:24pt;text-align:center"><b>Yellow</b><br>try</p>'},
        {'id': f'legend-maybe-{pid}', 'type': 'rectangle', 'boundingBox': {'x': 3340, 'y': y0 - 530, 'w': 260, 'h': 300},
         'style': {'fill': {'type': 'color', 'color': '#A3E4FF'}, 'stroke': {'color': '#1565C0', 'width': 2, 'style': 'solid'}},
         'text': '<p style="font-size:24pt;text-align:center"><b>Blue</b><br>maybe</p>'},
    ]

def flow_shapes(flow, y0, shapes, lines):
    steps = sorted([e for e in entries if e['flow'] == flow], key=lambda e: e['index'])
    base = f'{a.asset_host}/{PREFIX}-{flow}/'
    if a.layout == 'rows':
        shapes.append({'id': f'row-title-{flow}', 'type': 'text', 'boundingBox': {'x': 0, 'y': y0 - 200, 'w': 3000, 'h': 120},
                       'text': f'<p style="font-size:32pt;text-align:left"><b>{esc(steps[0]["flowName"].replace("→", ">"))}</b></p>'})
    for i, e in enumerate(steps):
        fx, fy = i * (FW + GAP), y0
        fid = f'frame-{e["stepKey"]}'
        label = f'{e["stepKey"]} · {e["route"]} · {e["title"]}'
        fr = {'id': fid, 'type': a.frame_type, 'boundingBox': {'x': fx, 'y': fy, 'w': FW, 'h': FH},
              'customData': [{'key': 'stepKey', 'value': e['stepKey']}, {'key': 'route', 'value': e['route']},
                             {'key': 'cycle', 'value': str(CYCLE)}, {'key': 'flow', 'value': flow}]}
        if a.frame_type == 'sparkFrame': fr['title'] = label
        else: fr['containerTitle'] = {'text': label}
        shapes.append(fr)
        act = (f'  —  click: {e["clicked"]["role"]} “{esc(e["clicked"]["name"])}”' if e.get('clicked') else '  —  end state')
        shapes.append({'id': f'hdr-{e["stepKey"]}', 'type': 'text', 'boundingBox': {'x': fx + MX, 'y': fy + 60, 'w': IW, 'h': 150},
                       'text': f'<p style="font-size:30pt"><b>{i+1}. {e["stepKey"]}</b>  ·  {e["route"]}<br>'
                               f'<span style="font-size:22pt">{esc(e["title"])}  —  h1: “{esc(e["h1"])}”{act}</span></p>'})
        shapes.append({'id': f'img-{e["stepKey"]}', 'type': 'image', 'boundingBox': {'x': fx + MX, 'y': fy + MTOP, 'w': IW, 'h': IH},
                       'image': {'type': 'image', 'url': base + os.path.basename(e['annotated'])},
                       'stroke': {'color': '#C9CED8', 'width': 2, 'style': 'solid'}})
        if i:
            lines.append({'id': f'arrow-{flow}-{i}', 'lineType': 'straight',  # keep ids short: Lucid import 400s on long ids 'lineType': 'straight',
                          'endpoint1': {'type': 'shapeEndpoint', 'style': 'none', 'shapeId': f'frame-{steps[i-1]["stepKey"]}', 'position': {'x': 1, 'y': 0.45}},
                          'endpoint2': {'type': 'shapeEndpoint', 'style': 'arrow', 'shapeId': fid, 'position': {'x': 0, 'y': 0.45}},
                          'stroke': {'color': '#3A4FD8', 'width': 6, 'style': 'solid'}})
    return steps

first = entries[0]
sub = (f'Desktop {first["viewport"]["width"]}×{first["viewport"]["height"]} · commit {first["commit"][:7]} · '
       f'{first["deployUrl"]}')
pages, counts = [], {}
if a.layout == 'pages':
    for n, flow in enumerate(flow_keys, 1):
        shapes, lines = header_shapes(f'p{n}', 0, ''), []
        steps = flow_shapes(flow, 0, shapes, lines)
        shapes[0]['text'] = shapes[0]['text'].replace('<span style="font-size:20pt"></span>',
                            f'<span style="font-size:20pt">{esc(steps[0]["flowName"].replace("→", ">"))} · {esc(sub)}</span>')
        pages.append({'id': f'p{n}', 'title': f'{n}. {flow} · cycle {CYCLE}', 'shapes': shapes, 'lines': lines})
        counts[flow] = len(steps)
else:
    shapes, lines = header_shapes('p1', 0, sub), []
    for r, flow in enumerate(flow_keys):
        counts[flow] = len(flow_shapes(flow, r * (FH + ROW_GAP), shapes, lines))
    pages.append({'id': 'p1', 'title': f'Cycle {CYCLE} review', 'shapes': shapes, 'lines': lines})
doc = {'version': 1, 'pages': pages}
s = json.dumps(doc, separators=(',', ':'), ensure_ascii=False)
open(a.out, 'w').write(s)
json.dump({'layout': a.layout, 'frame': {'w': FW, 'h': FH, 'margin_x': MX, 'margin_top': MTOP, 'margin_bottom': MBOT, 'gap': GAP,
           'row_gap': ROW_GAP}, 'pages': [p['title'] for p in pages], 'framesPerFlow': counts, 'assetBase': f'{a.asset_host}/{PREFIX}-<flow>/'},
          open(os.path.splitext(a.out)[0] + '-layout.json', 'w'), indent=2)
print(a.out, len(s), 'bytes', counts)
