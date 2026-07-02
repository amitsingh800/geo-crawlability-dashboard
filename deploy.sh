#!/bin/bash

# Quick Deployment Script for GEO Crawlability Dashboard
# This script helps you deploy to Streamlit Community Cloud

echo "🚀 GEO Crawlability Dashboard - Deployment Helper"
echo "=================================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit - GEO Crawlability Dashboard"
    git branch -M main
    echo "✅ Git repository initialized"
    echo ""
else
    echo "✅ Git repository already exists"
    echo ""
fi

# Check if remote exists
if ! git remote | grep -q origin; then
    echo "🔗 Setting up GitHub remote..."
    echo ""
    echo "Please enter your GitHub username:"
    read github_username
    echo ""
    echo "Please enter your repository name (e.g., geo-crawlability-dashboard):"
    read repo_name
    echo ""
    
    git remote add origin "https://github.com/$github_username/$repo_name.git"
    echo "✅ Remote added: https://github.com/$github_username/$repo_name.git"
    echo ""
    echo "⚠️  IMPORTANT: Create this repository on GitHub first!"
    echo "   Go to: https://github.com/new"
    echo "   Repository name: $repo_name"
    echo "   Make it PUBLIC (required for free Streamlit Cloud)"
    echo ""
    echo "Press Enter when you've created the repository..."
    read
else
    echo "✅ GitHub remote already configured"
    echo ""
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git add .
git commit -m "Update for deployment" || echo "No changes to commit"
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "🎉 Next Steps:"
    echo "=============="
    echo ""
    echo "1. Go to: https://share.streamlit.io/"
    echo "2. Click 'New app'"
    echo "3. Connect your GitHub account (if not already connected)"
    echo "4. Select your repository"
    echo "5. Main file path: app.py"
    echo "6. Click 'Deploy'"
    echo ""
    echo "Your app will be live at:"
    echo "https://YOUR_USERNAME-$(basename $(pwd)).streamlit.app"
    echo ""
    echo "⏱️  Deployment usually takes 2-5 minutes"
    echo ""
    echo "📚 For more deployment options, see DEPLOYMENT.md"
else
    echo ""
    echo "❌ Failed to push to GitHub"
    echo ""
    echo "Common issues:"
    echo "- Repository doesn't exist on GitHub (create it first)"
    echo "- Authentication failed (check your GitHub credentials)"
    echo "- Remote URL is incorrect"
    echo ""
    echo "Manual steps:"
    echo "1. Create repository on GitHub: https://github.com/new"
    echo "2. Run: git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    echo "3. Run: git push -u origin main"
fi

# Made with Bob
