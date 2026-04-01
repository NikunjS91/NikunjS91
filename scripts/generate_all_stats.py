#!/usr/bin/env python3
import datetime as dt
import json
import os
import subprocess
from pathlib import Path
from collections import Counter


def run_graphql_query(query: str, fields: dict[str, str]) -> dict:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in fields.items():
        cmd.extend(["-F", f"{key}={value}"])
    output = subprocess.check_output(cmd, text=True)
    return json.loads(output)


def fmt_date(date_str: str) -> str:
    if not date_str:
        return "-"
    parsed = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
    return parsed.strftime("%d %b %Y")


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


def build_streak_svg(total: int, streak: int, streak_start: str, streak_end: str, longest: int, longest_start: str, longest_end: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="495" height="195" viewBox="0 0 495 195">
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
  </defs>
  
  <rect x="0.5" y="0.5" width="494" height="194" rx="12" fill="url(#bgGradient)" stroke="#667eea" stroke-width="2"/>
  
  <rect x="15" y="40" width="140" height="120" rx="10" fill="#1f2937" opacity="0.6"/>
  <text x="85" y="80" text-anchor="middle" fill="#ffffff" font-size="32" font-family="Segoe UI, sans-serif" font-weight="700">{total}</text>
  <text x="85" y="105" text-anchor="middle" fill="url(#statGradient)" font-size="12" font-family="Segoe UI, sans-serif" font-weight="600">Total Contributions</text>
  <text x="85" y="140" text-anchor="middle" fill="#9ca3af" font-size="9" font-family="Segoe UI, sans-serif">2025 - Present</text>
  
  <rect x="177" y="30" width="140" height="140" rx="10" fill="#1f2937" opacity="0.7"/>
  <text x="247" y="75" text-anchor="middle" fill="#ffffff" font-size="40" font-family="Segoe UI, sans-serif" font-weight="700">{streak}</text>
  <text x="247" y="105" text-anchor="middle" fill="url(#fireGradient)" font-size="13" font-family="Segoe UI, sans-serif" font-weight="700">🔥 Current Streak</text>
  <text x="247" y="140" text-anchor="middle" fill="#d1d5db" font-size="9" font-family="Segoe UI, sans-serif">{fmt_date(streak_start)}</text>
  <text x="247" y="155" text-anchor="middle" fill="#d1d5db" font-size="9" font-family="Segoe UI, sans-serif">{fmt_date(streak_end)}</text>
  
  <rect x="339" y="40" width="140" height="120" rx="10" fill="#1f2937" opacity="0.6"/>
  <text x="409" y="80" text-anchor="middle" fill="#ffffff" font-size="32" font-family="Segoe UI, sans-serif" font-weight="700">{longest}</text>
  <text x="409" y="105" text-anchor="middle" fill="url(#statGradient)" font-size="12" font-family="Segoe UI, sans-serif" font-weight="600">Longest Streak</text>
  <text x="409" y="133" text-anchor="middle" fill="#9ca3af" font-size="9" font-family="Segoe UI, sans-serif">{fmt_date(longest_start)}</text>
  <text x="409" y="145" text-anchor="middle" fill="#9ca3af" font-size="9" font-family="Segoe UI, sans-serif">{fmt_date(longest_end)}</text>
</svg>
"""


def build_stats_svg(stars: int, commits: int, prs: int, issues: int, repos: int) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="495" height="195" viewBox="0 0 495 195">
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1b27;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#26264d;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="accentGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <rect x="0.5" y="0.5" width="494" height="194" rx="12" fill="url(#bgGradient)" stroke="#667eea" stroke-width="2"/>
  
  <text x="247.5" y="35" text-anchor="middle" fill="#ffffff" font-size="16" font-family="Segoe UI, sans-serif" font-weight="700">GitHub Statistics</text>
  
  <g transform="translate(40, 60)">
    <text x="0" y="20" fill="url(#accentGradient)" font-size="13" font-family="Segoe UI, sans-serif" font-weight="600">⭐ Total Stars</text>
    <text x="180" y="20" fill="#ffffff" font-size="22" font-family="Segoe UI, sans-serif" font-weight="700">{stars}</text>
  </g>
  
  <g transform="translate(40, 95)">
    <text x="0" y="20" fill="url(#accentGradient)" font-size="13" font-family="Segoe UI, sans-serif" font-weight="600">💻 Total Commits</text>
    <text x="180" y="20" fill="#ffffff" font-size="22" font-family="Segoe UI, sans-serif" font-weight="700">{commits}</text>
  </g>
  
  <g transform="translate(270, 60)">
    <text x="0" y="20" fill="url(#accentGradient)" font-size="13" font-family="Segoe UI, sans-serif" font-weight="600">📦 Public Repos</text>
    <text x="140" y="20" fill="#ffffff" font-size="22" font-family="Segoe UI, sans-serif" font-weight="700">{repos}</text>
  </g>
  
  <g transform="translate(270, 95)">
    <text x="0" y="20" fill="url(#accentGradient)" font-size="13" font-family="Segoe UI, sans-serif" font-weight="600">🔀 Pull Requests</text>
    <text x="140" y="20" fill="#ffffff" font-size="22" font-family="Segoe UI, sans-serif" font-weight="700">{prs}</text>
  </g>
  
  <g transform="translate(155, 130)">
    <text x="0" y="20" fill="url(#accentGradient)" font-size="13" font-family="Segoe UI, sans-serif" font-weight="600">🐛 Issues</text>
    <text x="100" y="20" fill="#ffffff" font-size="22" font-family="Segoe UI, sans-serif" font-weight="700">{issues}</text>
  </g>
</svg>
"""


def build_languages_svg(languages: dict[str, int]) -> str:
    total = sum(languages.values())
    colors = {
        "Python": "#3572A5",
        "JavaScript": "#f1e05a",
        "TypeScript": "#2b7489",
        "HTML": "#e34c26",
        "CSS": "#563d7c",
        "Jupyter Notebook": "#DA5B0B",
        "R": "#198CE7",
    }
    
    sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
    
    svg_parts = ["""<svg xmlns="http://www.w3.org/2000/svg" width="495" height="195" viewBox="0 0 495 195">
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1b27;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#26264d;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <rect x="0.5" y="0.5" width="494" height="194" rx="12" fill="url(#bgGradient)" stroke="#667eea" stroke-width="2"/>
  
  <text x="247.5" y="35" text-anchor="middle" fill="#ffffff" font-size="16" font-family="Segoe UI, sans-serif" font-weight="700">Top Languages</text>
"""]
    
    y_pos = 65
    for lang, bytes_count in sorted_langs:
        pct = (bytes_count / total) * 100
        color = colors.get(lang, "#858585")
        
        svg_parts.append(f"""  <g transform="translate(40, {y_pos})">
    <circle cx="5" cy="5" r="5" fill="{color}"/>
    <text x="20" y="10" fill="#d1d5db" font-size="12" font-family="Segoe UI, sans-serif">{lang}</text>
    <text x="420" y="10" fill="#ffffff" font-size="12" font-family="Segoe UI, sans-serif" font-weight="600">{pct:.1f}%</text>
  </g>
""")
        y_pos += 25
    
    svg_parts.append("</svg>\n")
    return "".join(svg_parts)


def main() -> None:
    user = os.environ.get("GITHUB_USER", "NikunjS91")
    now = dt.datetime.now(dt.timezone.utc)
    start = (now - dt.timedelta(days=364)).replace(hour=0, minute=0, second=0, microsecond=0)

    # Get contribution data for streak
    contrib_query = """
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
    contrib_data = run_graphql_query(contrib_query, {
        "login": user,
        "from": start.isoformat(),
        "to": now.isoformat(),
    })

    calendar = contrib_data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    total = calendar["totalContributions"]
    days = [d for w in calendar["weeks"] for d in w["contributionDays"]]

    streak, streak_start, streak_end = current_streak(days)
    longest, longest_start, longest_end = longest_streak(days)

    # Get stats data
    stats_query = """
query($login:String!) {
  user(login:$login) {
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10) {
          edges {
            size
            node { name }
          }
        }
      }
    }
    pullRequests(first: 1) { totalCount }
    issues(first: 1) { totalCount }
    contributionsCollection {
      totalCommitContributions
    }
  }
}
"""
    stats_data = run_graphql_query(stats_query, {"login": user})
    user_data = stats_data["data"]["user"]

    stars = sum(repo["stargazerCount"] for repo in user_data["repositories"]["nodes"])
    repos = user_data["repositories"]["totalCount"]
    commits = user_data["contributionsCollection"]["totalCommitContributions"]
    prs = user_data["pullRequests"]["totalCount"]
    issues = user_data["issues"]["totalCount"]

    # Calculate languages
    lang_bytes = Counter()
    for repo in user_data["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            lang_bytes[edge["node"]["name"]] += edge["size"]

    # Generate SVGs
    out_dir = Path("assets")
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "streak.svg").write_text(build_streak_svg(total, streak, streak_start, streak_end, longest, longest_start, longest_end), encoding="utf-8")
    (out_dir / "stats.svg").write_text(build_stats_svg(stars, commits, prs, issues, repos), encoding="utf-8")
    (out_dir / "languages.svg").write_text(build_languages_svg(dict(lang_bytes)), encoding="utf-8")
    
    print(f"✅ Generated 3 stat cards")


if __name__ == "__main__":
    main()
