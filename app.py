"""
GEO Crawlability Dashboard - Main Streamlit Application
"""

import streamlit as st
import streamlit.components.v1 as components
import sys
import os
import time
import subprocess
from datetime import datetime
from typing import Tuple, Optional

# Install Playwright Chromium browser on first run (needed on Streamlit Cloud)
# This is a no-op if the browser is already installed.
try:
    subprocess.run(
        ["playwright", "install", "chromium", "--with-deps"],
        check=False, capture_output=True, timeout=120
    )
except Exception:
    pass

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from utils.crawler import Crawler
from utils.scoring import CrawlabilityScorer
from checkers.bot_access import BotAccessChecker
from checkers.cloudflare import CloudflareChecker
from checkers.renderability import RenderabilityChecker
from checkers.structure import StructureChecker
import validators


# Page configuration
st.set_page_config(
    page_title="GEO Crawlability Checker",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.html("""
<title>GEO Crawlability Checker | AI Crawler SEO Audit</title>
<meta name="description" content="Audit your website for AI crawlability, structured data, heading hierarchy, metadata, and bot access signals used by AI crawlers and citation tools.">
<link rel="canonical" href="https://geo-crawlability.streamlit.app/">
<meta property="og:title" content="GEO Crawlability Checker | AI Crawler SEO Audit">
<meta property="og:description" content="Audit your website for AI crawlability, structured data, heading hierarchy, metadata, and bot access signals used by AI crawlers and citation tools.">
<meta property="og:url" content="https://geo-crawlability.streamlit.app/">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="GEO Crawlability Checker | AI Crawler SEO Audit">
<meta name="twitter:description" content="Audit your website for AI crawlability, structured data, heading hierarchy, metadata, and bot access signals used by AI crawlers and citation tools.">
<script type="application/ld+json">
[
  {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "name": "GEO Crawlability Checker",
    "url": "https://geo-crawlability.streamlit.app/",
    "description": "Audit your website for AI crawlability, structured data, heading hierarchy, metadata, and bot access signals used by AI crawlers and citation tools.",
    "applicationCategory": "SEO Tool",
    "speakable": {
      "@type": "SpeakableSpecification",
      "cssSelector": [".geo-title", ".geo-subtitle"]
    }
  },
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is GEO crawlability?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "GEO crawlability measures how accessible your website is to AI-powered search engines like ChatGPT Search, Perplexity, and Google AI Overviews. A high score means your content is more likely to be cited in AI-generated answers."
        }
      },
      {
        "@type": "Question",
        "name": "How do I allow AI crawlers to access my website?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Add explicit Allow rules for AI bot user-agents in your robots.txt file. Key bots to allow include GPTBot (OpenAI), ClaudeBot (Anthropic), Google-Extended, and PerplexityBot."
        }
      },
      {
        "@type": "Question",
        "name": "What is a good GEO crawlability score?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Scores of 80-100 are Good, meaning your site is well optimised for AI crawlers. Scores of 50-79 need improvement, and scores below 50 indicate critical issues blocking AI access."
        }
      }
    ]
  }
]
</script>
""")

# Custom CSS — soft lavender × yellow palette
st.markdown("""
<style>
    /* ── HERO ── */
    .geo-hero {
        background: linear-gradient(150deg, #c4b5fd 0%, #a78bfa 45%, #9061f9 100%);
        padding: 2.8rem 2rem 0;
        text-align: center;
        position: relative;
        overflow: hidden;
        margin: -1rem -1rem 0 -1rem;
        border-radius: 0 0 0 0;
    }
    .geo-hero::before {
        content: '';
        position: absolute;
        top: -40px; right: -50px;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(250,204,21,0.22) 0%, transparent 65%);
        pointer-events: none;
    }
    .geo-hero::after {
        content: '';
        position: absolute;
        bottom: 10px; left: -60px;
        width: 260px; height: 260px;
        background: radial-gradient(circle, rgba(109,40,217,0.18) 0%, transparent 70%);
        pointer-events: none;
    }
    .geo-eyebrow {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        color: #1e0a3c;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        padding: 0.25rem 0.9rem;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.38);
        margin-bottom: 0.8rem;
    }
    .geo-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #1e0a3c;
        line-height: 1.15;
        margin-bottom: 0.4rem;
        letter-spacing: -0.02em;
    }
    .geo-title span { color: #facc15; }
    .geo-subtitle {
        color: rgba(46,26,71,0.7);
        font-size: 0.9rem;
        margin-bottom: 1.6rem;
        white-space: nowrap;
    }
    /* Hero shelf (white lift) */
    .geo-shelf {
        background: #f5f3ff;
        border-radius: 16px 16px 0 0;
        padding: 1.5rem 1.5rem 0;
        margin-top: 1.8rem;
    }

    /* ── SUMMARY STRIP ── */
    .summary-strip {
        display: grid;
        grid-template-columns: auto 1fr auto;
        gap: 1.25rem;
        background: white;
        border: 1.5px solid #ddd6fe;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        align-items: center;
        margin-bottom: 1.25rem;
    }
    .score-badge {
        background: linear-gradient(135deg, #6d28d9, #4c1d95);
        color: white;
        border-radius: 10px;
        width: 82px; height: 82px;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        flex-shrink: 0;
        text-align: center;
    }
    .score-badge .snum {
        font-size: 2.2rem; font-weight: 800; line-height: 1; color: #facc15;
    }
    .score-badge .sgrade {
        font-size: 0.72rem; font-weight: 700; color: rgba(224,210,255,0.88);
    }
    .summary-body h3 {
        font-size: 0.98rem; font-weight: 700; margin-bottom: 0.25rem; color: #2e1a47;
    }
    .summary-body p {
        font-size: 0.86rem; color: #57606a; line-height: 1.6; margin: 0;
    }
    .status-row {
        display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.7rem;
    }
    .stat-pill {
        display: inline-flex; align-items: center; gap: 0.35rem;
        background: #f5f3ff; border: 1px solid #ddd6fe;
        border-radius: 6px; padding: 0.28rem 0.65rem; font-size: 0.75rem;
        color: #2e1a47;
    }
    .dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
    .dot-crit { background: #dc2626; }
    .dot-warn { background: #d97706; }
    .dot-good { background: #16a34a; }
    .summary-meta {
        font-size: 0.76rem; color: #57606a; text-align: right;
        display: flex; flex-direction: column; gap: 0.22rem; white-space: nowrap;
    }
    .summary-meta strong { color: #2e1a47; }
    .summary-meta .ok { color: #16a34a; font-weight: 700; }

    /* ── SECTION LABEL ── */
    .section-label {
        font-size: 0.68rem; font-weight: 800; letter-spacing: 0.1em;
        text-transform: uppercase; color: #5b21b6;
        display: flex; align-items: center; gap: 0.5rem;
        margin: 1.5rem 0 0.9rem;
    }
    .section-label::after {
        content: ''; flex: 1; height: 1.5px; background: #ddd6fe;
    }

    /* ── CATEGORY CARDS ── */
    .cat-grid {
        display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.9rem;
        margin-bottom: 1rem;
    }
    .cat-card {
        background: white; border: 1.5px solid #ddd6fe;
        border-radius: 10px; padding: 1.1rem;
    }
    .cat-card-top {
        display: flex; justify-content: space-between; align-items: flex-start;
        margin-bottom: 0.7rem;
    }
    .cat-title { font-size: 0.83rem; font-weight: 700; color: #2e1a47; max-width: 74%; }
    .cat-score { font-size: 1.7rem; font-weight: 800; line-height: 1; }
    .cat-score.good  { color: #16a34a; }
    .cat-score.warn  { color: #d97706; }
    .cat-score.crit  { color: #dc2626; }
    .cat-badge {
        display: inline-block; padding: 0.16rem 0.6rem;
        border-radius: 20px; font-size: 0.68rem; font-weight: 700; margin-bottom: 0.7rem;
    }
    .cat-badge.good { background: #dcfce7; color: #166534; }
    .cat-badge.warn { background: #fef9c3; color: #854d0e; }
    .cat-badge.crit { background: #fee2e2; color: #991b1b; }
    .cat-divider { height: 1px; background: #ede9fe; margin: 0.65rem 0; }
    .check-list { font-size: 0.79rem; display: flex; flex-direction: column; gap: 0.28rem; }
    .check-item { display: flex; align-items: flex-start; gap: 0.35rem; color: #57606a; line-height: 1.45; }

    /* ── FIX CARDS ── */
    .fix-card {
        background: white; border: 1.5px solid #ddd6fe;
        border-left: 4px solid #dc2626;
        border-radius: 10px; padding: 1.1rem 1.3rem; margin-bottom: 0.8rem;
    }
    .fix-card.warn { border-left-color: #d97706; }
    .fix-top {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 0.45rem; gap: 0.8rem;
    }
    .fix-title { font-size: 0.9rem; font-weight: 700; color: #2e1a47; }
    .fix-badge {
        font-size: 0.68rem; font-weight: 700; padding: 0.16rem 0.6rem;
        border-radius: 20px; white-space: nowrap; flex-shrink: 0;
    }
    .fix-badge.crit { background: #fee2e2; color: #991b1b; }
    .fix-badge.warn { background: #fef9c3; color: #854d0e; }
    .fix-body { font-size: 0.84rem; color: #57606a; line-height: 1.6; }
    .fix-body code {
        background: #f5f3ff; border: 1px solid #ddd6fe;
        border-radius: 4px; padding: 0.08rem 0.35rem;
        font-size: 0.78rem; color: #5b21b6;
    }

    /* ── SCORE CONTAINER (top result) ── */
    .score-container {
        text-align: center; padding: 1.5rem;
        border-radius: 10px; margin: 1.5rem 0;
        border: 1.5px solid #ddd6fe;
    }
    .score-good    { background: #f0fdf4; border-color: #bbf7d0; }
    .score-warning { background: #fefce8; border-color: #fde68a; }
    .score-critical{ background: #fff1f2; border-color: #fecdd3; }
    .score-number  { font-size: 3.8rem; font-weight: 800; margin: 0.75rem 0; color: #2e1a47; }

    /* ── CHECK RESULTS ── */
    .check-pass { color: #16a34a; font-weight: 700; }
    .check-warn { color: #d97706; font-weight: 700; }
    .check-fail { color: #dc2626; font-weight: 700; }
    .fix-suggestion {
        background: #f5f3ff; padding: 0.5rem 0.75rem;
        border-left: 3px solid #7c3aed;
        margin-top: 0.5rem; font-style: italic;
        font-size: 0.88rem; color: #3b1a5e; border-radius: 0 6px 6px 0;
    }

    /* ── MISC ── */
    .main-header {
        font-size: 2.5rem; font-weight: 800; text-align: center; margin-bottom: 0.5rem; color: #2e1a47;
    }
    .subtitle { text-align: center; color: #6d4fa0; margin-bottom: 1.5rem; }
</style>
""", unsafe_allow_html=True)


def display_header():
    """Display the hero section with search bar"""
    st.markdown("""
    <div class="geo-hero">
      <div class="geo-eyebrow">✦ Generative Engine Optimisation</div>
      <div class="geo-title">Is your site <span>AI-ready</span>?</div>
      <div class="geo-subtitle">Check how well AI crawlers can access, read &amp; cite your content — in seconds.</div>
    </div>
    """, unsafe_allow_html=True)


def _html_block(html: str, height: int = 120) -> None:
    """Render HTML via components.html to bypass Streamlit's HTML sanitiser."""
    components.html(
        f"""<!DOCTYPE html><html><head><meta charset="utf-8">
        <style>
          * {{ margin:0; padding:0; box-sizing:border-box; }}
          body {{ font-family:-apple-system,"Segoe UI",system-ui,sans-serif;
                 background:transparent; color:#1f1035; }}
        </style></head><body>{html}</body></html>""",
        height=height,
        scrolling=False
    )


def display_score(scores):
    """Display the overall score with traffic light indicator"""
    total_score = scores['total']
    grade = scores['grade']

    if total_score >= 80:
        bg, border = "#f0fdf4", "#bbf7d0"
    elif total_score >= 50:
        bg, border = "#fefce8", "#fde68a"
    else:
        bg, border = "#fff1f2", "#fecdd3"

    _html_block(f"""
    <div style="text-align:center;padding:1.4rem;border-radius:10px;
                background:{bg};border:1.5px solid {border};">
      <div style="font-size:1rem;color:#5b21b6;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;">Overall GEO Score</div>
      <div style="font-size:3.6rem;font-weight:800;margin:0.5rem 0;color:#2e1a47;">{total_score}</div>
      <div style="font-size:1.4rem;font-weight:800;color:#2e1a47;">{grade}</div>
    </div>""", height=160)


def _score_color(s):
    if s >= 80: return "#16a34a"
    if s >= 50: return "#d97706"
    return "#dc2626"

def _badge_style(s):
    if s >= 80: return "background:#dcfce7;color:#166534;"
    if s >= 50: return "background:#fef9c3;color:#854d0e;"
    return "background:#fee2e2;color:#991b1b;"

def _badge_label(s):
    if s >= 80: return "Good"
    if s >= 50: return "Needs Work"
    return "Critical"

def _cat_card(title, score, checks_html):
    """Render one category card as HTML string."""
    return f"""
    <div style="background:white;border:1.5px solid #ddd6fe;border-radius:10px;padding:1.1rem;">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.6rem;">
        <div style="font-size:0.83rem;font-weight:700;color:#2e1a47;line-height:1.3;max-width:74%;">{title}</div>
        <div style="font-size:1.75rem;font-weight:800;line-height:1;color:{_score_color(score)};flex-shrink:0;">{score}</div>
      </div>
      <span style="display:inline-block;padding:0.15rem 0.6rem;border-radius:20px;
                   font-size:0.68rem;font-weight:700;margin-bottom:0.65rem;{_badge_style(score)}">{_badge_label(score)}</span>
      <div style="height:1px;background:#ede9fe;margin:0.6rem 0;"></div>
      <div style="font-size:0.79rem;color:#57606a;line-height:1.5;">{checks_html}</div>
    </div>"""


def _check_row(icon, text):
    return f'<div style="display:flex;gap:0.35rem;margin:0.25rem 0;">{icon} {text}</div>'


def display_category_scores(results):
    """Render 6 wireframe-style category cards split from the 3 real checker categories."""
    scores = results['scores']
    checks = results['checks']

    # ── Derive per-card scores from real check results ──────────────────────
    def subscore(check_list, names):
        """Score a subset of checks by name substring match."""
        matched = [c for c in check_list if any(n.lower() in c['name'].lower() for n in names)]
        if not matched:
            return None
        passes = sum(1 for c in matched if c['status'] == 'pass')
        warns  = sum(1 for c in matched if c['status'] == 'warn')
        return round((passes + warns * 0.5) / len(matched) * 100)

    def all_score(check_list):
        if not check_list: return 50
        passes = sum(1 for c in check_list if c['status'] == 'pass')
        warns  = sum(1 for c in check_list if c['status'] == 'warn')
        return round((passes + warns * 0.5) / len(check_list) * 100)

    bot_checks    = checks.get('bot_access', [])
    rend_checks   = checks.get('renderability', [])
    struct_checks = checks.get('structure', [])

    # Card 1 — AI Crawler Access (robots.txt, meta robots, cloudflare)
    ai_crawler_checks = [c for c in bot_checks if any(k in c['name'].lower()
        for k in ['robot', 'crawl', 'bot', 'gpt', 'claude', 'google', 'perplexity', 'cloudflare', 'blocking', 'detection'])]
    ai_crawler_score = all_score(ai_crawler_checks) if ai_crawler_checks else scores['bot_access']

    # Card 2 — Structured Data (schema, og, twitter, canonical)
    schema_checks = [c for c in struct_checks if any(k in c['name'].lower()
        for k in ['schema', 'structured', 'json', 'open graph', 'og:', 'twitter', 'canonical'])]
    schema_score = all_score(schema_checks) if schema_checks else round(scores['structure'] * 0.4)

    # Card 3 — Sitemap & Discovery (sitemap, llms.txt, lang, charset)
    sitemap_checks = [c for c in struct_checks if any(k in c['name'].lower()
        for k in ['sitemap', 'llms', 'lang', 'charset', 'encoding', 'hreflang'])]
    sitemap_score = all_score(sitemap_checks) if sitemap_checks else round(scores['structure'] * 0.6)

    # Card 4 — Performance (renderability)
    perf_score = scores['renderability']

    # Card 5 — Content Citability (headings, title, meta desc, h1)
    content_checks = [c for c in struct_checks if any(k in c['name'].lower()
        for k in ['heading', 'title', 'description', 'h1', 'h2', 'content'])]
    content_score = all_score(content_checks) if content_checks else round(scores['structure'] * 0.5)

    # Card 6 — Internationalisation (lang, charset, hreflang)
    intl_checks = [c for c in struct_checks if any(k in c['name'].lower()
        for k in ['lang', 'charset', 'encoding', 'hreflang', 'international'])]
    intl_score = all_score(intl_checks) if intl_checks else round(scores['structure'] * 0.7)

    # ── Build check-item HTML for each card ─────────────────────────────────
    def checks_html(check_list):
        if not check_list:
            return '<div style="color:#aaa;font-size:0.78rem;">No checks available</div>'
        rows = []
        for c in check_list[:4]:  # show up to 4 items per card
            icon = "✅" if c['status'] == 'pass' else ("⚠️" if c['status'] == 'warn' else "❌")
            rows.append(_check_row(icon, c['name']))
        return "".join(rows)

    # Fallback check lists for cards with no matched checks
    def fallback(category_checks, keyword_groups):
        result = []
        for group in keyword_groups:
            matched = [c for c in category_checks if any(k in c['name'].lower() for k in group)]
            result.extend(matched)
        return result if result else category_checks[:3]

    ai_html      = checks_html(ai_crawler_checks or bot_checks[:4])
    schema_html  = checks_html(schema_checks or fallback(struct_checks, [['schema','json'],['og','graph'],['twitter']]))
    sitemap_html = checks_html(sitemap_checks or fallback(struct_checks, [['sitemap'],['llms'],['lang']]))
    perf_html    = checks_html(rend_checks[:4])
    content_html = checks_html(content_checks or fallback(struct_checks, [['heading','h1'],['title'],['description']]))
    intl_html    = checks_html(intl_checks or fallback(struct_checks, [['lang'],['charset'],['hreflang']]))

    row1 = f"""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.9rem;margin-bottom:0.9rem;">
      {_cat_card("🤖 AI Crawler Access",      ai_crawler_score, ai_html)}
      {_cat_card("📄 Structured Data",         schema_score,     schema_html)}
      {_cat_card("📡 Sitemap &amp; Discovery", sitemap_score,    sitemap_html)}
    </div>"""

    row2 = f"""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.9rem;">
      {_cat_card("⚡ Performance",          perf_score,    perf_html)}
      {_cat_card("🔗 Content Citability",   content_score, content_html)}
      {_cat_card("🌐 Internationalisation", intl_score,    intl_html)}
    </div>"""

    _html_block(f"""
    <div style="font-size:0.68rem;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;
                color:#5b21b6;display:flex;align-items:center;gap:0.5rem;margin:0 0 0.9rem;">
      Category Breakdown
      <span style="flex:1;height:1.5px;background:#ddd6fe;display:inline-block;"></span>
    </div>
    {row1}{row2}""", height=490)


def display_check_result(check):
    """Display a single check result"""
    status  = check['status']
    name    = check['name']
    message = check['message']
    fix     = check.get('fix')

    if status == 'pass':
        icon      = "✅"
        color     = "#16a34a"
        label     = "PASS"
    elif status == 'warn':
        icon      = "⚠️"
        color     = "#d97706"
        label     = "WARN"
    else:
        icon      = "❌"
        color     = "#dc2626"
        label     = "FAIL"

    st.markdown(
        f"{icon} **{name}**: "
        f"<span style='color:{color};font-weight:700;'>{label}</span>",
        unsafe_allow_html=True
    )
    st.markdown(f"_{message}_")

    if fix:
        st.markdown(
            f'<div style="background:#f5f3ff;padding:0.5rem 0.75rem;border-left:3px solid #7c3aed;'
            f'margin-top:0.5rem;font-style:italic;font-size:0.88rem;color:#3b1a5e;border-radius:0 6px 6px 0;">'
            f'💡 Fix: {fix}</div>',
            unsafe_allow_html=True
        )

    st.markdown('<hr style="border:none;border-top:1px solid #ede9fe;margin:0.6rem 0;">', unsafe_allow_html=True)


def display_recommended_fixes(scorer):
    """Render all failed + warn checks as recommended fix cards."""
    all_checks = []
    for cat, checks in scorer.results.items():
        for c in checks:
            if c['status'] in ('fail', 'warn'):
                all_checks.append({**c, 'category': cat})

    if not all_checks:
        return

    fixes_html = ""
    for check in all_checks:
        is_crit   = check['status'] == 'fail'
        left_col  = "#dc2626" if is_crit else "#d97706"
        badge_bg  = "#fee2e2" if is_crit else "#fef9c3"
        badge_fg  = "#991b1b" if is_crit else "#854d0e"
        badge_lbl = "Critical"  if is_crit else "Warning"
        fix_line  = ""
        if check.get('fix'):
            fix_line = (f'<div style="margin-top:0.4rem;font-size:0.83rem;color:#57606a;">'
                        f'<strong style="color:#2e1a47;">Fix:</strong> {check["fix"]}</div>')
        fixes_html += f"""
        <div style="background:white;border:1.5px solid #ddd6fe;border-left:4px solid {left_col};
                    border-radius:10px;padding:1rem 1.25rem;margin-bottom:0.75rem;">
          <div style="display:flex;justify-content:space-between;align-items:center;
                      margin-bottom:0.4rem;gap:0.75rem;">
            <span style="font-size:0.88rem;font-weight:700;color:#2e1a47;">{check['name']}</span>
            <span style="font-size:0.67rem;font-weight:700;padding:0.15rem 0.6rem;border-radius:20px;
                         white-space:nowrap;flex-shrink:0;background:{badge_bg};color:{badge_fg};">{badge_lbl}</span>
          </div>
          <div style="font-size:0.83rem;color:#57606a;line-height:1.6;">{check['message']}</div>
          {fix_line}
        </div>"""

    n = len(all_checks)
    card_h = n * 115 + 55
    _html_block(f"""
    <div style="font-size:0.68rem;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;
                color:#5b21b6;display:flex;align-items:center;gap:0.5rem;margin:0 0 0.9rem;">
      Recommended Fixes
      <span style="flex:1;height:1.5px;background:#ddd6fe;display:inline-block;"></span>
    </div>
    {fixes_html}""", height=card_h)


def display_summary(results, url: str = "", elapsed: float = 0.0):
    """Display fully inline-styled summary strip via components.html"""
    summary  = results['summary']
    scores   = results['scores']
    total    = scores['total']
    grade    = scores['grade']
    passes   = summary['passes']
    warnings = summary['warnings']
    fails    = summary['fails']

    pill = ("display:inline-flex;align-items:center;gap:0.35rem;"
            "background:#f5f3ff;border:1px solid #ddd6fe;"
            "border-radius:6px;padding:0.28rem 0.65rem;font-size:0.75rem;color:#2e1a47;")
    dot  = "width:7px;height:7px;border-radius:50%;display:inline-block;"
    elapsed_pill = (f'<span style="{pill}">⚡ {elapsed:.1f}s</span>' if elapsed else "")

    _html_block(f"""
    <div style="font-size:0.68rem;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;
                color:#5b21b6;display:flex;align-items:center;gap:0.5rem;margin:0 0 0.9rem;">
      Analysis Summary
      <span style="flex:1;height:1.5px;background:#ddd6fe;display:inline-block;"></span>
    </div>
    <div style="display:grid;grid-template-columns:auto 1fr auto;gap:1.25rem;background:white;
                border:1.5px solid #ddd6fe;border-radius:12px;padding:1.25rem 1.5rem;
                align-items:center;">

      <div style="background:linear-gradient(135deg,#6d28d9,#4c1d95);border-radius:10px;
                  width:82px;height:82px;display:flex;flex-direction:column;
                  align-items:center;justify-content:center;flex-shrink:0;text-align:center;">
        <span style="font-size:2.2rem;font-weight:800;line-height:1;color:#facc15;">{total}</span>
        <span style="font-size:0.72rem;font-weight:700;color:rgba(224,210,255,0.88);">{grade}</span>
      </div>

      <div>
        <div style="font-size:0.98rem;font-weight:700;margin-bottom:0.25rem;color:#2e1a47;">
          {url or "Analysis Complete"}
        </div>
        <div style="font-size:0.86rem;color:#57606a;line-height:1.6;">
          GEO crawlability score across bot access, renderability, and structure checks.
        </div>
        <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-top:0.7rem;">
          <span style="{pill}"><span style="{dot}background:#dc2626;"></span><strong>{fails} Critical</strong></span>
          <span style="{pill}"><span style="{dot}background:#d97706;"></span><strong>{warnings} Warnings</strong></span>
          <span style="{pill}"><span style="{dot}background:#16a34a;"></span><strong>{passes} Passed</strong></span>
          {elapsed_pill}
        </div>
      </div>

      <div style="font-size:0.76rem;color:#57606a;text-align:right;
                  display:flex;flex-direction:column;gap:0.22rem;white-space:nowrap;">
        <div><strong style="color:#2e1a47;">Total:</strong> {summary['total_checks']} checks</div>
        <div><strong style="color:#2e1a47;">Bot Access:</strong> {scores['bot_access']}/100</div>
        <div><strong style="color:#2e1a47;">Renderability:</strong> {scores['renderability']}/100</div>
        <div><strong style="color:#2e1a47;">Structure:</strong> {scores['structure']}/100</div>
      </div>

    </div>""", height=175)


def find_best_url_match(user_input: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Find the best matching URL for user input by trying multiple variations.
    
    Args:
        user_input: User's input (could be domain, brand name, or partial URL)
    
    Returns:
        tuple: (best_url, message) - The working URL and an info message, or (None, error_msg)
    """
    import requests
    
    user_input = user_input.strip().lower()
    
    # If already has protocol, validate it
    if user_input.startswith('http://') or user_input.startswith('https://'):
        try:
            response = requests.head(user_input, timeout=5, allow_redirects=True)
            if response.status_code < 400:
                return user_input, None
        except:
            pass
        return user_input, None  # Return as-is, let main analyzer handle errors
    
    # Generate possible URL variations
    variations = []
    
    # If it looks like a domain (has dots)
    if '.' in user_input:
        variations.extend([
            f"https://{user_input}",
            f"https://www.{user_input}",
            f"http://{user_input}",
            f"http://www.{user_input}",
        ])
    else:
        # Just a name like "google" or "bbc" - try common TLDs
        variations.extend([
            f"https://{user_input}.com",
            f"https://www.{user_input}.com",
            f"https://{user_input}.co.uk",
            f"https://www.{user_input}.co.uk",
            f"https://{user_input}.org",
            f"https://www.{user_input}.org",
            f"https://{user_input}.net",
            f"https://www.{user_input}.net",
        ])
    
    # Try each variation
    for url in variations:
        try:
            response = requests.head(url, timeout=5, allow_redirects=True,
                                    headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code < 400:
                # Found a working URL
                final_url = response.url if response.url else url
                if final_url != user_input:
                    message = f"✅ Found: **{final_url}**"
                else:
                    message = None
                return final_url, message
        except:
            continue
    
    # No working URL found
    return None, f"❌ Could not find a working website for '{user_input}'. Please enter a valid domain."


def _display_blocked_results(results, scorer, url: str, blocking_msg: str, likely_system: str):
    """Render score + 6-category cards + recommended fixes for bot-blocked sites."""
    # Warning banner
    st.warning(
        f"⚠️ **Bot Protection Detected** — {blocking_msg}.  \n"
        f"Likely system: {likely_system}.  \n"
        "Scores below reflect the impact of blocking on AI crawlability."
    )
    # Summary strip + cards + fixes — same layout as a normal result
    display_summary(results, url=url)
    display_category_scores(results)
    display_recommended_fixes(scorer)


def analyze_url(url: str):
    """
    Main analysis function

    Args:
        url: URL to analyze
    """
    # Initialize components
    crawler = Crawler()
    scorer = CrawlabilityScorer()
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_detail = st.empty()
    timer_display = st.empty()
    
    # Start timer
    start_time = time.time()
    
    # Track blocking reason
    blocking_reason = None
    used_fallback = False
    
    def update_timer():
        elapsed = time.time() - start_time
        timer_display.info(f"⏱️ Elapsed time: {elapsed:.1f}s")
    
    try:
        # Step 1: Fetch main page
        status_text.text("📥 Fetching page content...")
        status_detail.caption(f"🌐 Connecting to: {url}")
        progress_bar.progress(10)
        update_timer()
        
        html_content, response, error = crawler.fetch_url(url)
        update_timer()
        
        # Handle timeout errors with browser fallback
        if error and ("timed out" in str(error).lower() or "timeout" in str(error).lower()):
            blocking_reason = "timeout"
            status_text.text("🔄 Request timed out, trying browser method...")
            status_detail.caption("⏳ Waiting for browser to load page (up to 90s)...")
            st.warning(f"⚠️ Initial request timed out. Attempting browser-based fetch (this may take longer)...")
            update_timer()
            
            try:
                render_checker = RenderabilityChecker()
                html_content = render_checker.get_rendered_html(url)
                update_timer()
                
                if html_content:
                    st.info("✅ Successfully fetched using browser method")
                    used_fallback = True
                    error = None
                    headers = {}
                    # Add blocking detection check
                    scorer.add_check(
                        'bot_access',
                        'Automated Request Blocking',
                        'fail',
                        'Site deliberately delays or blocks automated requests (timeout detected)',
                        'Review bot detection settings - site may be blocking AI crawlers with timeout mechanisms'
                    )
                else:
                    blocking_reason = "timeout_strict"
                    # Add bot-blocking checks
                    scorer.add_check(
                        'bot_access',
                        'Strict Bot Protection (Timeout)',
                        'fail',
                        'Site blocked all automated access within 30s — including real browser fallback',
                        'Disable advanced bot detection or whitelist AI crawler user-agents (GPTBot, ClaudeBot, etc.)'
                    )
                    scorer.add_check('bot_access', 'AI Crawler Access', 'fail',
                                     'Site is inaccessible to AI crawlers due to bot protection',
                                     'Whitelist GPTBot, ClaudeBot, PerplexityBot, Google-Extended in your WAF settings')
                    scorer.add_check('renderability', 'Content Accessibility', 'fail',
                                     'Could not analyse — site blocked access before content could be retrieved',
                                     'Fix bot protection to allow automated content analysis')
                    scorer.add_check('structure', 'Metadata & Schema', 'fail',
                                     'Could not analyse — site blocked access before structure could be checked',
                                     'Fix bot protection to allow structure and metadata analysis')

                    results = scorer.get_all_results()
                    progress_bar.empty()
                    status_text.empty()
                    status_detail.empty()
                    timer_display.empty()

                    _display_blocked_results(results, scorer, url,
                                             "Site blocked all access within 30s (timeout + browser fallback failed)",
                                             "Cloudflare Bot Management · Akamai · PerimeterX · DataDome · Custom WAF")
                    return
            except Exception as e:
                st.error(f"❌ Browser fetch failed: {str(e)}")
                return
        # If regular fetch fails with 403, try Playwright as fallback
        elif error and "403" in str(error):
            blocking_reason = "403_forbidden"
            status_text.text("🔄 Site blocked regular request, trying browser method...")
            status_detail.caption("🌐 Using real browser to bypass bot detection...")
            st.warning(f"⚠️ Initial request blocked (403). Attempting browser-based fetch...")
            update_timer()
            
            try:
                render_checker = RenderabilityChecker()
                html_content = render_checker.get_rendered_html(url)
                update_timer()
                
                if html_content:
                    st.info("✅ Successfully fetched using browser method")
                    used_fallback = True
                    error = None
                    headers = {}  # No headers available from Playwright
                    # Add blocking detection check
                    scorer.add_check(
                        'bot_access',
                        'Bot Detection System',
                        'fail',
                        'Site actively blocks automated requests (403 Forbidden) - likely using WAF or bot management',
                        'Disable or configure bot detection to allow AI crawlers (e.g., Cloudflare Bot Management, Akamai, PerimeterX)'
                    )
                else:
                    blocking_reason = "403_strict"
                    scorer.add_check(
                        'bot_access',
                        'Strict Bot Protection (403)',
                        'fail',
                        'Site returned 403 Forbidden for all automated access including real browser fallback',
                        'Contact your WAF/CDN provider to whitelist AI crawler user-agents'
                    )
                    scorer.add_check('bot_access', 'AI Crawler Access', 'fail',
                                     'Site is completely inaccessible to AI crawlers',
                                     'Whitelist GPTBot, ClaudeBot, PerplexityBot, Google-Extended in WAF settings')
                    scorer.add_check('renderability', 'Content Accessibility', 'fail',
                                     'Could not analyse — 403 blocked all access',
                                     'Fix bot protection to allow content analysis')
                    scorer.add_check('structure', 'Metadata & Schema', 'fail',
                                     'Could not analyse — 403 blocked all access',
                                     'Fix bot protection to allow structure analysis')

                    results = scorer.get_all_results()
                    progress_bar.empty()
                    status_text.empty()
                    status_detail.empty()
                    timer_display.empty()

                    _display_blocked_results(results, scorer, url,
                                             "Site returned 403 Forbidden — all automated access blocked",
                                             "Cloudflare Bot Management · Akamai · PerimeterX · DataDome · Custom WAF")
                    return
            except Exception as e:
                st.error(f"❌ Browser fetch also failed: {str(e)}")
                return
        elif error or not html_content:
            st.error(f"❌ Failed to fetch URL: {error}")
            st.info("💡 Possible reasons:")
            st.markdown("""
            - Site may be down or unreachable
            - Network connectivity issues
            - Site requires authentication
            - Geo-blocking or regional restrictions
            """)
            return
        
        headers = dict(response.headers) if response else {}
        
        # Step 2: Bot Access Checks
        status_text.text("🤖 Checking bot access...")
        status_detail.caption("📄 Analyzing robots.txt and access controls...")
        progress_bar.progress(30)
        update_timer()
        
        bot_checker = BotAccessChecker(url, crawler)
        bot_checker.run_all_checks(html_content, headers, scorer)
        
        # Step 3: Cloudflare Check
        status_text.text("☁️ Checking Cloudflare blocking...")
        status_detail.caption("🔍 Detecting bot protection systems...")
        progress_bar.progress(40)
        update_timer()
        
        cf_checker = CloudflareChecker()
        cf_checker.check_cloudflare_blocking(html_content, headers, scorer)
        
        # Step 4: Renderability Checks
        status_text.text("🎨 Analyzing renderability...")
        status_detail.caption("🖥️ Comparing raw HTML vs rendered content...")
        progress_bar.progress(60)
        update_timer()
        
        render_checker = RenderabilityChecker()
        render_checker.run_all_checks(url, html_content, scorer)
        
        # Step 5: Structure Checks
        status_text.text("📋 Validating structure and metadata...")
        status_detail.caption("🏗️ Checking schema, headings, and SEO elements...")
        progress_bar.progress(80)
        update_timer()
        
        structure_checker = StructureChecker(url, crawler)
        structure_checker.run_all_checks(html_content, scorer)
        
        # Step 6: Calculate final results
        status_text.text("📊 Calculating scores...")
        status_detail.caption("🧮 Computing final crawlability score...")
        progress_bar.progress(100)
        update_timer()
        
        results = scorer.get_all_results()

        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        status_detail.empty()

        # Display results with final time
        final_time = time.time() - start_time
        timer_display.empty()

        # Show blocking detection if applicable
        if blocking_reason or used_fallback:
            st.markdown("### 🚨 Bot Protection Detected")

            if blocking_reason == "timeout":
                st.error("**Blocking Method**: Timeout/Delay Mechanism")
                st.markdown("""
                **Impact**: Site deliberately delays responses to automated requests
                - **Severity**: High — AI crawlers will experience slow or failed access
                - **Likely System**: Rate limiting, bot detection, or WAF
                - **Score Impact**: -10 points from Bot Access category
                """)
            elif blocking_reason == "403_forbidden":
                st.error("**Blocking Method**: 403 Forbidden (Active Bot Detection)")
                st.markdown("""
                **Impact**: Site actively blocks automated requests but allows real browsers
                - **Severity**: Critical — AI crawlers are explicitly blocked
                - **Likely System**: Cloudflare Bot Management, Akamai, PerimeterX, or DataDome
                - **Score Impact**: -15 points from Bot Access category
                """)
            elif blocking_reason == "403_strict":
                st.error("**Blocking Method**: Strict Bot Protection (All Automated Access Blocked)")
                st.markdown("""
                **Impact**: Site blocks ALL automated access including real browsers
                - **Severity**: Extreme — Complete inaccessibility to AI crawlers
                - **Likely System**: Advanced WAF with strict fingerprinting
                - **Score Impact**: -25 points from Bot Access category
                """)

            if used_fallback:
                st.info("ℹ️ **Note**: Analysis completed using browser fallback method. Some checks may be limited.")

            st.markdown('<hr style="border:none;border-top:1px solid #ede9fe;margin:1rem 0">', unsafe_allow_html=True)

        # Summary strip (includes score badge)
        display_summary(results, url=url, elapsed=final_time)

        # 6-category card grid
        display_category_scores(results)

        # Recommended fixes (fails + warnings)
        display_recommended_fixes(scorer)
        
    except Exception as e:
        st.error(f"❌ An error occurred during analysis: {str(e)}")
        st.exception(e)


def _example_scenario():
    """Show a pre-rendered example result (example.com) on page load."""

    def ex_card(title, score, items):
        rows = "".join(
            f'<div style="display:flex;gap:0.35rem;margin:0.25rem 0;font-size:0.79rem;color:#57606a;">'
            f'{icon} {text}</div>'
            for icon, text in items
        )
        return f"""
        <div style="background:white;border:1.5px solid #ddd6fe;border-radius:10px;padding:1.1rem;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.6rem;">
            <div style="font-size:0.83rem;font-weight:700;color:#2e1a47;line-height:1.3;max-width:74%;">{title}</div>
            <div style="font-size:1.75rem;font-weight:800;line-height:1;color:{_score_color(score)};flex-shrink:0;">{score}</div>
          </div>
          <span style="display:inline-block;padding:0.15rem 0.6rem;border-radius:20px;font-size:0.68rem;
                       font-weight:700;margin-bottom:0.65rem;{_badge_style(score)}">{_badge_label(score)}</span>
          <div style="height:1px;background:#ede9fe;margin:0.6rem 0;"></div>
          {rows}
        </div>"""

    def ex_fix(name, msg, fix, is_crit=True):
        left  = "#dc2626" if is_crit else "#d97706"
        bb    = "#fee2e2" if is_crit else "#fef9c3"
        bf    = "#991b1b" if is_crit else "#854d0e"
        bl    = "Critical" if is_crit else "Warning"
        return f"""
        <div style="background:white;border:1.5px solid #ddd6fe;border-left:4px solid {left};
                    border-radius:10px;padding:1rem 1.25rem;margin-bottom:0.75rem;">
          <div style="display:flex;justify-content:space-between;align-items:center;
                      margin-bottom:0.4rem;gap:0.75rem;">
            <span style="font-size:0.88rem;font-weight:700;color:#2e1a47;">{name}</span>
            <span style="font-size:0.67rem;font-weight:700;padding:0.15rem 0.6rem;border-radius:20px;
                         white-space:nowrap;background:{bb};color:{bf};">{bl}</span>
          </div>
          <div style="font-size:0.83rem;color:#57606a;line-height:1.6;">{msg}</div>
          <div style="margin-top:0.4rem;font-size:0.83rem;color:#57606a;">
            <strong style="color:#2e1a47;">Fix:</strong> {fix}
          </div>
        </div>"""

    pill = ("display:inline-flex;align-items:center;gap:0.35rem;"
            "background:#f5f3ff;border:1px solid #ddd6fe;"
            "border-radius:6px;padding:0.28rem 0.65rem;font-size:0.75rem;color:#2e1a47;")
    dot = "width:7px;height:7px;border-radius:50%;display:inline-block;"

    # Summary strip
    _html_block(f"""
    <div style="font-size:0.68rem;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;
                color:#5b21b6;display:flex;align-items:center;gap:0.5rem;margin:0 0 0.9rem;">
      Analysis Summary &nbsp;<span style="font-weight:400;text-transform:none;color:#aaa;font-size:0.7rem;">— example.com preview</span>
      <span style="flex:1;height:1.5px;background:#ddd6fe;display:inline-block;"></span>
    </div>
    <div style="display:grid;grid-template-columns:auto 1fr auto;gap:1.25rem;background:white;
                border:1.5px solid #ddd6fe;border-radius:12px;padding:1.25rem 1.5rem;align-items:center;">
      <div style="background:linear-gradient(135deg,#6d28d9,#4c1d95);border-radius:10px;
                  width:82px;height:82px;display:flex;flex-direction:column;
                  align-items:center;justify-content:center;text-align:center;">
        <span style="font-size:2.2rem;font-weight:800;line-height:1;color:#facc15;">72</span>
        <span style="font-size:0.72rem;font-weight:700;color:rgba(224,210,255,0.88);">🟡 Needs Improvement</span>
      </div>
      <div>
        <div style="font-size:0.98rem;font-weight:700;margin-bottom:0.25rem;color:#2e1a47;">example.com — Analysis Complete</div>
        <div style="font-size:0.86rem;color:#57606a;line-height:1.6;">
          Solid foundation but GPTBot &amp; PerplexityBot are blocked, structured data is incomplete,
          and key pages lack content depth to be reliably cited by AI engines.
        </div>
        <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-top:0.7rem;">
          <span style="{pill}"><span style="{dot}background:#dc2626;"></span><strong>3 Critical</strong></span>
          <span style="{pill}"><span style="{dot}background:#d97706;"></span><strong>3 Warnings</strong></span>
          <span style="{pill}"><span style="{dot}background:#16a34a;"></span><strong>9 Passed</strong></span>
          <span style="{pill}">⚡ 312 ms</span>
          <span style="{pill}">200 OK</span>
        </div>
      </div>
      <div style="font-size:0.76rem;color:#57606a;text-align:right;display:flex;flex-direction:column;gap:0.22rem;white-space:nowrap;">
        <div><strong style="color:#2e1a47;">Scanned:</strong> 2 Jul 2025</div>
        <div>14:32 UTC</div>
        <div style="color:#16a34a;font-weight:700;">✓ HTTPS</div>
        <div style="color:#16a34a;font-weight:700;">✓ Sitemap found</div>
      </div>
    </div>""", height=175)

    # 6 category cards
    row1 = f"""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.9rem;margin-bottom:0.9rem;">
      {ex_card("🤖 AI Crawler Access", 38, [("❌","GPTBot blocked in robots.txt"),("❌","PerplexityBot not permitted"),("✅","Googlebot allowed")])}
      {ex_card("📄 Structured Data",   61, [("✅","JSON-LD present"),("✅","OpenGraph tags found"),("✅","Canonical URL set"),("❌","No Article / FAQPage schema")])}
      {ex_card("📡 Sitemap &amp; Discovery", 88, [("✅","sitemap.xml accessible"),("✅","Sitemap in robots.txt"),("✅","142 URLs indexed"),("✅","Last-modified dates present")])}
    </div>"""
    row2 = f"""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.9rem;">
      {ex_card("⚡ Performance",          91, [("✅","TTFB under 600 ms"),("✅","HTTPS enforced"),("✅","No render-blocking JS"),("✅","Alt text on images")])}
      {ex_card("🔗 Content Citability",   54, [("✅","Author information present"),("✅","Publication date set"),("❌","No summary / abstract"),("❌","Thin content (<400 words)")])}
      {ex_card("🌐 Internationalisation", 80, [("✅","lang attribute set (en)"),("✅","hreflang tags present"),("✅","Character encoding declared"),("⚠️","No regional variants")])}
    </div>"""

    _html_block(f"""
    <div style="font-size:0.68rem;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;
                color:#5b21b6;display:flex;align-items:center;gap:0.5rem;margin:0 0 0.9rem;">
      Category Breakdown
      <span style="flex:1;height:1.5px;background:#ddd6fe;display:inline-block;"></span>
    </div>
    {row1}{row2}""", height=490)

    # Recommended fixes
    fixes = [
        ex_fix("Allow GPTBot and PerplexityBot in robots.txt",
               "Your robots.txt blocks GPTBot and PerplexityBot, preventing ChatGPT Search and Perplexity from crawling.",
               "Add User-agent: GPTBot + Allow: / and repeat for PerplexityBot. Remove existing Disallow rules for these agents.",
               is_crit=True),
        ex_fix("Add Article or FAQPage JSON-LD schema",
               "Pages without Article or FAQPage structured data are less likely to appear in AI-generated responses.",
               "Add a &lt;script type='application/ld+json'&gt; block with Article or FAQPage schema to key landing pages.",
               is_crit=False),
        ex_fix("Increase content depth — aim for 400+ words per page",
               "The analysed page contains fewer than 400 words. AI models cite pages with substantial, self-contained explanations.",
               "Add a short intro paragraph answering the primary query directly — this is how AI models extract answer snippets.",
               is_crit=False),
        ex_fix("Add BreadcrumbList structured data",
               "Breadcrumb schema helps AI crawlers understand your site hierarchy and improves page-context signals.",
               "Add a BreadcrumbList JSON-LD block to all non-homepage pages.",
               is_crit=True),
    ]
    n = len(fixes)
    _html_block(f"""
    <div style="font-size:0.68rem;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;
                color:#5b21b6;display:flex;align-items:center;gap:0.5rem;margin:0 0 0.9rem;">
      Recommended Fixes
      <span style="flex:1;height:1.5px;background:#ddd6fe;display:inline-block;"></span>
    </div>
    {"".join(fixes)}""", height=n * 130 + 55)


def main():
    """Main application"""
    display_header()

    # ── Search bar (inside hero shelf styling) ──
    st.markdown('<div class="geo-shelf">', unsafe_allow_html=True)

    col_input, col_btn = st.columns([5, 1])
    with col_input:
        url = st.text_input(
            label="URL",
            label_visibility="collapsed",
            placeholder="https://your-website.com",
            help="Enter a full URL, domain, or brand name — e.g. example.com or just 'stripe'"
        )
    with col_btn:
        analyze_button = st.button("Analyse →", type="primary", use_container_width=True)

    # Example chips row
    st.markdown("""
    <div style="margin-top:0.5rem;margin-bottom:1rem;font-size:0.78rem;color:#8b6bbf;">
      Try: &nbsp;
      <span style="background:rgba(109,40,217,0.08);border:1px solid rgba(109,40,217,0.18);
        color:#5b21b6;padding:0.2rem 0.65rem;border-radius:20px;margin-right:0.3rem;">ibm.com</span>
      <span style="background:rgba(109,40,217,0.08);border:1px solid rgba(109,40,217,0.18);
        color:#5b21b6;padding:0.2rem 0.65rem;border-radius:20px;margin-right:0.3rem;">openai.com</span>
      <span style="background:rgba(109,40,217,0.08);border:1px solid rgba(109,40,217,0.18);
        color:#5b21b6;padding:0.2rem 0.65rem;border-radius:20px;margin-right:0.3rem;">bbc.co.uk</span>
      <span style="background:rgba(109,40,217,0.08);border:1px solid rgba(109,40,217,0.18);
        color:#5b21b6;padding:0.2rem 0.65rem;border-radius:20px;margin-right:0.3rem;">stripe.com</span>
      <span style="background:rgba(109,40,217,0.08);border:1px solid rgba(109,40,217,0.18);
        color:#5b21b6;padding:0.2rem 0.65rem;border-radius:20px;">vercel.com</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Example scenario shown on page load ──────────────────────────────────
    if not analyze_button:
        _example_scenario()

    # Perform analysis
    if analyze_button:
        if not url:
            st.warning("⚠️ Please enter a URL or website name")
        else:
            with st.spinner("🔍 Finding best URL match..."):
                working_url, message = find_best_url_match(url)

            if working_url is None:
                st.error(message)
                st.info("💡 **Tips:** Enter a full domain (`example.com`), a brand name (`stripe`), or include the protocol (`https://example.com`)")
            else:
                if message:
                    st.success(message)

                if not validators.url(working_url):
                    st.error("❌ Invalid URL format")
                else:
                    analyze_url(working_url)
    
    # Information section
    with st.expander("ℹ️ About This Tool"):
        st.markdown("""
        ## What does this tool check?

        **Bot Access (40% weight)**
        - robots.txt restrictions for AI bots
        - Crawl-delay setting (high values throttle AI indexing)
        - Cloudflare AI bot blocking
        - Meta robots (`noindex`, `noai`) and X-Robots-Tag headers

        **Renderability (30% weight)**
        - JavaScript-dependent content (raw HTML vs. rendered comparison)
        - Paywall detection
        - Login requirements

        **Structure & Metadata (30% weight)**
        - Schema.org structured data (Organization, Article, FAQPage, HowTo, Product)
        - AI Overview signals: FAQPage / HowTo schema, speakable property
        - Open Graph tags (og:title, og:description, og:url)
        - Twitter Card tags
        - Language declaration (`lang` attribute, hreflang)
        - Charset declaration (UTF-8)
        - Heading hierarchy (H1–H6)
        - Title and meta description
        - Canonical tags
        - Sitemap presence
        - llms.txt (AI-readable site summary at /llms.txt)

        ### Scoring
        - **80-100** 🟢 Good — Well optimised for AI crawlers
        - **50-79** 🟡 Needs Improvement — Some issues to address
        - **0-49** 🔴 Critical Issues — Major problems blocking AI access

        ### AI Bots Checked
        **OpenAI**: GPTBot, ChatGPT-User, OAI-SearchBot
        **Anthropic**: ClaudeBot, anthropic-ai, Claude-Web
        **Google**: Google-Extended, Googlebot
        **Perplexity**: PerplexityBot, DuckAssistBot
        **Meta**: meta-externalagent
        **Others**: CCBot, Amazonbot, Applebot-Extended, Bytespider, YouBot, cohere-ai, Diffbot, Timpibot
        """)

    with st.expander("💡 Quick Wins to Improve Your Score"):
        st.markdown("""
        ## Top actions to maximise AI crawlability

        1. **Allow all AI bots in robots.txt** — ensure no `Disallow: /` for GPTBot, ClaudeBot, etc.
        2. **Create /llms.txt** — a plain-text summary of your site ([spec](https://llmstxt.org))
        3. **Add FAQPage or HowTo JSON-LD** — highest impact for AI Overview eligibility
        4. **Add Open Graph tags** — `og:title`, `og:description`, `og:url` help AI citation tools
        5. **Set `<meta charset="utf-8">`** — first tag in `<head>`, prevents encoding issues
        6. **Add `lang="en"` to `<html>`** — tells AI the content language unambiguously
        7. **Reference your sitemap in robots.txt** — `Sitemap: https://yourdomain.com/sitemap.xml`
        8. **Remove `noai` / `noindex` directives** if you want AI tools to index content
        9. **Lower or remove Crawl-delay** — values > 10s severely throttle AI crawlers
        10. **Enable server-side rendering** — critical content should be visible in raw HTML

        ### Sample robots.txt for maximum AI access
        ```
        User-agent: *
        Allow: /

        User-agent: GPTBot
        Allow: /

        User-agent: ClaudeBot
        Allow: /

        User-agent: Google-Extended
        Allow: /

        Sitemap: https://yourdomain.com/sitemap.xml
        ```

        ### Minimal llms.txt template
        ```
        # My Website

        > One-line description of what your site does.

        ## Pages
        - [Home](https://yourdomain.com/): Main landing page
        - [About](https://yourdomain.com/about): Company background
        - [Blog](https://yourdomain.com/blog): Articles and updates

        ## Usage
        Content may be used for AI training and summarisation with attribution.
        ```
        """)


if __name__ == "__main__":
    main()

# Made with Bob
