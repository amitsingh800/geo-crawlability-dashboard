"""
Test script for GEO Crawlability Dashboard
Run this to verify the installation and test basic functionality
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from utils.crawler import Crawler
        print("✅ utils.crawler imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import utils.crawler: {e}")
        return False
    
    try:
        from utils.parser import RobotsParser, HTMLParser
        print("✅ utils.parser imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import utils.parser: {e}")
        return False
    
    try:
        from utils.scoring import CrawlabilityScorer
        print("✅ utils.scoring imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import utils.scoring: {e}")
        return False
    
    try:
        from checkers.bot_access import BotAccessChecker
        print("✅ checkers.bot_access imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import checkers.bot_access: {e}")
        return False
    
    try:
        from checkers.cloudflare import CloudflareChecker
        print("✅ checkers.cloudflare imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import checkers.cloudflare: {e}")
        return False
    
    try:
        from checkers.renderability import RenderabilityChecker
        print("✅ checkers.renderability imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import checkers.renderability: {e}")
        return False
    
    try:
        from checkers.structure import StructureChecker
        print("✅ checkers.structure imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import checkers.structure: {e}")
        return False
    
    try:
        from config.bots import AI_BOTS
        print("✅ config.bots imported successfully")
        print(f"   Found {len(AI_BOTS)} AI bots configured")
    except ImportError as e:
        print(f"❌ Failed to import config.bots: {e}")
        return False
    
    return True


def test_dependencies():
    """Test that all required dependencies are installed"""
    print("\nTesting dependencies...")
    
    dependencies = [
        'streamlit',
        'requests',
        'bs4',  # beautifulsoup4
        'lxml',
        'validators'
    ]
    
    all_installed = True
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} installed")
        except ImportError:
            print(f"❌ {dep} NOT installed")
            all_installed = False
    
    # Check Playwright separately
    try:
        from playwright.sync_api import sync_playwright
        print("✅ playwright installed")
    except ImportError:
        print("⚠️  playwright NOT installed (optional for renderability checks)")
    
    return all_installed


def test_basic_functionality():
    """Test basic functionality"""
    print("\nTesting basic functionality...")
    
    try:
        from utils.crawler import Crawler
        from utils.scoring import CrawlabilityScorer
        
        # Test crawler
        crawler = Crawler()
        print("✅ Crawler initialized")
        
        # Test scorer
        scorer = CrawlabilityScorer()
        scorer.add_check('bot_access', 'Test Check', 'pass', 'Test message', None)
        results = scorer.get_all_results()
        print("✅ Scorer working correctly")
        print(f"   Test score: {results['scores']['total']}/100")
        
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def test_robots_parser():
    """Test robots.txt parsing"""
    print("\nTesting robots.txt parser...")
    
    try:
        from utils.parser import RobotsParser
        
        # Sample robots.txt
        robots_content = """
User-agent: GPTBot
Disallow: /

User-agent: *
Allow: /
        """
        
        parser = RobotsParser(robots_content)
        is_blocked = parser.is_bot_blocked('GPTBot')
        
        if is_blocked:
            print("✅ Robots parser correctly detected blocked bot")
        else:
            print("❌ Robots parser failed to detect blocked bot")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Robots parser test failed: {e}")
        return False


def test_html_parser():
    """Test HTML parsing"""
    print("\nTesting HTML parser...")
    
    try:
        from utils.parser import HTMLParser
        
        # Sample HTML
        html_content = """
        <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="Test description">
            <meta name="robots" content="index, follow">
        </head>
        <body>
            <h1>Main Heading</h1>
            <h2>Subheading</h2>
            <p>Content</p>
        </body>
        </html>
        """
        
        parser = HTMLParser(html_content)
        
        title = parser.get_title()
        if title == "Test Page":
            print("✅ HTML parser correctly extracted title")
        else:
            print(f"❌ HTML parser failed to extract title (got: {title})")
            return False
        
        h1_count = parser.count_h1_tags()
        if h1_count == 1:
            print("✅ HTML parser correctly counted H1 tags")
        else:
            print(f"❌ HTML parser failed to count H1 tags (got: {h1_count})")
            return False
        
        return True
    except Exception as e:
        print(f"❌ HTML parser test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("GEO Crawlability Dashboard - Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Dependencies", test_dependencies()))
    results.append(("Basic Functionality", test_basic_functionality()))
    results.append(("Robots Parser", test_robots_parser()))
    results.append(("HTML Parser", test_html_parser()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The dashboard is ready to use.")
        print("\nTo run the dashboard:")
        print("  streamlit run app.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nMake sure you have:")
        print("  1. Activated the virtual environment")
        print("  2. Installed all dependencies: pip install -r requirements.txt")
        print("  3. Installed Playwright browsers: playwright install chromium")
        return 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
