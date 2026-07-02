# Quick Start Guide

## Installation

### Option 1: Automated Setup (Recommended)

Run the setup script:

```bash
cd geo-crawlability-dashboard
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

1. **Create virtual environment:**
```bash
cd geo-crawlability-dashboard
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install Playwright browsers:**
```bash
playwright install chromium
```

## Running the Dashboard

1. **Activate virtual environment** (if not already activated):
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Run the Streamlit app:**
```bash
streamlit run app.py
```

3. **Open your browser:**
The dashboard will automatically open at `http://localhost:8501`

## Using the Dashboard

1. Enter a website URL (e.g., `https://example.com`)
2. Click "🔍 Analyze Website"
3. Wait for the analysis to complete (typically 30-60 seconds)
4. Review your results:
   - **Overall Score**: 0-100 with traffic light indicator
   - **Category Scores**: Bot Access, Renderability, Structure
   - **Detailed Checks**: Expandable sections for each category
   - **Priority Fixes**: List of failed checks with actionable suggestions

## What Gets Checked?

### Bot Access (40% weight)
- ✅ robots.txt restrictions for 9 AI bots
- ✅ Cloudflare AI bot blocking
- ✅ Meta robots tags (noindex, noai)
- ✅ X-Robots-Tag HTTP headers

### Renderability (30% weight)
- ✅ JavaScript-dependent content detection
- ✅ Paywall patterns
- ✅ Login requirements

### Structure & Metadata (30% weight)
- ✅ Schema.org structured data (JSON-LD)
- ✅ Heading hierarchy (H1-H6)
- ✅ Title tag (30-60 chars optimal)
- ✅ Meta description (120-160 chars optimal)
- ✅ Canonical tag
- ✅ sitemap.xml presence
- ✅ llms.txt detection (informational)

## Scoring Guide

- **80-100** 🟢 **Good** - Well optimized for AI crawlers
- **50-79** 🟡 **Needs Improvement** - Some issues to address
- **0-49** 🔴 **Critical Issues** - Major accessibility problems

## Troubleshooting

### Playwright Installation Issues

If Playwright fails to install browsers:
```bash
playwright install --with-deps chromium
```

### Import Errors

Make sure you're in the project directory and virtual environment is activated:
```bash
cd geo-crawlability-dashboard
source venv/bin/activate
python -c "import streamlit; print('OK')"
```

### Port Already in Use

If port 8501 is busy, specify a different port:
```bash
streamlit run app.py --server.port 8502
```

## Example URLs to Test

Try these to see different scores:

- **Well-optimized site**: `https://www.wikipedia.org`
- **JS-heavy site**: `https://www.reddit.com`
- **News site**: `https://www.bbc.com`

## Next Steps

- Review the detailed README.md for architecture details
- Check failed checks and implement suggested fixes
- Re-run analysis after making changes to see improvements

## Support

For issues or questions:
1. Check the main README.md
2. Review error messages in the dashboard
3. Check browser console for JavaScript errors
4. Ensure all dependencies are installed correctly