# GEO Crawlability Dashboard - Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE LAYER                                │
│                         (Streamlit Web Application)                          │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                           app.py                                     │   │
│  │  • Main Streamlit Application                                       │   │
│  │  • URL Input & Validation                                           │   │
│  │  • Smart URL Detection (auto-complete domains)                      │   │
│  │  • Progress Tracking & Timer                                        │   │
│  │  • Score Display (Traffic Light System)                            │   │
│  │  • Results Visualization                                            │   │
│  │  • Error Handling & Fallback Logic                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
└────────────────────────────────────┼──────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATION LAYER                                  │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    analyze_url() Function                            │  │
│  │  • Coordinates all checks in sequence                               │  │
│  │  • Manages progress updates                                         │  │
│  │  • Handles timeout/403 fallback to browser method                   │  │
│  │  • Aggregates results from all checkers                             │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                          │
└────────────────────────────────────┼──────────────────────────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CHECKER MODULES LAYER                               │
│                                                                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │  BotAccessChecker│  │RenderabilityCheck│  │ StructureChecker │          │
│  │                  │  │                  │  │                  │          │
│  │ • robots.txt     │  │ • Raw vs Render  │  │ • Schema.org     │          │
│  │ • 20 AI bots     │  │ • JS dependency  │  │ • Open Graph     │          │
│  │ • Crawl-delay    │  │ • Paywall detect │  │ • Twitter Card   │          │
│  │ • Meta robots    │  │ • Login gates    │  │ • Headings       │          │
│  │   (noindex/noai) │  │ • Playwright     │  │ • Title/Meta     │          │
│  │ • X-Robots-Tag   │  │                  │  │ • Canonical      │          │
│  │   (noindex/noai) │  │                  │  │ • Sitemap        │          │
│  │                  │  │                  │  │ • llms.txt       │          │
│  │                  │  │                  │  │ • Language/lang  │          │
│  │                  │  │                  │  │ • hreflang       │          │
│  │                  │  │                  │  │ • AI signals     │          │
│  │                  │  │                  │  │   (FAQ/HowTo,    │          │
│  │                  │  │                  │  │    Speakable,    │          │
│  │                  │  │                  │  │    charset)      │          │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘          │
│           │                     │                     │                      │
│  ┌────────▼─────────────────────▼─────────────────────▼─────────┐          │
│  │              CloudflareChecker                                │          │
│  │  • Detects Cloudflare AI bot blocking                        │          │
│  │  • Checks cf-mitigated headers                               │          │
│  │  • Identifies challenge pages                                │          │
│  └──────────────────────────────────────────────────────────────┘          │
│                                    │                                          │
└────────────────────────────────────┼──────────────────────────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          UTILITY LAYER                                       │
│                                                                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │    Crawler       │  │     Parser       │  │     Scorer       │          │
│  │                  │  │                  │  │                  │          │
│  │ • HTTP requests  │  │ • HTML parsing   │  │ • Score calc     │          │
│  │ • robots.txt     │  │ • robots.txt     │  │ • Weighted avg   │          │
│  │ • Sitemap fetch  │  │ • Schema extract │  │ • Grade assign   │          │
│  │ • Retry logic    │  │ • Meta tags      │  │ • Results agg    │          │
│  │ • SSL handling   │  │ • Heading parse  │  │ • Check tracking │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CONFIGURATION LAYER                                    │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         config/bots.py                               │  │
│  │  • AI_BOTS list (GPTBot, ClaudeBot, etc.)                           │  │
│  │  • USER_AGENT configuration                                         │  │
│  │  • Timeout settings (REQUEST_TIMEOUT, PLAYWRIGHT_TIMEOUT)           │  │
│  │  • Renderability thresholds                                         │  │
│  │  • Detection patterns (paywall, login, Cloudflare)                  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       EXTERNAL DEPENDENCIES                                  │
│                                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Streamlit   │  │   Requests   │  │ BeautifulSoup│  │  Playwright  │   │
│  │  (Web UI)    │  │ (HTTP Client)│  │ (HTML Parser)│  │  (Browser)   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│  │    lxml      │  │  validators  │  │   urllib3    │                      │
│  │ (XML Parser) │  │(URL Validate)│  │(HTTP Utils)  │                      │
│  └──────────────┘  └──────────────┘  └──────────────┘                      │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌─────────────┐
│  User Input │
│   (URL)     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│  Smart URL Detection    │
│  • Try variations       │
│  • Find working URL     │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Fetch Main Page        │
│  • HTTP request         │
│  • Handle timeouts      │
│  • Fallback to browser  │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Bot Access Checks      │
│  • robots.txt (40%)     │
│  • Meta tags            │
│  • Headers              │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Cloudflare Check       │
│  • Detect blocking      │
│  • Challenge pages      │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Renderability Checks   │
│  • Raw vs Rendered (30%)│
│  • JS dependency        │
│  • Paywall/Login        │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Structure Checks       │
│  • Schema.org (30%)     │
│  • Metadata             │
│  • Sitemap              │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Score Calculation      │
│  • Weighted average     │
│  • Grade assignment     │
│  • 0-100 scale          │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Results Display        │
│  • Traffic light score  │
│  • Category breakdown   │
│  • Detailed checks      │
│  • Fix suggestions      │
└─────────────────────────┘
```

## Component Responsibilities

### 1. User Interface Layer (`app.py`)
- **Purpose**: Streamlit web application providing user interaction
- **Key Functions**:
  - `main()`: Entry point, handles URL input
  - `analyze_url()`: Orchestrates entire analysis workflow
  - `find_best_url_match()`: Smart URL detection and validation
  - `display_*()`: Various display functions for results
- **Features**:
  - Real-time progress tracking with timer
  - Traffic light scoring system (🟢 🟡 🔴)
  - Expandable detailed results
  - Actionable fix suggestions

### 2. Checker Modules

#### BotAccessChecker (`checkers/bot_access.py`)
- **Weight**: 40% of total score
- **Checks**:
  - `robots.txt` parsing for AI bot restrictions
  - `Crawl-delay` detection (warn > 5s, fail > 10s)
  - Meta robots tags (`noindex`, `noai`)
  - `X-Robots-Tag` headers (`noindex`, `noai`)
- **AI Bots Monitored (20 total)**:
  - OpenAI: GPTBot, ChatGPT-User, OAI-SearchBot
  - Anthropic: ClaudeBot, Claude-Web, anthropic-ai
  - Google: Googlebot, Google-Extended
  - Perplexity: PerplexityBot, DuckAssistBot
  - Meta: meta-externalagent
  - Common Crawl: CCBot
  - Amazon: Amazonbot
  - Apple: Applebot-Extended
  - ByteDance: Bytespider
  - You.com: YouBot
  - Cohere: cohere-ai
  - Diffbot: Diffbot
  - Timpi: Timpibot

#### CloudflareChecker (`checkers/cloudflare.py`)
- **Purpose**: Detect Cloudflare AI bot blocking
- **Detection Methods**:
  - `cf-mitigated` header
  - Challenge page patterns
  - Cloudflare cookies

#### RenderabilityChecker (`checkers/renderability.py`)
- **Weight**: 30% of total score
- **Checks**:
  - Raw HTML vs JavaScript-rendered content comparison
  - Content ratio analysis
  - Paywall detection
  - Login gate identification
- **Technology**: Uses Playwright for browser rendering

#### StructureChecker (`checkers/structure.py`)
- **Weight**: 30% of total score
- **Checks**:
  - Schema.org structured data (JSON-LD) — Organisation, Article, FAQPage, HowTo, Product, WebPage
  - Heading hierarchy (H1–H6)
  - Title tag (optimal: 30–60 chars) and meta description (optimal: 120–160 chars)
  - Canonical tags
  - Sitemap.xml presence
  - `llms.txt` detection
  - Open Graph tags (`og:title`, `og:description`, `og:url`)
  - Twitter Card tags
  - Language declaration (`<html lang="">`) and hreflang
  - AI signals: FAQPage / HowTo schema, Speakable schema, charset declaration

### 3. Utility Layer

#### Crawler (`utils/crawler.py`)
- **Purpose**: HTTP client for fetching web resources
- **Features**:
  - Realistic browser headers to avoid detection
  - Retry logic with exponential backoff
  - SSL certificate handling
  - Redirect following
  - Timeout management (60s default)

#### Parser (`utils/parser.py`)
- **Purpose**: Parse HTML and robots.txt content
- **Components**:
  - `RobotsParser`: Parse robots.txt rules
  - `HTMLParser`: Extract metadata, schema, headings
- **Technology**: BeautifulSoup4 + lxml

#### Scorer (`utils/scoring.py`)
- **Purpose**: Calculate crawlability scores
- **Algorithm**:
  - Weighted average: Bot Access (40%) + Renderability (30%) + Structure (30%)
  - Per-check scoring: pass (+points), warn (partial), fail (0 points)
  - Grade assignment: A (80-100), B (60-79), C (40-59), D (20-39), F (0-19)

### 4. Configuration Layer (`config/bots.py`)
- AI bot user-agent list
- Timeout configurations
- Detection patterns (paywall, login, Cloudflare)
- Renderability thresholds

## Error Handling & Fallback Strategy

```
┌─────────────────────┐
│  Initial Request    │
└──────┬──────────────┘
       │
       ▼
   ┌───────┐
   │Success?│──Yes──► Continue Analysis
   └───┬───┘
       │ No
       ▼
   ┌─────────────┐
   │ Timeout or  │
   │ 403 Error?  │
   └───┬─────────┘
       │ Yes
       ▼
┌──────────────────────┐
│ Fallback: Playwright │
│ (Real Browser)       │
└──────┬───────────────┘
       │
       ▼
   ┌───────┐
   │Success?│──Yes──► Continue with Warning
   └───┬───┘           (Bot Detection Noted)
       │ No
       ▼
┌──────────────────────┐
│ Partial Analysis     │
│ • Bot blocking: FAIL │
│ • Other checks: N/A  │
│ • Show recommendations│
└──────────────────────┘
```

## Scoring Algorithm

```
Total Score = (Bot Access × 0.40) + (Renderability × 0.30) + (Structure × 0.30)

Category Score = (Passes + Warnings × 0.5) / Total Checks × 100

Grade Assignment:
├─ 80-100: 🟢 Good
├─ 50-79:  🟡 Needs Improvement
└─ 0-49:   🔴 Critical Issues
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit | Web UI framework |
| **HTTP Client** | Requests | Fetch web pages |
| **HTML Parsing** | BeautifulSoup4 | Parse HTML content |
| **XML Parsing** | lxml | Parse XML/HTML efficiently |
| **Browser Automation** | Playwright | Render JavaScript content |
| **Validation** | validators | URL validation |
| **HTTP Utils** | urllib3 | Low-level HTTP operations |

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Streamlit Cloud                        │
│  ┌───────────────────────────────────────────────────┐ │
│  │  GEO Crawlability Dashboard                       │ │
│  │  • Auto-deployed from GitHub                      │ │
│  │  • Free tier available                            │ │
│  │  • HTTPS enabled                                  │ │
│  │  • Custom domain support                          │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              External Websites                          │
│  • Target sites for crawlability analysis               │
│  • robots.txt files                                     │
│  • Sitemap.xml files                                    │
└─────────────────────────────────────────────────────────┘
```

## Key Design Patterns

1. **Modular Checker Pattern**: Each checker is independent and focused on specific aspects
2. **Scorer Aggregation**: Central scorer collects results from all checkers
3. **Fallback Strategy**: Graceful degradation when primary methods fail
4. **Progressive Enhancement**: Basic checks first, advanced checks if possible
5. **Configuration-Driven**: Bot lists and thresholds externalized to config

## Performance Considerations

- **Timeout Management**: 60s for HTTP, 90s for browser rendering
- **Retry Logic**: 3 retries with exponential backoff
- **Parallel Potential**: Checkers could run in parallel (future enhancement)
- **Caching**: Session-based HTTP connection pooling
- **Resource Cleanup**: Playwright browser instances properly closed

---

**Version**: 1.0  
**Last Updated**: 2026-07-14  
**Made with ❤️ for better AI crawler accessibility**