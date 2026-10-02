#!/usr/bin/env python3
"""Unit checks for harvest.py (run: python3 journey/harvest/test_harvest.py).
1. Cycle 5 v1 board (saved condensed fetches): 8 purple board-format stickies, 0 app feedback.
2. Synthetic v2-layout page: keyword precedence over colour, start-only keywords, purple + 'Board:' notes,
   sticky on the previous-cycle thumbnail flagged onBeforePanel."""
import json, os, subprocess, sys, tempfile, unittest
H = os.path.dirname(os.path.abspath(__file__)); J = os.path.dirname(H)
C5 = os.path.join(J, 'cycles', '5', 'harvest')

def run(fetches, threads=None):
    out = tempfile.mktemp(suffix='.json')
    cmd = [sys.executable, os.path.join(H, 'harvest.py'), '--doc-id', 'test', '--cycle', '5', '--manifest', os.path.join(J, 'manifest.json'), '--out', out]
    for f in fetches: cmd += ['--fetch', f]
    if threads: cmd += ['--threads', threads]
    subprocess.run(cmd, check=True, capture_output=True)
    return json.load(open(out))

def bb(x, y, w, h): return f'x: {x}, y: {y}, w: {w}, h: {h}'
def sticky(i, text, fill, x, y): return {'itemId': i, 'properties': {'BlockClass': 'StickiesStickyNoteBlock', 'BoundingBox': bb(x, y, 160, 160),
                                          'FillColor': fill, 'TextAreas': [{'key': 'Text', 'text': text}]}}
SYN = {'pages': [{'pageId': 'p1', 'pageTitle': 'synthetic', 'items': [
    {'id': 'frame-home-00-landing', 'shapeType': 'Frame', 'childrenIds': ['img-home-00-landing', 'before-img-landing-1', 's-blue-mustdo', 's-on-before'],
     'properties': {'BlockClass': 'SparkFrameBlock', 'BoundingBox': bb(0, 0, 2240, 3522), 'FillColor': '#f2f3f5ff',
                    'TextAreas': [{'key': 'FrameTitle', 'text': 'home-00-landing · / · Home · Northwind AI Ops'}]}},
    {'id': 'img-home-00-landing', 'properties': {'BlockClass': 'UserImage2Block', 'BoundingBox': bb(400, 400, 1440, 1024)}},
    {'id': 'before-img-landing-1', 'properties': {'BlockClass': 'UserImage2Block', 'BoundingBox': bb(400, 2610, 720, 512)}},
    {'id': 'hdr-home-00-landing', 'properties': {'BlockClass': 'DefaultTextBlockNew', 'BoundingBox': bb(400, 1784, 1440, 200)}},
    {'id': 'legend-board-p1', 'properties': {'BlockClass': 'DefaultSquareBlock', 'BoundingBox': bb(3660, -530, 260, 300)}},
    sticky('s-blue-mustdo', 'Must do: make the CTA bigger', '#a3e4ffff', 500, 500),          # blue + Must do -> must (text wins)
    sticky('s-yellow-consider', 'consider: shorter headline', '#ffe342ff', 600, 700),       # yellow + Consider: -> maybe
    sticky('s-red-do-question', 'Do we need this section?', '#ff8a80ff', 700, 900),         # 'Do' without ':' -> colour (must)
    sticky('s-blue-midtext', 'Maybe we could, must do later', '#a3e4ffff', 800, 1100),     # keyword not at start -> colour (maybe)
    sticky('s-blue-do', 'DO: add a footer', '#a3e4ffff', 900, 1200),                         # case-insensitive Do: -> must
    sticky('s-on-before', 'Try: this looked better before', '#ffe342ff', 500, 2700),       # on the cycle-4 thumbnail
    sticky('s-purple', 'Make the legend smaller', '#ba23f6ff', 3700, -500),                 # board feedback (outside frames)
    sticky('s-violet-in', 'Less padding here', '#9c27b0ff', 100, 100),                      # violet, inside frame -> board
    {'id': 's-board-text', 'properties': {'BlockClass': 'DefaultTextBlockNew', 'BoundingBox': bb(400, 1500, 600, 80),
                                          'TextAreas': [{'key': 'Text', 'text': 'Board: arrows too thick'}]}},
]}]}

class CycleFiveV1(unittest.TestCase):
    def test_purple_only(self):
        d = run([os.path.join(C5, f'fetch-p{i}.json') for i in range(1, 5)], os.path.join(C5, 'threads.json'))
        self.assertEqual(sum(len(f['feedback']) for f in d['frames']), 0)
        self.assertEqual(len(d['outsideFrames']), 0)
        self.assertEqual(len(d['boardFeedback']), 8)
        self.assertTrue(all(b['fill'].lower().startswith('#ba23f6') for b in d['boardFeedback']))
        self.assertEqual(sum(1 for b in d['boardFeedback'] if b['frameId'] == 'frame-home-00-landing'), 4)
        self.assertEqual(len(d['frames']), 12)

class Synthetic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = tempfile.mktemp(suffix='.json'); json.dump(SYN, open(p, 'w')); cls.d = run([p])
        cls.fb = {x['itemId']: x for f in cls.d['frames'] for x in f['feedback']}
        cls.fb.update({x['itemId']: x for x in cls.d['outsideFrames']})
        cls.board = {x['itemId']: x for x in cls.d['boardFeedback']}
    def test_blue_must_do_is_must(self):
        x = self.fb['s-blue-mustdo']
        self.assertEqual((x['priority'], x['prioritySource'], x['colorPriority'], x['priorityConflict']), ('must', 'text', 'maybe', True))
        self.assertIn('s-blue-mustdo', [c['itemId'] for c in self.d['priorityConflicts']])
    def test_consider_and_case(self):
        self.assertEqual(self.fb['s-yellow-consider']['priority'], 'maybe')
        self.assertEqual(self.fb['s-blue-do']['priority'], 'must')
    def test_keywords_only_at_start(self):
        self.assertEqual((self.fb['s-red-do-question']['priority'], self.fb['s-red-do-question']['prioritySource']), ('must', 'color'))
        self.assertEqual((self.fb['s-blue-midtext']['priority'], self.fb['s-blue-midtext']['prioritySource']), ('maybe', 'color'))
    def test_on_before_panel(self):
        x = self.fb['s-on-before']
        self.assertTrue(x.get('onBeforePanel')); self.assertEqual(x['beforePanel'], 'before-img-landing-1'); self.assertEqual(x['priority'], 'try')
        self.assertFalse(self.fb['s-blue-mustdo'].get('onBeforePanel', False))
    def test_board_feedback_separate(self):
        self.assertEqual(set(self.board), {'s-purple', 's-violet-in', 's-board-text'})
        self.assertEqual(self.board['s-board-text']['boardSource'], 'text')
        self.assertEqual(self.board['s-violet-in']['frameId'], 'frame-home-00-landing')
        self.assertEqual(self.board['s-purple']['nearest'][0]['id'], 'legend-board-p1')
        self.assertFalse(set(self.board) & set(self.fb))

if __name__ == '__main__':
    unittest.main(verbosity=2)
