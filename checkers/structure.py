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
    
    def _get_base_url(self, url: str) -> str:
        """Extract base URL from full URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
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
            scorer.add_check(
                'structure',
                'Schema.org Structured Data',
                'fail',
                'No Schema.org structured data found',
                'Add JSON-LD structured data to <head> section (e.g., Organization or Article schema)'
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
            scorer.add_check(
                'structure',
                'H1 Tag',
                'fail',
                'No H1 tag found',
                'Add a single H1 tag for the main page heading'
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
            scorer.add_check(
                'structure',
                'Heading Structure',
                'fail',
                'No headings found on page',
                'Add proper heading hierarchy (H1-H6) to structure content'
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
            scorer.add_check(
                'structure',
                'Title Tag',
                'fail',
                'No title tag found',
                'Add <title> tag in <head> section'
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
            scorer.add_check(
                'structure',
                'Meta Description',
                'fail',
                'No meta description found',
                'Add <meta name="description" content="..."> in <head> section'
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
        Check for llms.txt (informational only)
        
        Args:
            scorer: Scoring object
            
        Returns:
            Dict with llms.txt detection results
        """
        results = {
            'has_llms_txt': False
        }
        
        llms_content, error = self.crawler.fetch_llms_txt(self.base_url)
        
        if llms_content and not error:
            results['has_llms_txt'] = True
            # Note: This is informational only, not scored
            scorer.add_check(
                'structure',
                'llms.txt (Informational)',
                'pass',
                'llms.txt found (emerging practice, not a ranking factor)',
                None
            )
        else:
            # Don't penalize for missing llms.txt
            scorer.add_check(
                'structure',
                'llms.txt (Informational)',
                'pass',
                'llms.txt not found (optional, not required)',
                None
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
            'llms_txt': self.check_llms_txt(scorer)
        }
        
        return results

# Made with Bob
