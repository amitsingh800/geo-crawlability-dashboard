"""
Parsing utilities for HTML, robots.txt, and other web content
"""

from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Set
import re
import json


class RobotsParser:
    """Parser for robots.txt files"""
    
    def __init__(self, robots_content: str):
        self.content = robots_content
        self.rules = self._parse_robots()
    
    def _parse_robots(self) -> Dict[str, List[str]]:
        """Parse robots.txt into a dictionary of user-agent rules"""
        rules = {}
        current_agent = None
        
        for line in self.content.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse user-agent
            if line.lower().startswith('user-agent:'):
                current_agent = line.split(':', 1)[1].strip()
                if current_agent not in rules:
                    rules[current_agent] = []
            
            # Parse disallow rules
            elif line.lower().startswith('disallow:') and current_agent:
                path = line.split(':', 1)[1].strip()
                if path:  # Only add non-empty disallow rules
                    rules[current_agent].append(path)
        
        return rules
    
    def is_bot_blocked(self, bot_name: str) -> bool:
        """
        Check if a specific bot is blocked
        
        Args:
            bot_name: Name of the bot to check
            
        Returns:
            True if bot is explicitly blocked, False otherwise
        """
        # Check specific bot rules
        if bot_name in self.rules:
            disallows = self.rules[bot_name]
            # If there's a disallow for root path, bot is blocked
            if '/' in disallows:
                return True
        
        # Check wildcard rules
        if '*' in self.rules:
            disallows = self.rules['*']
            if '/' in disallows:
                return True
        
        return False
    
    def get_bot_rules(self, bot_name: str) -> List[str]:
        """Get all disallow rules for a specific bot"""
        rules = []
        
        # Get specific bot rules
        if bot_name in self.rules:
            rules.extend(self.rules[bot_name])
        
        # Get wildcard rules
        if '*' in self.rules:
            rules.extend(self.rules['*'])
        
        return rules
    
    def has_sitemap_reference(self) -> bool:
        """Check if robots.txt references a sitemap"""
        return 'sitemap:' in self.content.lower()

    def get_crawl_delay(self, bot_name: str) -> Optional[float]:
        """
        Return the Crawl-delay value (in seconds) for a given bot or the wildcard.
        Returns None if no crawl-delay is set.
        """
        current_agent = None
        crawl_delays: Dict[str, float] = {}

        for line in self.content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.lower().startswith('user-agent:'):
                current_agent = line.split(':', 1)[1].strip()
            elif line.lower().startswith('crawl-delay:') and current_agent:
                try:
                    crawl_delays[current_agent] = float(line.split(':', 1)[1].strip())
                except ValueError:
                    pass

        # Check specific bot first, then wildcard
        if bot_name in crawl_delays:
            return crawl_delays[bot_name]
        if '*' in crawl_delays:
            return crawl_delays['*']
        return None

    def get_sitemap_urls(self) -> List[str]:
        """Extract sitemap URLs from robots.txt"""
        sitemaps = []
        for line in self.content.split('\n'):
            line = line.strip()
            if line.lower().startswith('sitemap:'):
                sitemap_url = line.split(':', 1)[1].strip()
                sitemaps.append(sitemap_url)
        return sitemaps


class HTMLParser:
    """Parser for HTML content"""
    
    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, 'lxml')
    
    def get_meta_robots(self) -> Optional[str]:
        """Get meta robots tag content"""
        meta_robots = self.soup.find('meta', attrs={'name': 'robots'})
        if meta_robots and meta_robots.get('content'):
            return meta_robots['content'].lower()
        return None
    
    def has_noindex(self) -> bool:
        """Check if page has noindex directive"""
        meta_robots = self.get_meta_robots()
        if meta_robots and 'noindex' in meta_robots:
            return True
        return False
    
    def has_noai(self) -> bool:
        """Check if page has noai directive"""
        meta_robots = self.get_meta_robots()
        if meta_robots and 'noai' in meta_robots:
            return True
        return False
    
    def get_title(self) -> Optional[str]:
        """Get page title"""
        title_tag = self.soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        return None
    
    def get_meta_description(self) -> Optional[str]:
        """Get meta description"""
        meta_desc = self.soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        return None
    
    def get_canonical(self) -> Optional[str]:
        """Get canonical URL"""
        canonical = self.soup.find('link', attrs={'rel': 'canonical'})
        if canonical and canonical.get('href'):
            return canonical['href']
        return None
    
    def get_headings(self) -> Dict[str, List[str]]:
        """Get all headings organized by level"""
        headings = {f'h{i}': [] for i in range(1, 7)}
        
        for level in range(1, 7):
            tags = self.soup.find_all(f'h{level}')
            headings[f'h{level}'] = [tag.get_text().strip() for tag in tags]
        
        return headings
    
    def count_h1_tags(self) -> int:
        """Count number of H1 tags"""
        return len(self.soup.find_all('h1'))
    
    def check_heading_hierarchy(self) -> Dict[str, any]:
        """
        Check if heading hierarchy is logical
        
        Returns:
            Dict with hierarchy analysis
        """
        headings = self.get_headings()
        h1_count = len(headings['h1'])
        
        # Check for single H1
        single_h1 = h1_count == 1
        
        # Check if headings exist
        has_headings = any(len(headings[f'h{i}']) > 0 for i in range(1, 7))
        
        return {
            'single_h1': single_h1,
            'h1_count': h1_count,
            'has_headings': has_headings,
            'headings': headings
        }
    
    def get_json_ld(self) -> List[Dict]:
        """Extract JSON-LD structured data"""
        json_ld_scripts = self.soup.find_all('script', type='application/ld+json')
        structured_data = []
        
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                structured_data.append(data)
            except (json.JSONDecodeError, AttributeError):
                continue
        
        return structured_data
    
    def get_schema_types(self) -> Set[str]:
        """Get all schema.org types present in the page"""
        json_ld_data = self.get_json_ld()
        types = set()
        
        for data in json_ld_data:
            if isinstance(data, dict):
                if '@type' in data:
                    type_value = data['@type']
                    if isinstance(type_value, list):
                        types.update(type_value)
                    else:
                        types.add(type_value)
                
                # Handle @graph structure
                if '@graph' in data and isinstance(data['@graph'], list):
                    for item in data['@graph']:
                        if isinstance(item, dict) and '@type' in item:
                            type_value = item['@type']
                            if isinstance(type_value, list):
                                types.update(type_value)
                            else:
                                types.add(type_value)
        
        return types
    
    def get_visible_text(self) -> str:
        """Get visible text content from the page"""
        # Remove script and style elements
        for script in self.soup(['script', 'style', 'meta', 'link']):
            script.decompose()
        
        # Get text
        text = self.soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def detect_paywall_patterns(self, patterns: List[str]) -> bool:
        """
        Detect paywall patterns in HTML
        
        Args:
            patterns: List of patterns to search for
            
        Returns:
            True if paywall patterns detected
        """
        html_lower = str(self.soup).lower()
        
        for pattern in patterns:
            if pattern.lower() in html_lower:
                return True
        
        return False
    
    def detect_login_required(self, patterns: List[str]) -> bool:
        """
        Detect login requirement patterns
        
        Args:
            patterns: List of patterns to search for
            
        Returns:
            True if login patterns detected
        """
        html_lower = str(self.soup).lower()
        
        for pattern in patterns:
            if pattern.lower() in html_lower:
                return True
        
        # Check for login forms
        login_forms = self.soup.find_all('form', class_=re.compile(r'login|signin|auth', re.I))
        if login_forms:
            return True
        
        return False

    def get_open_graph_tags(self) -> Dict[str, str]:
        """Return a dict of Open Graph property→content pairs present in <head>."""
        og_tags: Dict[str, str] = {}
        for tag in self.soup.find_all('meta', property=re.compile(r'^og:', re.I)):
            prop = tag.get('property', '').lower()
            content = tag.get('content', '')
            if prop and content:
                og_tags[prop] = content
        return og_tags

    def get_twitter_card_tags(self) -> Dict[str, str]:
        """Return a dict of Twitter Card name→content pairs present in <head>."""
        tc_tags: Dict[str, str] = {}
        for tag in self.soup.find_all('meta', attrs={'name': re.compile(r'^twitter:', re.I)}):
            name = tag.get('name', '').lower()
            content = tag.get('content', '')
            if name and content:
                tc_tags[name] = content
        return tc_tags

    def has_hreflang(self) -> bool:
        """Check whether any hreflang link tags are present."""
        return bool(self.soup.find('link', attrs={'rel': 'alternate', 'hreflang': True}))

    def get_lang_attribute(self) -> Optional[str]:
        """Return the lang attribute of the <html> element, or None."""
        html_tag = self.soup.find('html')
        if html_tag:
            return html_tag.get('lang') or html_tag.get('xml:lang')
        return None

    def has_speakable_schema(self) -> bool:
        """Return True if any JSON-LD block declares a 'speakable' property."""
        for data in self.get_json_ld():
            if isinstance(data, dict):
                if 'speakable' in data:
                    return True
                for item in data.get('@graph', []):
                    if isinstance(item, dict) and 'speakable' in item:
                        return True
        return False

    def get_content_type_charset(self) -> Optional[str]:
        """Return the charset declared in <meta charset> or http-equiv Content-Type."""
        # <meta charset="utf-8">
        meta_charset = self.soup.find('meta', charset=True)
        if meta_charset:
            return meta_charset.get('charset', '').lower()
        # <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        meta_ct = self.soup.find('meta', attrs={'http-equiv': re.compile(r'content-type', re.I)})
        if meta_ct:
            content = meta_ct.get('content', '')
            match = re.search(r'charset=([^\s;]+)', content, re.I)
            if match:
                return match.group(1).lower()
        return None

# Made with Bob
