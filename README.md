# GEO Crawlability Dashboard

A Streamlit-based dashboard that analyzes websites for AI crawler accessibility, renderability, and SEO structure, providing a 0-100 score with actionable recommendations.

## Features

### Bot Access Checks (40% weight)
- ✅ robots.txt parsing for AI bot restrictions
- ✅ Detects blocks against: GPTBot, ClaudeBot, ChatGPT-User, anthropic-ai, PerplexityBot, Google-Extended, CCBot, Amazonbot, Applebot-Extended
- ✅ Cloudflare AI-blocking detection
- ✅ X-Robots-Tag header analysis
- ✅ Meta robots tag parsing

### Renderability Checks (30% weight)
- ✅ Raw HTML vs rendered HTML comparison
- ✅ JavaScript-dependency detection
- ✅ Paywall/login gate identification

### Structure & Metadata Checks (30% weight)
- ✅ JSON-LD / Schema.org validation
- ✅ Heading hierarchy analysis
- ✅ Title tag and meta description validation
- ✅ Canonical tag presence
- ✅ Sitemap.xml detection
- ✅ llms.txt detection (informational)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd geo-crawlability-dashboard
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install chromium
```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

### How to Use
1. Enter a website URL or just the name (e.g., "google" or "example.com")
2. Click "🔍 Analyze Website"
3. View the overall score (0-100) with traffic light indicator at the top
4. Review category scores and detailed checks
5. Follow actionable fix suggestions for failed checks

### Smart URL Detection
The dashboard automatically finds the best matching URL:
- Type `google` → Finds `https://google.com`
- Type `bbc` → Finds `https://www.bbc.co.uk`
- Type `example.com` → Tries `https://example.com`, `https://www.example.com`, etc.
- Full URLs work too: `https://example.com`

## Scoring System

- **0-49** 🔴 Critical issues - Major accessibility problems
- **50-79** 🟡 Needs improvement - Some issues to address
- **80-100** 🟢 Good - Well optimized for AI crawlers

### Score Breakdown
- **Bot Access**: 40% of total score
- **Renderability**: 30% of total score
- **Structure/Metadata**: 30% of total score

## Architecture

```
geo-crawlability-dashboard/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── checkers/                 # Individual check modules
│   ├── bot_access.py        # AI bot access checks
│   ├── renderability.py     # HTML rendering comparison
│   ├── structure.py         # Metadata & schema validation
│   └── cloudflare.py        # Cloudflare detection
├── utils/                    # Utility modules
│   ├── crawler.py           # HTTP request utilities
│   ├── parser.py            # HTML/robots.txt parsing
│   └── scoring.py           # Scoring algorithm
└── config/                   # Configuration
    └── bots.py              # AI bot user-agent list
```

## Technical Details

### Dependencies
- **Streamlit**: Web UI framework
- **Requests**: HTTP client for fetching pages
- **BeautifulSoup4**: HTML parsing
- **Playwright**: Headless browser for rendering
- **lxml**: XML/HTML processing
- **validators**: URL validation

### Checks Performed

#### robots.txt Analysis
Parses robots.txt to check if AI bots are explicitly disallowed from crawling the site.

#### Cloudflare Detection
Identifies if Cloudflare's AI bot blocking is enabled by checking:
- Response headers (`cf-mitigated`)
- Challenge pages
- Cloudflare cookies

#### Renderability Test
Compares raw HTML content with JavaScript-rendered content to detect:
- Content hidden behind JavaScript
- Single-page applications (SPAs)
- Dynamic content loading

#### Schema.org Validation
Checks for structured data types:
- Organization
- Article
- FAQPage
- HowTo
- Product

## Deployment

### Quick Deploy (Easiest - FREE)

Deploy to Streamlit Community Cloud in 3 steps:

```bash
# 1. Run the deployment helper
./deploy.sh

# 2. Go to https://share.streamlit.io/
# 3. Click "New app" and select your repository
```

Your app will be live at: `https://YOUR_USERNAME-geo-crawlability-dashboard.streamlit.app`

### Other Deployment Options

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides on:
- **Streamlit Cloud** (FREE, recommended)
- **Railway** ($5 credit/month)
- **Render** (FREE tier)
- **Heroku** (FREE tier)
- **Google Cloud Run** (Pay-per-use)
- **DigitalOcean** ($5/month)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for any purpose.

## Support

For issues or questions, please open an issue on GitHub.

---

**Made with ❤️ for better AI crawler accessibility**