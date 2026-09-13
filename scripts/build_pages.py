#!/usr/bin/env python3
"""
scripts/build_pages.py
======================
AI-Agent Context & Architecture Documentation:
---------------------------------------------
This script is the core static site generator for the Sad Sausage (SS-Ops) initiative.
It generates a secure, accessible, zero-external-dependency static site in `_site/` for
deployment on GitHub Pages (https://theklython.github.io/sad-sausage/).

Key Responsibilities:
1. SEO & Discovery:
   - Injects canonical URLs, meta descriptions, OpenGraph, Twitter Cards, and
     Google-compliant Schema.org JSON-LD (SoftwareSourceCode & WebSite).
   - Generates a valid W3C/Sitemaps.org `sitemap.xml` referencing all pages and endpoints.
   - Updates `robots.txt` to point to the sitemap and explicitly welcome AI agents
     (Googlebot, GPTBot, ClaudeBot, PerplexityBot, CCBot, etc.).
2. Machine-Readable Agent Standards:
   - Emits `.nojekyll` so GitHub Pages serves dot-directories like `/.well-known/`.
   - Copies `llms.txt`, `llms-full.txt`, `agent_manifest.json`, and `.well-known/ai-agent.json`.
3. Security by Design:
   - Enforces Content Security Policy (CSP) headers via meta tags.
   - Ensures all external outbound links strictly carry `rel="noopener noreferrer"`.
   - Pure Python standard library implementation: zero external pip dependencies,
     eliminating supply chain vulnerabilities in the build pipeline.
4. Clean Markdown Rendering:
   - Transforms project markdown files (README, ARCHITECTURE, SECURITY, DONATIONS)
     into semantic, responsive HTML with modern dark-mode aesthetics.
"""

from __future__ import annotations
import datetime
import html
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET

# Base URLs and Repository Metadata
BASE_URL = "https://theklython.github.io/sad-sausage"
REPO_URL = "https://github.com/TheKlython/sad-sausage"
SPONSOR_URL = "https://buymeacoffee.com/klythoni"
SITE_TITLE = "Sad Sausage (SS-Ops) – Autonomous Edge AI Operations Agent"
SITE_DESCRIPTION = (
    "Deterministic, 100% solar-powered edge AI operations agent managing smart-home "
    "telemetry, IoT automations, and local IT infrastructure with zero cloud dependencies."
)

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "_site"


def get_shared_css() -> str:
    """
    Returns the complete responsive CSS stylesheet with dark-mode aesthetic,
    solar-themed accents, code blocks, navigation, cards, and tables.
    """
    return """
:root {
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    --bg-card: #21262d;
    --border-color: #30363d;
    --text-primary: #c9d1d9;
    --text-secondary: #8b949e;
    --text-accent: #58a6ff;
    --solar-gold: #f0883e;
    --solar-green: #3fb950;
    --link-color: #58a6ff;
    --code-bg: #111418;
    --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    background-color: var(--bg-primary);
    color: var(--text-primary);
    font-family: var(--font-family);
    line-height: 1.6;
    padding-bottom: 4rem;
}

/* Header & Navigation */
header {
    background-color: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    position: sticky;
    top: 0;
    z-index: 100;
}

.nav-container {
    max-width: 1100px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.85rem 1.5rem;
    flex-wrap: wrap;
    gap: 1rem;
}

.brand {
    font-size: 1.25rem;
    font-weight: 700;
    color: #fff;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.brand span.emoji {
    font-size: 1.4rem;
}

nav.nav-links {
    display: flex;
    gap: 1.25rem;
    align-items: center;
    flex-wrap: wrap;
}

nav.nav-links a {
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 0.95rem;
    font-weight: 500;
    transition: color 0.15s ease;
}

nav.nav-links a:hover, nav.nav-links a.active {
    color: var(--text-accent);
}

.btn-github {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    color: #fff !important;
    padding: 0.35rem 0.85rem;
    border-radius: 6px;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    text-decoration: none;
}

.btn-github:hover {
    background-color: #30363d;
    border-color: #8b949e;
}

/* Main Container */
.container {
    max-width: 1050px;
    margin: 2rem auto;
    padding: 0 1.5rem;
}

/* Hero Section */
.hero {
    background: linear-gradient(180deg, rgba(22,27,34,0.85) 0%, rgba(13,17,23,0.95) 100%);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 3rem 2rem;
    text-align: center;
    margin-bottom: 2.5rem;
}

.hero h1 {
    font-size: 2.5rem;
    color: #fff;
    margin-bottom: 0.8rem;
    line-height: 1.2;
}

.hero p.tagline {
    font-size: 1.2rem;
    color: var(--solar-gold);
    font-weight: 500;
    margin-bottom: 1.2rem;
}

.hero p.desc {
    max-width: 780px;
    margin: 0 auto 1.8rem auto;
    color: var(--text-secondary);
    font-size: 1.05rem;
}

.badge-row {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
}

.badge-row img {
    height: 22px;
}

/* Action Buttons */
.btn-group {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
    margin-top: 1.5rem;
}

.btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.4rem;
    font-size: 1rem;
    font-weight: 600;
    border-radius: 8px;
    text-decoration: none;
    transition: all 0.2s ease;
}

.btn-primary {
    background-color: var(--solar-gold);
    color: #0d1117;
    border: 1px solid #d97706;
}

.btn-primary:hover {
    background-color: #f59e0b;
}

.btn-secondary {
    background-color: var(--bg-card);
    color: #fff;
    border: 1px solid var(--border-color);
}

.btn-secondary:hover {
    border-color: var(--text-accent);
}

/* Feature Grid */
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 1.5rem;
    margin: 2.5rem 0;
}

.card {
    background-color: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 1.75rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.card h3 {
    color: #fff;
    font-size: 1.35rem;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.card p {
    color: var(--text-secondary);
    font-size: 0.95rem;
    margin-bottom: 1rem;
}

.card ul {
    list-style-type: none;
    margin-bottom: 1.2rem;
}

.card ul li {
    position: relative;
    padding-left: 1.25rem;
    margin-bottom: 0.5rem;
    color: var(--text-primary);
    font-size: 0.92rem;
}

.card ul li::before {
    content: "✓";
    position: absolute;
    left: 0;
    color: var(--solar-green);
    font-weight: bold;
}

.card a.card-link {
    color: var(--text-accent);
    text-decoration: none;
    font-weight: 600;
    font-size: 0.95rem;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
}

.card a.card-link:hover {
    text-decoration: underline;
}

/* Content Page Layout */
.content-wrapper {
    background-color: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 2.5rem;
    margin-top: 1.5rem;
}

.content-wrapper h1 {
    color: #fff;
    font-size: 2.2rem;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 0.8rem;
    margin-bottom: 1.5rem;
}

.content-wrapper h2 {
    color: #fff;
    font-size: 1.6rem;
    margin-top: 2rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 0.4rem;
}

.content-wrapper h3 {
    color: #fff;
    font-size: 1.25rem;
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
}

.content-wrapper p {
    margin-bottom: 1.2rem;
}

.content-wrapper ul, .content-wrapper ol {
    margin-bottom: 1.2rem;
    padding-left: 1.8rem;
}

.content-wrapper li {
    margin-bottom: 0.4rem;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 1.5rem 0;
    background-color: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    overflow: hidden;
}

th, td {
    padding: 0.75rem 1rem;
    text-align: left;
    border: 1px solid var(--border-color);
    font-size: 0.92rem;
}

th {
    background-color: var(--bg-card);
    color: #fff;
    font-weight: 600;
}

tr:nth-child(even) {
    background-color: rgba(255, 255, 255, 0.02);
}

/* Code Blocks & Inline Code */
pre {
    background-color: var(--code-bg);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1.2rem;
    overflow-x: auto;
    font-family: var(--font-mono);
    font-size: 0.9rem;
    margin: 1.2rem 0;
    line-height: 1.45;
}

code {
    background-color: rgba(110, 118, 129, 0.2);
    padding: 0.2em 0.4em;
    border-radius: 4px;
    font-family: var(--font-mono);
    font-size: 0.88em;
}

pre code {
    background-color: transparent;
    padding: 0;
    border-radius: 0;
}

/* Alerts / Blockquotes */
blockquote {
    border-left: 4px solid var(--border-color);
    padding: 0.8rem 1.2rem;
    margin: 1.2rem 0;
    background-color: rgba(33, 38, 45, 0.6);
    color: var(--text-primary);
    border-radius: 0 8px 8px 0;
}

blockquote.alert-tip {
    border-left-color: var(--solar-green);
    background-color: rgba(63, 185, 80, 0.08);
}

blockquote.alert-important {
    border-left-color: var(--text-accent);
    background-color: rgba(88, 166, 255, 0.08);
}

blockquote.alert-caution {
    border-left-color: #f85149;
    background-color: rgba(248, 81, 73, 0.08);
}

/* Footer */
footer {
    border-top: 1px solid var(--border-color);
    margin-top: 4rem;
    padding-top: 2rem;
    text-align: center;
    color: var(--text-secondary);
    font-size: 0.9rem;
}

footer a {
    color: var(--text-accent);
    text-decoration: none;
}

footer a:hover {
    text-decoration: underline;
}

.endpoints-box {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1rem 1.5rem;
    margin-top: 1.5rem;
    text-align: left;
}

.endpoints-box h4 {
    color: #fff;
    margin-bottom: 0.6rem;
}

.endpoint-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
}

.endpoint-tag {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    padding: 0.3rem 0.6rem;
    border-radius: 6px;
    font-family: var(--font-mono);
    font-size: 0.85rem;
    color: var(--solar-gold);
    text-decoration: none;
}

.endpoint-tag:hover {
    border-color: var(--solar-gold);
}
"""


def render_html_document(
    title: str,
    description: str,
    canonical_rel: str,
    content_html: str,
    active_nav: str = "home",
) -> str:
    """
    Renders a complete HTML5 document with:
    - Content Security Policy (Security by Design)
    - Full Google SEO Meta tags & OpenGraph / Twitter Cards
    - Schema.org JSON-LD Structured Data
    - Responsive Navigation & Footer
    """
    canonical_url = f"{BASE_URL}/{canonical_rel}".rstrip("/")
    if canonical_rel == "" or canonical_rel == "index.html":
        canonical_url = f"{BASE_URL}/"

    # Schema.org JSON-LD structured data for Google Search Indexing
    schema_json = {
        "@context": "https://schema.org",
        "@type": "SoftwareSourceCode",
        "name": "Sad Sausage (SS-Ops)",
        "description": description,
        "url": canonical_url,
        "codeRepository": REPO_URL,
        "license": "https://opensource.org/licenses/MIT",
        "programmingLanguage": ["Python", "C++", "Shell"],
        "operatingSystem": "Linux, ESP32, Docker",
        "author": {
            "@type": "Person",
            "name": "TheKlython",
            "url": "https://github.com/TheKlython",
        },
    }

    schema_script = json.dumps(schema_json, indent=2)

    # Navigation items
    nav_items = [
        ("home", "./", "Home"),
        ("architecture", "architecture.html", "Architecture"),
        ("security", "security.html", "Security Policy"),
        ("donations", "donations.html", "Financial Ledger"),
    ]

    nav_links_html = []
    for key, href, label in nav_items:
        cls = ' class="active"' if key == active_nav else ""
        nav_links_html.append(f'<a href="{href}"{cls}>{label}</a>')
    nav_str = "\n                ".join(nav_links_html)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    
    <!-- Security by Design: Content Security Policy -->
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline'; font-src 'self'; script-src 'self' 'unsafe-inline';">
    
    <!-- SEO Meta Tags for Google & Search Engine Indexers -->
    <meta name="description" content="{html.escape(description)}">
    <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
    <link rel="canonical" href="{canonical_url}">
    
    <!-- OpenGraph (Facebook, LinkedIn, Discord) -->
    <meta property="og:title" content="{html.escape(title)}">
    <meta property="og:description" content="{html.escape(description)}">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Sad Sausage (SS-Ops)">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{html.escape(title)}">
    <meta name="twitter:description" content="{html.escape(description)}">
    
    <!-- Schema.org JSON-LD Structured Data for Rich Search Results -->
    <script type="application/ld+json">
{schema_script}
    </script>
    
    <style>
{get_shared_css()}
    </style>
</head>
<body>
    <header>
        <div class="nav-container">
            <a href="./" class="brand">
                <span class="emoji">🌭⚡</span> Sad Sausage
            </a>
            <nav class="nav-links">
                {nav_str}
                <a href="{REPO_URL}" class="btn-github" target="_blank" rel="noopener noreferrer">
                    <svg height="16" width="16" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path></svg>
                    GitHub
                </a>
            </nav>
        </div>
    </header>

    <main class="container">
        {content_html}
    </main>

    <footer class="container">
        <div class="endpoints-box">
            <h4>🤖 Machine-Readable AI Endpoints & Standards</h4>
            <div class="endpoint-list">
                <a href="./llms.txt" class="endpoint-tag" target="_blank" rel="noopener noreferrer">/llms.txt</a>
                <a href="./llms-full.txt" class="endpoint-tag" target="_blank" rel="noopener noreferrer">/llms-full.txt</a>
                <a href="./agent_manifest.json" class="endpoint-tag" target="_blank" rel="noopener noreferrer">/agent_manifest.json</a>
                <a href="./.well-known/ai-agent.json" class="endpoint-tag" target="_blank" rel="noopener noreferrer">/.well-known/ai-agent.json</a>
                <a href="./robots.txt" class="endpoint-tag" target="_blank" rel="noopener noreferrer">/robots.txt</a>
                <a href="./sitemap.xml" class="endpoint-tag" target="_blank" rel="noopener noreferrer">/sitemap.xml</a>
            </div>
        </div>
        <p style="margin-top: 1.5rem;">
            Sad Sausage (SS-Ops) &bull; Open-Source under <a href="{REPO_URL}/blob/main/LICENSE" target="_blank" rel="noopener noreferrer">MIT License</a> &bull;
            100% Solar-Powered &amp; Net-Zero CO₂ Operations.
        </p>
    </footer>
</body>
</html>
"""


def parse_markdown_to_html(md_content: str) -> str:
    """
    Lightweight, secure Markdown to HTML parser using Python standard library.
    Handles:
    - Headings (#, ##, ###)
    - Code blocks (```lang ... ```)
    - Tables (| ... |)
    - Blockquotes and GitHub Alerts (> [!TIP], > [!NOTE], etc.)
    - Unordered & Ordered Lists
    - Inline styling (bold, italic, code, links, images)
    - Strictly adds rel="noopener noreferrer" to external links for Security by Design.
    """
    lines = md_content.splitlines()
    output: List[str] = []
    in_code_block = False
    code_lang = ""
    code_lines: List[str] = []
    in_table = False
    table_header_done = False
    in_list = False
    list_type = "ul"

    def close_list():
        nonlocal in_list, list_type
        if in_list:
            output.append(f"</{list_type}>")
            in_list = False

    def close_table():
        nonlocal in_table, table_header_done
        if in_table:
            output.append("</tbody></table>")
            in_table = False
            table_header_done = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # 1. Code block handling
        if line.startswith("```"):
            close_list()
            close_table()
            if in_code_block:
                escaped_code = html.escape("\n".join(code_lines))
                output.append(f'<pre><code class="language-{code_lang}">{escaped_code}</code></pre>')
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
                code_lang = line[3:].strip()
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        stripped = line.strip()

        # 2. Blank line handling
        if not stripped:
            close_list()
            close_table()
            i += 1
            continue

        # 3. Horizontal Rule
        if re.match(r"^(\-{3,}|\*{3,}|_{3,})$", stripped):
            close_list()
            close_table()
            output.append("<hr style='border: none; border-top: 1px solid var(--border-color); margin: 2rem 0;'>")
            i += 1
            continue

        # 4. Tables (| col | col |)
        if stripped.startswith("|") and stripped.endswith("|"):
            close_list()
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            # Check if this is a separator line (| --- | --- |)
            if all(re.match(r"^:?-+:?$", c) for c in cells):
                table_header_done = True
                i += 1
                continue

            if not in_table:
                in_table = True
                output.append("<table>")
                output.append("<thead><tr>" + "".join(f"<th>{render_inline(c)}</th>" for c in cells) + "</tr></thead>")
                output.append("<tbody>")
            else:
                output.append("<tr>" + "".join(f"<td>{render_inline(c)}</td>" for c in cells) + "</tr>")
            i += 1
            continue
        else:
            close_table()

        # 5. Headings
        m_heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m_heading:
            close_list()
            level = len(m_heading.group(1))
            text = render_inline(m_heading.group(2))
            output.append(f"<h{level}>{text}</h{level}>")
            i += 1
            continue

        # 6. GitHub Alerts & Blockquotes
        if stripped.startswith(">"):
            close_list()
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip()[1:].strip())
                i += 1
            
            quote_text = " ".join(quote_lines)
            alert_class = ""
            if quote_text.startswith("[!NOTE]"):
                alert_class = "alert-note"
                quote_text = quote_text[7:].strip()
            elif quote_text.startswith("[!TIP]"):
                alert_class = "alert-tip"
                quote_text = quote_text[6:].strip()
            elif quote_text.startswith("[!IMPORTANT]"):
                alert_class = "alert-important"
                quote_text = quote_text[12:].strip()
            elif quote_text.startswith("[!CAUTION]") or quote_text.startswith("[!WARNING]"):
                alert_class = "alert-caution"
                quote_text = re.sub(r"^\[!(CAUTION|WARNING)\]", "", quote_text).strip()
            
            cls_attr = f' class="{alert_class}"' if alert_class else ""
            output.append(f"<blockquote{cls_attr}><p>{render_inline(quote_text)}</p></blockquote>")
            continue

        # 7. Unordered / Ordered Lists
        m_ul = re.match(r"^[\*\-]\s+(.*)$", stripped)
        m_ol = re.match(r"^\d+\.\s+(.*)$", stripped)
        if m_ul or m_ol:
            target_type = "ol" if m_ol else "ul"
            content = m_ol.group(1) if m_ol else m_ul.group(1)
            if not in_list:
                in_list = True
                list_type = target_type
                output.append(f"<{list_type}>")
            output.append(f"<li>{render_inline(content)}</li>")
            i += 1
            continue
        else:
            close_list()

        # 8. Regular paragraph
        output.append(f"<p>{render_inline(stripped)}</p>")
        i += 1

    close_list()
    close_table()
    return "\n".join(output)


def render_inline(text: str) -> str:
    """
    Renders inline Markdown elements: code, bold, italic, links, badges/images.
    Security: Applies rel="noopener noreferrer" to external links.
    """
    # Inline code: `code`
    text = re.sub(r"`([^`]+)`", lambda m: f"<code>{html.escape(m.group(1))}</code>", text)

    # Images: ![alt](url)
    text = re.sub(
        r"!\[([^\]]*)\]\(([^\)]+)\)",
        lambda m: f'<img src="{m.group(2)}" alt="{html.escape(m.group(1))}">',
        text,
    )

    # Links: [text](url)
    def link_repl(match):
        label = match.group(1)
        url = match.group(2)
        # Check if local markdown link like (ARCHITECTURE.md) -> (architecture.html)
        if url.endswith(".md"):
            url = url.replace(".md", ".html").lower()
        if url.startswith("http://") or url.startswith("https://"):
            return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label}</a>'
        return f'<a href="{url}">{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^\)]+)\)", link_repl, text)

    # Bold: **text**
    text = re.sub(r"\*\*([^\*]+)\*\*", r"<strong>\1</strong>", text)

    # Italic: *text*
    text = re.sub(r"(?<!\*)\*([^\*]+)\*(?!\*)", r"<em>\1</em>", text)

    return text


def build_home_page() -> str:
    """
    Constructs the feature-rich, high-impact landing page (index.html)
    highlighting the Sad Sausage core vision, solar compute scheduling,
    the ESP32 showcases, and AI agent endpoints.
    """
    hero_badges = f"""
    <div class="badge-row">
        <a href="{REPO_URL}/blob/main/LICENSE" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square" alt="MIT License"></a>
        <a href="https://www.python.org/" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+"></a>
        <a href="https://modelcontextprotocol.io" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/MCP-2024--11--05-purple.svg?style=flat-square" alt="MCP Protocol"></a>
        <img src="https://img.shields.io/badge/Architecture-Local_Edge_AI-brightgreen.svg?style=flat-square" alt="Local Edge">
        <img src="https://img.shields.io/badge/Energy-100%25_Solar_Powered-brightgreen.svg?style=flat-square" alt="100% Solar">
        <img src="https://img.shields.io/badge/Carbon-Net--Zero_CO%E2%82%82-success.svg?style=flat-square" alt="Net-Zero CO2">
    </div>
    """

    content = f"""
    <div class="hero">
        <h1>Sad Sausage (SS-Ops)</h1>
        <p class="tagline">☀️ Autonomous &bull; 100% Solar-Powered &bull; Deterministic Edge AI</p>
        <p class="desc">
            An open-source, deterministic Edge AI operations agent deployed in self-hosted environments.
            Powered entirely by 100% rooftop solar energy and residential battery storage, operating
            completely CO₂-neutral. Autonomously monitors IoT telemetry via Home Assistant, performs
            local incident triage, and engineers sanitized automation blueprints with zero cloud dependencies.
        </p>
        {hero_badges}
        <div class="btn-group">
            <a href="{REPO_URL}" class="btn btn-primary" target="_blank" rel="noopener noreferrer">
                Explore Source Code on GitHub &rarr;
            </a>
            <a href="architecture.html" class="btn btn-secondary">
                System Architecture
            </a>
            <a href="{SPONSOR_URL}" class="btn btn-secondary" target="_blank" rel="noopener noreferrer">
                ☕ Sponsor Hardware Fund
            </a>
        </div>
    </div>

    <h2 style="color: #fff; font-size: 1.8rem; margin-bottom: 1.2rem; text-align: center;">🌟 Featured Smart-Home Showcases</h2>
    
    <div class="grid">
        <div class="card">
            <div>
                <h3>🧯 Gas Meter Tracker</h3>
                <p>Enterprise-grade, outage-resilient hardware pulse counter for mechanical diaphragm gas meters using ESP32 &amp; OH49E Hall sensor.</p>
                <ul>
                    <li>NVS Flash state restoration across outages</li>
                    <li>Home Assistant downtime immunity (no lost pulses)</li>
                    <li>Energy Dashboard native (m³ &amp; kWh)</li>
                    <li>Live calibration entity in HA Dashboard</li>
                    <li>Encrypted Native API (Noise PSK)</li>
                </ul>
            </div>
            <a href="{REPO_URL}/tree/main/Gasmeter_ESP" class="card-link" target="_blank" rel="noopener noreferrer">
                View Hardware &amp; ESPHome Config &rarr;
            </a>
        </div>

        <div class="card">
            <div>
                <h3>🎬 Optoma Projector Controller</h3>
                <p>Enterprise-grade bi-directional RS232 serial bridge and smart controller for Optoma laser/cinema projectors via ESPHome.</p>
                <ul>
                    <li>True 4-phase state machine (Standby/Warming/On/Cooling)</li>
                    <li>Hardware fault monitoring (Overheat, Fan Locked)</li>
                    <li>Full HA control (Inputs, HDR, sliders, D-Pad)</li>
                    <li>Anti-saturation query caching state machine</li>
                    <li>Encrypted Native API &amp; WPA2 fallback</li>
                </ul>
            </div>
            <a href="{REPO_URL}/tree/main/Optoma%20UHZ%20ESP%20remote" class="card-link" target="_blank" rel="noopener noreferrer">
                View RS232 Protocol &amp; Config &rarr;
            </a>
        </div>

        <div class="card">
            <div>
                <h3>⚡ Solar Compute Scheduling</h3>
                <p>Aligns heavy inference passes, continuous log vectorization, and model benchmark evaluations dynamically to solar yield curves.</p>
                <ul>
                    <li>Zero operational carbon footprint</li>
                    <li>Dynamic Home Assistant PV &amp; SOC integration</li>
                    <li>Adaptive sliding-window KV cache allocation</li>
                    <li>Standardized MCP server interface (stdio / JSON-RPC)</li>
                </ul>
            </div>
            <a href="architecture.html" class="card-link">
                Read Architectural Specifications &rarr;
            </a>
        </div>
    </div>

    <div class="content-wrapper" style="margin-top: 3rem;">
        <h2>🏛️ Transparent Co-Investment Governance</h2>
        <p>
            To ensure genuine skin-in-the-game and long-term commitment, <strong>the project maintainer
            co-invests 30% of all hardware procurement costs from personal funds</strong>.
            Community sponsorship covers the remaining 70%. 100% of all sponsorship capital is allocated
            strictly to component procurement itemized in our public ledger.
        </p>
        <div style="margin: 1.5rem 0;">
            <a href="donations.html" class="btn btn-secondary">
                View Financial Governance &amp; Hardware Fund Ledger &rarr;
            </a>
        </div>
    </div>
    """

    return render_html_document(
        title=SITE_TITLE,
        description=SITE_DESCRIPTION,
        canonical_rel="index.html",
        content_html=content,
        active_nav="home",
    )


def build_markdown_page(
    md_file_path: Path,
    title: str,
    description: str,
    canonical_rel: str,
    active_nav: str,
) -> str:
    """
    Reads a project Markdown file, converts it into semantic HTML, and wraps
    it inside the complete HTML5 document template.
    """
    if not md_file_path.exists():
        content_html = f"<div class='content-wrapper'><h1>{html.escape(title)}</h1><p>Document not found.</p></div>"
    else:
        raw_md = md_file_path.read_text(encoding="utf-8")
        parsed_body = parse_markdown_to_html(raw_md)
        content_html = f"<div class='content-wrapper'>{parsed_body}</div>"

    return render_html_document(
        title=title,
        description=description,
        canonical_rel=canonical_rel,
        content_html=content_html,
        active_nav=active_nav,
    )


def generate_sitemap(urls: List[Dict[str, str]], output_path: Path) -> None:
    """
    Generates a standard-compliant XML Sitemap (http://www.sitemaps.org/schemas/sitemap/0.9)
    essential for search engine web crawlers and indexers (Googlebot, Bingbot).
    """
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    
    for item in urls:
        url_el = ET.SubElement(urlset, "url")
        loc_el = ET.SubElement(url_el, "loc")
        loc_el.text = item["loc"]
        
        lastmod_el = ET.SubElement(url_el, "lastmod")
        lastmod_el.text = item.get("lastmod", now_iso)
        
        changefreq_el = ET.SubElement(url_el, "changefreq")
        changefreq_el.text = item.get("changefreq", "weekly")
        
        priority_el = ET.SubElement(url_el, "priority")
        priority_el.text = item.get("priority", "0.8")

    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ", level=0)
    
    # Write with XML declaration
    with open(output_path, "wb") as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        tree.write(f, encoding="utf-8", xml_declaration=False)


def prepare_robots_txt(source_path: Path, dest_path: Path) -> None:
    """
    Copies the project's robots.txt and ensures the Sitemap reference is explicitly declared
    for web indexers (e.g. Googlebot).
    """
    content = ""
    if source_path.exists():
        content = source_path.read_text(encoding="utf-8").strip()
    else:
        content = "User-agent: *\nAllow: /"

    sitemap_line = f"Sitemap: {BASE_URL}/sitemap.xml"
    if sitemap_line not in content:
        content = f"{content}\n\n# Canonical Sitemap for Search Engines\n{sitemap_line}\n"

    dest_path.write_text(content, encoding="utf-8")


def copy_agent_manifests(root_dir: Path, output_dir: Path) -> None:
    """
    Copies machine-readable context files for AI agents:
    - llms.txt, llms-full.txt
    - agent_manifest.json
    - .well-known/ai-agent.json
    - .nojekyll (tells GitHub Pages not to ignore directories starting with dot)
    """
    files_to_copy = [
        "llms.txt",
        "llms-full.txt",
        "agent_manifest.json",
    ]
    for filename in files_to_copy:
        src = root_dir / filename
        if src.exists():
            shutil.copy2(src, output_dir / filename)

    # .well-known directory
    well_known_src = root_dir / ".well-known"
    well_known_dest = output_dir / ".well-known"
    if well_known_src.exists():
        well_known_dest.mkdir(parents=True, exist_ok=True)
        for item in well_known_src.glob("*"):
            if item.is_file():
                shutil.copy2(item, well_known_dest / item.name)

    # Search Engine verification files (Google Search Console, Bing, etc.)
    for verify_file in root_dir.glob("google*.html"):
        if verify_file.is_file():
            shutil.copy2(verify_file, output_dir / verify_file.name)

    # .nojekyll flag
    (output_dir / ".nojekyll").write_text("", encoding="utf-8")


def build_site() -> Path:
    """
    Orchestrates the static site build pipeline:
    1. Prepares `_site/` directory
    2. Builds index.html, architecture.html, security.html, donations.html
    3. Copies machine-readable files (llms.txt, manifests, .well-known)
    4. Configures robots.txt and generates sitemap.xml
    """
    print(f"[BUILD] Generating static site for {BASE_URL}...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Home page
    home_html = build_home_page()
    (OUTPUT_DIR / "index.html").write_text(home_html, encoding="utf-8")
    print("  [OK] Built index.html")

    # 2. Architecture page
    arch_html = build_markdown_page(
        md_file_path=ROOT_DIR / "ARCHITECTURE.md",
        title="System Architecture – Sad Sausage (SS-Ops)",
        description="Comprehensive architectural specifications, telemetry ingestion ring buffer, and solar compute scheduling.",
        canonical_rel="architecture.html",
        active_nav="architecture",
    )
    (OUTPUT_DIR / "architecture.html").write_text(arch_html, encoding="utf-8")
    print("  [OK] Built architecture.html")

    # 3. Security Policy page
    sec_html = build_markdown_page(
        md_file_path=ROOT_DIR / "SECURITY.md",
        title="Security Policy & Principles – Sad Sausage (SS-Ops)",
        description="Security by Design principles, local-first isolation, encrypted API transport, and vulnerability reporting protocol.",
        canonical_rel="security.html",
        active_nav="security",
    )
    (OUTPUT_DIR / "security.html").write_text(sec_html, encoding="utf-8")
    print("  [OK] Built security.html")

    # 4. Donations & Governance page
    donations_html = build_markdown_page(
        md_file_path=ROOT_DIR / "DONATIONS.md",
        title="Financial Governance & Hardware Fund Ledger – Sad Sausage (SS-Ops)",
        description="Public audit log, 30% maintainer co-investment commitment, and itemized hardware milestone roadmap.",
        canonical_rel="donations.html",
        active_nav="donations",
    )
    (OUTPUT_DIR / "donations.html").write_text(donations_html, encoding="utf-8")
    print("  [OK] Built donations.html")

    # 5. Agent manifests & .nojekyll
    copy_agent_manifests(ROOT_DIR, OUTPUT_DIR)
    print("  [OK] Copied machine-readable AI manifests & created .nojekyll")

    # 6. robots.txt
    prepare_robots_txt(ROOT_DIR / "robots.txt", OUTPUT_DIR / "robots.txt")
    print("  [OK] Configured robots.txt with sitemap directive")

    # 7. sitemap.xml
    sitemap_urls = [
        {"loc": f"{BASE_URL}/", "priority": "1.0", "changefreq": "weekly"},
        {"loc": f"{BASE_URL}/architecture.html", "priority": "0.8", "changefreq": "monthly"},
        {"loc": f"{BASE_URL}/security.html", "priority": "0.7", "changefreq": "monthly"},
        {"loc": f"{BASE_URL}/donations.html", "priority": "0.8", "changefreq": "weekly"},
        {"loc": f"{BASE_URL}/llms.txt", "priority": "0.9", "changefreq": "weekly"},
        {"loc": f"{BASE_URL}/agent_manifest.json", "priority": "0.8", "changefreq": "monthly"},
    ]
    generate_sitemap(sitemap_urls, OUTPUT_DIR / "sitemap.xml")
    print("  [OK] Generated sitemap.xml")

    print(f"[SUCCESS] Static site generation complete: {OUTPUT_DIR}")
    return OUTPUT_DIR


if __name__ == "__main__":
    build_site()
