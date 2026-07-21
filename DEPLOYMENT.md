# 🚀 Deployment Guide - GEO Crawlability Dashboard

## Easiest Option: Streamlit Community Cloud (FREE) ⭐

**Best for:** Quick deployment, no cost, minimal setup

### Steps:

1. **Push to GitHub**
   ```bash
   cd geo-crawlability-dashboard
   git init
   git add .
   git commit -m "Initial commit - GEO Crawlability Dashboard"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/geo-crawlability-dashboard.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io/
   - Click "New app"
   - Connect your GitHub account
   - Select your repository: `geo-crawlability-dashboard`
   - Main file path: `app.py`
   - Click "Deploy"

3. **Done!** 🎉
   - Your app will be live at: `https://YOUR_USERNAME-geo-crawlability-dashboard.streamlit.app`
   - Free SSL certificate included
   - Auto-deploys on git push

### Important Notes for Streamlit Cloud:

**Playwright Setup:**
Add this to your repository root as `packages.txt`:
```
chromium
chromium-driver
```

**System Dependencies:**
The `requirements.txt` already includes all Python packages.

**Resource Limits:**
- Free tier: 1 GB RAM, 1 CPU core
- Should be sufficient for this app
- If you hit limits, consider upgrading to Streamlit Cloud Pro ($20/month)

---

## Alternative 1: Heroku (FREE tier available)

**Best for:** More control, custom domain support

### Steps:

1. **Install Heroku CLI**
   ```bash
   brew install heroku/brew/heroku  # macOS
   # or download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Heroku App**
   ```bash
   cd geo-crawlability-dashboard
   heroku login
   heroku create your-app-name
   ```

3. **Add Buildpacks**
   ```bash
   heroku buildpacks:add --index 1 heroku/python
   heroku buildpacks:add --index 2 https://github.com/heroku/heroku-buildpack-apt
   ```

4. **Create Required Files**

   **Procfile:**
   ```
   web: sh setup.sh && streamlit run app.py
   ```

   **setup.sh:**
   ```bash
   mkdir -p ~/.streamlit/
   echo "\
   [server]\n\
   headless = true\n\
   port = $PORT\n\
   enableCORS = false\n\
   \n\
   " > ~/.streamlit/config.toml
   ```

   **Aptfile:**
   ```
   chromium-browser
   chromium-chromedriver
   ```

5. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

6. **Open App**
   ```bash
   heroku open
   ```

**Cost:** Free tier available (550-1000 dyno hours/month)

---

## Alternative 2: Railway (Modern, Easy)

**Best for:** Modern deployment, generous free tier

### Steps:

1. **Go to Railway.app**
   - Visit https://railway.app/
   - Sign up with GitHub

2. **Deploy from GitHub**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway auto-detects Streamlit

3. **Add Environment Variables** (if needed)
   - Click on your service
   - Go to "Variables" tab
   - Add any custom variables

4. **Generate Domain**
   - Click "Settings"
   - Click "Generate Domain"
   - Your app is live!

**Cost:** $5 free credit/month (enough for this app)

---

## Alternative 3: Render (Simple & Reliable)

**Best for:** Production-ready apps, good free tier

### Steps:

1. **Go to Render.com**
   - Visit https://render.com/
   - Sign up with GitHub

2. **Create Web Service**
   - Click "New +"
   - Select "Web Service"
   - Connect your GitHub repository

3. **Configure Service**
   - Name: `geo-crawlability-dashboard`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt && playwright install chromium`
   - Start Command: `streamlit run app.py --server.port=$PORT --server.address=127.0.0.1`

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)

**Cost:** Free tier available (750 hours/month)

---

## Alternative 4: Google Cloud Run (Scalable)

**Best for:** High traffic, enterprise use

### Steps:

1. **Create Dockerfile**
   ```dockerfile
   FROM registry.redhat.io/ubi9/python-311-minimal:latest

   WORKDIR /app

   # Create non-root user
   RUN useradd -m -u 1001 appuser

   # Copy and install dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt && \
       playwright install chromium --with-deps

   # Copy app
   COPY --chown=appuser:appuser . .

   # Switch to non-root user
   USER 1001

   # Expose port
   EXPOSE 8080

   # Run app (bind to localhost only; Cloud Run handles external TLS termination)
   CMD streamlit run app.py --server.port=8080 --server.address=127.0.0.1
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy geo-crawlability \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

**Cost:** Pay-per-use (very cheap for low traffic, ~$0.10/day)

---

## Alternative 5: DigitalOcean App Platform

**Best for:** Simple VPS-like experience

### Steps:

1. **Go to DigitalOcean**
   - Visit https://cloud.digitalocean.com/apps
   - Click "Create App"

2. **Connect GitHub**
   - Select your repository
   - Choose branch: `main`

3. **Configure**
   - Detected as: Python
   - Build Command: `pip install -r requirements.txt && playwright install chromium`
   - Run Command: `streamlit run app.py --server.port=8080 --server.address=127.0.0.1`

4. **Deploy**
   - Click "Next" → "Launch App"

**Cost:** $5/month (Basic plan)

---

## Comparison Table

| Platform | Free Tier | Ease | Speed | Best For |
|----------|-----------|------|-------|----------|
| **Streamlit Cloud** | ✅ Yes | ⭐⭐⭐⭐⭐ | Fast | Quick demos, MVPs |
| **Railway** | ✅ $5 credit | ⭐⭐⭐⭐ | Fast | Modern apps |
| **Render** | ✅ 750hrs | ⭐⭐⭐⭐ | Medium | Production apps |
| **Heroku** | ✅ Limited | ⭐⭐⭐ | Medium | Traditional apps |
| **Cloud Run** | ✅ Pay-per-use | ⭐⭐ | Fast | High traffic |
| **DigitalOcean** | ❌ $5/mo | ⭐⭐⭐ | Fast | Full control |

---

## Recommended: Streamlit Community Cloud

**Why?**
- ✅ Completely free
- ✅ Zero configuration
- ✅ Auto-deploys from GitHub
- ✅ Built specifically for Streamlit apps
- ✅ Free SSL certificate
- ✅ No credit card required
- ✅ 1GB RAM (sufficient for this app)

**Limitations:**
- Public apps only (code must be on public GitHub repo)
- 1GB RAM limit
- Community support only

**Perfect for:**
- Demos and MVPs
- Portfolio projects
- Internal tools
- Low-to-medium traffic apps

---

## Quick Start (Streamlit Cloud)

```bash
# 1. Create GitHub repo
cd geo-crawlability-dashboard
git init
git add .
git commit -m "Initial commit"
git branch -M main

# 2. Push to GitHub (create repo first on github.com)
git remote add origin https://github.com/YOUR_USERNAME/geo-crawlability-dashboard.git
git push -u origin main

# 3. Deploy
# Go to https://share.streamlit.io/
# Click "New app" → Select your repo → Deploy
# Done! 🎉
```

Your app will be live at:
`https://YOUR_USERNAME-geo-crawlability-dashboard.streamlit.app`

---

## Custom Domain (Optional)

### For Streamlit Cloud:
- Upgrade to Streamlit Cloud Pro ($20/month)
- Add custom domain in settings

### For Other Platforms:
- Most support custom domains on free tier
- Add CNAME record: `your-domain.com` → `your-app.platform.com`
- Enable SSL (usually automatic)

---

## Monitoring & Analytics

### Add Google Analytics (Optional)

Add to `app.py`:
```python
# Add to the HTML head section
st.markdown("""
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
""", unsafe_allow_html=True)
```

---

## Security Considerations

1. **Rate Limiting**: Consider adding rate limiting for public deployment
2. **API Keys**: Use environment variables for any API keys
3. **CORS**: Already configured in Streamlit
4. **HTTPS**: Automatic on all platforms
5. **Input Validation**: Already implemented

---

## Troubleshooting

### Playwright Issues:
```bash
# Add to packages.txt (Streamlit Cloud)
chromium
chromium-driver

# Or install manually
playwright install chromium
```

### Memory Issues:
- Reduce timeout values in `config/bots.py`
- Disable Playwright for free tier (use HTTP only)
- Upgrade to paid tier

### Slow Performance:
- Add caching with `@st.cache_data`
- Reduce concurrent checks
- Use CDN for static assets

---

## Support

- **Streamlit Docs**: https://docs.streamlit.io/
- **Community Forum**: https://discuss.streamlit.io/
- **GitHub Issues**: Create issues in your repo

---

**Ready to deploy? Start with Streamlit Cloud - it's the easiest! 🚀**