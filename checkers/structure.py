"""
Structure and metadata checker
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Dict, Set
from utils.parser import HTMLParser
from utils.crawler import Crawler
from utils.scoring import CrawlabilityScorer


class StructureChecker:
    """Check page structure and metadata"""
    
    def __init__(self, url: str, crawler: Crawler):
        self.url = url
        self.crawler = crawler
        self.base_url = self._get_base_url(url)
        self.is_streamlit_app = self._is_streamlit_app_url(url)
    
    def _get_base_url(self, url: str) -> str:
        """Extract base URL from full URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _is_streamlit_app_url(self, url: str) -> bool:
        """Return True when the target URL is a Streamlit-hosted app shell."""
        from urllib.parse import urlparse
        hostname = (urlparse(url).hostname or '').lower()
        return hostname.endswith('.streamlit.app')
    
    def check_schema_org(self, html_content: str, scorer: CrawlabilityScorer) -> Dict:
        """
        Check for Schema.org structured data
        
        Args:
            html_content: HTML content
            scorer: Scoring object
            
        Returns:
            Dict with schema detection results
        """
        results = {
            'has_schema': False,
            'types': set()
        }
        
        parser = HTMLParser(html_content)
        schema_types = parser.get_schema_types()
        
        if schema_types:
            results['has_schema'] = True
            results['types'] = schema_types
            
            # Check for common valuable types
            valuable_types = {'Organization', 'Article', 'FAQPage', 'HowTo', 'Product', 'WebPage'}
            found_valuable = schema_types.intersection(valuable_types)
            
            if found_valuable:
                scorer.add_check(
                    'structure',
                    'Schema.org Structured Data',
                    'pass',
                    f'Found valuable schema types: {", ".join(found_valuable)}',
                    None
                )
            else:
                scorer.add_check(
                    'structure',
                    'Schema.org Structured Data',
                    'warn',
                    f'Schema.org present but no high-value types found: {", ".join(schema_types)}',
                    'Add Organization, Article, FAQPage, HowTo, or Product schema'
                )
        else:
            status = 'warn' if self.is_streamlit_app else 'fail'
            message = 'No Schema.org structured data found in raw HTML response'
            fix = 'Add JSON-LD structured data to the server-rendered <head> section (e.g., Organization or Article schema)'
            if self.is_streamlit_app:
                fix = 'Streamlit app shells do not expose JSON-LD in raw HTML. Use a custom domain/app host with server-rendered metadata if this URL must self-score.'
            scorer.add_check(
                'structure',
                'Schema.org Structured Data',
                status,
                message,
                fix
            )
        
        return results
    
    def check_heading_hierarchy(self, html_content: str, scorer: CrawlabilityScorer) -> Dict:
        """
        Check heading hierarchy
        
        Args:
            html_content: HTML content
            scorer: Scoring object
            
        Returns:
            Dict with heading analysis
        """
        parser = HTMLParser(html_content)
        hierarchy = parser.check_heading_hierarchy()
        
        results = {
            'single_h1': hierarchy['single_h1'],
            'h1_count': hierarchy['h1_count'],
            'has_headings': hierarchy['has_headings']
        }
        
        # Check for single H1
        if hierarchy['single_h1']:
            scorer.add_check(
                'structure',
                'H1 Tag',
                'pass',
                'Single H1 tag found (best practice)',
                None
            )
        elif hierarchy['h1_count'] == 0:
            status = 'warn' if self.is_streamlit_app else 'fail'
            fix = 'Add a single H1 tag for the main page heading'
            if self.is_streamlit_app:
                fix = 'Streamlit app shells may not expose heading tags in raw HTML. Use a server-rendered host if this URL must self-score.'
            scorer.add_check(
                'structure',
                'H1 Tag',
                status,
                'No H1 tag found',
                fix
            )
        else:
            scorer.add_check(
                'structure',
                'H1 Tag',
                'warn',
                f'Multiple H1 tags found ({hierarchy["h1_count"]})',
                'Use only one H1 tag for the main heading, convert others to H2 or lower'
            )
        
        # Check for heading presence
        if hierarchy['has_headings']:
            scorer.add_check(
                'structure',
                'Heading Structure',
                'pass',
                'Page has heading structure',
                None
            )
        else:
            status = 'warn' if self.is_streamlit_app else 'fail'
            fix = 'Add proper heading hierarchy (H1-H6) to structure content'
            if self.is_streamlit_app:
                fix = 'Streamlit app shells may not expose heading markup in raw HTML. Use a server-rendered host if this URL must self-score.'
            scorer.add_check(
                'structure',
                'Heading Structure',
                status,
                'No headings found on page',
                fix
            )
        
        return results
    
    def check_title_tag(self, html_content: str, scorer: CrawlabilityScorer) -> Dict:
        """
        Check title tag
        
        Args:
            html_content: HTML content
            scorer: Scoring object
            
        Returns:
            Dict with title analysis
        """
        parser = HTMLParser(html_content)
        title = parser.get_title()
        
        results = {
            'has_title': False,
            'title': None,
            'length': 0,
            'optimal': False
        }
        
        if title:
            results['has_title'] = True
            results['title'] = title
            results['length'] = len(title)
            
            # Check length (optimal: 30-60 characters)
            if 30 <= results['length'] <= 60:
                results['optimal'] = True
                scorer.add_check(
                    'structure',
                    'Title Tag',
                    'pass',
                    f'Title tag present and optimal length ({results["length"]} chars)',
                    None
                )
            elif results['length'] < 30:
                scorer.add_check(
                    'structure',
                    'Title Tag',
                    'warn',
                    f'Title tag too short ({results["length"]} chars, recommended: 30-60)',
                    'Expand title to 30-60 characters for better SEO'
                )
            else:
                scorer.add_check(
                    'structure',
                    'Title Tag',
                    'warn',
                    f'Title tag too long ({results["length"]} chars, recommended: 30-60)',
                    'Shorten title to 30-60 characters'
                )
        else:
            status = 'warn' if self.is_streamlit_app else 'fail'
            fix = 'Add <title> tag in <head> section'
            if self.is_streamlit_app:
                fix = 'Streamlit app shells may not expose a page-specific <title> in the raw HTML fetched by this checker.'
            scorer.add_check(
                'structure',
                'Title Tag',
                status,
                'No title tag found',
                fix
            )
        
        return results
    
    def check_meta_description(self, html_content: str, scorer: CrawlabilityScorer) -> Dict:
        """
        Check meta description
        
        Args:
            html_content: HTML content
            scorer: Scoring object
            
        Returns:
            Dict with meta description analysis
        """
        parser = HTMLParser(html_content)
        description = parser.get_meta_description()
        
        results = {
            'has_description': False,
            'description': None,
            'length': 0,
            'optimal': False
        }
        
        if description:
            results['has_description'] = True
            results['description'] = description
            results['length'] = len(description)
            
            # Check length (optimal: 120-160 characters)
            if 120 <= results['length'] <= 160:
                results['optimal'] = True
                scorer.add_check(
                    'structure',
                    'Meta Description',
                    'pass',
                    f'Meta description present and optimal length ({results["length"]} chars)',
                    None
                )
            elif results['length'] < 120:
                scorer.add_check(
                    'structure',
                    'Meta Description',
                    'warn',
                    f'Meta description too short ({results["length"]} chars, recommended: 120-160)',
                    'Expand meta description to 120-160 characters'
                )
            else:
                scorer.add_check(
                    'structure',
                    'Meta Description',
                    'warn',
                    f'Meta description too long ({results["length"]} chars, recommended: 120-160)',
                    'Shorten meta description to 120-160 characters'
                )
        else:
            status = 'warn' if self.is_streamlit_app else 'fail'
            fix = 'Add <meta name="description" content="..."> in <head> section'
            if self.is_streamlit_app:
                fix = 'Streamlit app shells may not expose a page-specific meta description in the raw HTML fetched by this checker.'
            scorer.add_check(
                'structure',
                'Meta Description',
                status,
                'No meta description found',
                fix
            )
        
        return results
    
    def check_canonical(self, html_content: str, scorer: CrawlabilityScorer) -> Dict:
        """
        Check canonical tag
        
        Args:
            html_content: HTML content
            scorer: Scoring object
            
        Returns:
            Dict with canonical analysis
        """
        parser = HTMLParser(html_content)
        canonical = parser.get_canonical()
        
        results = {
            'has_canonical': False,
            'canonical_url': None
        }
        
        if canonical:
            results['has_canonical'] = True
            results['canonical_url'] = canonical
            scorer.add_check(
                'structure',
                'Canonical Tag',
                'pass',
                'Canonical tag present',
                None
            )
        else:
            scorer.add_check(
                'structure',
                'Canonical Tag',
                'warn',
                'No canonical tag found',
                'Add <link rel="canonical" href="..."> to specify preferred URL'
            )
        
        return results
    
    def check_sitemap(self, scorer: CrawlabilityScorer) -> Dict:
        """
        Check for sitemap.xml
        
        Args:
            scorer: Scoring object
            
        Returns:
            Dict with sitemap detection results
        """
        results = {
            'has_sitemap': False,
            'accessible': False
        }
        
        sitemap_content, error = self.crawler.fetch_sitemap(self.base_url)
        
        if sitemap_content and not error:
            results['has_sitemap'] = True
            results['accessible'] = True
            scorer.add_check(
                'structure',
                'Sitemap.xml',
                'pass',
                'sitemap.xml found and accessible',
                None
            )
        else:
            scorer.add_check(
                'structure',
                'Sitemap.xml',
                'warn',
                'sitemap.xml not found or inaccessible',
                'Create sitemap.xml and place it at the root of your domain'
            )
        
        return results
    
    def check_llms_txt(self, scorer: CrawlabilityScorer) -> Dict:
        """
        Check for llms.txt — awards a small bonus point for sites that have adopted
        the emerging convention of exposing an AI-readable summary at /llms.txt.
        """
        results = {'has_llms_txt': False}

        llms_content, error = self.crawler.fetch_llms_txt(self.base_url)

        if llms_content and not error:
            results['has_llms_txt'] = True
            scorer.add_check(
                'structure',
                'llms.txt',
                'pass',
                'llms.txt found — site provides an AI-readable summary document',
                None
            )
        else:
            scorer.add_check(
                'structure',
                'llms.txt',
                'warn',
                'llms.txt not found — add /llms.txt to help AI assistants understand your site',
                'Create /llms.txt with a concise plain-text description of your site, its pages, '
                'and any usage permissions. See https://llmstxt.org for the spec.'
            )

        return results

    def check_open_graph(self, html_content: str, scorer: CrawlabilityScorer) -> Dict:
        """Check Open Graph and Twitter Card social-preview metadata."""
        from utils.parser import HTMLParser
        parser = HTMLParser(html_content)

        og_tags = parser.get_open_graph_tags()
        tc_tags = parser.get_twitter_card_tags()

        required_og = {'og:title', 'og:description', 'og:url'}
        present_og = set(og_tags.keys())
        missing_og = required_og - present_og

        results = {
            'has_og': bool(og_tags),
            'has_twitter_card': bool(tc_tags),
            'missing_og': list(missing_og),
        }

        if not missing_og:
            scorer.add_check(
                'structure',
                'Open Graph Tags',
                'pass',
                f'Core Open Graph tags present ({", ".join(sorted(present_og & required_og))})',
                None
            )
        elif og_tags:
            scorer.add_check(
                'structure',
                'Open Graph Tags',
                'warn',
                f'Open Graph present but missing: {", ".join(sorted(missing_og))}',
                'Add the missing og: meta tags so AI assistants and social previews show rich context'
            )
        else:
            status = 'warn' if self.is_streamlit_app else 'fail'
            fix = 'Add <meta property="og:title">, <meta property="og:description">, and <meta property="og:url"> to <head>'
            if self.is_streamlit_app:
                fix = 'Streamlit app shells may not expose Open Graph tags in the raw HTML fetched by this checker.'
            scorer.add_check(
                'structure',
                'Open Graph Tags',
                status,
                'No Open Graph tags found — AI citation tools use og:title / og:description for context',
                fix
            )

        if tc_tags:
            scorer.add_check(
                'structure',
                'Twitter Card Tags',
                'pass',
                f'Twitter Card tags present ({len(tc_tags)} tags)',
                None
            )
        else:
            scorer.add_check(
                'structure',
                'Twitter Card Tags',
                'warn',
                'No Twitter Card tags found',
                'Add <meta name="twitter:card" content="summary_large_image"> and twitter:title/description'
            )

        return results

    def check_language_signals(self, html_content: str, scorer: CrawlabilityScorer) -> Dict:
        """Check language declaration and hreflang for international sites."""
        from utils.parser import HTMLParser
        parser = HTMLParser(html_content)

        lang = parser.get_lang_attribute()
        has_hreflang = parser.has_hreflang()

        results = {'lang': lang, 'has_hreflang': has_hreflang}

        if lang:
            scorer.add_check(
                'structure',
                'Language Declaration',
                'pass',
                f'HTML lang attribute set to "{lang}" — helps AI understand content language',
                None
            )
        else:
            fix = 'Add lang="en" (or appropriate BCP-47 code) to the <html> tag'
            if self.is_streamlit_app:
                fix = 'Streamlit app shells may not expose a custom lang attribute in the raw HTML fetched by this checker.'
            scorer.add_check(
                'structure',
                'Language Declaration',
                'warn',
                'No lang attribute on <html> element',
                fix
            )

        if has_hreflang:
            scorer.add_check(
                'structure',
                'Hreflang Tags',
                'pass',
                'Hreflang alternate links found — correct international signals for AI',
                None
            )
        # hreflang is optional for single-language sites; no penalty if absent

        return results

    def check_ai_signals(self, html_content: str, scorer: CrawlabilityScorer) -> Dict:
        """
        Check for schema types that improve AI Overview / featured-snippet eligibility:
        FAQPage, HowTo, speakable, and charset declaration.
        """
        from utils.parser import HTMLParser
        parser = HTMLParser(html_content)

        schema_types = parser.get_schema_types()
        has_faq = 'FAQPage' in schema_types
        has_howto = 'HowTo' in schema_types
        has_speakable = parser.has_speakable_schema()
        charset = parser.get_content_type_charset()

        results = {
            'has_faq_schema': has_faq,
            'has_howto_schema': has_howto,
            'has_speakable': has_speakable,
            'charset': charset,
        }

        # FAQ / HowTo schema
        aio_types = [t for t in ('FAQPage', 'HowTo') if t in schema_types]
        if aio_types:
            scorer.add_check(
                'structure',
                'AI Overview Schema',
                'pass',
                f'High-value AIO schema found: {", ".join(aio_types)} — increases eligibility for AI-generated answers',
                None
            )
        else:
            scorer.add_check(
                'structure',
                'AI Overview Schema',
                'warn',
                'No FAQPage or HowTo schema detected',
                'Add FAQPage or HowTo JSON-LD to Q&A / instructional content to improve AI citation likelihood'
            )

        # Speakable
        if has_speakable:
            scorer.add_check(
                'structure',
                'Speakable Schema',
                'pass',
                'speakable property found — content optimised for voice/AI assistants',
                None
            )
        else:
            scorer.add_check(
                'structure',
                'Speakable Schema',
                'warn',
                'No speakable schema detected',
                'Add a speakable property to your Article/WebPage schema to flag the most AI-readable sections'
            )

        # Charset
        if charset and charset in ('utf-8', 'utf8'):
            scorer.add_check(
                'structure',
                'Charset Declaration',
                'pass',
                f'Charset declared as "{charset}" — ensures correct text encoding for AI parsers',
                None
            )
        elif charset:
            scorer.add_check(
                'structure',
                'Charset Declaration',
                'warn',
                f'Charset declared as "{charset}" — UTF-8 is strongly preferred',
                'Set <meta charset="utf-8"> to ensure maximum compatibility with AI crawlers'
            )
        else:
            fix = 'Add <meta charset="utf-8"> as the first tag inside <head>'
            if self.is_streamlit_app:
                fix = 'Streamlit app shells may not expose a custom charset tag in the raw HTML fetched by this checker.'
            scorer.add_check(
                'structure',
                'Charset Declaration',
                'warn',
                'No charset declaration found',
                fix
            )

        return results

    def run_all_checks(self, html_content: str, scorer: CrawlabilityScorer) -> Dict:
        """Run all structure checks"""
        results = {
            'schema': self.check_schema_org(html_content, scorer),
            'headings': self.check_heading_hierarchy(html_content, scorer),
            'title': self.check_title_tag(html_content, scorer),
            'description': self.check_meta_description(html_content, scorer),
            'canonical': self.check_canonical(html_content, scorer),
            'sitemap': self.check_sitemap(scorer),
            'llms_txt': self.check_llms_txt(scorer),
            'open_graph': self.check_open_graph(html_content, scorer),
            'language': self.check_language_signals(html_content, scorer),
            'ai_signals': self.check_ai_signals(html_content, scorer),
        }

        return results

# Made with Bob
