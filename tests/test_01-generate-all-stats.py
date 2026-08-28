"""
Tests for the 01-generate-all-stats spec:
Validates that build_streak_svg() in scripts/generate_all_stats.py
uses the upgraded streak card design (glow filter, circle frame,
fire path, accessibility attributes, updated font family).
"""

import json
import os
import sys
import xml.etree.ElementTree as ET
from unittest.mock import patch, MagicMock

import pytest

# Ensure repo root is on sys.path so `scripts` package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.generate_all_stats import build_streak_svg, fmt_date, main  # noqa: E402

# ---------------------------------------------------------------------------
# Shared fixture: a standard SVG output used by most tests
# ---------------------------------------------------------------------------

STANDARD_SVG = build_streak_svg(
    100, 5, "2026-08-01", "2026-08-05", 10, "2026-07-01", "2026-07-10"
)


# ---------------------------------------------------------------------------
# Test 1 — SVG structure: glow filter present
# ---------------------------------------------------------------------------

def test_glow_filter_present():
    """Root <defs> must contain a <filter id='glow'> with feGaussianBlur and feMerge."""
    svg = STANDARD_SVG
    assert '<filter id="glow">' in svg, "Expected <filter id=\"glow\"> in SVG output"
    assert "feGaussianBlur" in svg, "Expected feGaussianBlur inside glow filter"
    assert "feMerge" in svg, "Expected feMerge inside glow filter"


# ---------------------------------------------------------------------------
# Test 2 — SVG structure: accessibility attributes on root <svg>
# ---------------------------------------------------------------------------

def test_accessibility_attributes():
    """Root <svg> element must carry role='img' and aria-label='GitHub streak stats'."""
    svg = STANDARD_SVG
    assert 'role="img"' in svg, "Expected role=\"img\" on root <svg>"
    assert 'aria-label="GitHub streak stats"' in svg, (
        "Expected aria-label=\"GitHub streak stats\" on root <svg>"
    )


# ---------------------------------------------------------------------------
# Test 3 — SVG structure: circle frame on current streak card
# ---------------------------------------------------------------------------

def test_circle_frame_present():
    """Current streak card must render a <circle> with cx='247' and cy='65'."""
    svg = STANDARD_SVG
    assert "<circle" in svg, "Expected <circle element in SVG output"
    assert 'cx="247"' in svg, "Expected cx=\"247\" on circle element"
    assert 'cy="65"' in svg, "Expected cy=\"65\" on circle element"


# ---------------------------------------------------------------------------
# Test 4 — SVG structure: decorative fire path present
# ---------------------------------------------------------------------------

def test_fire_path_present():
    """A <path> element using the fireGradient fill must be present."""
    svg = STANDARD_SVG
    assert "<path" in svg, "Expected <path element in SVG output"
    assert "fireGradient" in svg, (
        "Expected fireGradient referenced on a path element"
    )


# ---------------------------------------------------------------------------
# Test 5 — SVG structure: font family updated
# ---------------------------------------------------------------------------

def test_font_family():
    """All text must use 'Segoe UI, Ubuntu, sans-serif' font stack."""
    svg = STANDARD_SVG
    assert "Segoe UI, Ubuntu, sans-serif" in svg, (
        "Expected font-family 'Segoe UI, Ubuntu, sans-serif' in SVG output"
    )


# ---------------------------------------------------------------------------
# Test 6 — SVG values: streak number rendered correctly
# ---------------------------------------------------------------------------

def test_streak_number_rendered():
    """The current streak count must appear as text in the SVG."""
    svg = build_streak_svg(100, 7, "2026-08-01", "2026-08-07", 10, "2026-07-01", "2026-07-10")
    assert ">7<" in svg, "Expected streak value '7' to appear as SVG text content"


# ---------------------------------------------------------------------------
# Test 7 — SVG values: total contributions rendered
# ---------------------------------------------------------------------------

def test_total_contributions_rendered():
    """The total contributions count must appear as text in the SVG."""
    svg = build_streak_svg(42, 5, "2026-08-01", "2026-08-05", 10, "2026-07-01", "2026-07-10")
    assert ">42<" in svg, "Expected total contributions '42' to appear as SVG text content"


# ---------------------------------------------------------------------------
# Test 8 — SVG values: longest streak rendered
# ---------------------------------------------------------------------------

def test_longest_streak_rendered():
    """The longest streak count must appear as text in the SVG."""
    svg = build_streak_svg(100, 5, "2026-08-01", "2026-08-05", 15, "2026-07-01", "2026-07-15")
    assert ">15<" in svg, "Expected longest streak '15' to appear as SVG text content"


# ---------------------------------------------------------------------------
# Test 9 — SVG values: date formatting via fmt_date
# ---------------------------------------------------------------------------

def test_date_formatting():
    """streak_start='2026-08-01' must render as '01 Aug 2026' in the SVG."""
    svg = build_streak_svg(100, 5, "2026-08-01", "2026-08-05", 10, "2026-07-01", "2026-07-10")
    assert "01 Aug 2026" in svg, (
        "Expected fmt_date('2026-08-01') == '01 Aug 2026' to appear in SVG output"
    )


# ---------------------------------------------------------------------------
# Test 10 — Edge case: zero streak
# ---------------------------------------------------------------------------

def test_zero_streak():
    """streak=0 with empty date strings must render '0' and '-' for missing dates."""
    svg = build_streak_svg(50, 0, "", "", 3, "2026-07-01", "2026-07-03")
    assert ">0<" in svg, "Expected '0' for zero current streak"
    # fmt_date("") returns "-"; it should appear at least once for the two empty dates
    assert "-" in svg, "Expected '-' placeholder for empty streak date strings"


# ---------------------------------------------------------------------------
# Test 11 — Edge case: zero contributions, SVG is valid XML
# ---------------------------------------------------------------------------

def test_zero_contributions_valid_xml():
    """total=0 must produce '0' in output and the result must parse as valid XML."""
    svg = build_streak_svg(0, 0, "", "", 0, "", "")
    assert ">0<" in svg, "Expected '0' to appear in SVG for zero total contributions"
    # Will raise if not well-formed
    ET.fromstring(svg)


# ---------------------------------------------------------------------------
# Test 12 — SVG validity: well-formed XML
# ---------------------------------------------------------------------------

def test_svg_is_well_formed_xml():
    """Output of build_streak_svg() with typical values must parse without error."""
    svg = STANDARD_SVG
    try:
        ET.fromstring(svg)
    except ET.ParseError as exc:
        pytest.fail(f"build_streak_svg() produced invalid XML: {exc}")


# ---------------------------------------------------------------------------
# Test 13 — Gradient IDs preserved
# ---------------------------------------------------------------------------

def test_gradient_ids_preserved():
    """bgGradient, fireGradient, and statGradient must all be defined in <defs>."""
    svg = STANDARD_SVG
    assert 'id="bgGradient"' in svg, "Expected id=\"bgGradient\" in SVG defs"
    assert 'id="fireGradient"' in svg, "Expected id=\"fireGradient\" in SVG defs"
    assert 'id="statGradient"' in svg, "Expected id=\"statGradient\" in SVG defs"


# ---------------------------------------------------------------------------
# Test 14 — main() with mocked GraphQL: all three SVG files written
# ---------------------------------------------------------------------------

def _make_fake_graphql_response(call_count: list) -> bytes:
    """Return alternating fake GraphQL JSON bodies for the two queries main() issues."""
    call_count[0] += 1
    if call_count[0] == 1:
        # First call: contribution / streak query
        return json.dumps({
            "data": {
                "user": {
                    "contributionsCollection": {
                        "contributionCalendar": {
                            "totalContributions": 123,
                            "weeks": [
                                {
                                    "contributionDays": [
                                        {"date": "2026-08-01", "contributionCount": 3},
                                        {"date": "2026-08-02", "contributionCount": 5},
                                    ]
                                }
                            ],
                        }
                    }
                }
            }
        }).encode()
    else:
        # Second call: stats / languages query
        return json.dumps({
            "data": {
                "user": {
                    "repositories": {
                        "totalCount": 10,
                        "nodes": [
                            {
                                "stargazerCount": 7,
                                "languages": {
                                    "edges": [
                                        {"size": 10000, "node": {"name": "Python"}},
                                    ]
                                },
                            }
                        ],
                    },
                    "pullRequests": {"totalCount": 2},
                    "issues": {"totalCount": 1},
                    "contributionsCollection": {"totalCommitContributions": 50},
                }
            }
        }).encode()


def test_main_writes_all_three_svgs(tmp_path):
    """main() with mocked subprocess must write streak.svg, stats.svg, and languages.svg."""
    call_count = [0]

    def fake_check_output(cmd, text=False):
        raw = _make_fake_graphql_response(call_count)
        return raw.decode() if text else raw

    # Redirect asset output to tmp_path so we never touch the real assets/ directory
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        with patch("subprocess.check_output", side_effect=fake_check_output):
            with patch.dict(os.environ, {"GITHUB_USER": "TestUser"}):
                main()

        assert (tmp_path / "assets" / "streak.svg").exists(), "assets/streak.svg not written"
        assert (tmp_path / "assets" / "stats.svg").exists(), "assets/stats.svg not written"
        assert (tmp_path / "assets" / "languages.svg").exists(), "assets/languages.svg not written"
    finally:
        os.chdir(original_cwd)


# ---------------------------------------------------------------------------
# Test 15 — Deleted script: generate_streak_svg.py must not exist
# ---------------------------------------------------------------------------

def test_deleted_script_does_not_exist():
    """scripts/generate_streak_svg.py must have been deleted as part of this change."""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    deleted_path = os.path.join(repo_root, "scripts", "generate_streak_svg.py")
    assert not os.path.exists(deleted_path), (
        f"scripts/generate_streak_svg.py still exists at {deleted_path}; "
        "it should have been deleted as part of this spec."
    )
