#!/bin/bash

# Step 1: Rebuild the dashboard
echo "🛠  Rebuilding dashboard..."
python3 scripts/generate_dashboard.py

# Step 2: Move to project root
cd "$(dirname "$0")/.."

# Step 3: Git add, commit, push
echo "📦 Committing dashboard updates..."
git add docs/
git commit -m "🔄 Auto-updated dashboard at $(date)"
git push origin main
