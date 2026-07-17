"""
Scoring algorithm for crawlability checks
"""

from typing import Dict, List, Any


class CrawlabilityScorer:
    """Calculate crawlability scores based on check results"""
    
    # Weights for each category
    BOT_ACCESS_WEIGHT = 0.40
    RENDERABILITY_WEIGHT = 0.30
    STRUCTURE_WEIGHT = 0.30
    
    def __init__(self):
        self.results = {
            'bot_access': [],
            'renderability': [],
            'structure': []
        }
    
    def add_check(self, category: str, check_name: str, status: str, 
                  message: str, fix_suggestion: str = None):
        """
        Add a check result
        
        Args:
            category: Category of check (bot_access, renderability, structure)
            check_name: Name of the check
            status: Status (pass, fail, warn)
            message: Description message
            fix_suggestion: Optional fix suggestion for failed checks
        """
        if category not in self.results:
            raise ValueError(f"Invalid category: {category}")
        
        self.results[category].append({
            'name': check_name,
            'status': status,
            'message': message,
            'fix': fix_suggestion
        })
    
    def calculate_category_score(self, category: str) -> float:
        """
        Calculate score for a specific category
        
        Args:
            category: Category to score
            
        Returns:
            Score from 0-100
        """
        if category not in self.results or not self.results[category]:
            return 0.0
        
        checks = self.results[category]
        total_checks = len(checks)
        
        # Count passes and warnings
        passes = sum(1 for c in checks if c['status'] == 'pass')
        warnings = sum(1 for c in checks if c['status'] == 'warn')
        
        # Warnings count as 0.5 of a pass
        score = (passes + (warnings * 0.5)) / total_checks * 100
        
        return round(score, 1)
    
    def calculate_total_score(self) -> Dict[str, Any]:
        """
        Calculate total weighted score
        
        Returns:
            Dict with total score and category subscores
        """
        bot_access_score = self.calculate_category_score('bot_access')
        renderability_score = self.calculate_category_score('renderability')
        structure_score = self.calculate_category_score('structure')
        
        # Calculate weighted total
        total_score = (
            bot_access_score * self.BOT_ACCESS_WEIGHT +
            renderability_score * self.RENDERABILITY_WEIGHT +
            structure_score * self.STRUCTURE_WEIGHT
        )
        
        return {
            'total': round(total_score),
            'bot_access': bot_access_score,
            'renderability': renderability_score,
            'structure': structure_score,
            'grade': self._get_grade(total_score)
        }
    
    def _get_grade(self, score: float) -> str:
        """Get letter grade for score"""
        if score >= 80:
            return '🟢 Good'
        elif score >= 50:
            return '🟡 Needs Improvement'
        else:
            return '🔴 Critical Issues'
    
    def get_all_results(self) -> Dict[str, Any]:
        """
        Get complete results with scores and checks
        
        Returns:
            Dict with scores and all check results
        """
        scores = self.calculate_total_score()
        
        return {
            'scores': scores,
            'checks': self.results,
            'summary': self._generate_summary()
        }
    
    def _generate_summary(self) -> Dict[str, int]:
        """Generate summary statistics"""
        total_checks = sum(len(checks) for checks in self.results.values())
        total_passes = sum(
            sum(1 for c in checks if c['status'] == 'pass')
            for checks in self.results.values()
        )
        total_warnings = sum(
            sum(1 for c in checks if c['status'] == 'warn')
            for checks in self.results.values()
        )
        total_fails = sum(
            sum(1 for c in checks if c['status'] == 'fail')
            for checks in self.results.values()
        )
        
        return {
            'total_checks': total_checks,
            'passes': total_passes,
            'warnings': total_warnings,
            'fails': total_fails
        }
    
    def get_failed_checks(self) -> List[Dict[str, Any]]:
        """Get all failed checks with fix suggestions"""
        failed = []
        
        for category, checks in self.results.items():
            for check in checks:
                if check['status'] == 'fail':
                    failed.append({
                        'category': category,
                        'name': check['name'],
                        'message': check['message'],
                        'fix': check['fix']
                    })
        
        return failed
    
    def get_warnings(self) -> List[Dict[str, Any]]:
        """Get all warning checks"""
        warnings = []
        
        for category, checks in self.results.items():
            for check in checks:
                if check['status'] == 'warn':
                    warnings.append({
                        'category': category,
                        'name': check['name'],
                        'message': check['message'],
                        'fix': check['fix']
                    })
        
        return warnings

# Made with Bob
