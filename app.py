"""
GEO Crawlability Dashboard - Main Streamlit Application
"""

import streamlit as st
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

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .score-container {
        text-align: center;
        padding: 2rem;
        border-radius: 10px;
        margin: 2rem 0;
    }
    .score-good {
        background-color: #d4edda;
        border: 2px solid #28a745;
    }
    .score-warning {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
    }
    .score-critical {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
    }
    .score-number {
        font-size: 4rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .category-score {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
        background-color: #f8f9fa;
    }
    .check-pass {
        color: #28a745;
        font-weight: bold;
    }
    .check-warn {
        color: #ffc107;
        font-weight: bold;
    }
    .check-fail {
        color: #dc3545;
        font-weight: bold;
    }
    .fix-suggestion {
        background-color: #e7f3ff;
        padding: 0.5rem;
        border-left: 3px solid #0066cc;
        margin-top: 0.5rem;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)


def display_header():
    """Display the main header"""
    st.markdown('<div class="main-header">🤖 GEO Crawlability Checker</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Analyze your website\'s accessibility to AI crawlers</div>', unsafe_allow_html=True)


def display_score(scores):
    """Display the overall score with traffic light indicator"""
    total_score = scores['total']
    grade = scores['grade']
    
    # Determine CSS class based on score
    if total_score >= 80:
        css_class = "score-good"
    elif total_score >= 50:
        css_class = "score-warning"
    else:
        css_class = "score-critical"
    
    st.markdown(f"""
    <div class="score-container {css_class}">
        <div style="font-size: 1.5rem;">{grade}</div>
        <div class="score-number">{total_score}</div>
        <div style="font-size: 1.2rem;">Overall Crawlability Score</div>
    </div>
    """, unsafe_allow_html=True)


def display_category_scores(scores):
    """Display category breakdown scores"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🚫 Bot Access")
        st.markdown(f"**Score: {scores['bot_access']}/100**")
        st.progress(scores['bot_access'] / 100)
        st.caption("Weight: 40%")
    
    with col2:
        st.markdown("### 🎨 Renderability")
        st.markdown(f"**Score: {scores['renderability']}/100**")
        st.progress(scores['renderability'] / 100)
        st.caption("Weight: 30%")
    
    with col3:
        st.markdown("### 📋 Structure")
        st.markdown(f"**Score: {scores['structure']}/100**")
        st.progress(scores['structure'] / 100)
        st.caption("Weight: 30%")


def display_check_result(check):
    """Display a single check result"""
    status = check['status']
    name = check['name']
    message = check['message']
    fix = check.get('fix')
    
    # Status icon and color
    if status == 'pass':
        icon = "✅"
        css_class = "check-pass"
    elif status == 'warn':
        icon = "⚠️"
        css_class = "check-warn"
    else:
        icon = "❌"
        css_class = "check-fail"
    
    st.markdown(f"{icon} **{name}**: <span class='{css_class}'>{status.upper()}</span>", unsafe_allow_html=True)
    st.markdown(f"_{message}_")
    
    if fix:
        st.markdown(f'<div class="fix-suggestion">💡 Fix: {fix}</div>', unsafe_allow_html=True)
    
    st.markdown("---")


def display_detailed_results(results):
    """Display detailed check results by category"""
    st.markdown("## 📊 Detailed Results")
    
    # Bot Access Checks
    with st.expander("🚫 Bot Access Checks", expanded=True):
        checks = results['checks']['bot_access']
        if checks:
            for check in checks:
                display_check_result(check)
        else:
            st.info("No bot access checks performed")
    
    # Renderability Checks
    with st.expander("🎨 Renderability Checks", expanded=True):
        checks = results['checks']['renderability']
        if checks:
            for check in checks:
                display_check_result(check)
        else:
            st.info("No renderability checks performed")
    
    # Structure Checks
    with st.expander("📋 Structure & Metadata Checks", expanded=True):
        checks = results['checks']['structure']
        if checks:
            for check in checks:
                display_check_result(check)
        else:
            st.info("No structure checks performed")


def display_summary(results):
    """Display summary statistics"""
    summary = results['summary']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Checks", summary['total_checks'])
    with col2:
        st.metric("Passed", summary['passes'], delta=None, delta_color="normal")
    with col3:
        st.metric("Warnings", summary['warnings'], delta=None, delta_color="off")
    with col4:
        st.metric("Failed", summary['fails'], delta=None, delta_color="inverse")


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


def analyze_url(url: str, score_placeholder):
    """
    Main analysis function
    
    Args:
        url: URL to analyze
        score_placeholder: Streamlit placeholder for displaying score at top
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
                    
                    # Display partial score at the top (in the placeholder)
                    with score_placeholder.container():
                        display_score(results['scores'])
                        st.markdown("---")
                    
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
            st.markdown("## 🚨 Bot Protection Detected")
            
            if blocking_reason == "timeout":
                st.error("**Blocking Method**: Timeout/Delay Mechanism")
                st.markdown("""
                **Impact**: Site deliberately delays responses to automated requests
                - **Severity**: High - AI crawlers will experience slow or failed access
                - **Likely System**: Rate limiting, bot detection, or WAF
                - **Score Impact**: -10 points from Bot Access category
                """)
            elif blocking_reason == "403_forbidden":
                st.error("**Blocking Method**: 403 Forbidden (Active Bot Detection)")
                st.markdown("""
                **Impact**: Site actively blocks automated requests but allows real browsers
                - **Severity**: Critical - AI crawlers are explicitly blocked
                - **Likely System**: Cloudflare Bot Management, Akamai, PerimeterX, or DataDome
                - **Score Impact**: -15 points from Bot Access category
                """)
            elif blocking_reason == "403_strict":
                st.error("**Blocking Method**: Strict Bot Protection (All Automated Access Blocked)")
                st.markdown("""
                **Impact**: Site blocks ALL automated access including real browsers
                - **Severity**: Extreme - Complete inaccessibility to AI crawlers
                - **Likely System**: Advanced WAF with strict fingerprinting
                - **Score Impact**: -25 points from Bot Access category
                """)
            
            if used_fallback:
                st.info("ℹ️ **Note**: Analysis completed using browser fallback method. Some checks may be limited.")
            
            st.markdown("---")
        
        # Display score at the top (in the placeholder)
        with score_placeholder.container():
            display_score(results['scores'])
            st.markdown("---")
        
        # Summary statistics
        display_summary(results)
        
        st.markdown("---")
        
        # Category scores
        display_category_scores(results['scores'])
        
        st.markdown("---")
        
        # Detailed results
        display_detailed_results(results)
        
        # Failed checks summary
        failed_checks = scorer.get_failed_checks()
        if failed_checks:
            st.markdown("## 🔧 Priority Fixes")
            st.warning(f"You have {len(failed_checks)} failed checks that need attention:")
            for i, check in enumerate(failed_checks, 1):
                st.markdown(f"**{i}. {check['name']}**")
                st.markdown(f"   - Issue: {check['message']}")
                if check['fix']:
                    st.markdown(f"   - Fix: {check['fix']}")
        
    except Exception as e:
        st.error(f"❌ An error occurred during analysis: {str(e)}")
        st.exception(e)


def main():
    """Main application"""
    display_header()
    
    # URL input
    url = st.text_input(
        "Enter website URL to analyze:",
        placeholder="https://example.com",
        help="Enter the full URL including https://"
    )
    
    # Analyze button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        analyze_button = st.button("🔍 Analyze Website", type="primary", use_container_width=True)
    
    # Create a placeholder for the score display (shown after analysis)
    score_placeholder = st.empty()
    
    # Perform analysis
    if analyze_button:
        if not url:
            st.warning("⚠️ Please enter a URL or website name")
        else:
            # Find best matching URL
            with st.spinner("🔍 Finding best URL match..."):
                working_url, message = find_best_url_match(url)
            
            if working_url is None:
                # No URL found
                st.error(message)
                st.info("💡 **Tips:**")
                st.markdown("""
                - Enter a full domain: `example.com` or `www.example.com`
                - Enter a brand name: `google`, `bbc`, `amazon`
                - Include protocol if needed: `https://example.com`
                """)
            else:
                # Show what URL was found if different from input
                if message:
                    st.success(message)
                
                # Validate the URL
                if not validators.url(working_url):
                    st.error("❌ Invalid URL format")
                else:
                    # Proceed with analysis
                    analyze_url(working_url, score_placeholder)
    
    # Information section
    with st.expander("ℹ️ About This Tool"):
        st.markdown("""
        ### What does this tool check?
        
        **Bot Access (40% weight)**
        - robots.txt restrictions for AI bots
        - Cloudflare AI bot blocking
        - Meta robots and X-Robots-Tag headers
        
        **Renderability (30% weight)**
        - JavaScript-dependent content
        - Paywall detection
        - Login requirements
        
        **Structure & Metadata (30% weight)**
        - Schema.org structured data
        - Heading hierarchy
        - Title and meta description
        - Canonical tags
        - Sitemap presence
        
        ### Scoring
        - **80-100** 🟢 Good - Well optimized
        - **50-79** 🟡 Needs Improvement - Some issues
        - **0-49** 🔴 Critical Issues - Major problems
        
        ### AI Bots Checked
        GPTBot, ClaudeBot, ChatGPT-User, anthropic-ai, PerplexityBot, 
        Google-Extended, CCBot, Amazonbot, Applebot-Extended
        """)


if __name__ == "__main__":
    main()

# Made with Bob
