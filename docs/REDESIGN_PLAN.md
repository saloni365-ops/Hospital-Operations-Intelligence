# Frontend Redesign Plan

- [x] **A: Design foundations** — shared theme tokens, mode constants, typography, components, Phaser 4 upgrade, React Router shell, Zustand store.
- [x] **B: Existing UI fixes** — standardized mode names, segmented speed, seeded feed, unit chart layouts and exit from native select.
- [x] **C: Isometric scene** — procedural dimetric map, generated textures, Tiled-compatible map JSON, overlay and camera controls.
- [x] **D: Control Room** — navy HUD, ticker, KPI badges, controls, objectives, shift card, ward and decision panels.
- [x] **E: Characters and effects** — procedural patients/nurses/bed and disruption objects, animated alert behavior and live ward decisions.
- [x] **F: Failure backend** — thresholds, trace store, measured detector and replay/comparison API routes.
- [x] **G: Dashboard and Failure Lab** — async job polling, mode scorecards and real measured failure timelines.
- [x] **H: Report exports and docs** — export script, report source material and asset credit documentation.
- [x] **I: Arena and polish** — Arena route is implemented; local settings provide opt-in sound, remembered tour state and achievement messaging.

Validation after every phase: unit tests, TypeScript/Vite build, run backend/frontend, 1440×900 and 1920×1080 screenshots, overlap/contrast/blank-chart checks.

## Final Status

- Core and stretch implementation items are complete.
- Live browser QA passed route loading and Run/disruption interactions.
- Control Room captures exist at 1440×900 and 1920×1080 in `results/`.
- Measured report PNG/SVG and CSV/Markdown table exports exist in `docs/report_figures/`.
- Remaining risks are bundle size, optional remote D-Wave credentials and synthetic-data clinical validity, all documented rather than hidden.
