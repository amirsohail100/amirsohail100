#!/usr/bin/env python3
"""Generates an animated skills grid (SVG) with brand-coloured logos.
Logos are fetched from the simple-icons CDN while the GitHub Action runs; if a logo
can't be fetched, a coloured monogram is drawn instead, so the SVG always builds.
Standard library only. Set ICON_DIR to read logos from a local folder (for testing)."""
import os, re, urllib.request
from html import escape

OUT = os.environ.get("OUT_FILE", "dist/skills.svg")
ICON_DIR = os.environ.get("ICON_DIR")
CDN = "https://cdn.jsdelivr.net/npm/simple-icons@13/icons/{}.svg"
COLS = 10

# (simple-icons slug, label, brand colour)
SKILLS = [
    ("python", "Python", "3776AB"), ("c", "C", "A8B9CC"), ("cplusplus", "C++", "00599C"),
    ("csharp", "C#", "512BD4"), ("javascript", "JavaScript", "F7DF1E"), ("html5", "HTML5", "E34F26"),
    ("css3", "CSS3", "1572B6"), ("nodedotjs", "Node.js", "5FA04E"), ("fastapi", "FastAPI", "009688"),
    ("flask", "Flask", "FFFFFF"),
    ("tensorflow", "TensorFlow", "FF6F00"), ("pytorch", "PyTorch", "EE4C2C"), ("keras", "Keras", "D00000"),
    ("scikitlearn", "scikit-learn", "F7931E"), ("numpy", "NumPy", "4DABCF"), ("pandas", "Pandas", "8F7BE8"),
    ("plotly", "Plotly", "7A8CC2"), ("mlflow", "MLflow", "0194E2"), ("huggingface", "Hugging Face", "FFD21E"),
    ("langchain", "LangChain", "1C9C8C"),
    ("streamlit", "Streamlit", "FF4B4B"), ("docker", "Docker", "2496ED"), ("kubernetes", "Kubernetes", "326CE5"),
    ("amazonaws", "AWS", "FF9900"), ("googlecloud", "Google Cloud", "4285F4"), ("mongodb", "MongoDB", "47A248"),
    ("mysql", "MySQL", "4479A1"), ("git", "Git", "F05032"), ("github", "GitHub", "C9D1D9"),
    ("powerbi", "Power BI", "F2C811"),
]

def lighten(hexcol):
    r, g, b = (int(hexcol[i:i + 2], 16) for i in (0, 2, 4))
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    if lum < 0.35:
        r, g, b = (int(c + (255 - c) * 0.55) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"

def load_path(slug):
    """Return the SVG path 'd' of a simple-icons logo, or None."""
    try:
        if ICON_DIR:
            with open(os.path.join(ICON_DIR, f"{slug}.svg"), encoding="utf-8") as f:
                svg = f.read()
        else:
            req = urllib.request.Request(CDN.format(slug), headers={"User-Agent": "skills-grid"})
            with urllib.request.urlopen(req, timeout=15) as r:
                svg = r.read().decode("utf-8")
        m = re.search(r'<path[^>]*\sd="([^"]+)"', svg)
        return m.group(1) if m else None
    except Exception:
        return None

def build():
    cw, ch = 84, 92
    rows = -(-len(SKILLS) // COLS)
    W, H = COLS * cw + 2, rows * ch + 2
    cells, found = [], 0
    for i, (slug, label, col) in enumerate(SKILLS):
        x, y = 1 + (i % COLS) * cw, 1 + (i // COLS) * ch
        color = lighten(col)
        d = load_path(slug)
        if d:
            found += 1
            glyph = f'<g transform="translate({cw/2-17:.1f} 16) scale(1.4167)"><path d="{d}" fill="{color}"/></g>'
        else:
            mono = escape(label[:2] if len(label) > 2 and not label.startswith(("C", "J")) else label[:1] if label in ("C",) else label[:2])
            glyph = (f'<rect x="{cw/2-17:.1f}" y="16" width="34" height="34" rx="8" fill="{color}" fill-opacity=".16" '
                     f'stroke="{color}" stroke-opacity=".6"/>'
                     f'<text x="{cw/2}" y="38.5" text-anchor="middle" font-size="13" font-weight="700" fill="{color}" '
                     f'font-family="Segoe UI,Arial,sans-serif">{mono}</text>')
        delay = 0.05 * i
        cells.append(
            f'<g transform="translate({x} {y})">'
            f'<rect width="{cw}" height="{ch}" class="cell"/>'
            f'<g class="pop" style="animation-delay:{delay:.2f}s"><g class="float" style="animation-delay:{(i*0.37)%3:.2f}s">'
            f'{glyph}</g>'
            f'<text x="{cw/2}" y="76" class="lbl" text-anchor="middle">{escape(label)}</text></g></g>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Skills">
<style>
  .cell{{fill:#0d1117;stroke:#21262d;stroke-width:1}}
  .lbl{{fill:#8b949e;font:600 10px 'Segoe UI',Arial,sans-serif}}
  .pop{{opacity:0;animation:pop .6s ease-out forwards}}
  .float{{animation:float 3.2s ease-in-out infinite}}
  @keyframes pop{{from{{opacity:0;transform:translateY(10px) scale(.85)}}to{{opacity:1;transform:none}}}}
  @keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-4px)}}}}
</style>
{"".join(cells)}
</svg>'''
    return svg, found

if __name__ == "__main__":
    svg, found = build()
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(svg)
    print(f"Wrote {OUT}: {len(SKILLS)} skills, {found} logos loaded, {len(SKILLS)-found} monogram fallbacks")
