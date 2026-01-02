#!/bin/bash
# Script to move assets from customization commit to initial commit
# This will reduce the diff size by having assets in the initial commit

set -e

echo "Analyzing asset structure..."

# Get the initial commit
INITIAL_COMMIT=$(git log --oneline --all | grep -i "initial" | head -1 | cut -d' ' -f1)
INTERMEDIATE_COMMIT="1f360ef"  # The commit before customization
CUSTOMIZATION_COMMIT="2337499"  # The customization commit

echo "Initial commit: $INITIAL_COMMIT"
echo "Intermediate commit: $INTERMEDIATE_COMMIT"
echo "Customization commit: $CUSTOMIZATION_COMMIT"

# Check what assets were added in customization commit
echo ""
echo "Assets added in customization commit:"
git diff --name-only --diff-filter=A $INTERMEDIATE_COMMIT $CUSTOMIZATION_COMMIT | grep "^assets/" | head -10

# Count new assets
NEW_ASSETS_COUNT=$(git diff --name-only --diff-filter=A $INTERMEDIATE_COMMIT $CUSTOMIZATION_COMMIT | grep "^assets/" | wc -l | tr -d ' ')
echo "Total new assets: $NEW_ASSETS_COUNT"

# Check if assets/670903a26ae4eb4eb6eb91a2 exists in intermediate commit
echo ""
echo "Checking if assets/670903a26ae4eb4eb6eb91a2 exists in intermediate commit..."
if git ls-tree -r --name-only $INTERMEDIATE_COMMIT | grep -q "^assets/670903a26ae4eb4eb6eb91a2/"; then
    echo "  ✓ assets/670903a26ae4eb4eb6eb91a2 exists in intermediate commit"
else
    echo "  ✗ assets/670903a26ae4eb4eb6eb91a2 does NOT exist in intermediate commit"
fi

# Check if assets/670903a26ae4eb4eb6eb920a exists in intermediate commit
if git ls-tree -r --name-only $INTERMEDIATE_COMMIT | grep -q "^assets/670903a26ae4eb4eb6eb920a/"; then
    echo "  ✓ assets/670903a26ae4eb4eb6eb920a exists in intermediate commit"
else
    echo "  ✗ assets/670903a26ae4eb4eb6eb920a does NOT exist in intermediate commit"
fi

echo ""
echo "To move these assets to the initial commit, you would need to:"
echo "1. Checkout the initial commit"
echo "2. Cherry-pick or add the assets from the customization commit"
echo "3. Amend the initial commit"
echo "4. Rebase the intermediate and customization commits on top"
echo ""
echo "This is a complex operation. Would you like me to create a script to do this?"







