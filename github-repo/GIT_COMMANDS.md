# Commands to create and push repository

# 1. Create repository on GitHub
# Go to https://github.com/new
# Repository name: ebd-manager
# Description: Sistema de gerenciamento para Escola Bíblica Dominical
# Make it public
# Don't initialize with README (we already have one)

# 2. Initialize git and push
cd /path/to/ebd-manager
git init
git add .
git commit -m "feat: initial commit - complete EBD management system"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ebd-manager.git
git push -u origin main

# 3. After pushing, you can:
# - Enable GitHub Pages (optional)
# - Configure repository settings
# - Add collaborators
# - Set up branch protection rules