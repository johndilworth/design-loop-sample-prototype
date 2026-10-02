#!/usr/bin/env python3
"""Harvest reviewer feedback from a Lucid journey doc into feedback.json.

The Lucid connector is called by the agent (MCP), not by this script. Steps:
  1. fetch(id=DOC, metadata_only=True) -> page_count / page_region_counts
  2. fetch(id=DOC, page_index=N) for every page (or region_index chunks) -> save raw responses
  3. list_document_threads(DOC) -> for each thread list_document_thread_comments -> save as
     [{"threadId":..., "status":..., "created":..., "comments":[...]}]
  4. python3 journey/harvest/harvest.py --doc-id DOC --cycle 1 --fetch raw/p1.json [--fetch raw/p2.json] \
        --threads raw/threads.json --manifest journey/manifest.json --out feedback.json

Frame containment: uses the fetch field `childrenIds` on nodes with shapeType "Frame" /
BlockClass "SparkFrameBlock" (primary), and independently recomputes containment from
`BoundingBox` (fallback / cross-check). Disagreements are reported per item.
"""
import argparse, json, re, sys, datetime

GENERATED_PREFIXES = ('frame-', 'hdr-', 'img-', 'doc-title', 'arrow-', 'legend-', 'row-title-')  # ids we create on import
FEEDBACK_CLASSES = {'StickiesStickyNoteBlock': 'sticky', 'TextBlock': 'text', 'DefaultTextBlockNew': 'text',
                    'LucidCardBlock': 'card', 'SparkCalloutSquareBlock': 'callout'}
FRAME_CLASSES = {'SparkFrameBlock'}
def priority_from_fill(fill):
    """Legend on the board: Red = must, Yellow = try, Blue = maybe (by hue of the sticky fill)."""
    import colorsys
    m = re.match(r'#?([0-9a-f]{6})', (fill or '').lower())
    if not m: return None
    r, g, b = (int(m.group(1)[i:i+2], 16) / 255 for i in (0, 2, 4))
    h, l, sat = colorsys.rgb_to_hls(r, g, b)
    if sat < 0.25: return None
    h *= 360
    if h < 20 or h >= 320: return 'must'
    if 40 <= h < 70: return 'try'
    if 180 <= h < 260: return 'maybe'
    return None

PRIORITY_RE = re.compile(r'^\s*(?:test\s*[:\-]?\s*)?(must|try|maybe)\b\s*[:\-]?', re.I)

def parse_bbox(s):
    if isinstance(s, dict):
        return {k: float(s[k]) for k in ('x', 'y', 'w', 'h')}
    m = dict(re.findall(r'(\w+):\s*(-?[\d.]+)', s or ''))
    return {k: float(m[k]) for k in ('x', 'y', 'w', 'h')} if all(k in m for k in 'xywh') else None

def walk(o):
    """Yield every dict that looks like a Lucid item (has properties.BlockClass) anywhere in fetch data."""
    if isinstance(o, dict):
        if isinstance(o.get('properties'), dict) and 'BlockClass' in o['properties']:
            yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)

def norm(item, page):
    p = item['properties']
    tas = p.get('TextAreas') or []
    text = '\n'.join(t.get('text', '') for t in tas if t.get('text')) or item.get('label') or item.get('text') or ''
    return {'id': item.get('id') or item.get('itemId'), 'blockClass': p.get('BlockClass'), 'shapeType': item.get('shapeType'),
            'text': text, 'bbox': parse_bbox(p.get('BoundingBox')), 'fill': p.get('FillColor'),
            'childrenIds': item.get('childrenIds'), 'pageId': page.get('pageId'), 'pageTitle': page.get('pageTitle')}

def overlap_ratio(a, f):
    ix = max(0, min(a['x'] + a['w'], f['x'] + f['w']) - max(a['x'], f['x']))
    iy = max(0, min(a['y'] + a['h'], f['y'] + f['h']) - max(a['y'], f['y']))
    area = a['w'] * a['h'] or 1
    return ix * iy / area

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--doc-id', required=True); ap.add_argument('--cycle', type=int, required=True)
    ap.add_argument('--fetch', action='append', required=True); ap.add_argument('--threads')
    ap.add_argument('--manifest', required=True); ap.add_argument('--out', default='feedback.json')
    ap.add_argument('--min-overlap', type=float, default=0.5)
    a = ap.parse_args()

    manifest = json.load(open(a.manifest))
    steps = {e['stepKey']: e for e in manifest['entries'] if e['cycle'] == a.cycle}
    items = {}
    for fp in a.fetch:
        raw = json.load(open(fp))
        data = json.loads(raw['text']) if isinstance(raw.get('text'), str) else raw
        for page in data.get('pages', []):
            for it in walk(page):
                n = norm(it, page)
                items[n['id']] = n

    frames = [n for n in items.values() if n['blockClass'] in FRAME_CLASSES or n['shapeType'] == 'Frame']
    def step_for_frame(f):
        if f['id'].startswith('frame-') and f['id'][6:] in steps:
            return f['id'][6:], 'frame-id'
        key = f['text'].split(' · ')[0].strip()  # visible title "stepKey · route · title"
        return (key, 'frame-title') if key in steps else (None, 'unmatched')
    frame_info = {}
    for f in frames:
        sk, how = step_for_frame(f)
        frame_info[f['id']] = {'frameId': f['id'], 'frameTitle': f['text'], 'stepKey': sk, 'matchedBy': how, 'pageId': f['pageId'],
                               'bbox': f['bbox'], 'childrenIds': f['childrenIds'] or []}
    parent_by_children = {c: fid for fid, fi in frame_info.items() for c in fi['childrenIds']}

    groups = {fid: [] for fid in frame_info}
    outside, disagreements = [], []
    for n in items.values():
        if n['blockClass'] not in FEEDBACK_CLASSES or (n['id'] or '').startswith(GENERATED_PREFIXES):
            continue
        by_child = parent_by_children.get(n['id'])
        ratios = {fid: overlap_ratio(n['bbox'], fi['bbox']) for fid, fi in frame_info.items() if n['bbox'] and fi['bbox']}
        best = max(ratios, key=ratios.get) if ratios else None
        if best and ratios[best] <= 0: best = None
        by_bbox = best if best and ratios[best] >= a.min_overlap else None
        m = PRIORITY_RE.match(n['text'])
        pr_color = priority_from_fill(n['fill']) if FEEDBACK_CLASSES[n['blockClass']] == 'sticky' else None
        fb = {'itemId': n['id'], 'kind': FEEDBACK_CLASSES[n['blockClass']], 'text': n['text'],
              'priority': (m.group(1).lower() if m else pr_color),
              'prioritySource': ('text' if m else 'color' if pr_color else None), 'fill': n['fill'], 'bbox': n['bbox'],
              'containment': {'childrenIds': by_child, 'bbox': by_bbox,
                              'bestOverlap': {'frameId': best, 'ratio': round(ratios[best], 3)} if best else None}}
        assigned = by_child or by_bbox
        if by_child != by_bbox:
            disagreements.append({'itemId': n['id'], 'childrenIds': by_child, 'bbox': by_bbox})
        (groups[assigned] if assigned else outside).append(fb)

    threads = json.load(open(a.threads)) if a.threads else []
    out = {
        'docId': a.doc_id, 'cycle': a.cycle, 'harvestedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'containmentMethod': 'childrenIds (Frame nodes in fetch) with BoundingBox overlap >= %.2f as cross-check' % a.min_overlap,
        'frames': [], 'outsideFrames': outside, 'containmentDisagreements': disagreements,
        'comments': {'note': 'list_document_threads returns only threadId/created/status and comments carry no shape anchor; '
                             'comments cannot be mapped to frames via the connector', 'unanchored': threads},
    }
    for fid, fi in sorted(frame_info.items(), key=lambda kv: (kv[1]['pageId'] or '', (kv[1]['bbox'] or {}).get('y', 0), (kv[1]['bbox'] or {}).get('x', 0))):
        e = steps.get(fi['stepKey'], {})
        out['frames'].append({
            'frameId': fid, 'pageId': fi['pageId'], 'frameTitle': fi['frameTitle'], 'stepKey': fi['stepKey'], 'matchedBy': fi['matchedBy'],
            'flow': e.get('flow'), 'route': e.get('route'), 'url': e.get('url'), 'title': e.get('title'), 'h1': e.get('h1'),
            'clicked': ({k: e['clicked'][k] for k in ('role', 'name', 'cssPath')} if e.get('clicked') else None),
            'commit': e.get('commit'), 'screenshot': e.get('annotated') or e.get('screenshot'),
            'feedback': groups[fid]})
    json.dump(out, open(a.out, 'w'), indent=2, ensure_ascii=False)
    print(f"frames={len(frame_info)} feedback_in_frames={sum(len(v) for v in groups.values())} outside={len(outside)} "
          f"disagreements={len(disagreements)} threads={len(threads)} -> {a.out}")

if __name__ == '__main__':
    main()
