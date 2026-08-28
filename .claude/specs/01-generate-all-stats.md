# Spec: Generate All Stats

## Overview
Two scripts currently generate streak SVGs — `generate_all_stats.py` (used by the workflow) and `generate_streak_svg.py` (unused, standalone). The standalone script has a significantly better streak card design: it adds a glow filter, a decorative fire-path SVG icon, and a circular frame around the streak number, along with `role="img"` and `aria-label` accessibility attributes. The `generate_all_stats.py` streak card is visually flat by comparison. This spec consolidates the two scripts by adopting the superior streak card design from `generate_streak_svg.py` into `generate_all_stats.py`, then deleting the now-redundant standalone script. No external service dependencies are introduced; everything stays hand-built in Python.

## Depends on
- `scripts/generate_all_stats.py` — the script being improved (already called by `streak.yml`)
- `scripts/generate_streak_svg.py` — donor of the improved streak card design; deleted after merge
- `.github/workflows/streak.yml` — the workflow that runs `generate_all_stats.py`; no changes needed to the workflow itself

## Workflow changes
No workflow changes. `streak.yml` already calls `scripts/generate_all_stats.py` and writes output to `assets/`. The schedule, permissions, retry logic, and commit message remain unchanged.

## Script changes
**`scripts/generate_all_stats.py`**
- `build_streak_svg()` — replace the flat SVG body with the design from `generate_streak_svg.py::build_svg()`:
  - Add `<filter id="glow">` with `feGaussianBlur` + `feMerge` to `<defs>`
  - Add `role="img"` and `aria-label="GitHub streak stats"` to the root `<svg>` element
  - Replace the current streak centre card (plain rect + plain number) with the circle-frame + fire-path + glow design from the standalone script
  - Adjust card vertical positions to match the standalone script's layout (total: y=30, current: y=20 h=160, longest: y=30)
  - Update font-family from `Segoe UI, sans-serif` to `Segoe UI, Ubuntu, sans-serif` to match the standalone script
- All other functions (`build_stats_svg`, `build_languages_svg`, `main`, GraphQL queries) are unchanged.

**`scripts/generate_streak_svg.py`** — deleted (fully superseded by the updated `generate_all_stats.py`).

## README changes
No README changes. `assets/streak.svg` is not currently embedded in `README.md`; it is used only by third-party badge services. No new references needed.

## Files to change
- `scripts/generate_all_stats.py` — update `build_streak_svg()` as described above

## Files to create
None.

## Files to delete
- `scripts/generate_streak_svg.py`

## New dependencies
No new dependencies.

## Rules for implementation
- No external SVG-generation service dependency — SVGs stay hand-built in Python with the existing gradient styling
- Keep the pull-rebase-retry loop (3 attempts, 5s sleep) in any workflow that commits back to the repo
- Use `[skip ci]` for badge-refresh-only commits; do not add it to stat-card commits
- Never hardcode tokens — use `${{ secrets.* }}` / `GITHUB_TOKEN`
- Keep GraphQL queries minimal — request only the fields needed
- Do not alter the function signature of `build_streak_svg()` — it must still accept the same seven positional arguments
- Preserve the existing `fmt_date()` helper; do not duplicate it
- The glow filter `id` must remain `glow` and the gradient IDs (`bgGradient`, `fireGradient`, `statGradient`) must remain unchanged to avoid breaking SVG rendering

## Definition of done
- [ ] Running `GH_TOKEN=$(gh auth token) GITHUB_USER=NikunjS91 python3 scripts/generate_all_stats.py` locally produces `assets/streak.svg` that contains `<filter id="glow">`, a `<circle>` element, and `role="img"`
- [ ] The generated `assets/streak.svg` opens correctly in a browser and shows the fire-circle design around the streak number
- [ ] `scripts/generate_streak_svg.py` no longer exists in the repo
- [ ] `scripts/generate_all_stats.py` still generates `assets/stats.svg` and `assets/languages.svg` correctly (content unchanged)
- [ ] Triggering `streak.yml` via `workflow_dispatch` on GitHub completes successfully and commits a new `assets/streak.svg`
