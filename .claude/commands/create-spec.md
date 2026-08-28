---
description: Create a spec file and feature branch for the next NikunjS91 profile repo change
argument-hint: "Step number and feature name e.g. 4 languages-card-redesign"
allowed-tools: Read, Write, Glob, Bash(git:*)
---

You are a senior developer spinning up a new change for the
NikunjS91/NikunjS91 GitHub profile README repository. Always
follow the rules in CLAUDE.md.

User input: $ARGUMENTS

## Step 1 — Check working directory is clean
Run `git status` and check for uncommitted, unstaged, or
untracked files. If any exist, stop immediately and tell
the user to commit or stash changes before proceeding.
DO NOT CONTINUE until the working directory is clean.

## Step 2 — Parse the arguments
From $ARGUMENTS extract:

1. `step_number` — zero-padded to 2 digits: 4 → 04, 11 → 11

2. `feature_title` — human readable title in Title Case
   - Example: "Languages Card Redesign" or "Streak Workflow Retry Fix"

3. `feature_slug` — git and file safe slug
   - Lowercase, kebab-case
   - Only a-z, 0-9 and -
   - Maximum 40 characters
   - Example: languages-card-redesign, streak-retry-fix

4. `branch_name` — format: `feature/<feature_slug>`
   - Example: `feature/languages-card-redesign`

If you cannot infer these from $ARGUMENTS, ask the user
to clarify before proceeding.

## Step 3 — Check branch name is not taken
Run `git branch` to list existing branches.
If `branch_name` is already taken, append a number:
`feature/languages-card-redesign-01`, `-02`, etc.

## Step 4 — Switch to main and pull latest
Run:
```
git checkout main
git pull origin main
```

## Step 5 — Create and switch to the feature branch
Run:
```
git checkout -b <branch_name>
```

## Step 6 — Research the codebase
Read these files before writing the spec:
- `CLAUDE.md` — conventions and design decisions
- `README.md` — current profile page structure and badge/section layout
- `.github/workflows/*.yml` — existing workflows (refresh-stats, snake, streak)
- `scripts/generate_all_stats.py` and `scripts/generate_streak_svg.py`
- All files in `.claude/specs/` — avoid duplicating existing specs

Check `CLAUDE.md` to confirm the requested change is not already
marked complete or superseded. If it is, warn the user and stop.

## Step 7 — Write the spec
Generate a spec document with this exact structure:

---
# Spec: <feature_title>

## Overview
One paragraph describing what this change does and why it's
needed (visual/README change, new workflow, script behavior change,
bugfix in the stat pipeline, etc).

## Depends on
Which previous steps or existing workflows/scripts this change
requires or touches.

## Workflow changes
For each `.github/workflows/*.yml` file affected:
- File name, trigger/schedule change, new or modified jobs/steps,
  permissions or secrets needed.
If none: state "No workflow changes".

## Script changes
For each file in `scripts/` affected:
- Functions added or modified, GraphQL query changes, SVG output changes.
If none: state "No script changes".

## README changes
Sections, badges, or `<picture>`/image references added, removed,
or restructured in `README.md`.
If none: state "No README changes".

## Files to change
Every file that will be modified.

## Files to create
Every new file that will be created.

## New dependencies
Any new pip packages or GitHub Actions used. If none: state
"No new dependencies".

## Rules for implementation
Specific constraints Claude must follow. Always include:
- No external SVG-generation service dependency — SVGs stay
  hand-built in Python with the existing gradient styling
- Keep the pull-rebase-retry loop (3 attempts, 5s sleep) in any
  workflow that commits back to the repo
- Use `[skip ci]` for badge-refresh-only commits; do not add it
  to stat-card commits
- Never hardcode tokens — use `${{ secrets.* }}` / `GITHUB_TOKEN`
- Keep GraphQL queries minimal — request only the fields needed

## Definition of done
A specific testable checklist. Each item must be verifiable by
running the script locally, triggering the workflow manually
(`workflow_dispatch`), or viewing the rendered `README.md`.
---

## Step 8 — Save the spec
Save to: `.claude/specs/<step_number>-<feature_slug>.md`

## Step 9 — Report to the user
Print a short summary in this exact format:
```
Branch:    <branch_name>
Spec file: .claude/specs/<step_number>-<feature_slug>.md
Title:     <feature_title>
```

Then tell the user:
"Review the spec at `.claude/specs/<step_number>-<feature_slug>.md`
then enter Plan Mode with Shift+Tab twice to begin implementation."

Do not print the full spec in chat unless explicitly asked.
