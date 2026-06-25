#!/usr/bin/env python3
"""
기존 paper-summaries를 읽어 paper-wiki/papers/에 구조화된 논문 위키 페이지 생성
- 요약 파일에서 섹션별로 내용 추출 (개요, 방법론, 기여, 결과, 한계)
- 키워드 기반 concept 페이지 자동 연결
- Obsidian frontmatter + cross-reference 지원
"""
import os
import re
import csv
import sys

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER_SUMMARIES = os.path.join(WORKSPACE, "paper-summaries")
WIKI_DIR = os.path.join(WORKSPACE, "paper-wiki")
PAPERS_DIR = os.path.join(WIKI_DIR, "papers")
CSV_PATH = os.path.join(WORKSPACE, "paper_index", "paper_status.csv")

CONCEPTS = {
    "dram": {
        "title": "DRAM",
        "keywords": ["dram", "hbm", "ddr", "lpddr", "rowham", "refresh", "retention", "sdram", "dimm"],
    },
    "rowhammer": {
        "title": "RowHammer",
        "keywords": ["rowham", "row hammer", "bit flip", "disturbance", "trr", "target row refresh"],
    },
    "pim": {
        "title": "Processing-in-Memory",
        "keywords": ["processing-in-memory", "pim", "near-data", "processing in memory", "near memory",
                      "in-memory computing", "in-memory acceleration", "near-bank"],
    },
    "llm-inference": {
        "title": "LLM Inference",
        "keywords": ["llm", "transformer", "attention", "kv cach", "inference", "token generat",
                      "language model", "large language"],
    },
    "virtual-memory": {
        "title": "Virtual Memory",
        "keywords": ["virtual memory", "tlb", "page table", "address translation", "huge page",
                      "page walk", "mmu", "page fault"],
    },
    "storage": {
        "title": "Storage",
        "keywords": ["ssd", "flash", "nand", "storage", "key-value", "file system", "ftl",
                      "nvme", "scm", "storage-class"],
    },
    "cache": {
        "title": "Cache",
        "keywords": ["cache", "prefetch", "replacement policy", "llc", "l1", "l2", "l3"],
    },
    "security": {
        "title": "Security",
        "keywords": ["security", "encryption", "tee", "confidential", "trusted execution",
                      "side-channel", "covert channel", "integrity"],
    },
    "memory-tiering": {
        "title": "Memory Tiering",
        "keywords": ["tiered memory", "memory tier", "memory pooling", "far memory",
                      "memory disaggregation", "memory offload", "cxl memory"],
    },
    "nvm": {
        "title": "Non-Volatile Memory",
        "keywords": ["nvm", "persistent memory", "pmem", "non-volatile", "nvram",
                      "storage-class memory", "3dxpoint"],
    },
    "compression": {
        "title": "Compression",
        "keywords": ["compression", "compress", "encoding", "deduplication", "data reduction"],
    },
    "gpu": {
        "title": "GPU",
        "keywords": ["gpu", "cuda", "graphics", "mcm-gpu"],
    },
    "disaggregation": {
        "title": "Disaggregation",
        "keywords": ["disaggregat", "cxl", "compute express link", "fabric-attached",
                      "rack-scale", "interconnect"],
    },
    "near-data-processing": {
        "title": "Near-Data Processing",
        "keywords": ["near-data processing", "ndp", "computational storage", "smartssd",
                      "smart ssd", "near-memory"],
    },
}


def classify_paper(text):
    text_lower = text.lower()
    matched = []
    for slug, info in CONCEPTS.items():
        for kw in info["keywords"]:
            if kw in text_lower:
                matched.append(slug)
                break
    return sorted(set(matched))


def extract_title(md_text):
    for line in md_text.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return None


def extract_venue(md_text):
    for line in md_text.split("\n")[:15]:
        if line.startswith("**Venue:**"):
            return line.replace("**Venue:**", "").strip()
    return ""


def extract_authors(md_text):
    for line in md_text.split("\n")[:15]:
        if "**저자:**" in line:
            return line.split("**저자:**")[1].strip()
        if "**Authors:**" in line:
            return line.split("**Authors:**")[1].strip()
    return ""


def parse_csv():
    rows = []
    if not os.path.exists(CSV_PATH):
        return rows
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r.get("has_summary") == "Y":
                rows.append(r)
    return rows


def make_page_filename(pdf_filename):
    slug = os.path.splitext(pdf_filename)[0].lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def extract_section(text, start_patterns, end_patterns=None):
    """Extract a section from markdown text based on heading patterns."""
    lines = text.split("\n")
    content = []
    in_section = False
    
    for line in lines:
        # Check if we're entering the section
        if not in_section:
            for pattern in start_patterns:
                if pattern in line and line.startswith("#"):
                    in_section = True
                    break
        else:
            # Check if we're leaving the section
            if end_patterns:
                for pattern in end_patterns:
                    if pattern in line and line.startswith("#"):
                        return "\n".join(content).strip()
            content.append(line)
    
    return "\n".join(content).strip()


def extract_overview(text):
    """Extract overview from 문제 배경 section."""
    content = extract_section(text, ["## 1. 문제 배경", "## 문제 배경"], ["## 2.", "## 3.", "## Threat Model", "## 설계"])
    if not content:
        # Try to get first paragraph
        for line in text.split("\n"):
            if line.strip() and not line.startswith("#") and not line.startswith("**"):
                return line.strip()
    return content


def extract_methodology(text):
    """Extract methodology from 설계/메커니즘 section."""
    return extract_section(text, ["## 3.", "## 2. vAttention", "## 설계", "## 메커니즘"], ["## 4.", "## 5.", "## 평가", "## 구현"])


def extract_contributions(text):
    """Extract key contributions from 결론 및 Takeaway."""
    content = extract_section(text, ["## 6. 결론", "## 결론"], None)
    if not content:
        content = extract_section(text, ["## 결론"], None)
    return content


def extract_results(text):
    """Extract key results from 평가 section."""
    return extract_section(text, ["## 4.", "## 5. 평가", "## 평가"], ["## 5.", "## 6.", "## 결론", "## 한계", "## 대응책"])


def extract_limitations(text):
    """Extract limitations."""
    return extract_section(text, ["## 한계", "## limitations"], ["## 결론", "## 대응책", "## 논의"])


def generate_paper_page(row, summary_text):
    title = extract_title(summary_text) or row["pdf_filename"]
    venue = extract_venue(summary_text)
    authors = extract_authors(summary_text)
    year = row.get("year", "")
    venue_dir = row.get("venue_dir", "")
    concepts = classify_paper(title + " " + summary_text[:3000])
    summary_rel = os.path.relpath(row["summary_path"], WIKI_DIR).replace("\\", "/")

    # Extract structured sections
    overview = extract_overview(summary_text)
    methodology = extract_methodology(summary_text)
    contributions = extract_contributions(summary_text)
    results = extract_results(summary_text)
    limitations = extract_limitations(summary_text)

    # Build concept links
    concept_links = ""
    for c in concepts:
        cinfo = CONCEPTS.get(c, {})
        concept_links += f"- [[paper-wiki/concepts/{c}.md|{cinfo.get('title', c)}]]\n"

    tags_str = ", ".join([f"paper, {year}, {venue_dir}"] + [f"topic/{c}" for c in concepts])

    # Build the page
    page = f"""---
tags: [{tags_str}]
venue: "{venue}"
year: {year}
summary_path: "{summary_rel}"
---

# {title}

**Venue:** {venue}
**저자:** {authors}

## 개요

{overview if overview else "(요약 파일의 문제 배경 섹션 참조)"}

## 방법론

{methodology if methodology else "(요약 파일의 설계/메커니즘 섹션 참조)"}

## 핵심 기여

{contributions if contributions else "(요약 파일의 결론 섹션 참조)"}

## 주요 결과

{results if results else "(요약 파일의 평가 섹션 참조)"}

## 한계점

{limitations if limitations else "- (상세 내용은 요약 파일 참조)"}

## 관련 개념

{concept_links if concept_links else "- 개념 매칭 없음"}

## 전체 요약

[[{summary_rel}|전체 요약 보기]]
"""
    return page


def main():
    os.makedirs(PAPERS_DIR, exist_ok=True)
    rows = parse_csv()
    count = 0

    for row in rows:
        summary_path = row["summary_path"]
        if not summary_path or not os.path.exists(summary_path):
            continue

        pdf_filename = row["pdf_filename"]
        slug = make_page_filename(pdf_filename)
        out_path = os.path.join(PAPERS_DIR, slug + ".md")

        with open(summary_path, "r", encoding="utf-8") as f:
            summary_text = f.read()

        page = generate_paper_page(row, summary_text)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(page)
        count += 1

    print(f"Generated {count} paper pages in {PAPERS_DIR}")


if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    main()
