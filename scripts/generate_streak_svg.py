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
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1b27;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#26264d;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="fireGradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#ff6b35;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#f7931e;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#ffd23f;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="statGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  
  <rect x="0.5" y="0.5" width="494" height="194" rx="12" fill="url(#bgGradient)" stroke="#667eea" stroke-width="2"/>
  
  <!-- Total Contributions Card -->
  <rect x="15" y="30" width="140" height="140" rx="10" fill="#1f2937" opacity="0.6"/>
  <text x="85" y="85" text-anchor="middle" fill="#ffffff" font-size="36" font-family="Segoe UI, Ubuntu, sans-serif" font-weight="700" filter="url(#glow)">{total}</text>
  <text x="85" y="110" text-anchor="middle" fill="url(#statGradient)" font-size="13" font-family="Segoe UI, Ubuntu, sans-serif" font-weight="600">Total</text>
  <text x="85" y="125" text-anchor="middle" fill="url(#statGradient)" font-size="13" font-family="Segoe UI, Ubuntu, sans-serif" font-weight="600">Contributions</text>
  <text x="85" y="150" text-anchor="middle" fill="#9ca3af" font-size="10" font-family="Segoe UI, Ubuntu, sans-serif">2025 - Present</text>
  
  <!-- Current Streak Card (Featured) -->
  <rect x="177" y="20" width="140" height="160" rx="10" fill="#1f2937" opacity="0.7"/>
  <circle cx="247" cy="65" r="32" fill="none" stroke="url(#fireGradient)" stroke-width="5" filter="url(#glow)"/>
  <path d="M 247 42 l 5 6 l -2.5 0 l 0 12 l -5 0 l 0 -12 l -2.5 0 z" fill="url(#fireGradient)" filter="url(#glow)"/>
  <text x="247" y="73" text-anchor="middle" fill="#ffffff" font-size="30" font-family="Segoe UI, Ubuntu, sans-serif" font-weight="700" filter="url(#glow)">{streak}</text>
  <text x="247" y="115" text-anchor="middle" fill="url(#fireGradient)" font-size="14" font-family="Segoe UI, Ubuntu, sans-serif" font-weight="700">Current Streak</text>
  <text x="247" y="145" text-anchor="middle" fill="#d1d5db" font-size="10" font-family="Segoe UI, Ubuntu, sans-serif">{fmt_date(streak_start)}</text>
  <text x="247" y="165" text-anchor="middle" fill="#d1d5db" font-size="10" font-family="Segoe UI, Ubuntu, sans-serif">{fmt_date(streak_end)}</text>
  
  <!-- Longest Streak Card -->
  <rect x="339" y="30" width="140" height="140" rx="10" fill="#1f2937" opacity="0.6"/>
  <text x="409" y="85" text-anchor="middle" fill="#ffffff" font-size="36" font-family="Segoe UI, Ubuntu, sans-serif" font-weight="700" filter="url(#glow)">{longest}</text>
  <text x="409" y="110" text-anchor="middle" fill="url(#statGradient)" font-size="13" font-family="Segoe UI, Ubuntu, sans-serif" font-weight="600">Longest</text>
  <text x="409" y="125" text-anchor="middle" fill="url(#statGradient)" font-size="13" font-family="Segoe UI, Ubuntu, sans-serif" font-weight="600">Streak</text>
  <text x="409" y="145" text-anchor="middle" fill="#9ca3af" font-size="10" font-family="Segoe UI, Ubuntu, sans-serif">{fmt_date(longest_start)}</text>
  <text x="409" y="157" text-anchor="middle" fill="#9ca3af" font-size="10" font-family="Segoe UI, Ubuntu, sans-serif">{fmt_date(longest_end)}</text>
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
