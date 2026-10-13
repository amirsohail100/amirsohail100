#!/usr/bin/env python3
"""Generates two extra animated cards next to your existing stats cards:
  dist/now.svg     - 'Currently Exploring' strip (static text, animated chips)
  dist/rhythm.svg  - 'Coding Rhythm' (weekday + monthly activity patterns)
These cards never show total counts, so they can't disagree with your accurate stats cards.
Standard library only. Run with --demo to build samples without network."""
import json, os, sys, urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from html import escape

USER = os.environ.get("GH_USER") or os.environ.get("GITHUB_REPOSITORY_OWNER") or "amirsohail100"
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
OUT_DIR = os.environ.get("OUT_DIR", "dist")

# Edit this list any time: what you're exploring right now.
EXPLORING = ["Agentic AI & LangGraph", "Fine-tuning LLMs", "Advanced Vector DBs", "AWS & Kubernetes", "CI/CD Pipelines"]

FONT = "'Segoe UI',Arial,sans-serif"
ACC = "#22d3ee"

def fetch_days():
    now = datetime.now(timezone.utc); start = now - timedelta(days=365)
    q = """query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){
      contributionsCollection(from:$from,to:$to){contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"""
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": q, "variables": {"login": USER, "from": start.isoformat(), "to": now.isoformat()}}).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json", "User-Agent": "extras-generator"})
    with urllib.request.urlopen(req, timeout=40) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(f"GitHub API error: {data['errors']}")
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return {d["date"]: d["contributionCount"] for w in weeks for d in w["contributionDays"]}

def demo_days():
    import random; random.seed(11)
    t = date.today(); out = {}
    for i in range(365):
        d = t - timedelta(days=i)
        out[d.isoformat()] = random.randint(0, 25) * (2 if d.weekday() in (1, 2) else 1)
    return out

def now_svg():
    W = 800; x = 24; y = 90; chips = ""; i = 0; rows = 1
    for label in EXPLORING:
        w = len(label) * 7.1 + 40
        if x + w > W - 24:
            x = 24; y += 40; rows += 1
        chips += (f'<g class="rise" style="animation-delay:{.12*i:.2f}s"><rect x="{x}" y="{y-20}" width="{w:.0f}" height="30" rx="15" class="chip"/>'
                  f'<circle cx="{x+16}" cy="{y-5}" r="4" class="dot" style="animation-delay:{.4*i:.1f}s"/>'
                  f'<text x="{x+28}" y="{y}" class="ct">{escape(label)}</text></g>')
        x += w + 10; i += 1
    H = y + 28
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Currently exploring">
<style>
  .bg{{fill:#0d1117;stroke:#30363d}}
  .t{{fill:#e6edf3;font:800 18px {FONT}}}
  .s{{fill:#8b949e;font:600 12px {FONT}}}
  .chip{{fill:#11161d;stroke:#21262d}}
  .ct{{fill:#c9d1d9;font:600 13px {FONT}}}
  .dot{{fill:{ACC};animation:pulse 1.8s ease-in-out infinite}}
  .rise{{opacity:0;animation:rise .6s ease-out forwards}}
  @keyframes pulse{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}
  @keyframes rise{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
</style>
<rect class="bg" x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14"/>
<text class="t" x="24" y="34">Currently Exploring</text>
<text class="s" x="24" y="52">What I'm learning and building right now</text>
{chips}
</svg>'''

DAYN = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
DAYF = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONF = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def rhythm_svg(days):
    wk = [0] * 7; months = defaultdict(int); active = 0
    for ds, c in days.items():
        d = date.fromisoformat(ds)
        wk[(d.weekday() + 1) % 7] += c          # Sunday = 0
        months[(d.year, d.month)] += c
        active += c > 0
    keys = sorted(months)[-12:]
    mvals = [months[k] for k in keys]
    best_day = DAYF[wk.index(max(wk))]
    best_month = MONF[keys[mvals.index(max(mvals))][1] - 1]
    active_pct = round(100 * active / max(len(days), 1))
    W, H = 800, 318
    tiles = [("Most Active Day", best_day), ("Most Active Month", best_month), ("Days With Activity", f"{active_pct}%")]
    tw = 242; t = ""
    for i, (lab, val) in enumerate(tiles):
        x = 24 + i * (tw + 13)
        t += (f'<g class="rise" style="animation-delay:{.15*i:.2f}s"><rect x="{x}" y="70" width="{tw}" height="56" rx="8" class="tile"/>'
              f'<text x="{x+tw/2}" y="96" class="tv" text-anchor="middle">{val}</text>'
              f'<text x="{x+tw/2}" y="115" class="tl" text-anchor="middle">{lab}</text></g>')
    def bars(vals, labels, x0, w, hi_idx, delay0):
        top, base = 178, 282; mh = base - top; mx = max(vals) or 1
        n = len(vals); gap = 8; bw = (w - gap * (n - 1)) / n; out = ""
        for i, v in enumerate(vals):
            h = max(3, mh * v / mx); x = x0 + i * (bw + gap)
            cls = "hi" if i == hi_idx else "lo"
            out += (f'<rect x="{x:.1f}" y="{base-h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="3" class="bar {cls}" '
                    f'style="animation-delay:{delay0+.07*i:.2f}s"><title>{labels[i]}</title></rect>'
                    f'<text x="{x+bw/2:.1f}" y="{base+16}" class="bl" text-anchor="middle">{labels[i]}</text>')
        return out
    wbars = bars(wk, DAYN, 44, 330, wk.index(max(wk)), 1.0)
    mbars = bars(mvals, [MON[k[1]-1][0] for k in keys], 438, 318, mvals.index(max(mvals)), 1.2)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Coding rhythm">
<style>
  .bg{{fill:#0d1117;stroke:#30363d}}
  .tile{{fill:#11161d;stroke:#21262d}}
  .t{{fill:#e6edf3;font:800 20px {FONT}}}
  .s{{fill:#8b949e;font:600 12px {FONT}}}
  .tv{{fill:{ACC};font:800 20px {FONT}}}
  .tl{{fill:#8b949e;font:600 10.5px {FONT}}}
  .sec{{fill:#e6edf3;font:700 13px {FONT}}}
  .bl{{fill:#8b949e;font:600 10px {FONT}}}
  .bar{{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:up .8s cubic-bezier(.2,.8,.2,1) forwards}}
  .hi{{fill:{ACC}}} .lo{{fill:#1d6f80}}
  .rise{{opacity:0;animation:rise .6s ease-out forwards}}
  @keyframes up{{to{{transform:scaleY(1)}}}}
  @keyframes rise{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
</style>
<rect class="bg" x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14"/>
<text class="t" x="24" y="38">Coding Rhythm</text>
<text class="s" x="24" y="56">Activity patterns over the last 12 months (relative, not totals)</text>
{t}
<g class="rise" style="animation-delay:.7s"><rect x="24" y="142" width="370" height="162" rx="10" class="tile"/>
<text x="40" y="164" class="sec">By weekday</text></g>
<g class="rise" style="animation-delay:.8s"><rect x="406" y="142" width="370" height="162" rx="10" class="tile"/>
<text x="422" y="164" class="sec">By month</text></g>
{wbars}
{mbars}
</svg>'''

if __name__ == "__main__":
    days = demo_days() if "--demo" in sys.argv else fetch_days()
    os.makedirs(OUT_DIR, exist_ok=True)
    open(os.path.join(OUT_DIR, "now.svg"), "w", encoding="utf-8").write(now_svg())
    open(os.path.join(OUT_DIR, "rhythm.svg"), "w", encoding="utf-8").write(rhythm_svg(days))
    print(f"Wrote now.svg and rhythm.svg to {OUT_DIR}")
