"""
Bot access checker - validates AI bot accessibility
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Dict, List, Tuple
from utils.crawler import Crawler
from utils.parser import RobotsParser, HTMLParser
from utils.scoring import CrawlabilityScorer
from config.bots import AI_BOTS


class BotAccessChecker:
    """Check if AI bots can access the website"""
    
    def __init__(self, url: str, crawler: Crawler):
        self.url = url
        self.crawler = crawler
        self.base_url = self._get_base_url(url)
    
    def _get_base_url(self, url: str) -> str:
        """Extract base URL from full URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def check_robots_txt(self, scorer: CrawlabilityScorer) -> Dict:
        """Check robots.txt for AI bot restrictions"""
        results = {
            'found': False,
            'blocked_bots': [],
            'has_sitemap': False
        }
        
        # Fetch robots.txt
        robots_content, error = self.crawler.fetch_robots_txt(self.base_url)
        
        if error or not robots_content:
            scorer.add_check(
                'bot_access',
                'robots.txt',
                'warn',
                f'robots.txt not found or inaccessible: {error}',
                'Create a robots.txt file at the root of your domain'
            )
            return results
        
        results['found'] = True
        
        # Parse robots.txt
        parser = RobotsParser(robots_content)
        
        # Check each AI bot
        blocked_bots = []
        for bot in AI_BOTS:
            if parser.is_bot_blocked(bot):
                blocked_bots.append(bot)
        
        results['blocked_bots'] = blocked_bots
        
        # Add checks for each bot
        if blocked_bots:
            for bot in blocked_bots:
                scorer.add_check(
                    'bot_access',
                    f'{bot} Access',
                    'fail',
                    f'{bot} is blocked in robots.txt',
                    f'Add "User-agent: {bot}\\nAllow: /" to robots.txt'
                )
        else:
            scorer.add_check(
                'bot_access',
                'AI Bot Access',
                'pass',
                'No AI bots are explicitly blocked in robots.txt',
                None
            )
        
        # Check for sitemap reference
        results['has_sitemap'] = parser.has_sitemap_reference()
        
        if results['has_sitemap']:
            scorer.add_check(
                'bot_access',
                'Sitemap Reference',
                'pass',
                'robots.txt references sitemap',
                None
            )
        else:
            from urllib.parse import urlparse
            parsed = urlparse(self.base_url)
            sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
            scorer.add_check(
                'bot_access',
                'Sitemap Reference',
                'pass',
                'No sitemap reference in robots.txt — not required, but recommended',
                f'Optionally add "Sitemap: {sitemap_url}" to robots.txt to help crawlers discover pages faster'
            )

        # Check Crawl-delay — a high delay throttles AI crawlers significantly
        crawl_delay = parser.get_crawl_delay('*')
        if crawl_delay is not None:
            if crawl_delay > 10:
                scorer.add_check(
                    'bot_access',
                    'Crawl-delay',
                    'fail',
                    f'Crawl-delay set to {crawl_delay}s — severely throttles AI crawlers',
                    'Lower Crawl-delay to 1–5 seconds or remove it to allow faster AI indexing'
                )
            elif crawl_delay > 5:
                scorer.add_check(
                    'bot_access',
                    'Crawl-delay',
                    'warn',
                    f'Crawl-delay set to {crawl_delay}s — may slow AI crawler discovery',
                    'Consider lowering Crawl-delay to ≤5 seconds for faster AI indexing'
                )
            else:
                scorer.add_check(
                    'bot_access',
                    'Crawl-delay',
                    'pass',
                    f'Crawl-delay set to {crawl_delay}s — acceptable for AI crawlers',
                    None
                )
        # No crawl-delay is fine; no check needed

        return results
    
    def check_meta_robots(self, html_content: str, scorer: CrawlabilityScorer) -> Dict:
        """Check meta robots tags"""
        results = {
            'has_noindex': False,
            'has_noai': False
        }
        
        parser = HTMLParser(html_content)
        
        # Check for noindex
        if parser.has_noindex():
            results['has_noindex'] = True
            scorer.add_check(
                'bot_access',
                'Meta Robots - noindex',
                'fail',
                'Page has noindex directive in meta robots tag',
                'Remove "noindex" from <meta name="robots" content="..."> tag'
            )
        else:
            scorer.add_check(
                'bot_access',
                'Meta Robots - noindex',
                'pass',
                'No noindex directive found',
                None
            )
        
        # Check for noai
        if parser.has_noai():
            results['has_noai'] = True
            scorer.add_check(
                'bot_access',
                'Meta Robots - noai',
                'fail',
                'Page has noai directive blocking AI crawlers',
                'Remove "noai" from <meta name="robots" content="..."> tag'
            )
        else:
            scorer.add_check(
                'bot_access',
                'Meta Robots - noai',
                'pass',
                'No noai directive found',
                None
            )
        
        return results
    
    def check_x_robots_tag(self, headers: Dict, scorer: CrawlabilityScorer) -> Dict:
        """Check X-Robots-Tag HTTP header"""
        results = {
            'has_header': False,
            'has_noindex': False,
            'has_noai': False
        }
        
        # Check for X-Robots-Tag header (case-insensitive)
        x_robots = None
        for key, value in headers.items():
            if key.lower() == 'x-robots-tag':
                x_robots = value.lower()
                results['has_header'] = True
                break
        
        if not x_robots:
            scorer.add_check(
                'bot_access',
                'X-Robots-Tag Header',
                'pass',
                'No restrictive X-Robots-Tag header found',
                None
            )
            return results
        
        # Check for noindex
        if 'noindex' in x_robots:
            results['has_noindex'] = True
            scorer.add_check(
                'bot_access',
                'X-Robots-Tag - noindex',
                'fail',
                'X-Robots-Tag header contains noindex',
                'Remove "noindex" from X-Robots-Tag HTTP header'
            )
        
        # Check for noai
        if 'noai' in x_robots:
            results['has_noai'] = True
            scorer.add_check(
                'bot_access',
                'X-Robots-Tag - noai',
                'fail',
                'X-Robots-Tag header contains noai',
                'Remove "noai" from X-Robots-Tag HTTP header'
            )
        
        if not results['has_noindex'] and not results['has_noai']:
            scorer.add_check(
                'bot_access',
                'X-Robots-Tag Header',
                'pass',
                'X-Robots-Tag header present but not restrictive',
                None
            )
        
        return results
    
    def run_all_checks(self, html_content: str, headers: Dict, scorer: CrawlabilityScorer) -> Dict:
        """Run all bot access checks"""
        results = {
            'robots_txt': self.check_robots_txt(scorer),
            'meta_robots': self.check_meta_robots(html_content, scorer),
            'x_robots_tag': self.check_x_robots_tag(headers, scorer)
        }
        
        return results

# Made with Bob
