# GEO Crawlability Dashboard

A Streamlit-based dashboard that analyses websites for AI crawler accessibility, renderability, and SEO structure, providing a 0–100 score with actionable recommendations.

## Features

### Bot Access Checks (40% weight)
- ✅ `robots.txt` parsing for AI bot restrictions
- ✅ `Crawl-delay` detection (warns if > 5s, fails if > 10s)
- ✅ Detects blocks against 20 AI bots:
  - **OpenAI**: GPTBot, ChatGPT-User, OAI-SearchBot
  - **Anthropic**: ClaudeBot, Claude-Web, anthropic-ai
  - **Google**: Googlebot, Google-Extended
  - **Perplexity**: PerplexityBot, DuckAssistBot
  - **Meta**: meta-externalagent
  - **Common Crawl**: CCBot
  - **Amazon**: Amazonbot
  - **Apple**: Applebot-Extended
  - **ByteDance**: Bytespider
  - **You.com**: YouBot
  - **Cohere**: cohere-ai
  - **Diffbot**: Diffbot
  - **Timpi**: Timpibot
- ✅ Cloudflare AI-blocking detection (`cf-mitigated` header, challenge pages, CF cookies)
- ✅ `X-Robots-Tag` header analysis (noindex, noai)
- ✅ Meta robots tag parsing (noindex, noai)

### Renderability Checks (30% weight)
- ✅ Raw HTML vs rendered HTML comparison (Playwright headless Chromium)
- ✅ JavaScript-dependency detection (content ratio analysis)
- ✅ Paywall pattern identification
- ✅ Login gate identification

### Structure & Metadata Checks (30% weight)
- ✅ JSON-LD / Schema.org validation (Organisation, Article, FAQPage, HowTo, Product, WebPage)
- ✅ Heading hierarchy analysis (H1–H6)
- ✅ Title tag validation (optimal: 30–60 chars)
- ✅ Meta description validation (optimal: 120–160 chars)
- ✅ Canonical tag presence
- ✅ Sitemap.xml detection
- ✅ `llms.txt` detection
- ✅ Open Graph tags (`og:title`, `og:description`, `og:url`)
- ✅ Twitter Card tags
- ✅ Language declaration (`<html lang="">`) and hreflang
- ✅ AI signal schema: FAQPage / HowTo, Speakable, charset declaration

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
1. Enter a website URL or just the name (e.g., `google` or `example.com`)
2. Click **🔍 Analyze Website**
3. View the overall score (0–100) with traffic light indicator at the top
4. Review the 6 category cards and detailed checks
5. Follow actionable fix suggestions for failed checks

### Smart URL Detection
The dashboard automatically finds the best matching URL:
- Type `google` → Finds `https://google.com`
- Type `bbc` → Finds `https://www.bbc.co.uk`
- Type `example.com` → Tries `https://example.com`, `https://www.example.com`, etc.
- Full URLs work too: `https://example.com`

## Scoring System

| Score | Grade | Meaning |
|---|---|---|
| 80–100 | 🟢 Good | Well optimised for AI crawlers |
| 50–79 | 🟡 Needs Improvement | Some issues to address |
| 0–49 | 🔴 Critical Issues | Major accessibility problems |

### Score Breakdown
- **Bot Access**: 40% of total score
- **Renderability**: 30% of total score
- **Structure / Metadata**: 30% of total score

### Category Score Formula
```
Category Score = (Passes + Warnings × 0.5) / Total Checks × 100
Total Score    = (Bot Access × 0.40) + (Renderability × 0.30) + (Structure × 0.30)
```

Warnings count as half a pass, so they penalise the score but do not zero it out.

## Architecture

```
geo-crawlability-dashboard/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── packages.txt              # System packages (Chromium)
├── checkers/                 # Individual check modules
│   ├── bot_access.py        # robots.txt, meta robots, X-Robots-Tag, Crawl-delay
│   ├── renderability.py     # HTML rendering comparison, paywall/login detection
│   ├── structure.py         # Metadata, schema, OG tags, language, AI signals
│   └── cloudflare.py        # Cloudflare bot-blocking detection
├── utils/                    # Utility modules
│   ├── crawler.py           # HTTP request utilities (retry, SSL, redirects)
│   ├── parser.py            # HTML / robots.txt parsing
│   └── scoring.py           # Weighted scoring algorithm
└── config/                   # Configuration
    └── bots.py              # AI bot user-agent list, timeouts, detection patterns
```

## Technical Details

### Dependencies

| Package | Purpose |
|---|---|
| Streamlit | Web UI framework |
| Requests | HTTP client for fetching pages |
| BeautifulSoup4 | HTML parsing |
| lxml | XML / HTML processing |
| Playwright | Headless Chromium for rendering |
| validators | URL validation |
| urllib3 | Low-level HTTP utilities |

### Checks Performed

#### robots.txt Analysis
Parses `robots.txt` to check if any of the 20 monitored AI bots are explicitly disallowed, and checks `Crawl-delay` values that may throttle crawler throughput.

#### Cloudflare Detection
Identifies Cloudflare AI bot blocking by checking:
- Response headers (`cf-mitigated: challenge`)
- Challenge page HTML patterns
- Cloudflare cookies (`__cf_bm`, `cf_clearance`)

#### Renderability Test
Compares raw HTTP response HTML with Playwright-rendered HTML to detect:
- Content hidden behind JavaScript (SPA / dynamic loading)
- Paywalls and login gates

#### Schema.org Validation
Checks for high-value structured data types:
- Organisation, Article, FAQPage, HowTo, Product, WebPage

#### Open Graph & Twitter Card
Checks for social-preview metadata (`og:title`, `og:description`, `og:url`, `twitter:card`), which AI citation tools use for context.

#### Language & Internationalisation
Checks for `<html lang="">` attribute and `hreflang` alternate links.

#### AI Signal Checks
- **FAQPage / HowTo schema** — increases eligibility for AI-generated answers and AI Overviews
- **Speakable schema** — flags content optimised for voice / AI assistants
- **Charset declaration** — ensures UTF-8 encoding for correct AI text parsing

### Fallback Strategy
When a site returns a 403 or times out, the analyser automatically retries using Playwright (headless Chromium). If that also fails, partial results are returned with appropriate fail scores and fix recommendations.

## Deployment

### Quick Deploy (Easiest — FREE)

Deploy to Streamlit Community Cloud in 3 steps:

```bash
# 1. Push to GitHub
git push -u origin main

# 2. Go to https://share.streamlit.io/
# 3. Click "New app" and select your repository
```

Your app will be live at: `https://YOUR_USERNAME-geo-crawlability-dashboard.streamlit.app`

### Other Deployment Options

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides on:
- **Streamlit Cloud** (FREE, recommended)
- **Railway** ($5 credit/month)
- **Render** (FREE tier)
- **Google Cloud Run** (pay-per-use)
- **DigitalOcean** ($5/month)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License — feel free to use this project for any purpose.

## Support

For issues or questions, please open an issue on GitHub.

---

**Made with ❤️ for better AI crawler accessibility**
