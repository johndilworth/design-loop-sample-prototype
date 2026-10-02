#!/usr/bin/env python3
"""Build Lucid Standard Import JSON: one frame per step, screenshot inside with ~400px margin."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('LUCID_OUT', '/tmp')
FRAME_TYPE = sys.argv[1] if len(sys.argv) > 1 else 'sparkFrame'
FLOW, CYCLE = 'vendor-approval', 1
M = json.load(open(os.path.join(HERE, '..', 'manifest.json')))
steps = [e for e in M['entries'] if e['flow'] == FLOW and e['cycle'] == CYCLE]
BASE = f'https://journey-assets-ai-xform.netlify.app/design-loop-c{CYCLE}-{FLOW}/'
IW, IH = 1440, 1024
MX, MTOP, MBOT = 400, 260, 400
FW, FH = MX * 2 + IW, MTOP + IH + MBOT
GAP = 480
shapes, lines = [], []
title = {'id': 'doc-title', 'type': 'text', 'boundingBox': {'x': 0, 'y': -260, 'w': 2400, 'h': 140},
         'text': f'<p style="font-size:40pt"><b>Northwind AI Ops · {steps[0]["flowName"].replace("→","&gt;")} · cycle {CYCLE}</b><br><span style="font-size:20pt">Desktop 1440×1024 · commit {steps[0]["commit"][:7]} · {steps[0]["deployUrl"]} · Add stickies inside a frame to give feedback on that screen</span></p>'}
shapes.append(title)
for i, e in enumerate(steps):
    fx = i * (FW + GAP); fy = 0
    fid = f'frame-{e["stepKey"]}'
    label = f'{e["stepKey"]} · {e["route"]} · {e["title"]}'
    fr = {'id': fid, 'type': FRAME_TYPE, 'boundingBox': {'x': fx, 'y': fy, 'w': FW, 'h': FH},
          'customData': [{'key': 'stepKey', 'value': e['stepKey']}, {'key': 'route', 'value': e['route']},
                         {'key': 'cycle', 'value': str(CYCLE)}, {'key': 'flow', 'value': FLOW}]}
    if FRAME_TYPE == 'sparkFrame':
        fr['title'] = label
    else:
        fr['containerTitle'] = {'text': label}
    shapes.append(fr)
    shapes.append({'id': f'hdr-{e["stepKey"]}', 'type': 'text', 'boundingBox': {'x': fx + MX, 'y': fy + 60, 'w': IW, 'h': 150},
                   'text': f'<p style="font-size:30pt"><b>{i+1}. {e["stepKey"]}</b>  ·  {e["route"]}<br><span style="font-size:22pt">{e["title"].replace("&","&amp;")}  —  h1: “{e["h1"]}”' + (f'  —  click: {e["clicked"]["role"]} “{e["clicked"]["name"]}”' if e.get('clicked') else '  —  end state') + '</span></p>'})
    shapes.append({'id': f'img-{e["stepKey"]}', 'type': 'image', 'boundingBox': {'x': fx + MX, 'y': fy + MTOP, 'w': IW, 'h': IH},
                   'image': {'type': 'image', 'url': BASE + e['annotated'].split('/')[-1]},
                   'stroke': {'color': '#C9CED8', 'width': 2, 'style': 'solid'}})
    if i:
        prev = f'frame-{steps[i-1]["stepKey"]}'
        lines.append({'id': f'arrow-{i}', 'lineType': 'straight',
                      'endpoint1': {'type': 'shapeEndpoint', 'style': 'none', 'shapeId': prev, 'position': {'x': 1, 'y': 0.45}},
                      'endpoint2': {'type': 'shapeEndpoint', 'style': 'arrow', 'shapeId': fid, 'position': {'x': 0, 'y': 0.45}},
                      'stroke': {'color': '#3A4FD8', 'width': 6, 'style': 'solid'}})
doc = {'version': 1, 'pages': [{'id': 'p1', 'title': f'{FLOW} cycle {CYCLE}', 'shapes': shapes, 'lines': lines}]}
json.dump(doc, open(os.path.join(OUT, f'spec-{FRAME_TYPE}.json'), 'w'), separators=(',', ':'), ensure_ascii=False)
json.dump({'frame': {'w': FW, 'h': FH, 'margin_x': MX, 'margin_top': MTOP, 'margin_bottom': MBOT, 'gap': GAP}}, open(os.path.join(OUT, 'layout.json'), 'w'))
print(len(json.dumps(doc)))
