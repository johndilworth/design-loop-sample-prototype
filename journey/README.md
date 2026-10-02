# Journey loop tooling (Phase 0–1 spike)

Pipeline: `flows.yaml` → `capture.mjs` (Playwright, 1440×1024) → `manifest.json` + raw PNGs →
`annotate.py` (3× cursor, hotspot = tip at 27,30 in the 141×198 sprite, clamped in-frame) →
copy annotated PNGs to the journey-assets Netlify host (`design-loop-c<cycle>-<flow>/`) →
`lucid/build_spec.py` (one Lucid **frame** per step) → reviewers add stickies → `harvest/harvest.py` → `feedback.json`.

```bash
npm ci && npx playwright install chromium
node journey/capture.mjs --cycle 1 [--base-url https://deploy-preview-N--design-loop-sample.netlify.app] [--flow vendor-approval]
python3 journey/annotate.py --cycle 1
LUCID_OUT=/tmp python3 journey/lucid/build_spec.py   # -> /tmp/spec-sparkFrame.json for lucid_create_diagram_from_specification (use_assisted_layout=false)
```

No `data-journey-id` attributes: screens are identified by route template (ids → `:id`, query stripped),
`document.title`, `h1`, and a text fingerprint (sha256 of visible headings/labels/buttons/links, 16 hex).
Click targets are located by ARIA role + accessible name.

## Lucid layout
- Frame shape: `sparkFrame` in Standard Import → `SparkFrameBlock` (works in a Lucidchart doc).
- Frame 2240×1684: screenshot 1440×1024 at (+400, +260); 400 px margin left/right/below for stickies; 480 px gap between frames; arrows frame→frame.
- Frame title (visible tab) = `stepKey · route · document.title`; plus a visible header text block inside the frame. No shape `note` fields are used.
- Import ids are preserved (`frame-<stepKey>`, `img-<stepKey>`, `hdr-<stepKey>`), so harvest maps frame → step by id, falling back to the visible title.
- `customData` (stepKey/route/cycle/flow) is set on frames but is **not** returned by the connector's `fetch`.

## Harvest findings (connector, Oct 2026)
- `fetch` returns frames as nodes with `"shapeType": "Frame"`, `properties.BlockClass: "SparkFrameBlock"`, and **`childrenIds`** listing the items inside. Items placed geometrically inside a frame (no `container_id`) were auto-parented too.
- Items not in any frame appear under `standaloneClusters` with **`itemId` / `text`** keys (frame children use `id` / `label`) — harvest handles both.
- A sticky straddling a frame edge was **not** a child; bbox overlap was 0.467. Harvest reports it under `outsideFrames` with `bestOverlap` so a human can decide.
- Comments: `list_document_threads` → `{threadId, created, status}`; `list_document_thread_comments` → `{threadId, userId, userName, comment, created, assignees}`. **No anchor/shape id** in either, and there is no create-thread tool (only `post_document_thread_comment` on an existing thread). Comments go to `comments.unanchored`.

## Harvest usage
See the docstring in `harvest/harvest.py`. Sample input/output: `harvest/sample-fetch-cycle-1.json`, `harvest/sample-feedback-cycle-1.json`.
Priority is parsed from a leading `must` / `try` / `maybe` (optionally after `TEST:`).
