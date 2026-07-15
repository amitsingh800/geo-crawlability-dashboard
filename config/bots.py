"""
Configuration for AI bot user agents to check
"""

# AI bots to check in robots.txt and meta tags
AI_BOTS = [
    # OpenAI
    'GPTBot',
    'ChatGPT-User',
    'OAI-SearchBot',
    # Anthropic
    'ClaudeBot',
    'anthropic-ai',
    'Claude-Web',
    # Google
    'Google-Extended',
    'Googlebot',
    # Perplexity
    'PerplexityBot',
    'DuckAssistBot',
    # Meta
    'meta-externalagent',
    # Common Crawl (used by many AI training pipelines)
    'CCBot',
    # Amazon
    'Amazonbot',
    # Apple
    'Applebot-Extended',
    # Bytedance
    'Bytespider',
    # You.com
    'YouBot',
    # Cohere
    'cohere-ai',
    # Diffbot
    'Diffbot',
    # Timpi
    'Timpibot',
]

# User agent for our crawler
USER_AGENT = 'Mozilla/5.0 (compatible; GEO-Crawlability-Checker/1.0; +https://github.com/your-repo)'

# Timeout settings (in seconds)
REQUEST_TIMEOUT = 60  # Increased from 30 to handle slow sites
PLAYWRIGHT_TIMEOUT = 90000  # milliseconds (90 seconds)

# Renderability thresholds
RENDER_RATIO_CRITICAL = 0.5  # Below this is critical
RENDER_RATIO_WARNING = 0.7   # Below this is warning

# Paywall detection patterns
PAYWALL_PATTERNS = [
    'paywall',
    'subscribe',
    'subscription',
    'premium-content',
    'member-only',
    'login-required',
    'sign-in-to-read',
    'unlock-article',
    'continue-reading'
]

# Login detection patterns
LOGIN_PATTERNS = [
    'login',
    'sign-in',
    'signin',
    'log-in',
    'authentication-required',
    'auth-wall'
]

# Cloudflare challenge patterns
CLOUDFLARE_PATTERNS = [
    'Just a moment',
    'Checking your browser',
    'cf-browser-verification',
    'cf_clearance',
    '__cf_bm'
]

# Made with Bob
