#!/bin/bash

echo "⚠️  WARNING: This script will delete and re-create your local development branch!"
echo "Saving local changes to a backup branch first..."

# Step 1: Make sure you are not on 'development' branch
git checkout main || git checkout master || git checkout -

# Step 2: Create a backup branch for their current local development
git fetch origin
git branch backup-development-$(date +%Y%m%d%H%M%S) development
echo "✅ Backup created: $(git branch --show-current)"

# Step 3: Delete local development branch
git branch -D development
echo "🗑️  Deleted local development branch."

# Step 4: Recreate development branch from remote
git fetch origin
git checkout -b development origin/development
echo "✅ Development branch reset and tracking origin/development."

# Step 5: Done!
git status
echo "🚀 All done! You are now aligned with the latest remote development branch."
echo " "
