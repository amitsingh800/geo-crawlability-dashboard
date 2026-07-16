"""
HTTP crawler utilities for fetching web pages and resources
"""

import requests
from urllib.parse import urljoin, urlparse
from typing import Dict, Optional, Tuple
from config.bots import USER_AGENT, REQUEST_TIMEOUT
import urllib3

# Disable SSL warnings for sites with certificate issues
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Crawler:
    """HTTP crawler for fetching web pages"""
    
    def __init__(self):
        self.session = requests.Session()
        # More realistic browser headers to avoid bot detection
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Cache-Control': 'max-age=0'
        })
        # Add session configuration for better compatibility
        self.session.max_redirects = 10
    
    def fetch_url(self, url: str, allow_redirects: bool = True, retry_count: int = 3) -> Tuple[Optional[str], Optional[requests.Response], Optional[str]]:
        """
        Fetch a URL and return content, response object, and error message
        
        Args:
            url: URL to fetch
            allow_redirects: Whether to follow redirects
            retry_count: Number of retries for failed requests
            
        Returns:
            Tuple of (content, response, error_message)
        """
        last_error = None
        
        for attempt in range(retry_count):
            try:
                response = self.session.get(
                    url,
                    timeout=REQUEST_TIMEOUT,
                    allow_redirects=allow_redirects,
                    verify=False  # Skip SSL verification for problematic sites
                )
                response.raise_for_status()
                return response.text, response, None
            except requests.exceptions.Timeout:
                last_error = f"Request timed out after {REQUEST_TIMEOUT} seconds"
                if attempt < retry_count - 1:
                    continue
            except requests.exceptions.SSLError as e:
                last_error = f"SSL certificate error: {str(e)}"
                if attempt < retry_count - 1:
                    continue
            except requests.exceptions.ConnectionError as e:
                last_error = f"Failed to connect to the server: {str(e)}"
                if attempt < retry_count - 1:
                    continue
            except requests.exceptions.HTTPError as e:
                # Don't retry on HTTP errors (403, 404, etc.)
                return None, None, f"HTTP error: {e.response.status_code} - {e.response.reason}"
            except requests.exceptions.RequestException as e:
                last_error = f"Request failed: {str(e)}"
                if attempt < retry_count - 1:
                    continue
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                if attempt < retry_count - 1:
                    continue
        
        return None, None, last_error
    
    def fetch_robots_txt(self, base_url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Fetch robots.txt for a given base URL
        
        Args:
            base_url: Base URL of the website
            
        Returns:
            Tuple of (robots.txt content, error_message)
        """
        parsed = urlparse(base_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        content, response, error = self.fetch_url(robots_url, allow_redirects=False)
        
        if error:
            return None, error
        
        if response and response.status_code == 404:
            return None, "robots.txt not found (404)"
        
        return content, None
    
    def fetch_sitemap(self, base_url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Fetch sitemap.xml for a given base URL
        
        Args:
            base_url: Base URL of the website
            
        Returns:
            Tuple of (sitemap content, error_message)
        """
        parsed = urlparse(base_url)
        sitemap_urls = [
            f"{parsed.scheme}://{parsed.netloc}/sitemap.xml",
            f"{parsed.scheme}://{parsed.netloc}/app/static/sitemap.xml",
        ]

        for sitemap_url in sitemap_urls:
            content, response, error = self.fetch_url(sitemap_url, allow_redirects=False)
            if content and not error:
                return content, None
            if response and response.status_code != 404:
                return None, error

        return None, "sitemap.xml not found (404)"
    
    def fetch_llms_txt(self, base_url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Fetch llms.txt for a given base URL
        
        Args:
            base_url: Base URL of the website
            
        Returns:
            Tuple of (llms.txt content, error_message)
        """
        parsed = urlparse(base_url)
        llms_urls = [
            f"{parsed.scheme}://{parsed.netloc}/llms.txt",
            f"{parsed.scheme}://{parsed.netloc}/app/static/llms.txt",
        ]

        for llms_url in llms_urls:
            content, response, error = self.fetch_url(llms_url, allow_redirects=False)
            if content and not error:
                return content, None
            if response and response.status_code != 404:
                return None, error

        return None, "llms.txt not found (404)"
    
    def get_response_headers(self, url: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Get response headers for a URL
        
        Args:
            url: URL to check
            
        Returns:
            Tuple of (headers dict, error_message)
        """
        _, response, error = self.fetch_url(url)
        
        if error:
            return None, error
        
        if response:
            return dict(response.headers), None
        
        return None, "No response received"
    
    def check_url_accessible(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a URL is accessible
        
        Args:
            url: URL to check
            
        Returns:
            Tuple of (is_accessible, error_message)
        """
        _, response, error = self.fetch_url(url)
        
        if error:
            return False, error
        
        if response and response.status_code == 200:
            return True, None
        
        return False, f"Unexpected status code: {response.status_code if response else 'unknown'}"

# Made with Bob
