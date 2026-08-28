---
description: Runs parallel security and quality code
  review for a specific NikunjS91 profile repo change.
  Pass the spec name as argument e.g. /code-review-feature 04-languages-card-redesign
allowed-tools: Bash(git diff), Bash(git diff --staged)
---

Run the full code review pipeline for the change
specified in $ARGUMENTS.

If no argument is provided, stop immediately and say:
"Please provide a spec name. Usage: /code-review-feature
<spec-name> e.g. /code-review-feature 04-languages-card-redesign"

## Pre-flight Check

Before invoking any subagents, collect the diff:
- Run `git diff` for unstaged changes
- Run `git diff --staged` for staged changes
- Combine both into a single diff

If both are empty, stop immediately and say:
"No changes detected. Implement the change before
running code review."

---

## Step 1: Parallel Review

Invoke both subagents simultaneously with the same
context:

**profile-security-reviewer** receives:
- The combined diff from the pre-flight check
- Spec file for context: `.claude/specs/$ARGUMENTS.md`
- Source files to reference: `scripts/` directory and
  `.github/workflows/` directory
- Instruction: Review only the changed code for security
  vulnerabilities — hardcoded tokens/secrets, unsafe use of
  `${{ }}` expression interpolation in workflow `run:` steps
  (script injection risk), unpinned or untrusted third-party
  Actions, overly broad workflow `permissions:`, unsanitized
  input flowing into GraphQL queries or file paths. Do not
  comment on quality or style.

**profile-quality-reviewer** receives:
- The combined diff from the pre-flight check
- Spec file for context: `.claude/specs/$ARGUMENTS.md`
- Source files to reference: `scripts/` directory,
  `.github/workflows/` directory, and `README.md`
- Instruction: Review only the changed code for quality,
  Python best practices, and maintainability — including
  whether the pull-rebase-retry loop pattern was preserved
  where the workflow commits back to the repo, whether SVG
  generation stays free of external service dependencies,
  and whether `[skip ci]` is used correctly (badge-refresh
  commits only, not stat-card commits). Do not comment on
  security concerns.

Both subagents must run in parallel. Do not wait for
one to finish before starting the other.

---

## Step 2: Unified Report

Once both subagents have completed, combine their
findings into a single unified report. De-duplicate any
overlapping findings — if both agents flagged the same
line for different reasons, merge them into one finding
with both perspectives noted.

Structure the combined report as:
Code Review Report — $ARGUMENTS
Security Findings
[profile-security-reviewer output]
Quality Findings
[profile-quality-reviewer output]
Combined Action Plan
Ordered checklist of everything that needs to be fixed,
prioritized by severity:

[Critical/High security findings first]
[Quality CHANGES REQUESTED items second]
[Medium/Low security findings third]
[Quality APPROVED WITH SUGGESTIONS items last]

Overall Verdict
APPROVED — ready to commit
APPROVED WITH SUGGESTIONS — can commit, address
suggestions in future steps
CHANGES REQUESTED — must fix before committing,
see action plan above
---

## Step 3: Ask for Approval

After presenting the unified report, ask:

"Do you want me to implement the action plan now?"

Wait for explicit user confirmation before making
any changes. Do not touch any files until the user
approves.

---

## Rules
- Do NOT edit any files before user approval
- Do NOT start one reviewer before the other —
  both must run in parallel
- Do NOT skip the pre-flight diff check
- Do NOT proceed if the spec file at
  `.claude/specs/$ARGUMENTS.md` does not exist —
  report it and stop
- If either subagent fails or returns no output,
  report it and do not present a partial review
  as complete
