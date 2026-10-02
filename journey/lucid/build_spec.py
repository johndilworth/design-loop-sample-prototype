#!/usr/bin/env python3
"""Build Lucid Standard Import JSON for a review cycle: one Lucid frame per step, screenshot inside with
~400px margin for stickies, visible frame title 'stepKey · route · title', arrows between frames, and a
legend/instructions block at the top of each page. Shape `note` fields are never set.

Usage:
  python3 journey/lucid/build_spec.py --cycle 1 --asset-prefix design-loop-c1r [--flows signup,vendor-approval]
        [--layout pages|rows] [--out /tmp/spec-cycle-1.json]
  Images: https://journey-assets-ai-xform.netlify.app/<asset-prefix>-<flow>/<annotated filename>
  layout=pages -> one Lucid page per flow (default); layout=rows -> flows stacked as rows on one page.

Before/after (cycle >= 2):
  --before-urls journey/cycles/1/asset-urls.json   {stepKey: url} of the previous cycle's annotated shots
  --changes journey/cycles/2/changes.json          {"steps": {stepKey: [lines]}, "flows": {flow: {"default": [lines]}}}

Board layout (cycle 5 board feedback R1-R7, journey/cycles/5/harvest/board-feedback.json):
  R1 frames: fill #F2F3F5, stroke width 0 (no border). Standard Import has no corner-radius property, so radius
     stays at the Lucid default for sparkFrame (reviewer set it to 0 by hand).
  R2 PAD = 400 px on all four sides inside the frame; that margin is the reviewer's sticky area.
  R3 order inside each frame, left-aligned at frame.x + PAD: current screenshot 1440x1024, CAPTION_GAP (360),
     title + description (hdr-), 'Changes in this cycle' text (changes-), 'Cycle N-1 (before)' label
     (before-lbl-) and the 720x512 previous-cycle thumbnail (before-img-). Nothing is placed above the frames.
     Frames on one page share one height. Arrows connect screenshot centres (img- right edge -> next img- left edge).
  R4 no boxes/fills around text: changes, labels and legend are plain text shapes; no dashed before-box.
  R5/R6 legend: Do / Must do (red), Try (yellow), Consider (blue), Board format (purple) swatches.
  Ids before-/changes- stay ignored by harvest; a sticky on a before-img- is flagged onBeforePanel (R7).
"""
import argparse, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('--cycle', type=int, default=1)
ap.add_argument('--flows', default='')
ap.add_argument('--asset-prefix', default=None, help='default design-loop-c<cycle>')
ap.add_argument('--asset-host', default='https://journey-assets-ai-xform.netlify.app')
ap.add_argument('--layout', choices=['pages', 'rows'], default='pages')
ap.add_argument('--frame-type', default='sparkFrame')
ap.add_argument('--manifest', default=os.path.join(HERE, '..', 'manifest.json'))
ap.add_argument('--before-urls', default=None); ap.add_argument('--changes', default=None)
ap.add_argument('--title-suffix', default='')
ap.add_argument('--page-label', action='append', default=[], help='flow=Label for the Lucid page title (repeatable)')
ap.add_argument('--out', default=os.path.join(os.environ.get('LUCID_OUT', '/tmp'), 'spec-cycle.json'))
a = ap.parse_args()
CYCLE = a.cycle
PREFIX = a.asset_prefix or f'design-loop-c{CYCLE}'
M = json.load(open(a.manifest))
entries = [e for e in M['entries'] if e['cycle'] == CYCLE]
flow_keys = [f for f in a.flows.split(',') if f] or list(dict.fromkeys(e['flow'] for e in entries))

IW, IH = 1440, 1024
PAD = 400                                        # R2: equal padding on all sides (sticky area)
MX = MTOP = MBOT = PAD
CAPTION_GAP = 360                                # R3: screenshot -> title gap (approved ~360 px)
HDR_H, GAP_S, LBL_H = 200, 60, 90                # title block, gap between stacked blocks (>= 60 px preflight clearance), before label
FW = MX * 2 + IW                                 # 2240; FH is computed per page from the stacked content
FRAME_STYLE = {'fill': {'type': 'color', 'color': '#F2F3F5'}, 'stroke': {'color': '#F2F3F5', 'width': 0, 'style': 'solid'}}  # R1
GAP = 480                                        # horizontal gap between frames
ROW_GAP = 1600                                   # vertical gap between flow rows (layout=rows)
BEFORE = json.load(open(a.before_urls)) if a.before_urls else None
CHANGES = json.load(open(a.changes)) if a.changes else None
BW, BH = IW // 2, IH // 2                        # before thumbnail 720 x 512
LEGEND_TEXT = ('Leave feedback as sticky notes INSIDE the screen\'s frame. Start a note with <b>Do:</b>, <b>Must do</b>, '
               '<b>Try:</b> or <b>Consider:</b> to set its priority (the words win over the colour); otherwise the colour counts: '
               '<span style="color:#C62828"><b>Red = Do / Must do</b></span>, '
               '<span style="color:#9A7B00"><b>Yellow = Try</b></span>, '
               '<span style="color:#1565C0"><b>Blue = Consider</b></span>. '
               '<span style="color:#BA23F6"><b>Purple = Board format</b></span> (notes about this board\'s layout). '
               'Comments are read as general feedback.')
CHARS_PER_LINE, LINE_H = 56, 54                  # ~20pt text in a 1280 px wide block (measured on the cycle 5 board)
def text_h(lines):
    """Height for a 'Changes in this cycle' block: heading + blank line + wrapped bullets."""
    import math
    n = 2 + sum(max(1, math.ceil(len(t) / CHARS_PER_LINE)) for t in lines)
    return 32 + LINE_H * n
esc = lambda s: (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def header_shapes(pid, y0, subtitle):
    """Doc title + legend (plain text + 4 colour swatches) placed above y0 (top of first frame row)."""
    sw = lambda key, x, fill, line, label, tc=None: {
        'id': f'legend-{key}-{pid}', 'type': 'rectangle', 'boundingBox': {'x': x, 'y': y0 - 530, 'w': 260, 'h': 300},
        'style': dict({'fill': {'type': 'color', 'color': fill}, 'stroke': {'color': line, 'width': 2, 'style': 'solid'}}, **({'textColor': tc} if tc else {})),
        'text': f'<p style="font-size:24pt;text-align:center">{label}</p>'}
    return [
        {'id': f'doc-title-{pid}', 'type': 'text', 'boundingBox': {'x': 0, 'y': y0 - 860, 'w': 4400, 'h': 200},
         'text': f'<p style="font-size:40pt;text-align:left"><b>Northwind AI Ops · Design loop · Cycle {CYCLE} review{esc(a.title_suffix)}</b><br>'
                 f'<span style="font-size:20pt">{esc(subtitle)}</span></p>'},
        # R4: plain text, no box/fill
        {'id': f'legend-box-{pid}', 'type': 'text', 'boundingBox': {'x': 0, 'y': y0 - 560, 'w': 2600, 'h': 360},
         'text': f'<p style="font-size:22pt;text-align:left"><b>How to review</b><br>{LEGEND_TEXT}</p>'},
        sw('must', 2700, '#FF8A80', '#C62828', '<b>Red</b><br>Do / Must do'),
        sw('try', 3020, '#FFE066', '#9A7B00', '<b>Yellow</b><br>Try'),
        sw('maybe', 3340, '#A3E4FF', '#1565C0', '<b>Blue</b><br>Consider'),
        sw('board', 3660, '#BA23F6', '#7B1FA2', '<b>Purple</b><br>Board format', '#FFFFFF'),
    ]

def page_frame_h(flows):
    """R3: one frame height per page = PAD + screenshot + gap + title [+ changes] [+ before label + thumbnail] + PAD."""
    steps = [e for e in entries if e['flow'] in flows]
    ch = max([text_h(change_lines(e)) for e in steps]) if CHANGES else 0
    h = PAD + IH + CAPTION_GAP + HDR_H
    if CHANGES: h += GAP_S + ch
    if BEFORE: h += GAP_S + LBL_H + GAP_S + BH
    return h + PAD, ch

def change_lines(e):
    return (CHANGES.get('steps', {}).get(e['stepKey']) or CHANGES.get('flows', {}).get(e['flow'], {}).get('default')
            or ['No changes this cycle'])

def flow_shapes(flow, y0, shapes, lines, FH, CH):
    steps = sorted([e for e in entries if e['flow'] == flow], key=lambda e: e['index'])
    base = f'{a.asset_host}/{PREFIX}-{flow}/'
    if a.layout == 'rows':
        shapes.append({'id': f'row-title-{flow}', 'type': 'text', 'boundingBox': {'x': 0, 'y': y0 - 200, 'w': 3000, 'h': 120},
                       'text': f'<p style="font-size:32pt;text-align:left"><b>{esc(steps[0]["flowName"].replace("→", ">"))}</b></p>'})
    for i, e in enumerate(steps):
        fx, fy = i * (FW + GAP), y0
        fid = f'frame-{e["stepKey"]}'
        label = f'{e["stepKey"]} · {e["route"]} · {e["title"]}'
        fr = {'id': fid, 'type': a.frame_type, 'boundingBox': {'x': fx, 'y': fy, 'w': FW, 'h': FH}, 'style': FRAME_STYLE,
              'customData': [{'key': 'stepKey', 'value': e['stepKey']}, {'key': 'route', 'value': e['route']},
                             {'key': 'cycle', 'value': str(CYCLE)}, {'key': 'flow', 'value': flow}]}
        if a.frame_type == 'sparkFrame': fr['title'] = label
        else: fr['containerTitle'] = {'text': label}
        shapes.append(fr)                            # frame first so everything inside renders on top of it
        x, y = fx + PAD, fy + PAD
        shapes.append({'id': f'img-{e["stepKey"]}', 'type': 'image', 'boundingBox': {'x': x, 'y': y, 'w': IW, 'h': IH},
                       'image': {'type': 'image', 'url': base + os.path.basename(e['annotated'])},
                       'stroke': {'color': '#C9CED8', 'width': 2, 'style': 'solid'}})
        y += IH + CAPTION_GAP
        if e.get('entry'):
            ent = e['entry']
            act0 = f'  —  reached from {ent["fromRoute"]} via {ent["click"]["role"]} “{esc(ent["click"]["name"])}”'
        else: act0 = ''
        act = (f'  —  click: {e["clicked"]["role"]} “{esc(e["clicked"]["name"])}”' if e.get('clicked') else '  —  end state')
        # 22pt/16pt in a 200px box (cycle 3: 30pt/22pt in 150px wrapped and clipped). R3: caption BELOW the screenshot.
        shapes.append({'id': f'hdr-{e["stepKey"]}', 'type': 'text', 'boundingBox': {'x': x, 'y': y, 'w': IW, 'h': HDR_H},
                       'text': f'<p style="font-size:22pt;text-align:left"><b>{i+1}. {e["stepKey"]}</b>  ·  {e["route"]}<br>'
                               f'<span style="font-size:16pt">{esc(e["title"])}  —  h1: “{esc(e["h1"])}”{act}{act0}</span></p>'})
        y += HDR_H
        if CHANGES:
            y += GAP_S
            body = '<br>'.join('• ' + esc(t) for t in change_lines(e))
            # R4: plain text (no fill/border); blank line after the heading, as hand-edited on the cycle 5 board
            shapes.append({'id': f'changes-{flow}-{i+1}', 'type': 'text', 'boundingBox': {'x': x, 'y': y, 'w': 1280, 'h': CH},
                           'text': f'<p style="font-size:20pt;text-align:left"><b>Changes in this cycle</b> (vs cycle {CYCLE-1})<br><br>{body}</p>'})
            y += CH
        if BEFORE:
            y += GAP_S
            if BEFORE.get(e['stepKey']):
                shapes.append({'id': f'before-lbl-{flow}-{i+1}', 'type': 'text', 'boundingBox': {'x': x, 'y': y, 'w': 840, 'h': LBL_H},
                               'text': f'<p style="font-size:20pt;text-align:left"><b>Cycle {CYCLE-1} (before) · reference only</b></p>'})
                shapes.append({'id': f'before-img-{flow}-{i+1}', 'type': 'image', 'boundingBox': {'x': x, 'y': y + LBL_H + GAP_S, 'w': BW, 'h': BH},
                               'image': {'type': 'image', 'url': BEFORE[e['stepKey']]},
                               'stroke': {'color': '#C9CED8', 'width': 1, 'style': 'solid'}})
            else:
                # new screen: plain text line in the label slot, thumbnail slot left empty (R4: no dashed box)
                shapes.append({'id': f'before-lbl-{flow}-{i+1}', 'type': 'text', 'boundingBox': {'x': x, 'y': y, 'w': 1280, 'h': LBL_H},
                               'text': f'<p style="font-size:20pt;text-align:left"><b>New this cycle</b> · no cycle {CYCLE-1} capture of this screen</p>'})
        if i:
            # R3: arrows between screenshot centres (straight, both positions pinned)
            lines.append({'id': f'arrow-{flow}-{i}', 'lineType': 'straight',  # keep ids short: Lucid import 400s on long ids
                          'endpoint1': {'type': 'shapeEndpoint', 'style': 'none', 'shapeId': f'img-{steps[i-1]["stepKey"]}', 'position': {'x': 1, 'y': 0.5}},
                          'endpoint2': {'type': 'shapeEndpoint', 'style': 'arrow', 'shapeId': f'img-{e["stepKey"]}', 'position': {'x': 0, 'y': 0.5}},
                          'stroke': {'color': '#3A4FD8', 'width': 6, 'style': 'solid'}})
    return steps

first = entries[0]
sub = (f'Desktop {first["viewport"]["width"]}×{first["viewport"]["height"]} · commit {first["commit"][:7]} · '
       f'{first["deployUrl"]}')
pages, counts, frame_h = [], {}, {}
if a.layout == 'pages':
    for n, flow in enumerate(flow_keys, 1):
        shapes, lines = header_shapes(f'p{n}', 0, ''), []
        FH, CH = page_frame_h([flow]); frame_h[flow] = FH
        steps = flow_shapes(flow, 0, shapes, lines, FH, CH)
        shapes[0]['text'] = shapes[0]['text'].replace('<span style="font-size:20pt"></span>',
                            f'<span style="font-size:20pt">{esc(steps[0]["flowName"].replace("→", ">"))} · {esc(sub)}</span>')
        lbl = dict(x.split('=', 1) for x in a.page_label).get(flow, flow)
        pages.append({'id': f'p{n}', 'title': f'{n}. {lbl} · cycle {CYCLE}', 'shapes': shapes, 'lines': lines})
        counts[flow] = len(steps)
else:
    shapes, lines = header_shapes('p1', 0, sub), []
    FH, CH = page_frame_h(flow_keys)
    for r, flow in enumerate(flow_keys):
        frame_h[flow] = FH
        counts[flow] = len(flow_shapes(flow, r * (FH + ROW_GAP), shapes, lines, FH, CH))
    pages.append({'id': 'p1', 'title': f'Cycle {CYCLE} review', 'shapes': shapes, 'lines': lines})
# HTML attributes use single quotes so the import JSON has no escaped quotes (easier to pass through the connector)
for pg in pages:
    for sh in pg['shapes']:
        if isinstance(sh.get('text'), str):
            sh['text'] = re.sub(r'(\w+)="([^"]*)"', r"\1='\2'", sh['text'])
doc = {'version': 1, 'pages': pages}
s = json.dumps(doc, separators=(',', ':'), ensure_ascii=False)
open(a.out, 'w').write(s)
json.dump({'layout': a.layout, 'frame': {'w': FW, 'hByFlow': frame_h, 'pad': PAD, 'caption_gap': CAPTION_GAP, 'gap': GAP,
           'row_gap': ROW_GAP, 'style': FRAME_STYLE, 'order': ['img', 'hdr', 'changes', 'before-lbl', 'before-img'],
           'radius': 'not settable via Standard Import (Lucid default)'}, 'pages': [p['title'] for p in pages], 'framesPerFlow': counts, 'assetBase': f'{a.asset_host}/{PREFIX}-<flow>/'},
          open(os.path.splitext(a.out)[0] + '-layout.json', 'w'), indent=2)
print(a.out, len(s), 'bytes', counts)
