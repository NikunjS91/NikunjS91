---
description: Writes and runs tests for a specific NikunjS91 profile repo change. Pass the spec name as argument e.g. /test-feature 04-languages-card-redesign
allowed-tools: Bash(python -m pytest)
---

Run the full testing pipeline for the change specified
in $ARGUMENTS.

If no argument is provided, stop immediately and say:
"Please provide a spec name. Usage: /test-feature
<spec-name> e.g. /test-feature 04-languages-card-redesign"

If `.claude/specs/$ARGUMENTS.md` does not exist, stop
immediately and say:
"Spec file not found at .claude/specs/$ARGUMENTS.md.
Please check the spec name and try again."

---

## Step 1: Write Tests

Invoke the **profile-test-writer** subagent with the
following context:

- Spec file to base tests on:
  `.claude/specs/$ARGUMENTS.md`
- Source files to read for structure:
  - `scripts/generate_all_stats.py`
  - `scripts/generate_streak_svg.py`
  - Relevant file(s) in `.github/workflows/` if the spec touches a workflow
- Output test file to create:
  `tests/test_$ARGUMENTS.py`
- Instruction: Write tests based on what the spec says the
  change SHOULD do. Do NOT derive test logic from reading the
  implementation. Cover:
  - GraphQL response parsing (mock the GitHub API response —
    never call the real API in a test)
  - SVG output correctness: valid, well-formed XML; expected
    values inserted in the expected positions; correct gradient/
    styling attributes present
  - Edge cases: zero contributions, missing/null fields in the
    API response, rate-limit or error responses
  - If the spec touches a workflow file: a YAML-syntax/schema
    check (e.g. via `yamllint` or `python -c "import yaml..."`)
    rather than an actual GitHub Actions run

Wait for profile-test-writer to fully complete and confirm the
test file has been written before proceeding to Step 2.

---

## Step 2: Run Tests

Once profile-test-writer has finished, invoke the
**profile-test-runner** subagent with the following context:

- Test file to execute:
  `tests/test_$ARGUMENTS.py`
- Spec file for context:
  `.claude/specs/$ARGUMENTS.md`
- Source files to analyze against when diagnosing failures:
  - `scripts/generate_all_stats.py`
  - `scripts/generate_streak_svg.py`
- Run command:
  `python -m pytest tests/test_$ARGUMENTS.py -v`
- Instruction: Run ONLY the specified test file. Do NOT run
  the full test suite. Never call the live GitHub API — if a
  test would require network access, flag it instead of running
  it. Analyze any failures by cross-referencing the test code,
  the spec, and the source files. Classify each failure as a
  bug or a missing feature.

---

## Handoff Rules

- Do NOT start Step 2 until Step 1 is fully complete
- Do NOT attempt to fix any code regardless of what
  the test results show
- Do NOT run any tests beyond `tests/test_$ARGUMENTS.py`
- Never let a test hit the live GitHub GraphQL API
- If profile-test-writer reports it could not write
  the test file, stop and report the reason — do NOT
  proceed to Step 2

---

## Final Output

After both subagents complete, produce a combined summary:

### Testing Pipeline Report — $ARGUMENTS

**Step 1 — Tests Written**
- List each test written with a one-line description
  of which spec requirement it validates

**Step 2 — Test Results**
- Mirror the profile-test-runner's structured report

**Verdict**
One of:
- ✅ Ready for code review — all tests pass
- ❌ Needs fixes — list the failing tests and their root causes
