# 🚀 Manual Deployment Steps

Everything is ready! Just follow these commands in your terminal:

## Step 1: Create GitHub Repository

Go to: https://github.com/new

Fill in:
- Repository name: `geo-crawlability-dashboard`
- Visibility: **PUBLIC** ✅
- Do NOT initialize with README
- Click "Create repository"

## Step 2: Push to GitHub

Open your terminal and run these commands:

```bash
cd /Users/amitksingh/Desktop/geo-crawlability-dashboard

# Push to GitHub (you won't be prompted for password if SSH is configured)
git push -u origin main
```

**Expected output:**
```
Enumerating objects: 24, done.
Counting objects: 100% (24/24), done.
...
To https://github.com/amitsingh800/geo-crawlability-dashboard.git
 * [new branch]      main -> main
```

## Step 3: Deploy on Streamlit Cloud

1. Go to: **https://share.streamlit.io/**
2. Click **"Sign in"** (use GitHub)
3. Click **"New app"**
4. Fill in:
   - Repository: `amitsingh800/geo-crawlability-dashboard`
   - Branch: `main`
   - Main file path: `app.py`
5. Click **"Deploy!"**

## Step 4: Wait for Deployment (2-5 minutes)

Streamlit will install dependencies and deploy your app.

## 🎉 Your App Will Be Live At:

**https://amitsingh800-geo-crawlability-dashboard.streamlit.app**

---

## Troubleshooting

### If push fails with "repository not found":
Make sure you created the repository on GitHub first (Step 1)

### If push fails with authentication error:
You may need to set up SSH keys or use HTTPS with token:
```bash
# Option 1: Use SSH (recommended)
git remote set-url origin git@github.com:amitsingh800/geo-crawlability-dashboard.git
git push -u origin main

# Option 2: Use HTTPS with token
# Create token at: https://github.com/settings/tokens
git push -u origin main
# Enter username: amitsingh800
# Enter password: [paste your token]
```

### If Streamlit deployment fails:
- Check the logs in Streamlit Cloud dashboard
- Verify all files are pushed to GitHub
- Ensure repository is PUBLIC

---

## Quick Commands Summary

```bash
# 1. Navigate to project
cd /Users/amitksingh/Desktop/geo-crawlability-dashboard

# 2. Push to GitHub (after creating repo)
git push -u origin main

# 3. Go to Streamlit Cloud and deploy
# https://share.streamlit.io/
```

That's it! 🚀