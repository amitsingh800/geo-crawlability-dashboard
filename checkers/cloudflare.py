"""
Cloudflare AI bot blocking detection
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Dict
from utils.scoring import CrawlabilityScorer
from config.bots import CLOUDFLARE_PATTERNS


class CloudflareChecker:
    """Detect Cloudflare AI bot blocking"""
    
    def __init__(self):
        pass
    
    def check_cloudflare_blocking(self, html_content: str, headers: Dict, 
                                   scorer: CrawlabilityScorer) -> Dict:
        """
        Check for Cloudflare AI bot blocking
        
        Args:
            html_content: HTML content of the page
            headers: HTTP response headers
            scorer: Scoring object to add results
            
        Returns:
            Dict with detection results
        """
        results = {
            'detected': False,
            'indicators': []
        }
        
        # Check for cf-mitigated header
        for key, value in headers.items():
            if key.lower() == 'cf-mitigated':
                if 'challenge' in value.lower():
                    results['detected'] = True
                    results['indicators'].append('cf-mitigated header with challenge')
        
        # Check for Cloudflare challenge patterns in HTML
        html_lower = html_content.lower()
        for pattern in CLOUDFLARE_PATTERNS:
            if pattern.lower() in html_lower:
                results['detected'] = True
                results['indicators'].append(f'Challenge pattern: {pattern}')
        
        # Check for Cloudflare cookies in headers
        set_cookie = headers.get('Set-Cookie', '')
        if '__cf_bm' in set_cookie or 'cf_clearance' in set_cookie:
            results['detected'] = True
            results['indicators'].append('Cloudflare cookies detected')
        
        # Add check result
        if results['detected']:
            scorer.add_check(
                'bot_access',
                'Cloudflare AI Blocking',
                'fail',
                f'Cloudflare AI bot blocking detected: {", ".join(results["indicators"])}',
                'Disable Cloudflare AI bot blocking in your Cloudflare dashboard (Security > Bots)'
            )
        else:
            scorer.add_check(
                'bot_access',
                'Cloudflare AI Blocking',
                'pass',
                'No Cloudflare AI bot blocking detected',
                None
            )
        
        return results

# Made with Bob
