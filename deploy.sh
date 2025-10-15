#!/bin/bash

# AI Diwali Wish Maker - Quick Deployment Script
# This script helps you deploy to GitHub and Streamlit Cloud

echo "🪔 AI Diwali Wish Maker - Deployment Helper ✨"
echo "=============================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if we're in a git repo
if [ ! -d .git ]; then
    echo "📝 Initializing Git repository..."
    git init
    echo "✅ Git initialized"
fi

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << EOF
background_music.mp3
*.pyc
__pycache__/
.DS_Store
.env
*.mp3
*.wav
.streamlit/secrets.toml
venv/
ENV/
.venv/
EOF
    echo "✅ .gitignore created"
fi

# Ask for GitHub repository URL
echo ""
echo "📦 GitHub Repository Setup"
echo "=========================="
echo ""
echo "Do you have a GitHub repository created? (yes/no)"
read -r has_repo

if [ "$has_repo" = "no" ]; then
    echo ""
    echo "Please follow these steps:"
    echo "1. Go to https://github.com/new"
    echo "2. Create a new repository named: ai-diwali-wish-maker"
    echo "3. Do NOT initialize with README (we already have files)"
    echo "4. Come back here when done"
    echo ""
    echo "Press Enter when you've created the repository..."
    read -r
fi

echo ""
echo "Enter your GitHub repository URL:"
echo "Example: https://github.com/username/ai-diwali-wish-maker.git"
read -r repo_url

# Add remote if it doesn't exist
if git remote | grep -q origin; then
    echo "📝 Updating remote URL..."
    git remote set-url origin "$repo_url"
else
    echo "📝 Adding remote..."
    git remote add origin "$repo_url"
fi

# Add all files
echo "📝 Adding files to git..."
git add .

# Commit
echo "📝 Committing changes..."
git commit -m "Initial commit - AI Diwali Wish Maker" 2>/dev/null || git commit -m "Update - AI Diwali Wish Maker"

# Get current branch
current_branch=$(git branch --show-current)
if [ -z "$current_branch" ]; then
    current_branch="main"
    git branch -M main
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
if git push -u origin "$current_branch" 2>/dev/null; then
    echo "✅ Successfully pushed to GitHub!"
else
    echo "⚠️  Push failed. You might need to authenticate with GitHub."
    echo "Try running: git push -u origin $current_branch"
fi

echo ""
echo "=============================================="
echo "✅ GitHub Setup Complete!"
echo "=============================================="
echo ""
echo "📍 Your code is now on GitHub at:"
echo "   $repo_url"
echo ""
echo "🚀 Next Steps - Deploy to Streamlit Cloud:"
echo "=============================================="
echo ""
echo "1. Go to: https://share.streamlit.io/"
echo "2. Sign in with your GitHub account"
echo "3. Click 'New app'"
echo "4. Select your repository: ai-diwali-wish-maker"
echo "5. Branch: $current_branch"
echo "6. Main file: app.py"
echo "7. Click 'Deploy!'"
echo ""
echo "Your app will be live at:"
echo "https://YOUR-USERNAME-ai-diwali-wish-maker.streamlit.app"
echo ""
echo "🎉 Happy Diwali! Your app will be online in ~2-5 minutes! 🪔✨"
echo ""

