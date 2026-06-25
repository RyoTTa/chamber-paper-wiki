#!/usr/bin/env python3
"""
paper-wiki 의 마크다운 파일을 읽어 HTML 뷰어 생성
- 왼쪽 사이드바: 카테고리별 페이지 목록
- 오른쪽 본문: 렌더링된 마크다운
- 내부 링크: [[paper-wiki/...]] 형식을 JS 네비게이션으로 변환
- 검색/필터, 그래프 뷰 지원
"""
import os
import re
import sys
import json
import markdown

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI_DIR = os.path.join(WORKSPACE, "paper-wiki")
OUTPUT = os.path.join(WIKI_DIR, "wiki-viewer.html")

# Cross-reference pattern: [[paper-wiki/path.md|Label]]
XREF_PATTERN = re.compile(r'\[\[(paper-wiki/[^\]|]+\.md)\|([^\]]+)\]\]')
# Also handle bare [[paper-wiki/path.md]]
XREF_BARE = re.compile(r'\[\[(paper-wiki/[^\]|]+\.md)\]\]')
# Frontmatter (handle BOM)
FRONTMATTER_RE = re.compile(r'^\ufeff?---\s*\n(.*?)\n---\s*\n', re.DOTALL)

CATEGORY_ORDER = ["Overview", "Concepts", "Papers", "Entities", "Index / Log"]

IGNORE_FILES = {"generate_wiki_html.py", "generate_paper_pages.py"}


def parse_frontmatter(text):
    m = FRONTMATTER_RE.match(text)
    meta = {}
    if m:
        for line in m.group(1).strip().split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip()] = v.strip()
    return meta


def strip_frontmatter(text):
    return FRONTMATTER_RE.sub('', text, count=1)


def classify_page(rel_path):
    if rel_path == "overview.md":
        return "Overview"
    if rel_path.startswith("concepts/"):
        return "Concepts"
    if rel_path.startswith("papers/"):
        return "Papers"
    if rel_path.startswith("entities/"):
        return "Entities"
    if rel_path in ("index.md", "log.md"):
        return "Index / Log"
    return "Index / Log"


def get_page_title(md_text):
    for line in md_text.split('\n'):
        if line.startswith('# '):
            return line[2:].strip()
    return None


def load_pages():
    pages = []
    for root, dirs, files in os.walk(WIKI_DIR):
        for fname in sorted(files):
            if fname.endswith('.md') and fname not in IGNORE_FILES:
                full = os.path.join(root, fname)
                rel = os.path.relpath(full, WIKI_DIR).replace('\\', '/')
                with open(full, 'r', encoding='utf-8') as f:
                    raw = f.read()
                meta = parse_frontmatter(raw)
                body = strip_frontmatter(raw)
                title = get_page_title(body) or fname.replace('.md', '')
                category = classify_page(rel)
                pages.append({
                    'rel': rel,
                    'title': title,
                    'category': category,
                    'tags': meta.get('tags', ''),
                    'source_count': meta.get('source_count', ''),
                    'raw': raw,
                    'body': body,
                })
    return pages


def process_xrefs(html_body, pages_by_rel):
    def replace_xref(m):
        path = m.group(1)
        label = m.group(2)
        key = path.replace('paper-wiki/', '', 1)
        if key in pages_by_rel:
            return f'<a href="#" class="xref" onclick="navigate(\'{key}\');return false;">{label}</a>'
        return f'<span class="xref broken">{label}</span>'

    def replace_bare(m):
        path = m.group(1)
        key = path.replace('paper-wiki/', '', 1)
        if key in pages_by_rel:
            title = pages_by_rel[key].get('title', key)
            return f'<a href="#" class="xref" onclick="navigate(\'{key}\');return false;">{title}</a>'
        return m.group(0)

    html_body = XREF_PATTERN.sub(replace_xref, html_body)
    html_body = XREF_BARE.sub(replace_bare, html_body)
    return html_body


def build_xref_graph(pages):
    graph = {}
    for p in pages:
        src = p['rel']
        targets = set()
        for m in XREF_PATTERN.finditer(p['raw']):
            t = m.group(1).replace('paper-wiki/', '', 1)
            targets.add(t)
        for m in XREF_BARE.finditer(p['raw']):
            t = m.group(1).replace('paper-wiki/', '', 1)
            targets.add(t)
        graph[src] = sorted(targets)
    return graph


def render_markdown(md_text):
    return markdown.markdown(
        md_text,
        extensions=['fenced_code', 'tables', 'sane_lists']
    )


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')


def generate():
    pages = load_pages()
    pages.sort(key=lambda p: (CATEGORY_ORDER.index(p['category']), p['title']))

    pages_by_rel = {p['rel']: p for p in pages}
    graph = build_xref_graph(pages)

    # Render HTML for each page
    page_data = []
    for p in pages:
        html_body = render_markdown(p['body'])
        html_body = process_xrefs(html_body, pages_by_rel)
        page_data.append({
            'rel': p['rel'],
            'title': p['title'],
            'category': p['category'],
            'tags': p['tags'],
            'html': html_body,
        })

    pages_json = json.dumps(page_data, ensure_ascii=False)
    graph_json = json.dumps(graph, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Computer Architecture Wiki</title>
<style>
:root {{
  --bg: #0f1419;
  --bg-card: #1a1f2e;
  --bg-hover: #252b3d;
  --border: #2d3548;
  --text: #e1e4eb;
  --text-dim: #8892a4;
  --accent: #58a6ff;
  --accent2: #3fb950;
  --accent3: #d29922;
  --accent4: #f97583;
  --code-bg: #161b26;
  --header-bg: #0d1117;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ height: 100%; overflow: hidden; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
       background: var(--bg); color: var(--text); display: flex; flex-direction: column; }}
.header {{ background: var(--header-bg); border-bottom: 1px solid var(--border); padding: 16px 32px; flex-shrink: 0;
           display: flex; align-items: center; justify-content: space-between; }}
.header h1 {{ font-size: 20px; font-weight: 700; letter-spacing: -0.3px; }}
.header h1 span {{ color: var(--accent); }}
.header .stats {{ display: flex; gap: 10px; font-size: 13px; color: var(--text-dim); }}
.header .stats span {{ background: var(--bg-card); padding: 3px 12px; border-radius: 16px; font-weight: 500; border: 1px solid var(--border); }}
.graph-btn {{ background: var(--bg-card); border: 1px solid var(--border);
              color: var(--text-dim); padding: 6px 16px; border-radius: 8px; cursor: pointer; font-size: 13px;
              font-family: inherit; transition: all 0.15s; }}
.graph-btn:hover {{ background: var(--bg-hover); color: var(--text); }}
.graph-btn.active {{ background: var(--accent); border-color: var(--accent); color: #fff; }}
.filters {{ display: flex; gap: 8px; padding: 10px 32px; background: var(--bg-card);
           border-bottom: 1px solid var(--border); flex-wrap: wrap; flex-shrink: 0; }}
.filters input {{ flex: 1; min-width: 180px; padding: 6px 12px; border: 1px solid var(--border);
       border-radius: 6px; font-size: 13px; background: var(--bg); color: var(--text); font-family: inherit; }}
.filters input:focus {{ outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px rgba(88,166,255,0.15); }}
.filters input::placeholder {{ color: var(--text-dim); }}
.main {{ display: flex; flex: 1; overflow: hidden; }}
.sidebar {{ width: 340px; min-width: 340px; overflow-y: auto; background: var(--bg-card);
           border-right: 1px solid var(--border); }}
.sidebar .category-label {{ padding: 10px 18px 4px; font-size: 11px; font-weight: 700;
       color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px; background: var(--bg);
       border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 1; }}
.sidebar .item {{ padding: 10px 18px; border-bottom: 1px solid var(--border); cursor: pointer;
       transition: all 0.12s; font-size: 13px; }}
.sidebar .item:hover {{ background: var(--bg-hover); }}
.sidebar .item.active {{ background: var(--bg-hover); border-left: 4px solid var(--accent); padding-left: 14px; }}
.sidebar .item .title {{ font-weight: 600; color: var(--text); font-size: 13px; line-height: 1.4; }}
.sidebar .item .tags {{ font-size: 11px; color: var(--text-dim); margin-top: 3px; }}
.content {{ flex: 1; overflow-y: auto; padding: 28px 36px; background: var(--bg); display: flex; justify-content: center; }}
.content .placeholder {{ color: var(--text-dim); text-align: center; margin-top: 100px; font-size: 18px; line-height: 1.6; }}
.content .page {{ max-width: 860px; width: 100%; line-height: 1.8; }}
.content .page h1 {{ font-size: 26px; margin-bottom: 12px; color: var(--text); border-bottom: 2px solid var(--border); padding-bottom: 12px; }}
.content .page h2 {{ font-size: 20px; margin: 24px 0 12px; border-bottom: 1px solid var(--border);
       padding-bottom: 6px; color: var(--accent); }}
.content .page h3 {{ font-size: 17px; margin: 18px 0 8px; color: var(--accent2); }}
.content .page h4 {{ font-size: 15px; margin: 14px 0 6px; color: var(--accent3); }}
.content .page p {{ line-height: 1.8; margin: 8px 0; color: var(--text-dim); font-size: 15px; }}
.content .page ul, .content .page ol {{ margin: 8px 0 8px 24px; line-height: 1.7; color: var(--text-dim); }}
.content .page li {{ margin: 4px 0; font-size: 15px; }}
.content .page strong {{ color: var(--text); }}
.content .page table {{ border-collapse: collapse; margin: 12px 0; font-size: 14px; width: 100%; border-radius: 8px; overflow: hidden; }}
.content .page th, .content .page td {{ border: 1px solid var(--border); padding: 8px 12px; text-align: left; }}
.content .page th {{ background: var(--bg-hover); font-weight: 600; color: var(--text); }}
.content .page td {{ color: var(--text-dim); }}
.content .page code {{ background: var(--code-bg); padding: 2px 6px; border-radius: 4px; font-size: 14px; color: var(--accent4); }}
.content .page pre {{ background: var(--code-bg); color: var(--text); padding: 16px; border-radius: 8px;
       border: 1px solid var(--border); overflow-x: auto; font-size: 14px; margin: 12px 0; line-height: 1.5; }}
.content .page pre code {{ background: none; color: inherit; padding: 0; }}
.content .page blockquote {{ border-left: 3px solid var(--accent); padding: 12px 16px; margin: 12px 0;
       background: var(--bg-card); border-radius: 0 4px 4px 0; color: var(--text-dim); font-size: 14px; }}
.content .page hr {{ border: none; border-top: 1px solid var(--border); margin: 20px 0; }}
a.xref {{ color: var(--accent); text-decoration: none; font-weight: 500; border-bottom: 1px dashed rgba(88,166,255,0.4);
       transition: all 0.12s; }}
a.xref:hover {{ border-bottom-style: solid; color: #79c0ff; }}
span.xref.broken {{ color: var(--accent4); text-decoration: line-through; }}
.graph-panel {{ display: none; flex: 1; overflow: hidden; position: relative; }}
.graph-panel.visible {{ display: flex; flex-direction: column; }}
.graph-panel svg {{ flex: 1; width: 100%; background: var(--bg); }}
.graph-panel .graph-legend {{ position: absolute; top: 16px; left: 16px; background: rgba(13,17,23,0.9);
       border-radius: 10px; padding: 14px 18px; z-index: 10; border: 1px solid var(--border); }}
.graph-panel .graph-legend .legend-item {{ display: flex; align-items: center; gap: 8px; margin: 4px 0; font-size: 12px; color: var(--text-dim); }}
.graph-panel .graph-legend .legend-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
.graph-panel .graph-controls {{ position: absolute; bottom: 16px; left: 50%; transform: translateX(-50%);
       background: rgba(13,17,23,0.9); border-radius: 10px; padding: 10px 18px; z-index: 10;
       display: flex; gap: 12px; align-items: center; border: 1px solid var(--border); }}
.graph-panel .graph-controls button {{ background: var(--bg-card); border: 1px solid var(--border); color: var(--text);
       padding: 5px 14px; border-radius: 6px; cursor: pointer; font-size: 12px; font-family: inherit; }}
.graph-panel .graph-controls button:hover {{ background: var(--bg-hover); }}
.graph-panel .graph-controls button.active {{ background: var(--accent); border-color: var(--accent); color: #fff; }}
.graph-panel .graph-info {{ position: absolute; top: 16px; right: 16px; background: rgba(13,17,23,0.9);
       border-radius: 10px; padding: 10px 16px; z-index: 10; border: 1px solid var(--border);
       font-size: 12px; color: var(--text-dim); max-width: 280px; }}
.graph-panel .graph-info strong {{ color: var(--accent4); }}
.node-label {{ font-size: 11px; fill: var(--text); pointer-events: none; text-anchor: middle; font-weight: 500; text-shadow: 0 1px 3px rgba(0,0,0,0.8); }}
.edge {{ stroke: #475569; stroke-width: 0.5; stroke-opacity: 0.25; }}
.back-link {{ display: inline-block; margin-bottom: 16px; color: var(--accent); text-decoration: none;
       font-size: 13px; cursor: pointer; }}
.back-link:hover {{ text-decoration: underline; }}
@media (max-width: 768px) {{
  body {{ overflow: auto; }}
  .main {{ flex-direction: column; }}
  .sidebar {{ width: 100%; min-width: auto; max-height: 40vh; }}
}}
</style>
</head>
<body>
<div class="header">
  <div>
    <h1>Computer Architecture Wiki</h1>
    <div class="stats">
      <span>Pages: {len(pages)}</span>
      <span>Concepts: {sum(1 for p in pages if p['category'] == 'Concepts')}</span>
      <span>Papers: {sum(1 for p in pages if p['category'] == 'Papers')}</span>
    </div>
  </div>
  <button class="graph-btn" id="graphBtn" onclick="toggleGraph()">Graph</button>
</div>
<div class="filters">
  <input id="filterSearch" placeholder="Search pages..." oninput="render()">
</div>
<div class="main" id="mainView">
  <div class="sidebar" id="sidebar"></div>
  <div class="content" id="content">
    <div class="placeholder">Select a page from the left</div>
  </div>
</div>
<div class="graph-panel" id="graphPanel">
  <svg id="graphSvg"></svg>
  <div class="graph-legend">
    <div class="legend-item"><div class="legend-dot" style="background:#60a5fa"></div>Overview</div>
    <div class="legend-item"><div class="legend-dot" style="background:#f472b6"></div>Concepts</div>
    <div class="legend-item"><div class="legend-dot" style="background:#a78bfa"></div>Papers</div>
    <div class="legend-item"><div class="legend-dot" style="background:#34d399"></div>Entities</div>
    <div class="legend-item"><div class="legend-dot" style="background:#fbbf24"></div>Index / Log</div>
  </div>
  <div class="graph-info" id="graphInfo">Loading...</div>
  <div class="graph-controls">
    <button onclick="resetGraph()">Reset</button>
    <button onclick="togglePhysics()" id="physicsBtn" class="active">Physics</button>
    <button onclick="togglePapers()" id="papersBtn">Show Papers</button>
    <select id="yearFilter" onchange="filterByYear()" style="background:#1e293b;border:1px solid #334155;color:#e2e8f0;padding:5px 8px;border-radius:6px;font-size:12px;font-family:inherit;">
      <option value="all">All Years</option>
      <option value="2026">2026</option>
      <option value="2025">2025</option>
      <option value="2024">2024</option>
      <option value="2023">2023</option>
      <option value="2022">2022</option>
      <option value="2021">2021</option>
      <option value="2020">2020</option>
      <option value="2019">2019</option>
    </select>
    <button onclick="zoomIn()">Zoom In</button>
    <button onclick="zoomOut()">Zoom Out</button>
    <span style="color:#94a3b8;font-size:11px;margin-left:8px;">Double-click concept to highlight</span>
  </div>
</div>
<script>
const PAGES = {pages_json};
const GRAPH = {graph_json};

let currentIdx = null;
let graphMode = false;
let showPapers = false;
let selectedYear = 'all';

function navigate(rel) {{
  const idx = PAGES.findIndex(p => p.rel === rel);
  if (idx >= 0) {{
    graphMode = false;
    document.getElementById('mainView').style.display = 'flex';
    document.getElementById('graphPanel').classList.remove('visible');
    document.getElementById('graphBtn').classList.remove('active');
    show(idx);
  }}
}}

function togglePapers() {{
  showPapers = !showPapers;
  const btn = document.getElementById('papersBtn');
  btn.textContent = showPapers ? 'Hide Papers' : 'Show Papers';
  btn.classList.toggle('active', showPapers);
  applyVisibility();
  startSim();
}}

function filterByYear() {{
  selectedYear = document.getElementById('yearFilter').value;
  applyVisibility();
  startSim();
}}

function applyVisibility() {{
  graphNodes.forEach(n => {{
    if (n.category === 'Papers') {{
      const page = PAGES.find(p => p.rel === n.rel);
      if (page) {{
        const yearMatch = selectedYear === 'all' || page.tags.includes(selectedYear);
        n.hidden = !showPapers || !yearMatch;
      }}
    }}
  }});
  graphEdges.forEach(e => {{
    e.hidden = graphNodes[e.source].hidden || graphNodes[e.target].hidden;
  }});
}}

function startSim() {{
  if (graphAnimFrame) cancelAnimationFrame(graphAnimFrame);
  graphPaused = false;
  document.getElementById('physicsBtn').classList.add('active');
  document.getElementById('physicsBtn').textContent = 'Physics';
  const svg = document.getElementById('graphSvg');
  const rect = svg.getBoundingClientRect();
  const W = rect.width || 800, H = rect.height || 600;
  const N = graphNodes.length;
  const nodeR = [16, 11, 3, 8, 6];
  const nodeRadius = graphNodes.map(n => {{
    const catIdx = ['Overview','Concepts','Papers','Entities','Index / Log'].indexOf(n.category);
    return nodeR[catIdx] || 4;
  }});
  const degree = new Array(N).fill(0);
  graphEdges.forEach(e => {{ if (!e.hidden) {{ degree[e.source]++; degree[e.target]++; }} }});
  const maxDeg = Math.max(...degree, 1);
  
  let alpha = 0.6;
  const minAlpha = 0.05;
  const margin = 60;
  function tick() {{
    if (graphPaused) return;
    if (alpha > minAlpha) alpha *= 0.998;
    
    graphNodes.forEach(n => {{
      if (n.category === 'Concepts') conceptPositions[n.rel] = {{ x: n.x, y: n.y }};
    }});
    
    for (let i = 0; i < N; i++) {{
      const ni = graphNodes[i];
      if (ni.hidden) continue;
      const isConceptNode = ni.category === 'Concepts';
      
      // Center gravity (very weak, none for concepts)
      let fx = isConceptNode ? 0 : (W/2 - ni.x) * 0.0005;
      let fy = isConceptNode ? 0 : (H/2 - ni.y) * 0.0005;
      
      // Soft boundary push-back (stronger for concepts)
      const boundaryForce = isConceptNode ? 0.03 : 0.01;
      if (ni.x < margin) fx += (margin - ni.x) * boundaryForce;
      if (ni.x > W - margin) fx -= (ni.x - (W - margin)) * boundaryForce;
      if (ni.y < margin) fy += (margin - ni.y) * boundaryForce;
      if (ni.y > H - margin) fy -= (ni.y - (H - margin)) * boundaryForce;
      
      // Clustering: pull papers toward their concept
      if (ni.category === 'Papers') {{
        for (let ei = 0; ei < graphEdges.length; ei++) {{
          const e = graphEdges[ei];
          if (e.hidden) continue;
          let conceptIdx = null;
          if (e.source === i && graphNodes[e.target].category === 'Concepts') conceptIdx = e.target;
          if (e.target === i && graphNodes[e.source].category === 'Concepts') conceptIdx = e.source;
          if (conceptIdx !== null) {{
            const c = graphNodes[conceptIdx];
            fx += (c.x - ni.x) * 0.004 * alpha;
            fy += (c.y - ni.y) * 0.004 * alpha;
          }}
        }}
      }}
      
      // Repulsion (with min distance)
      const minDist = 80;
      for (let j = 0; j < N; j++) {{
        if (i === j || graphNodes[j].hidden) continue;
        const nj = graphNodes[j];
        let dx = ni.x - nj.x, dy = ni.y - nj.y;
        let dist = Math.sqrt(dx*dx + dy*dy) || 1;
        const bothConcepts = isConceptNode && nj.category === 'Concepts';
        const minD = bothConcepts ? 220 : minDist;
        if (dist < minD) dist = minD;
        const strength = bothConcepts ? 12000 : 3000;
        let force = strength * alpha / (dist * dist);
        fx += (dx / dist) * force;
        fy += (dy / dist) * force;
      }}
      ni.vx = (ni.vx + fx) * 0.92;
      ni.vy = (ni.vy + fy) * 0.92;
    }}
    
    // Edge attraction
    graphEdges.forEach(e => {{
      if (e.hidden) return;
      const s = graphNodes[e.source], t = graphNodes[e.target];
      let dx = t.x - s.x, dy = t.y - s.y;
      let dist = Math.sqrt(dx*dx + dy*dy) || 1;
      let force = (dist - 100) * 0.008 * alpha;
      s.vx += (dx / dist) * force; s.vy += (dy / dist) * force;
      t.vx -= (dx / dist) * force; t.vy -= (dy / dist) * force;
    }});
    
    // Apply velocity
    for (let i = 0; i < N; i++) {{
      const n = graphNodes[i];
      if (n.hidden) continue;
      if (n.fx !== null) {{ n.x = n.fx; n.y = n.fy; n.vx = 0; n.vy = 0; continue; }}
      n.x += n.vx;
      n.y += n.vy;
    }}
    
    renderSVG(svg, nodeRadius, degree, maxDeg);
    graphAnimFrame = requestAnimationFrame(tick);
  }}
  tick();
}}

function toggleGraph() {{
  graphMode = !graphMode;
  const btn = document.getElementById('graphBtn');
  const main = document.getElementById('mainView');
  const panel = document.getElementById('graphPanel');
  if (graphMode) {{
    btn.classList.add('active');
    main.style.display = 'none';
    panel.classList.add('visible');
    renderGraph();
  }} else {{
    btn.classList.remove('active');
    main.style.display = 'flex';
    panel.classList.remove('visible');
    if (graphAnimFrame) cancelAnimationFrame(graphAnimFrame);
  }}
}}

const GRAPH_COLORS = {{ 'Overview': '#60a5fa', 'Concepts': '#f472b6', 'Papers': '#a78bfa', 'Entities': '#34d399', 'Index / Log': '#fbbf24' }};
let graphNodes = [], graphEdges = [], graphSim = null, graphAnimFrame = null, graphPaused = false;
let highlightedConcept = null;
let conceptPositions = {{}};
let graphSvg = null;

function renderGraph() {{
  graphSvg = document.getElementById('graphSvg');
  const svg = graphSvg;
  const rect = svg.getBoundingClientRect();
  const W = rect.width || 800, H = rect.height || 600;
  svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
  const cx = W / 2, cy = H / 2;

  highlightedConcept = null;
  conceptPositions = {{}};

  // Separate concepts and papers for initial layout
  const concepts = PAGES.filter(p => p.category === 'Concepts');
  const others = PAGES.filter(p => p.category !== 'Concepts');
  const conceptCount = concepts.length;
  const conceptRadius = Math.min(W, H) * 0.3;
  
  graphNodes = [];
  let nodeId = 0;
  
  // Place concepts in a circle
  concepts.forEach((p, i) => {{
    const angle = (2 * Math.PI * i) / conceptCount;
    graphNodes.push({{
      id: nodeId++, rel: p.rel, title: p.title, category: p.category,
      x: cx + Math.cos(angle) * conceptRadius,
      y: cy + Math.sin(angle) * conceptRadius,
      vx: 0, vy: 0, fx: null, fy: null, hidden: false
    }});
  }});
  
  // Place others randomly
  others.forEach((p, i) => {{
    graphNodes.push({{
      id: nodeId++, rel: p.rel, title: p.title, category: p.category,
      x: cx + (Math.random() - 0.5) * Math.min(W, H) * 0.8,
      y: cy + (Math.random() - 0.5) * Math.min(W, H) * 0.8,
      vx: 0, vy: 0, fx: null, fy: null, hidden: false
    }});
  }});

  const nodeIdx = {{}};
  graphNodes.forEach((n, i) => {{ nodeIdx[n.rel] = i; }});

  graphEdges = [];
  Object.entries(GRAPH).forEach(([src, targets]) => {{
    targets.forEach(t => {{
      if (nodeIdx[src] !== undefined && nodeIdx[t] !== undefined) {{
        graphEdges.push({{ source: nodeIdx[src], target: nodeIdx[t], hidden: false }});
      }}
    }});
  }});

  document.getElementById('graphInfo').textContent = graphNodes.length + ' nodes, ' + graphEdges.length + ' edges';

  showPapers = false;
  selectedYear = 'all';
  document.getElementById('papersBtn').textContent = 'Show Papers';
  document.getElementById('papersBtn').classList.remove('active');
  document.getElementById('yearFilter').value = 'all';
  applyVisibility();
  startSim();
  initGraphEvents();
}}

function renderSVG(svg, nodeRadius, degree, maxDeg) {{
  window._nodeRadius = nodeRadius;
  window._degree = degree;
  window._maxDeg = maxDeg;

  // Determine connected papers if concept is highlighted
  let connectedPapers = new Set();
  let connectedEdges = new Set();
  if (highlightedConcept !== null) {{
    graphEdges.forEach((e, ei) => {{
      const src = graphNodes[e.source];
      const tgt = graphNodes[e.target];
      if (e.source === highlightedConcept && tgt.category === 'Papers') {{
        connectedPapers.add(e.target);
        connectedEdges.add(ei);
      }}
      if (e.target === highlightedConcept && src.category === 'Papers') {{
        connectedPapers.add(e.source);
        connectedEdges.add(ei);
      }}
    }});
  }}

  let html = '<defs><filter id="glow"><feGaussianBlur stdDeviation="3" result="blur"/>'
    + '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>';

  graphEdges.forEach((e, ei) => {{
    if (e.hidden) return;
    const s = graphNodes[e.source], t = graphNodes[e.target];
    const dimmed = highlightedConcept !== null && !connectedEdges.has(ei);
    const opacity = dimmed ? 0.1 : 0.6;
    const color = dimmed ? '#1e293b' : '#334155';
    html += '<line class="edge" x1="' + s.x + '" y1="' + s.y + '" x2="' + t.x + '" y2="' + t.y 
      + '" stroke="' + color + '" stroke-opacity="' + opacity + '"/>';
  }});

  graphNodes.forEach((n, i) => {{
    if (n.hidden) return;
    const r = nodeRadius[i];
    const color = GRAPH_COLORS[n.category] || '#94a3b8';
    const hover = degree[i] > maxDeg * 0.5 ? ' filter="url(#glow)"' : '';
    
    let opacity = 0.9;
    let stroke = '';
    if (highlightedConcept !== null) {{
      if (i === highlightedConcept) {{
        opacity = 1;
        stroke = ' stroke="#fff" stroke-width="3"';
      }} else if (n.category === 'Papers' && connectedPapers.has(i)) {{
        opacity = 1;
        stroke = ' stroke="#fff" stroke-width="1"';
      }} else {{
        opacity = 0.15;
      }}
    }}
    
    const cursor = n.category === 'Concepts' ? 'pointer' : 'grab';
    const isConcept = n.category === 'Concepts';
    const isHighlighted = highlightedConcept !== null && (i === highlightedConcept || connectedPapers.has(i));
    const showLabel = isConcept || isHighlighted;
    
    html += '<circle cx="' + n.x + '" cy="' + n.y + '" r="' + r + '" fill="' + color + '" opacity="' + opacity + '"'
      + hover + stroke + ' style="cursor:' + cursor + '" data-idx="' + i + '"/>';
    
    if (showLabel) {{
      const fontSize = isConcept ? '13px' : '10px';
      const fontWeight = isConcept ? 'bold' : 'normal';
      html += '<text class="node-label" x="' + n.x + '" y="' + (n.y - r - 6) + '" opacity="' + Math.max(opacity, 0.5) 
        + '" style="font-size:' + fontSize + ';font-weight:' + fontWeight + '">'
        + esc(n.title.length > 25 ? n.title.slice(0, 22) + '...' : n.title) + '</text>';
    }}
  }});

  svg.innerHTML = html;
  
  // Update info display
  const infoEl = document.getElementById('graphInfo');
  if (highlightedConcept !== null) {{
    const conceptName = graphNodes[highlightedConcept].title;
    infoEl.innerHTML = '<strong>' + esc(conceptName) + '</strong> — ' + connectedPapers.size + ' papers | Click empty to clear';
  }} else {{
    infoEl.textContent = graphNodes.length + ' nodes, ' + graphEdges.length + ' edges';
  }}
}}

let graphDrag = null;  // {{ idx, offsetX, offsetY }}
let graphPan = null;   // {{ startX, startY, vbX, vbY }}
let graphZoom = 1;
let graphViewBox = null; // {{ x, y, w, h }}
let graphInitialVB = null;

let graphEventsInitialized = false;
function initGraphEvents() {{
  if (graphEventsInitialized) return;
  graphEventsInitialized = true;
  const svg = document.getElementById('graphSvg');

  svg.addEventListener('mousedown', function(e) {{
    const pt = svgPoint(e);
    const hit = findNodeAt(pt.x, pt.y);
    if (hit !== null) {{
      e.preventDefault();
      const n = graphNodes[hit];
      
      // Double-click on concept: toggle highlight
      if (e.detail === 2 && n.category === 'Concepts') {{
        highlightedConcept = (highlightedConcept === hit) ? null : hit;
        renderSVG(graphSvg, window._nodeRadius, window._degree, window._maxDeg);
        return;
      }}
      
      n.fx = n.x; n.fy = n.y;
      graphDrag = {{ idx: hit, offsetX: pt.x - n.x, offsetY: pt.y - n.y }};
    }} else {{
      if (highlightedConcept !== null) {{
        highlightedConcept = null;
        renderSVG(graphSvg, window._nodeRadius, window._degree, window._maxDeg);
      }}
      e.preventDefault();
      const vb = getViewBox();
      graphPan = {{ startX: e.clientX, startY: e.clientY, vbX: vb.x, vbY: vb.y }};
    }}
  }});

  svg.addEventListener('mousemove', function(e) {{
    if (graphDrag) {{
      const pt = svgPoint(e);
      const n = graphNodes[graphDrag.idx];
      n.x = pt.x - graphDrag.offsetX;
      n.y = pt.y - graphDrag.offsetY;
      n.fx = n.x; n.fy = n.y;
      n.vx = 0; n.vy = 0;
      if (graphPaused) renderSVG(graphSvg, window._nodeRadius, window._degree, window._maxDeg);
    }} else if (graphPan) {{
      const dx = (e.clientX - graphPan.startX) / graphZoom;
      const dy = (e.clientY - graphPan.startY) / graphZoom;
      graphViewBox = {{ x: graphPan.vbX - dx, y: graphPan.vbY - dy, w: graphViewBox.w, h: graphViewBox.h }};
      applyViewBox();
    }}
  }});

  svg.addEventListener('mouseup', function(e) {{
    if (graphDrag) {{
      const n = graphNodes[graphDrag.idx];
      n.fx = null; n.fy = null;
      graphDrag = null;
    }}
    graphPan = null;
  }});

  svg.addEventListener('mouseleave', function() {{
    if (graphDrag) {{
      const n = graphNodes[graphDrag.idx];
      n.fx = null; n.fy = null;
      graphDrag = null;
    }}
    graphPan = null;
  }});

  svg.addEventListener('wheel', function(e) {{
    e.preventDefault();
    const factor = e.deltaY > 0 ? 1.1 : 0.9;
    const vb = getViewBox();
    const pt = svgPoint(e);
    const nw = vb.w * factor, nh = vb.h * factor;
    const nx = pt.x - (pt.x - vb.x) * factor;
    const ny = pt.y - (pt.y - vb.y) * factor;
    graphViewBox = {{ x: nx, y: ny, w: nw, h: nh }};
    graphZoom *= factor;
    applyViewBox();
  }}, {{ passive: false }});

  // Touch support
  let touchStart = null;
  svg.addEventListener('touchstart', function(e) {{
    if (e.touches.length === 1) {{
      const t = e.touches[0];
      const pt = svgPoint(t);
      const hit = findNodeAt(pt.x, pt.y);
      if (hit !== null) {{
        e.preventDefault();
        const n = graphNodes[hit];
        n.fx = n.x; n.fy = n.y;
        graphDrag = {{ idx: hit, offsetX: pt.x - n.x, offsetY: pt.y - n.y }};
      }} else {{
        e.preventDefault();
        touchStart = {{ x: t.clientX, y: t.clientY }};
        const vb = getViewBox();
        graphPan = {{ startX: t.clientX, startY: t.clientY, vbX: vb.x, vbY: vb.y }};
      }}
    }}
  }}, {{ passive: false }});

  svg.addEventListener('touchmove', function(e) {{
    if (e.touches.length === 1) {{
      const t = e.touches[0];
      if (graphDrag) {{
        e.preventDefault();
        const pt = svgPoint(t);
        const n = graphNodes[graphDrag.idx];
        n.x = pt.x - graphDrag.offsetX;
        n.y = pt.y - graphDrag.offsetY;
        n.fx = n.x; n.fy = n.y;
        if (graphPaused) renderSVG(graphSvg, window._nodeRadius, window._degree, window._maxDeg);
      }} else if (graphPan) {{
        e.preventDefault();
        const dx = (t.clientX - graphPan.startX) / graphZoom;
        const dy = (t.clientY - graphPan.startY) / graphZoom;
        graphViewBox = {{ x: graphPan.vbX - dx, y: graphPan.vbY - dy, w: graphViewBox.w, h: graphViewBox.h }};
        applyViewBox();
      }}
    }}
  }}, {{ passive: false }});

  svg.addEventListener('touchend', function() {{
    if (graphDrag) {{
      const n = graphNodes[graphDrag.idx];
      n.fx = null; n.fy = null;
      graphDrag = null;
    }}
    graphPan = null;
    touchStart = null;
  }});
}}

function svgPoint(e) {{
  const svg = document.getElementById('graphSvg');
  const rect = svg.getBoundingClientRect();
  const vb = getViewBox();
  const x = vb.x + (e.clientX - rect.left) / rect.width * vb.w;
  const y = vb.y + (e.clientY - rect.top) / rect.height * vb.h;
  return {{ x, y }};
}}

function findNodeAt(x, y) {{
  let best = null, bestDist = Infinity;
  graphNodes.forEach((n, i) => {{
    if (n.hidden) return;
    const dx = n.x - x, dy = n.y - y;
    const d = Math.sqrt(dx*dx + dy*dy);
    const r = window._nodeRadius ? window._nodeRadius[i] : 8;
    if (d < r + 4 && d < bestDist) {{ bestDist = d; best = i; }}
  }});
  return best;
}}

function getViewBox() {{
  if (graphViewBox) return graphViewBox;
  const svg = document.getElementById('graphSvg');
  const rect = svg.getBoundingClientRect();
  return {{ x: 0, y: 0, w: rect.width || 800, h: rect.height || 600 }};
}}

function applyViewBox() {{
  const svg = document.getElementById('graphSvg');
  const vb = graphViewBox;
  svg.setAttribute('viewBox', vb.x + ' ' + vb.y + ' ' + vb.w + ' ' + vb.h);
}}

function resetGraph() {{
  const svg = document.getElementById('graphSvg');
  const rect = svg.getBoundingClientRect();
  const W = rect.width || 800, H = rect.height || 600;
  const cx = W / 2, cy = H / 2;
  graphNodes.forEach(n => {{
    n.x = cx + (Math.random() - 0.5) * 400;
    n.y = cy + (Math.random() - 0.5) * 300;
    n.vx = 0; n.vy = 0;
    n.fx = null; n.fy = null;
  }});
  graphViewBox = {{ x: 0, y: 0, w: W, h: H }};
  graphZoom = 1;
  applyViewBox();
  highlightedConcept = null;
  showPapers = false;
  selectedYear = 'all';
  document.getElementById('papersBtn').textContent = 'Show Papers';
  document.getElementById('papersBtn').classList.remove('active');
  document.getElementById('yearFilter').value = 'all';
  applyVisibility();
  startSim();
}}

function togglePhysics() {{
  graphPaused = !graphPaused;
  const btn = document.getElementById('physicsBtn');
  if (graphPaused) {{
    btn.classList.remove('active');
    btn.textContent = 'Paused';
  }} else {{
    btn.classList.add('active');
    btn.textContent = 'Physics';
    startSim();
  }}
}}

function zoomIn() {{
  const svg = document.getElementById('graphSvg');
  const vb = svg.getAttribute('viewBox').split(' ').map(Number);
  const cx = vb[2] / 2, cy = vb[3] / 2;
  const nw = vb[2] * 0.8, nh = vb[3] * 0.8;
  svg.setAttribute('viewBox', (cx - nw/2) + ' ' + (cy - nh/2) + ' ' + nw + ' ' + nh);
}}

function zoomOut() {{
  const svg = document.getElementById('graphSvg');
  const vb = svg.getAttribute('viewBox').split(' ').map(Number);
  const cx = vb[0] + vb[2] / 2, cy = vb[1] + vb[3] / 2;
  const nw = vb[2] * 1.25, nh = vb[3] * 1.25;
  svg.setAttribute('viewBox', (cx - nw/2) + ' ' + (cy - nh/2) + ' ' + nw + ' ' + nh);
}}

function render() {{
  const q = document.getElementById('filterSearch').value.toLowerCase();
  const filtered = PAGES.map((p, idx) => ({{ p, idx }})).filter(({{ p }}) => {{
    if (q && !p.title.toLowerCase().includes(q) && !p.rel.toLowerCase().includes(q) &&
        !(p.tags && p.tags.toLowerCase().includes(q))) return false;
    return true;
  }});

  const sb = document.getElementById('sidebar');
  let html = '';
  let lastCat = '';
  filtered.forEach(({{ p, idx }}) => {{
    if (p.category !== lastCat) {{
      html += '<div class="category-label">' + esc(p.category) + '</div>';
      lastCat = p.category;
    }}
    html += '<div class="item' + (idx === currentIdx ? ' active' : '') +
            '" data-index="' + idx + '" onclick="show(' + idx + ')">';
    html += '<div class="title">' + esc(p.title) + '</div>';
    if (p.tags) {{
      html += '<div class="tags">' + esc(p.tags) + '</div>';
    }}
    html += '</div>';
  }});
  sb.innerHTML = html;
}}

function show(idx) {{
  const p = PAGES[idx];
  currentIdx = idx;
  const c = document.getElementById('content');
  document.querySelectorAll('.sidebar .item').forEach(el => el.classList.remove('active'));
  document.querySelector('.sidebar .item[data-index="' + idx + '"]')?.classList.add('active');
  c.innerHTML = '<div class="page">' + p.html + '</div>';
  c.scrollTop = 0;
}}

function esc(s) {{ const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }}

document.getElementById('filterSearch').addEventListener('input', render);
render();
</script>
</body>
</html>"""

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Generated: {OUTPUT}")
    print(f"Pages: {len(pages)} | Concepts: {sum(1 for p in pages if p['category'] == 'Concepts')}")

    # Git commit & push
    import subprocess
    try:
        subprocess.run(["git", "config", "user.name", "ryotta205"], cwd=WIKI_DIR, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "ryotta205@users.noreply.github.com"], cwd=WIKI_DIR, capture_output=True, check=True)
        subprocess.run(["git", "add", "-A"], cwd=WIKI_DIR, capture_output=True, check=True)
        subprocess.run(["git", "commit", "--allow-empty", "-m", "Update wiki viewer"], cwd=WIKI_DIR, capture_output=True, check=False)
        subprocess.run(["git", "push"], cwd=WIKI_DIR, capture_output=True, check=True)
        print("  Git push OK")
    except Exception as e:
        print(f"  Git push failed: {e}")


if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    generate()
