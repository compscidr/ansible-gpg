#!/bin/bash

# Fix Ansible Galaxy version comparison issue by removing inconsistent tag
# 
# Problem: The tag 'v0.0.8' has a 'v' prefix while all other tags follow 'x.y.z' format
# This causes Ansible Galaxy to fail when determining the most recent version
# 
# Solution: Delete the problematic 'v0.0.8' tag since it points to the same commit as '0.0.9'

echo "🔍 Checking current tag situation..."

echo "Current tags (sorted by version):"
git tag --list --sort=-version:refname

echo ""
echo "📊 Verifying that v0.0.8 and 0.0.9 point to the same commit:"
echo "v0.0.8 commit: $(git rev-list -n 1 v0.0.8 2>/dev/null || echo 'Tag not found')"
echo "0.0.9 commit:  $(git rev-list -n 1 0.0.9 2>/dev/null || echo 'Tag not found')"

echo ""
if git rev-parse --verify v0.0.8 >/dev/null 2>&1; then
    echo "🚀 Fixing the issue by removing the problematic v0.0.8 tag..."
    
    # Delete the tag from remote repository
    echo "Deleting v0.0.8 tag from remote repository..."
    git push --delete origin v0.0.8
    
    # Delete the tag from local repository
    echo "Deleting v0.0.8 tag from local repository..."
    git tag --delete v0.0.8
    
    echo ""
    echo "✅ Fixed! New tag list (sorted by version):"
    git tag --list --sort=-version:refname
    
    echo ""
    echo "🎉 The versioning issue has been resolved!"
    echo "   Ansible Galaxy should now be able to determine the most recent version correctly."
else
    echo "✅ The v0.0.8 tag has already been removed!"
    echo "   The versioning issue should be resolved."
fi

echo ""
echo "📝 All tags now follow the consistent 'x.y.z' format without prefixes."