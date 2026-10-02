# Journey loop tooling (Phase 0–1 spike)

Pipeline: `flows.yaml` → `capture.mjs` (Playwright, 1440×1024) → `manifest.json` + raw PNGs →
`annotate.py` (3× cursor, hotspot = tip at 27,30 in the 141×198 sprite, clamped in-frame) →
copy annotated PNGs to the journey-assets Netlify host (new folder per run, e.g. `design-loop-c1r-<flow>/`, files are cached immutable) →
`lucid/build_spec.py` (one Lucid **frame** per step, one page per flow, legend at top) → reviewers add stickies → `harvest/harvest.py` → `feedback.json`.

```bash
npm ci && npx playwright install chromium
node journey/capture.mjs --cycle 1 [--base-url https://deploy-preview-N--design-loop-sample-prototype.netlify.app] [--flow vendor-approval]
python3 journey/annotate.py --cycle 1
python3 journey/lucid/build_spec.py --cycle 1 --asset-prefix design-loop-c1r --layout pages --out journey/cycles/1/lucid-spec.json
#   -> standard_import_json for lucid_create_diagram_from_specification (product=lucidchart, use_assisted_layout=false)
#   --layout rows stacks flows as rows on one page (1600px vertical gap)
```

No `data-journey-id` attributes: screens are identified by route template (ids → `:id`, query stripped),
`document.title`, `h1`, and a text fingerprint (sha256 of visible headings/labels/buttons/links, 16 hex).
Click targets are located by ARIA role + accessible name.

## Lucid layout
- One page per flow (`p1`, `p2`, ...). Each page has a title line plus a legend block (`legend-*` ids): "Leave feedback as sticky notes INSIDE the screen's frame. Red = must, Yellow = try, Blue = maybe. Comments are read as general feedback."
- **Keep import ids short** (≤ ~36 chars): a 52-char line id made the Lucid import fail with a bare 400. Arrows are `arrow-<flow>-<n>`. Avoid `→` in text (use `>`).
- Frame shape: `sparkFrame` in Standard Import → `SparkFrameBlock` (works in a Lucidchart doc).
- Frame 2240×1684: screenshot 1440×1024 at (+400, +260); 400 px margin left/right/below for stickies; 480 px gap between frames; arrows frame→frame.
- Frame title (visible tab) = `stepKey · route · document.title`; plus a visible header text block inside the frame. No shape `note` fields are used.
- Import ids are preserved (`frame-<stepKey>`, `img-<stepKey>`, `hdr-<stepKey>`), so harvest maps frame → step by id, falling back to the visible title.
- `customData` (stepKey/route/cycle/flow) is set on frames but is **not** returned by the connector's `fetch`.

## Harvest findings (connector, Oct 2026)
- `fetch` returns frames as nodes with `"shapeType": "Frame"`, `properties.BlockClass: "SparkFrameBlock"`, and **`childrenIds`** listing the items inside. Items placed geometrically inside a frame (no `container_id`) were auto-parented too.
- Items not in any frame appear under `standaloneClusters` with **`itemId` / `text`** keys (frame children use `id` / `label`) — harvest handles both.
- A sticky dropped onto the screenshot can be parented to the **image** (`img-<stepKey>`), not the frame. Harvest resolves
  childrenIds transitively up to the frame (`containment.via`), so these count as in-frame with no disagreement
  (cycle 1 re-harvest: 6 former disagreements → 0, same 11 assignments).
- A sticky straddling a frame edge was **not** a child; bbox overlap was 0.467. Harvest reports it under `outsideFrames` with `bestOverlap` so a human can decide.
- Comments: `list_document_threads` → `{threadId, created, status}`; `list_document_thread_comments` → `{threadId, userId, userName, comment, created, assignees}`. **No anchor/shape id** in either, and there is no create-thread tool (only `post_document_thread_comment` on an existing thread). Comments go to `comments.unanchored`.

## Before/after layout (cycle ≥ 2)
```bash
COMMIT_SHA=<PR head sha> node journey/capture.mjs --cycle 2 --base-url https://deploy-preview-1--design-loop-sample-prototype.netlify.app
python3 journey/annotate.py --cycle 2
python3 journey/lucid/build_spec.py --cycle 2 --asset-prefix design-loop-c2 --layout pages \
  --before-urls journey/cycles/1/asset-urls.json --changes journey/cycles/2/changes.json \
  --title-suffix ' (PR #1)' --out journey/cycles/2/lucid-spec.json
```
- Above each review frame (outside it, y 0..660; frame moves to y=900): a dashed grey **before panel**
  (`before-box/lbl/img-<flow>-<n>`, previous-cycle image at 720×512, label "Cycle N-1 (before) · reference only")
  and a green **"Changes in this cycle"** block (`changes-<flow>-<n>`, text from `changes.json`; flows without changes use
  `flows.<flow>.default`). These are plain shapes, never frames, so harvest ignores them by id prefix.
- HTML attributes in shape text use single quotes so the import JSON contains no escaped quotes.
- Lucid preflight flags before-box/before-img "overlap" as errors; it is intentional (background panel) and non-blocking.

## Harvest usage
See the docstring in `harvest/harvest.py`. Sample input/output: `harvest/sample-fetch-cycle-1.json`, `harvest/sample-feedback-cycle-1.json`.
Priority is parsed from a leading `must` / `try` / `maybe` (optionally after `TEST:`); otherwise from the sticky colour (red/pink = must, yellow = try, blue = maybe; `prioritySource` says which).

## Cycles
`journey/cycles/<N>/` holds the frozen artifacts of a review cycle: `manifest.json`, `annotated/`, `asset-urls.json`, `lucid-spec.json`, `lucid-doc.json` (doc id / URLs), `export/` (Lucid PNG exports), `harvest/` (fetch transcription + `feedback.json`).
