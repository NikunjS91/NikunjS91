#!/usr/bin/env python3
import datetime as dt
import json
import os
import subprocess
from pathlib import Path


def run_graphql_query(query: str, fields: dict[str, str]) -> dict:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in fields.items():
        cmd.extend(["-F", f"{key}={value}"])
    output = subprocess.check_output(cmd, text=True)
    return json.loads(output)


def current_streak(days: list[dict]) -> tuple[int, str, str]:
    streak = 0
    streak_start = ""
    streak_end = ""
    for day in reversed(days):
        if day["contributionCount"] > 0:
            streak += 1
            streak_start = day["date"]
            if not streak_end:
                streak_end = day["date"]
        else:
            break
    return streak, streak_start, streak_end


def longest_streak(days: list[dict]) -> tuple[int, str, str]:
    best_len = 0
    best_start = ""
    best_end = ""
    cur_len = 0
    cur_start = ""
    cur_end = ""

    for day in days:
        if day["contributionCount"] > 0:
            if cur_len == 0:
                cur_start = day["date"]
            cur_len += 1
            cur_end = day["date"]
            if cur_len > best_len:
                best_len = cur_len
                best_start = cur_start
                best_end = cur_end
        else:
            cur_len = 0
    return best_len, best_start, best_end


def fmt_date(date_str: str) -> str:
    if not date_str:
        return "-"
    parsed = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
    return parsed.strftime("%d %b %Y")


def build_svg(total: int, streak: int, streak_start: str, streak_end: str, longest: int, longest_start: str, longest_end: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="495" height="195" viewBox="0 0 495 195" role="img" aria-label="GitHub streak stats">
  <rect x="0.5" y="0.5" width="494" height="194" rx="4.5" fill="#151515" stroke="#30363d"/>
  <line x1="165" y1="28" x2="165" y2="170" stroke="#30363d"/>
  <line x1="330" y1="28" x2="330" y2="170" stroke="#30363d"/>

  <text x="82.5" y="80" text-anchor="middle" fill="#f0f6fc" font-size="28" font-family="Segoe UI, Ubuntu, sans-serif" font-weight="700">{total}</text>
  <text x="82.5" y="114" text-anchor="middle" fill="#f0f6fc" font-size="14" font-family="Segoe UI, Ubuntu, sans-serif">Total Contributions</text>

  <circle cx="247.5" cy="71" r="40" fill="none" stroke="#fb8c00" stroke-width="5"/>
  <text x="247.5" y="80" text-anchor="middle" fill="#f0f6fc" font-size="28" font-family="Segoe UI, Ubuntu, sans-serif" font-weight="700">{streak}</text>
  <text x="247.5" y="114" text-anchor="middle" fill="#fb8c00" font-size="14" font-family="Segoe UI, Ubuntu, sans-serif" font-weight="700">Current Streak</text>
  <text x="247.5" y="132" text-anchor="middle" fill="#8b949e" font-size="12" font-family="Segoe UI, Ubuntu, sans-serif">{fmt_date(streak_start)} - {fmt_date(streak_end)}</text>

  <text x="412.5" y="80" text-anchor="middle" fill="#f0f6fc" font-size="28" font-family="Segoe UI, Ubuntu, sans-serif" font-weight="700">{longest}</text>
  <text x="412.5" y="114" text-anchor="middle" fill="#f0f6fc" font-size="14" font-family="Segoe UI, Ubuntu, sans-serif">Longest Streak</text>
  <text x="412.5" y="132" text-anchor="middle" fill="#8b949e" font-size="12" font-family="Segoe UI, Ubuntu, sans-serif">{fmt_date(longest_start)} - {fmt_date(longest_end)}</text>
</svg>
"""


def main() -> None:
    user = os.environ.get("GITHUB_USER", "NikunjS91")
    now = dt.datetime.now(dt.timezone.utc)
    # GitHub GraphQL limits contribution range queries to <= 1 year.
    start = (now - dt.timedelta(days=364)).replace(hour=0, minute=0, second=0, microsecond=0)

    query = """
query($login:String!, $from:DateTime!, $to:DateTime!) {
  user(login:$login) {
    contributionsCollection(from:$from, to:$to) {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""
    response = run_graphql_query(
        query,
        {
            "login": user,
            "from": start.isoformat(),
            "to": now.isoformat(),
        },
    )

    calendar = response["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    total = calendar["totalContributions"]
    days = [d for w in calendar["weeks"] for d in w["contributionDays"]]

    streak, streak_start, streak_end = current_streak(days)
    longest, longest_start, longest_end = longest_streak(days)

    svg = build_svg(total, streak, streak_start, streak_end, longest, longest_start, longest_end)
    out_path = Path("assets/streak.svg")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
