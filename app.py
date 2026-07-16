"""
GEO Crawlability Dashboard - Main Streamlit Application
"""

import streamlit as st
import streamlit.components.v1 as components
import sys
import os
import time
from datetime import datetime
from typing import Tuple, Optional

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
<meta property="og:title" content="GEO Crawlability Checker | AI Crawler SEO Audit">
<meta property="og:description" content="Audit your website for AI crawlability, structured data, heading hierarchy, metadata, and bot access signals used by AI crawlers and citation tools.">
<meta property="og:url" content="https://geo-crawlability.streamlit.app/">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "GEO Crawlability Checker",
  "url": "https://geo-crawlability.streamlit.app/",
  "description": "Audit your website for AI crawlability, structured data, heading hierarchy, metadata, and bot access signals used by AI crawlers and citation tools."
}
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
      <div style="font-size:1.4rem;font-weight:800;color:#2e1a47;">Grade {grade}</div>
    </div>""", height=160)


def _score_class(score: int) -> str:
    if score >= 80:
        return "good"
    elif score >= 50:
        return "warn"
    return "crit"


def _score_label(score: int) -> str:
    if score >= 80:
        return "Good"
    elif score >= 50:
        return "Needs Work"
    return "Critical"


def display_category_scores(scores):
    """Display category breakdown as fully inline-styled cards"""
    bot    = scores['bot_access']
    render = scores['renderability']
    struct = scores['structure']

    def score_color(s):
        if s >= 80: return "#16a34a"
        if s >= 50: return "#d97706"
        return "#dc2626"

    def badge_style(s):
        if s >= 80: return "background:#dcfce7;color:#166534;"
        if s >= 50: return "background:#fef9c3;color:#854d0e;"
        return "background:#fee2e2;color:#991b1b;"

    def badge_label(s):
        if s >= 80: return "Good"
        if s >= 50: return "Needs Work"
        return "Critical"

    def card(title, score, detail):
        return f"""
        <div style="background:white;border:1.5px solid #ddd6fe;border-radius:10px;
                    padding:1.1rem;flex:1;min-width:0;">
          <div style="display:flex;justify-content:space-between;
                      align-items:flex-start;margin-bottom:0.7rem;">
            <div style="font-size:0.83rem;font-weight:700;color:#2e1a47;
                        max-width:72%;line-height:1.3;">{title}</div>
            <div style="font-size:1.7rem;font-weight:800;line-height:1;
                        color:{score_color(score)};flex-shrink:0;">{score}</div>
          </div>
          <span style="display:inline-block;padding:0.16rem 0.6rem;border-radius:20px;
                       font-size:0.68rem;font-weight:700;margin-bottom:0.7rem;
                       {badge_style(score)}">{badge_label(score)}</span>
          <div style="height:1px;background:#ede9fe;margin:0.65rem 0;"></div>
          <div style="font-size:0.79rem;color:#57606a;line-height:1.5;">{detail}</div>
        </div>"""

    bot_detail    = "🤖 robots.txt · meta robots · Cloudflare AI block"
    rend_detail   = "🎨 JS dependency · paywall · login walls"
    struct_detail = "📋 Schema.org · Open Graph · headings · sitemap · llms.txt"

    _html_block(f"""
    <div style="font-size:0.68rem;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;
                color:#5b21b6;display:flex;align-items:center;gap:0.5rem;margin:0 0 0.9rem;">
      Category Breakdown
      <span style="flex:1;height:1.5px;background:#ddd6fe;display:inline-block;"></span>
    </div>
    <div style="display:flex;gap:0.9rem;">
      {card("🚫 Bot Access · 40%",          bot,    bot_detail)}
      {card("🎨 Renderability · 30%",        render, rend_detail)}
      {card("📋 Structure &amp; Meta · 30%", struct, struct_detail)}
    </div>""", height=210)


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


def display_detailed_results(results):
    """Display detailed check results by category"""
    st.markdown("## 📊 Detailed Results")
    
    # Bot Access Checks
    with st.expander("## 🚫 Bot Access Checks", expanded=True):
        checks = results['checks']['bot_access']
        if checks:
            for check in checks:
                display_check_result(check)
        else:
            st.info("No bot access checks performed")
    
    # Renderability Checks
    with st.expander("## 🎨 Renderability Checks", expanded=True):
        checks = results['checks']['renderability']
        if checks:
            for check in checks:
                display_check_result(check)
        else:
            st.info("No renderability checks performed")
    
    # Structure Checks
    with st.expander("## 📋 Structure & Metadata Checks", expanded=True):
        checks = results['checks']['structure']
        if checks:
            for check in checks:
                display_check_result(check)
        else:
            st.info("No structure checks performed")


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
        <span style="font-size:0.72rem;font-weight:700;color:rgba(224,210,255,0.88);">Grade {grade}</span>
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
                    st.error(f"❌ Site blocks automated access even with real browser")
                    st.warning("🤖 **Bot Detection Active**: This site uses sophisticated bot protection that detects and blocks automated tools, even when using a real browser engine.")
                    st.info("💡 **What this means**: The site loads fine in Chrome because you're a human user, but blocks automated crawlers (including AI bots) through advanced fingerprinting and behavioral analysis.")
                    
                    # Add critical blocking checks
                    scorer.add_check(
                        'bot_access',
                        'Strict Bot Protection (Timeout)',
                        'fail',
                        'Site blocks ALL automated access including real browsers via timeout mechanisms',
                        'Critical: Disable advanced bot detection or whitelist AI crawler user-agents'
                    )
                    
                    # Add placeholder checks for areas that couldn't be tested
                    scorer.add_check('renderability', 'Content Analysis', 'fail',
                                   'Could not analyze - site blocked access',
                                   'Fix bot protection to enable content analysis')
                    scorer.add_check('structure', 'Metadata Analysis', 'fail',
                                   'Could not analyze - site blocked access',
                                   'Fix bot protection to enable structure analysis')
                    
                    # Calculate partial score and display
                    st.markdown("---")
                    st.markdown("## 📊 Partial Analysis Results")
                    st.warning("⚠️ **Limited Analysis**: Only bot protection could be assessed. Other checks were blocked.")
                    
                    results = scorer.get_all_results()
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    status_detail.empty()
                    final_time = time.time() - start_time
                    timer_display.error(f"⛔ Analysis blocked after {final_time:.1f}s")
                    
                    # Show blocking report
                    st.markdown("## 🚨 Bot Protection Detected")
                    st.error("**Blocking Method**: Strict Timeout Protection (All Access Blocked)")
                    st.markdown("""
                    **Impact**: Site blocks ALL automated access including real browsers
                    - **Severity**: Extreme - Complete inaccessibility to AI crawlers
                    - **Likely System**: Advanced WAF with strict fingerprinting and behavioral analysis
                    - **Score Impact**: Maximum penalty - site is completely inaccessible
                    """)
                    
                    # Show partial score
                    display_score(results['scores'])

                    st.markdown("### ❌ Checks That Could Not Be Performed")
                    st.error("""
                    Due to bot protection blocking, the following could not be analyzed:
                    - ❌ **Renderability Checks**: JavaScript content analysis, paywall detection
                    - ❌ **Structure Checks**: Schema.org, headings, metadata, sitemap
                    - ⚠️ **Bot Access**: Only blocking detection was possible, robots.txt not checked
                    """)
                    
                    st.markdown("---")
                    st.markdown("### 💡 Recommendations")
                    st.info("""
                    **To improve this score:**
                    1. Disable or configure bot detection to allow AI crawlers
                    2. Whitelist specific AI bot user-agents (GPTBot, ClaudeBot, etc.)
                    3. Implement rate limiting instead of complete blocking
                    4. Contact your WAF/CDN provider to adjust bot management settings
                    
                    **Current systems that may be blocking:**
                    - Cloudflare Bot Management
                    - Akamai Bot Manager
                    - PerimeterX
                    - DataDome
                    - Custom WAF rules
                    """)
                    
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
                    st.error(f"❌ Failed to fetch URL even with browser: Site has strong bot protection")
                    st.info("💡 This site actively blocks automated access. Consider:")
                    st.markdown("""
                    - Checking if the site allows AI crawlers in robots.txt
                    - Contacting the site owner for API access
                    - Using the site's official API if available
                    """)
                    # Add severe blocking check
                    scorer.add_check(
                        'bot_access',
                        'Strict Bot Protection',
                        'fail',
                        'Site blocks ALL automated access including real browsers - extremely restrictive',
                        'Critical: Site is completely inaccessible to AI crawlers. Contact site owner to whitelist AI bot user-agents'
                    )
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
        timer_display.success(f"✅ Analysis complete in {final_time:.1f}s")

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

        # Summary strip (includes score badge — no separate score card needed)
        display_summary(results, url=url, elapsed=final_time)

        # Category cards
        display_category_scores(results['scores'])

        # Detailed check results inside expanders
        display_detailed_results(results)

        # Priority fixes as styled cards
        failed_checks = scorer.get_failed_checks()
        if failed_checks:
            fixes_html = ""
            for check in failed_checks:
                fix_line = ""
                if check['fix']:
                    fix_line = (f'<div style="margin-top:0.4rem;font-size:0.84rem;color:#57606a;">'
                                f'<strong style="color:#2e1a47;">Fix:</strong> {check["fix"]}</div>')
                fixes_html += f"""
                <div style="background:white;border:1.5px solid #ddd6fe;
                            border-left:4px solid #dc2626;border-radius:10px;
                            padding:1.1rem 1.3rem;margin-bottom:0.8rem;">
                  <div style="display:flex;justify-content:space-between;
                              align-items:center;margin-bottom:0.45rem;gap:0.8rem;">
                    <span style="font-size:0.9rem;font-weight:700;color:#2e1a47;">
                      {check['name']}
                    </span>
                    <span style="font-size:0.68rem;font-weight:700;padding:0.16rem 0.6rem;
                                 border-radius:20px;white-space:nowrap;flex-shrink:0;
                                 background:#fee2e2;color:#991b1b;">Critical</span>
                  </div>
                  <div style="font-size:0.84rem;color:#57606a;line-height:1.6;">
                    <strong style="color:#2e1a47;">Issue:</strong> {check['message']}
                  </div>
                  {fix_line}
                </div>"""

            card_height = 140 * len(failed_checks) + 60
            _html_block(f"""
            <div style="font-size:0.68rem;font-weight:800;letter-spacing:0.1em;
                        text-transform:uppercase;color:#5b21b6;display:flex;
                        align-items:center;gap:0.5rem;margin:0 0 0.9rem;">
              Priority Fixes
              <span style="flex:1;height:1.5px;background:#ddd6fe;display:inline-block;"></span>
            </div>
            {fixes_html}""", height=card_height)
        
    except Exception as e:
        st.error(f"❌ An error occurred during analysis: {str(e)}")
        st.exception(e)


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
