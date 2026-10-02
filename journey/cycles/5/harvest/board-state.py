#!/usr/bin/env python3
"""Cycle 5 board state as fetched 2026-10-02 ~11:25 MDT (Lucid fetch page_index 1-4 of 80e68a74-...).
Page 1 is transcribed item by item (heavily edited by the reviewer). Pages 2-4: every generated shape was
checked in the fetch and matched the spec (normalized as Lucid reports it: #RRGGBBaa, frame default
fill #ffffff / line #000000 / white title) EXCEPT the overrides listed below, so those pages are rebuilt
from lucid-spec.json + overrides. Writes board-state.json and harvest-compatible fetch-p<N>.json."""
import json, os
H = os.path.dirname(os.path.abspath(__file__)); C5 = os.path.dirname(H)
spec = json.load(open(os.path.join(C5, 'lucid-spec.json')))
PURPLE = '#ba23f6ff'
def st(i, txt, x, y):  # purple reviewer sticky (all 160x160, LineWidth 0, white text)
    return {'id': i, 'blockClass': 'StickiesStickyNoteBlock', 'bbox': {'x': x, 'y': y, 'w': 160, 'h': 160},
            'fill': PURPLE, 'line': '#000000ff', 'lineWidth': 0, 'textColor': '#ffffffff', 'text': txt}
P1_STICKIES = [
    st('XbIz-bjbxpkg', 'formatting updates for cycle board in Lucidchart are in purple.', -421.756715403985, 595.6294200268935),
    st('jfIz4vMwkkTy', 'formatting updates for cycle board in Lucidchart are in purple.', -385.75671540398616, -530),
    st('6hIz-4FiXxk6', 'Change  from Red/Yellow/Blue to  \n\nDo or Must Do\nTry\nConsider\n\n\nKeep color coding, but also if text of any sticky not contains those words set the priority based on text over color (a blue sticky with "Do or Must Do" should be considered as Red ( maybe even change the colors during the "harvest cycle" pull.', 3709.1420974445064, -560),
    st('icIz1BsecLhj', 'set border to zero and radius to zero for frame style', -282.2527671416587, 1082.8521647040548),
    st('3dIzN_rAGpYV', 'Create equal spacing around frame \u2014 this is where people can easily add notations to each screen without overlapping content or screenshots', 501.79840462619904, 325.1596225452313),
    st('EdIz~gM9LFYo', 'Move screenshot title and description below screenshot', 162.45683097954714, 1980.6390752884245),
    st('YgIzRzAthhEC', 'Move changes in this cycle and the previous cycle screenshot below the title, that way current images are always front and center', 142.09818817686755, 2360.667074270663),
    st('DhIzzUw.36NA', 'Remove borders and background around text.', 142.09818817686755, 2580.695073252893),
]
P1_FRAME_ITEMS = ['before-img-landing-1', 'img-home-00-landing', 'DhIzzUw.36NA', 'changes-landing-1', 'hdr-home-00-landing',
                  'EdIz~gM9LFYo', 'YgIzRzAthhEC', 'before-lbl-landing-1', '3dIzN_rAGpYV']
# observed values that differ from the spec (bbox / style / text); 'deleted' = absent from the fetch
OVERRIDES = {
    'p1': {
        'frame-home-00-landing': {'bbox': {'x': 0, 'y': 211.50396061047718, 'w': 2240, 'h': 3351.8421713905364},
                                  'fill': '#f2f3f5ff', 'line': '#00000000', 'titleColor': '#010000ff'},
        'img-home-00-landing': {'bbox': {'x': 400, 'y': 570.7352580820352, 'w': 1440, 'h': 1024}},
        'hdr-home-00-landing': {'bbox': {'x': 400, 'y': 1960.6390752884245, 'w': 1440, 'h': 200}},
        'changes-landing-1': {'bbox': {'x': 385.5767490262617, 'y': 2195.1680759901833, 'w': 1280, 'h': 342.4027930539951},
                              'fill': '#00000000', 'line': '#00000000',
                              'text': 'Changes in this cycle (vs cycle 4)\n\n\u2022 [try] Testimonials section \u201cWhat teams say\u201d: 4 clearly fictional sample quotes, below the value props, before the CTA band (#1)\n\u2022 Spacing tightened so the page still fits 1440\u00d71024'},
        'before-lbl-landing-1': {'bbox': {'x': 391.888371641056, 'y': 2561.0157913172948, 'w': 840, 'h': 90}},
        'before-img-landing-1': {'bbox': {'x': 391.888371641056, 'y': 2692.9711544985817, 'w': 720, 'h': 512}},
        'before-box-landing-1': 'deleted',
        'legend-box-p1': {'bbox': {'x': 0, 'y': -560, 'w': 2600, 'h': 273.43407665382256}, 'fill': '#00000000', 'line': '#00000000'},
    },
    'p2': {'frame-signup-01-create-account': {'fill': '#f2f3f5ff', 'line': '#00000000', 'titleColor': '#010000ff'}},
    'p3': {}, 'p4': {},
}
def hexa(c): return (c or '').lower() + 'ff' if c and len(c) == 7 else (c or '').lower()
def from_spec(sh):
    t, s = sh['type'], sh.get('style', {})
    o = {'id': sh['id'], 'type': t, 'bbox': dict(sh['boundingBox'])}
    if t == 'sparkFrame':
        o.update(blockClass='SparkFrameBlock', fill='#ffffffff', line='#000000ff', lineWidth=2, titleColor='#ffffffff', text=sh.get('title'))
    elif t == 'rectangle':
        o.update(blockClass='DefaultSquareBlock', fill=hexa(s['fill']['color']), line=hexa(s['stroke']['color']),
                 lineWidth=s['stroke']['width'], strokeStyle=s['stroke']['style'])
    elif t == 'image':
        o.update(blockClass='UserImage2Block', line=hexa(sh['stroke']['color']), lineWidth=sh['stroke']['width'], url=sh['image']['url'])
    else:
        o.update(blockClass='DefaultTextBlockNew')
    return o
state = {'docId': '80e68a74-a706-4fe1-b22f-4dfc5c5eb215', 'fetchedAt': '2026-10-02T17:25:00Z', 'pages': []}
for pg in spec['pages']:
    ov = OVERRIDES[pg['id']]; items = []
    for sh in pg['shapes']:
        o = ov.get(sh['id'])
        if o == 'deleted': continue
        it = from_spec(sh)
        if o: it.update(o)
        items.append(it)
    for ln in pg.get('lines', []):
        items.append({'id': ln['id'], 'type': 'line', 'line': hexa(ln['stroke']['color']), 'lineWidth': ln['stroke']['width'],
                      'from': ln['endpoint1']['shapeId'], 'to': ln['endpoint2']['shapeId']})
    if pg['id'] == 'p1': items += P1_STICKIES
    state['pages'].append({'pageId': pg['id'], 'pageTitle': pg['title'], 'items': items})
json.dump(state, open(os.path.join(H, 'board-state.json'), 'w'), indent=1, ensure_ascii=False)
# harvest-compatible condensed fetch (frames carry childrenIds; p1 frame came back as a childContainer)
for pg in state['pages']:
    nodes = []
    for it in pg['items']:
        if it.get('type') == 'line': continue
        props = {'BlockClass': it['blockClass'], 'BoundingBox': 'x: {x}, y: {y}, w: {w}, h: {h}'.format(**it['bbox'])}
        if it.get('fill'): props['FillColor'] = it['fill']
        if it.get('text'): props['TextAreas'] = [{'key': 'FrameTitle' if it['blockClass'] == 'SparkFrameBlock' else 'Text', 'text': it['text']}]
        n = {('itemId' if it['blockClass'] == 'StickiesStickyNoteBlock' else 'id'): it['id'], 'properties': props}
        if it['blockClass'] == 'SparkFrameBlock':
            if pg['pageId'] == 'p1':
                n = {'containerId': it['id'], 'label': it['text'], 'properties': props, 'itemIds': P1_FRAME_ITEMS}
            else:
                sk = it['id'][6:]; n['shapeType'] = 'Frame'; n['childrenIds'] = [f'img-{sk}', f'hdr-{sk}']
        nodes.append(n)
    json.dump({'_note': 'Condensed from Lucid fetch(page_index=%s) 2026-10-02 ~11:25 MDT via board-state.py; see board-state.json' % pg['pageId'][1:],
               'pages': [{'pageId': pg['pageId'], 'pageTitle': pg['pageTitle'], 'items': nodes}]},
              open(os.path.join(H, f'fetch-{pg["pageId"]}.json'), 'w'), indent=1, ensure_ascii=False)
print('ok', [len(p['items']) for p in state['pages']])
