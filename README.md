# design-loop-sample-prototype

Small Vite + React prototype ("Northwind AI Ops") used to exercise a design-feedback loop:
capture flows → Lucid journey map with frames → reviewer stickies → harvest → PRs → repeat.

Flows (see `journey/flows.yaml`):
- **signup**: `/signup` → `/onboarding/role` → `/onboarding/goals` → `/workspace/:id`
- **vendor-approval**: `/vendors` → `/vendors/:id` → `/vendors/:id/review` → `/vendors/:id/approved`

The copy and UX are deliberately imperfect (vague errors, "Submit"/"Proceed"/"OK" buttons, both review
buttons red, pre-checked marketing opt-in, "Step 1" vs "Step 2 of 2", generic "Success!") so feedback has something to fix.

```bash
npm install && npm run dev      # local
npm run build                   # dist/ (Netlify: netlify.toml, SPA redirect)
```
Deployed: https://design-loop-sample.netlify.app
