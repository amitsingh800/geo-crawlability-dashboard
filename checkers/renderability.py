"""
Renderability checker - compares raw HTML vs rendered content
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Dict, Optional
from utils.parser import HTMLParser
from utils.scoring import CrawlabilityScorer
from config.bots import (
    RENDER_RATIO_CRITICAL, 
    RENDER_RATIO_WARNING,
    PAYWALL_PATTERNS,
    LOGIN_PATTERNS,
    PLAYWRIGHT_TIMEOUT
)


class RenderabilityChecker:
    """Check if content is accessible without JavaScript"""
    
    def __init__(self):
        self.playwright_available = self._check_playwright()
    
    def _check_playwright(self) -> bool:
        """Check if Playwright is available"""
        try:
            from playwright.sync_api import sync_playwright
            return True
        except ImportError:
            return False
    
    def get_rendered_html(self, url: str) -> Optional[str]:
        """
        Get HTML after JavaScript rendering using Playwright
        
        Args:
            url: URL to render
            
        Returns:
            Rendered HTML content or None if failed
        """
        if not self.playwright_available:
            return None
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=PLAYWRIGHT_TIMEOUT, wait_until='networkidle')
                content = page.content()
                browser.close()
                return content
        except Exception as e:
            print(f"Playwright rendering failed: {e}")
            return None
    
    def compare_content(self, raw_html: str, rendered_html: Optional[str], 
                       scorer: CrawlabilityScorer) -> Dict:
        """
        Compare raw HTML vs rendered HTML
        
        Args:
            raw_html: Raw HTML content
            rendered_html: Rendered HTML content (can be None)
            scorer: Scoring object
            
        Returns:
            Dict with comparison results
        """
        results = {
            'render_ratio': 1.0,
            'raw_text_length': 0,
            'rendered_text_length': 0,
            'js_dependent': False
        }
        
        if not rendered_html:
            scorer.add_check(
                'renderability',
                'JavaScript Rendering',
                'warn',
                'Could not perform JavaScript rendering check (Playwright not available)',
                'Install Playwright: pip install playwright && playwright install chromium'
            )
            return results
        
        # Parse both versions
        raw_parser = HTMLParser(raw_html)
        rendered_parser = HTMLParser(rendered_html)
        
        # Get visible text
        raw_text = raw_parser.get_visible_text()
        rendered_text = rendered_parser.get_visible_text()
        
        results['raw_text_length'] = len(raw_text)
        results['rendered_text_length'] = len(rendered_text)
        
        # Calculate ratio
        if results['rendered_text_length'] > 0:
            results['render_ratio'] = results['raw_text_length'] / results['rendered_text_length']
        
        # Determine if content is JS-dependent
        if results['render_ratio'] < RENDER_RATIO_CRITICAL:
            results['js_dependent'] = True
            scorer.add_check(
                'renderability',
                'Content Accessibility',
                'fail',
                f'Critical: Only {results["render_ratio"]:.1%} of content visible without JavaScript',
                'Implement server-side rendering (SSR) or provide static HTML fallback for critical content'
            )
        elif results['render_ratio'] < RENDER_RATIO_WARNING:
            results['js_dependent'] = True
            scorer.add_check(
                'renderability',
                'Content Accessibility',
                'warn',
                f'Warning: Only {results["render_ratio"]:.1%} of content visible without JavaScript',
                'Consider improving static HTML content or implementing progressive enhancement'
            )
        else:
            scorer.add_check(
                'renderability',
                'Content Accessibility',
                'pass',
                f'Good: {results["render_ratio"]:.1%} of content accessible without JavaScript',
                None
            )
        
        return results
    
    def check_paywall(self, html_content: str, scorer: CrawlabilityScorer) -> Dict:
        """
        Check for paywall patterns
        
        Args:
            html_content: HTML content to check
            scorer: Scoring object
            
        Returns:
            Dict with paywall detection results
        """
        results = {
            'detected': False,
            'patterns_found': []
        }
        
        parser = HTMLParser(html_content)
        
        if parser.detect_paywall_patterns(PAYWALL_PATTERNS):
            results['detected'] = True
            scorer.add_check(
                'renderability',
                'Paywall Detection',
                'warn',
                'Paywall patterns detected - content may be restricted for AI crawlers',
                'Ensure AI crawlers can access content, or provide alternative access via structured data'
            )
        else:
            scorer.add_check(
                'renderability',
                'Paywall Detection',
                'pass',
                'No paywall patterns detected',
                None
            )
        
        return results
    
    def check_login_required(self, html_content: str, scorer: CrawlabilityScorer) -> Dict:
        """
        Check for login requirement patterns
        
        Args:
            html_content: HTML content to check
            scorer: Scoring object
            
        Returns:
            Dict with login detection results
        """
        results = {
            'detected': False,
            'patterns_found': []
        }
        
        parser = HTMLParser(html_content)
        
        if parser.detect_login_required(LOGIN_PATTERNS):
            results['detected'] = True
            scorer.add_check(
                'renderability',
                'Login Requirement',
                'fail',
                'Login requirement detected - content not accessible to crawlers',
                'Make content publicly accessible or provide alternative access for crawlers'
            )
        else:
            scorer.add_check(
                'renderability',
                'Login Requirement',
                'pass',
                'No login requirement detected',
                None
            )
        
        return results
    
    def run_all_checks(self, url: str, raw_html: str, scorer: CrawlabilityScorer) -> Dict:
        """Run all renderability checks"""
        
        # Get rendered HTML
        rendered_html = self.get_rendered_html(url)
        
        results = {
            'comparison': self.compare_content(raw_html, rendered_html, scorer),
            'paywall': self.check_paywall(raw_html, scorer),
            'login': self.check_login_required(raw_html, scorer)
        }
        
        return results

# Made with Bob
