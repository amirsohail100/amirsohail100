#!/usr/bin/env python3
"""Generates an animated skills grid (SVG) with brand-coloured logos.
Logos are fetched from the simple-icons CDN while the GitHub Action runs; if a logo
can't be fetched, a coloured monogram is drawn instead, so the SVG always builds.
Logo order: Simple Icons CDN, then assets/icons/<slug>.svg (your own icons), then a monogram.
Standard library only. Set NO_CDN=1 to test offline."""
import os, re, urllib.request
from html import escape

OUT = os.environ.get("OUT_FILE", "dist/skills.svg")
LOCAL_DIR = os.environ.get("LOCAL_ICONS", "assets/icons")
CDNS = ["https://cdn.jsdelivr.net/npm/simple-icons@13/icons/{}.svg", "https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/{}.svg"]
COLS = 10

# (simple-icons slug, label, brand colour, optional fallback text if the logo can't load)
SKILLS = [
    ("python", "Python", "3776AB"), ("c", "C", "A8B9CC"), ("cplusplus", "C++", "00599C", "C++"),
    ("csharp", "C#", "512BD4"), ("javascript", "JavaScript", "F7DF1E", "JS"), ("html5", "HTML5", "E34F26", "HTML"),
    ("css3", "CSS3", "1572B6", "CSS"), ("nodedotjs", "Node.js", "5FA04E", "JS"), ("powershell", "PowerShell", "5391FE", "PS"),
    ("dotnet", ".NET", "512BD4", ".NET"),
    ("fastapi", "FastAPI", "009688", "API"), ("flask", "Flask", "FFFFFF", "Fl"), ("streamlit", "Streamlit", "FF4B4B", "St"),
    ("tensorflow", "TensorFlow", "FF6F00", "TF"), ("pytorch", "PyTorch", "EE4C2C", "PT"), ("keras", "Keras", "D00000", "K"),
    ("scikitlearn", "scikit-learn", "F7931E", "sk"), ("numpy", "NumPy", "4DABCF", "Np"), ("pandas", "Pandas", "8F7BE8", "Pd"),
    ("plotly", "Plotly", "7A8CC2", "Pl"),
    ("mlflow", "MLflow", "0194E2", "ML"), ("shap", "SHAP", "FF0051", "SHAP"), ("huggingface", "Hugging Face", "FFD21E", "HF"),
    ("langchain", "LangChain", "1C9C8C", "LC"), ("langgraph", "LangGraph", "1C9C8C", "LG"),
    ("opencv", "OpenCV", "8C7BFF", "CV"), ("dvc", "DVC", "945DD6", "DVC"), ("pydantic", "Pydantic", "E92063", "Pyd"),
    ("jupyter", "Jupyter", "F37626", "Jp"), ("ollama", "Ollama", "FFFFFF", "Ol"), ("powerbi", "Power BI", "F2C811", "BI"),
    ("microsoftexcel", "Excel", "217346", "XL"),
    ("docker", "Docker", "2496ED", "Dk"), ("kubernetes", "Kubernetes", "326CE5", "K8s"), ("amazonaws", "AWS", "FF9900", "AWS"),
    ("googlecloud", "Google Cloud", "4285F4", "GCP"),
    ("githubactions", "GitHub Actions", "2088FF", "GA"), ("gitlab", "GitLab", "FC6D26", "GL"), ("cicd", "CI/CD", "58A6FF", "CI/CD"),
    ("git", "Git", "F05032", "Git"), ("github", "GitHub", "C9D1D9", "GH"), ("gitee", "Gitee", "C71D23", "Ge"),
    ("mysql", "MySQL", "4479A1", "SQL"), ("mongodb", "MongoDB", "47A248", "Mg"),
    ("postgresql", "PostgreSQL", "4169E1", "PG"), ("firebase", "Firebase", "FFCA28", "FB"), ("faiss", "FAISS", "0467DF", "FAISS"),
    ("vectordb", "Vector DBs", "8B5CF6", "VDB"),
    ("unity", "Unity", "FFFFFF", "U"), ("godotengine", "Godot", "478CBF", "Gd"),
]

def lighten(hexcol):
    r, g, b = (int(hexcol[i:i + 2], 16) for i in (0, 2, 4))
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    if lum < 0.35:
        r, g, b = (int(c + (255 - c) * 0.55) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"

def load_icon(slug, color):
    """Return an <svg> string for the logo (coloured), or None."""
    if not os.environ.get("NO_CDN"):
        for url in CDNS:
            try:
                req = urllib.request.Request(url.format(slug), headers={"User-Agent": "skills-grid"})
                with urllib.request.urlopen(req, timeout=15) as r:
                    svg = r.read().decode("utf-8")
                m = re.search(r'<path[^>]*\sd="([^"]+)"', svg)
                if m:
                    return f'<svg viewBox="0 0 24 24"><path d="{m.group(1)}" fill="{color}"/></svg>'
            except Exception:
                pass
    try:
        with open(os.path.join(LOCAL_DIR, f"{slug}.svg"), encoding="utf-8") as f:
            svg = f.read()
        svg = re.sub(r"<title>.*?</title>", "", svg, flags=re.S).replace("currentColor", color)
        root = re.match(r"<svg[^>]*>", svg.strip()).group(0)
        clean = re.sub(r'\s(xmlns|width|height)="[^"]*"', "", root)
        return svg.strip().replace(root, clean, 1)
    except Exception:
        return None

def build():
    cw, ch = 84, 92
    rows = -(-len(SKILLS) // COLS)
    W, H = COLS * cw + 2, rows * ch + 2
    cells, found = [], 0
    for i, (slug, label, col, *rest) in enumerate(SKILLS):
        x, y = 1 + (i % COLS) * cw, 1 + (i // COLS) * ch
        color = lighten(col)
        ic = load_icon(slug, color)
        if ic:
            found += 1
            glyph = ic.replace("<svg", f'<svg x="{cw/2-17:.1f}" y="16" width="34" height="34"', 1)
        else:
            mono_raw = rest[0] if rest else label[:2]
            mono = escape(mono_raw)
            fs = 13 if len(mono_raw) <= 2 else 11 if len(mono_raw) == 3 else 8.5
            glyph = (f'<rect x="{cw/2-17:.1f}" y="16" width="34" height="34" rx="8" fill="{color}" fill-opacity=".16" '
                     f'stroke="{color}" stroke-opacity=".6"/>'
                     f'<text x="{cw/2}" y="38.5" text-anchor="middle" font-size="{fs}" font-weight="700" fill="{color}" '
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
