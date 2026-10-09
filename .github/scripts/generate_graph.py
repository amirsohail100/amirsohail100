#!/usr/bin/env python3
"""Generates an animated contribution line graph (SVG) for the last 31 days.
Uses only the Python standard library. Run with --demo to test without network."""
import json, os, random, sys, urllib.request
from datetime import datetime, timedelta, timezone
from html import escape

USER = os.environ.get("GH_USER") or os.environ.get("GITHUB_REPOSITORY_OWNER") or "amirsohail100"
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
OUT = os.environ.get("OUT_FILE", "dist/contribution-graph.svg")
DAYS = 31

def fetch_days():
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=DAYS + 2)
    query = """query($login:String!,$from:DateTime!,$to:DateTime!){
      user(login:$login){contributionsCollection(from:$from,to:$to){
        contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"""
    body = json.dumps({"query": query, "variables": {
        "login": USER, "from": start.isoformat(), "to": end.isoformat()}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=body, headers={
        "Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json",
        "User-Agent": "contribution-graph-generator"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(f"GitHub API error: {data['errors']}")
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    counts = {d["date"]: d["contributionCount"] for w in weeks for d in w["contributionDays"]}
    today = end.date()
    days = [today - timedelta(days=i) for i in range(DAYS - 1, -1, -1)]
    return [(d, counts.get(d.isoformat(), 0)) for d in days]

def demo_days():
    random.seed(7)
    today = datetime.now(timezone.utc).date()
    return [(today - timedelta(days=i), random.randint(0, 45)) for i in range(DAYS - 1, -1, -1)]

def smooth_path(pts, y_min, y_max):
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[max(i - 1, 0)]; p1 = pts[i]; p2 = pts[i + 1]; p3 = pts[min(i + 2, len(pts) - 1)]
        c1x = p1[0] + (p2[0] - p0[0]) / 6; c1y = p1[1] + (p2[1] - p0[1]) / 6
        c2x = p2[0] - (p3[0] - p1[0]) / 6; c2y = p2[1] - (p3[1] - p1[1]) / 6
        c1y = min(max(c1y, y_min), y_max); c2y = min(max(c2y, y_min), y_max)
        d += f" C{c1x:.1f},{c1y:.1f} {c2x:.1f},{c2y:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d

def build_svg(days):
    W, H = 800, 340
    L, R, T, B = 56, 24, 62, 52
    pw, ph = W - L - R, H - T - B
    peak = max(c for _, c in days)
    step = max(1, -(-peak // 5))            # ceil(peak / 5)
    ymax = step * 5
    xs = [L + pw * i / (len(days) - 1) for i in range(len(days))]
    ys = [T + ph - ph * c / ymax for _, c in days]
    pts = list(zip(xs, ys))
    line = smooth_path(pts, T, T + ph)
    area = f"{line} L{xs[-1]:.1f},{T+ph} L{xs[0]:.1f},{T+ph} Z"
    grid = "".join(
        f'<line x1="{L}" y1="{T+ph-ph*k/5:.1f}" x2="{W-R}" y2="{T+ph-ph*k/5:.1f}" class="grid"/>'
        f'<text x="{L-10}" y="{T+ph-ph*k/5+4:.1f}" class="ylab" text-anchor="end">{step*k}</text>'
        for k in range(6))
    xlabs = "".join(
        f'<text x="{x:.1f}" y="{T+ph+20}" class="xlab" text-anchor="middle">{d.day}</text>'
        for x, (d, _) in zip(xs, days))
    dots = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.6" class="dot" style="animation-delay:{1.2 + i*0.07:.2f}s">'
        f'<title>{d.strftime("%d %b")}: {c} contributions</title></circle>'
        for i, ((x, y), (d, c)) in enumerate(zip(pts, days)))
    title = escape(f"{USER}'s Contribution Graph")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{title}">
<style>
  .bg{{fill:#0d1117}}
  .title{{fill:#c9d1d9;font:700 15px 'Segoe UI',Arial,sans-serif}}
  .grid{{stroke:#22d3ee;stroke-opacity:.12;stroke-width:1}}
  .ylab,.xlab{{fill:#8b949e;font:600 10px 'Segoe UI',Arial,sans-serif}}
  .axis{{fill:#8b949e;font:600 10px 'Segoe UI',Arial,sans-serif}}
  .line{{fill:none;stroke:#22d3ee;stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round;
         stroke-dasharray:1;stroke-dashoffset:1;animation:draw 2.6s ease-out .2s forwards}}
  .area{{fill:url(#g);opacity:0;animation:fade 1.6s ease-out 1.2s forwards}}
  .dot{{fill:#fff;stroke:#22d3ee;stroke-width:1.5;opacity:0;animation:pop .4s ease-out forwards}}
  @keyframes draw{{to{{stroke-dashoffset:0}}}}
  @keyframes fade{{to{{opacity:1}}}}
  @keyframes pop{{from{{opacity:0}}to{{opacity:1}}}}
</style>
<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#22d3ee" stop-opacity=".32"/><stop offset="1" stop-color="#22d3ee" stop-opacity="0"/>
</linearGradient></defs>
<rect class="bg" width="{W}" height="{H}" rx="10"/>
<text class="title" x="{W/2}" y="30" text-anchor="middle">{title}</text>
{grid}
<path class="area" d="{area}"/>
<path class="line" pathLength="1" d="{line}"/>
{dots}
{xlabs}
<text class="axis" x="{W/2}" y="{H-10}" text-anchor="middle">Days (last {DAYS})</text>
<text class="axis" transform="translate(14 {T+ph/2}) rotate(-90)" text-anchor="middle">Contributions</text>
</svg>'''

def main():
    days = demo_days() if "--demo" in sys.argv else fetch_days()
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(build_svg(days))
    print(f"Wrote {OUT} ({len(days)} days, peak {max(c for _, c in days)})")

if __name__ == "__main__":
    main()
