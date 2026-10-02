#!/usr/bin/env python3
"""Diff board-state.json (current board) against lucid-spec.json (generated) and anchor purple / 'Board:' notes
to the nearest board element by bounding-box edge distance. Writes board-diff.json."""
import json, os, re, colorsys
H = os.path.dirname(os.path.abspath(__file__)); C5 = os.path.dirname(H)
state = json.load(open(os.path.join(H, 'board-state.json')))
spec = json.load(open(os.path.join(C5, 'lucid-spec.json')))
def is_board_note(it):
    if it.get('blockClass') not in ('StickiesStickyNoteBlock', 'DefaultTextBlockNew'): return False
    if re.match(r'\s*board\s*:', it.get('text') or '', re.I): return True
    m = re.match(r'#?([0-9a-f]{6})', (it.get('fill') or '').lower())
    if not m: return False
    r, g, b = (int(m.group(1)[i:i+2], 16) / 255 for i in (0, 2, 4)); h, l, s = colorsys.rgb_to_hls(r, g, b)
    return s >= 0.25 and 260 <= h * 360 < 320          # purple / violet / magenta-violet band
def dist(a, b):
    dx = max(0, max(a['x'], b['x']) - min(a['x'] + a['w'], b['x'] + b['w']))
    dy = max(0, max(a['y'], b['y']) - min(a['y'] + a['h'], b['y'] + b['h']))
    return (dx * dx + dy * dy) ** .5
def kind(i):
    for p, k in (('frame-', 'frame'), ('hdr-', 'frame title/description (hdr)'), ('img-', 'screenshot'), ('before-', 'before panel'),
                 ('changes-', 'changes block'), ('legend-', 'legend'), ('doc-title', 'page header'), ('arrow-', 'arrow')):
        if i.startswith(p): return k
    return 'other'
out = {'pages': []}
for pg, sp in zip(state['pages'], spec['pages']):
    cur = {i['id']: i for i in pg['items']}
    gen = {s['id']: s for s in sp['shapes']}
    edits = []
    for sid, s in gen.items():
        c = cur.get(sid)
        if not c: edits.append({'id': sid, 'element': kind(sid), 'change': 'deleted', 'generated': s['boundingBox']}); continue
        d = {}
        gb, cb = s['boundingBox'], c['bbox']
        for k in 'xywh':
            if abs(gb[k] - cb[k]) > 0.5: d[k] = {'generated': gb[k], 'current': round(cb[k], 1), 'delta': round(cb[k] - gb[k], 1)}
        st_ = s.get('style', {})
        gfill = (st_.get('fill', {}).get('color') or ('#FFFFFF' if s['type'] == 'sparkFrame' else None))
        gline = (st_.get('stroke', {}).get('color') or ('#000000' if s['type'] == 'sparkFrame' else None))
        for k, gv in (('fill', gfill), ('line', gline)):
            if gv and c.get(k) and c[k].lower() != (gv.lower() + 'ff'): d[k] = {'generated': gv, 'current': c[k]}
        if c.get('titleColor') and s['type'] == 'sparkFrame' and c['titleColor'] != '#ffffffff': d['titleColor'] = {'generated': '#ffffff (on black title chip)', 'current': c['titleColor']}
        if 'text' in c and s['type'] == 'rectangle' and sid.startswith('changes-') and '\n\n' in c['text']: d['text'] = 'blank line inserted after the "Changes in this cycle" heading'
        if d: edits.append({'id': sid, 'element': kind(sid), 'change': 'modified', 'diff': d})
    for cid, c in cur.items():
        if cid not in gen and c.get('type') != 'line' and not is_board_note(c) and c.get('blockClass') != 'StickiesStickyNoteBlock':
            edits.append({'id': cid, 'element': 'added', 'change': 'added', 'bbox': c['bbox']})
    notes = []
    for c in pg['items']:
        if not is_board_note(c): continue
        cands = sorted(((dist(c['bbox'], o['bbox']), o['id']) for o in pg['items'] if o.get('bbox') and o['id'] != c['id']
                        and not o.get('blockClass') == 'StickiesStickyNoteBlock' and not (o['id'].startswith('frame-') and dist(c['bbox'], o['bbox']) == 0)), key=lambda t: t[0])
        frame = next((o['id'] for o in pg['items'] if o['id'].startswith('frame-') and dist(c['bbox'], o['bbox']) == 0), None)
        notes.append({'itemId': c['id'], 'fill': c['fill'], 'text': c['text'], 'bbox': c['bbox'], 'insideFrame': frame,
                      'nearest': [{'id': i, 'element': kind(i), 'distance': round(dd, 1)} for dd, i in cands[:3]]})
    out['pages'].append({'pageId': pg['pageId'], 'pageTitle': pg['pageTitle'], 'edits': edits, 'boardNotes': notes})
json.dump(out, open(os.path.join(H, 'board-diff.json'), 'w'), indent=1, ensure_ascii=False)
for p in out['pages']:
    print(p['pageId'], len(p['edits']), 'edits', len(p['boardNotes']), 'notes')
    for e in p['edits']: print('  E', json.dumps(e)[:260])
    for n in p['boardNotes']: print('  N', n['itemId'], n['insideFrame'], [(x['id'], x['distance']) for x in n['nearest']])
