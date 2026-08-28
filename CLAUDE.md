# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

This is the **NikunjS91/NikunjS91** GitHub profile README repository. The `README.md` renders as the public GitHub profile page. There is no build system or package manager — everything is static Markdown, SVG, and Python scripts run by GitHub Actions.

## GitHub Actions Workflows

Three workflows automate the profile content:

| Workflow | File | Schedule | What it does |
|---|---|---|---|
| Refresh Stats Badges | `refresh-stats.yml` | Every 2 hours + push | Rewrites `&t=<timestamp>` cache-busting params on badge URLs in README.md |
| Generate Snake Animation | `snake.yml` | Every 12 hours + push | Uses `Platane/snk` to generate contribution grid snake SVGs; pushes to the `output` branch |
| Generate Streak Card | `streak.yml` | Every 30 min + push | Runs `scripts/generate_all_stats.py` via `gh` CLI GraphQL; writes `assets/streak.svg`, `assets/stats.svg`, `assets/languages.svg` |

All workflows use a pull-rebase-retry loop (3 attempts, 5s sleep) before pushing to avoid race conditions when multiple workflows run concurrently.

## Stats Script

`scripts/generate_all_stats.py` calls the GitHub GraphQL API via the `gh` CLI (requires `GH_TOKEN` env var) and generates three SVG files under `assets/`. To run locally:

```bash
GH_TOKEN=$(gh auth token) GITHUB_USER=NikunjS91 python3 scripts/generate_all_stats.py
```

The script fetches 364 days of contribution history for streak calculation and all public repos for stars/languages aggregation.

## Key Conventions

- **Badge cache-busting**: Stats badge URLs in README.md carry a `&t=<unix_timestamp>` suffix. The `refresh-stats.yml` workflow regenerates this automatically — do not remove the `&t=` parameter or the pattern will break.
- **Snake SVGs**: Served from the `output` branch, not `main`. Referenced in README.md via `raw.githubusercontent.com/.../output/github-contribution-grid-snake*.svg`. The `<picture>` tag provides dark/light variants using `github-contribution-grid-snake-dark.svg` and `github-contribution-grid-snake.svg`.
- **Commit messages from bots use `[skip ci]`**: The badge refresh commits use `[skip ci]` to avoid re-triggering the workflow; the stat card commits do not (intentional, they update different files).
- **Workflow permissions**: All three workflows require `contents: write` to commit back to the repo.
