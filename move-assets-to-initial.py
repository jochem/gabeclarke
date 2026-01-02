#!/usr/bin/env python3
"""
Move assets from customization commit to initial commit.

This script will:
1. Extract assets from the customization commit
2. Add them to the initial commit
3. Remove them from the customization commit
4. Rebase the intermediate commits

This reduces the diff size by having assets in the initial commit.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_cmd(cmd, check=True):
    """Run a git command and return output."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=check)
    if result.stdout:
        print(result.stdout)
    if result.stderr and result.returncode != 0:
        print(result.stderr, file=sys.stderr)
    return result

def get_commit_hash(pattern):
    """Get commit hash matching pattern."""
    result = run_cmd(['git', 'log', '--oneline', '--all'], check=False)
    for line in result.stdout.split('\n'):
        if pattern.lower() in line.lower():
            return line.split()[0]
    return None

def main():
    # Find commits
    initial_commit = get_commit_hash('initial')
    intermediate_commit = '1f360ef'  # Move commit
    customization_commit = '2337499'  # Customization commit
    
    if not initial_commit:
        print("Error: Could not find initial commit")
        sys.exit(1)
    
    print(f"Initial commit: {initial_commit}")
    print(f"Intermediate commit: {intermediate_commit}")
    print(f"Customization commit: {customization_commit}")
    print()
    
    # Get list of assets added in customization commit
    print("Getting list of assets added in customization commit...")
    result = run_cmd(['git', 'diff', '--name-only', '--diff-filter=A', 
                     intermediate_commit, customization_commit])
    
    asset_files = [line for line in result.stdout.strip().split('\n') 
                   if line.startswith('assets/')]
    
    if not asset_files:
        print("No assets found to move")
        return
    
    print(f"Found {len(asset_files)} asset files to move")
    print(f"Sample files: {asset_files[:3]}")
    print()
    
    # Get unique asset directories
    asset_dirs = set()
    for f in asset_files:
        parts = f.split('/')
        if len(parts) >= 2:
            asset_dirs.add('/'.join(parts[:2]))
    
    print(f"Asset directories to move: {sorted(asset_dirs)}")
    print()
    
    print("=" * 60)
    print("WARNING: This will rewrite git history!")
    print("=" * 60)
    print()
    print("Steps that will be performed:")
    print("1. Create a backup branch")
    print("2. Checkout initial commit")
    print("3. Extract assets from customization commit")
    print("4. Add assets to initial commit (amend)")
    print("5. Rebase intermediate commit on top")
    print("6. Rebase customization commit on top (without assets)")
    print()
    
    # Allow non-interactive mode via environment variable or command line
    import sys
    if '--yes' in sys.argv or os.environ.get('AUTO_YES') == '1':
        print("Auto-proceeding (--yes flag or AUTO_YES=1 set)")
    else:
        response = input("Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted")
            return
    
    # Create backup branch
    print("\n1. Creating backup branch...")
    run_cmd(['git', 'branch', 'backup-before-asset-move', 'HEAD'])
    
    # Get current branch
    result = run_cmd(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    current_branch = result.stdout.strip()
    print(f"Current branch: {current_branch}")
    
    # Checkout initial commit
    print("\n2. Checking out initial commit...")
    run_cmd(['git', 'checkout', initial_commit, '--detach'])
    
    # Extract assets from customization commit
    print("\n3. Extracting assets from customization commit...")
    for asset_file in asset_files:
        run_cmd(['git', 'checkout', customization_commit, '--', asset_file])
    
    # Stage assets
    print("\n4. Staging assets...")
    run_cmd(['git', 'add'] + asset_files)
    
    # Amend initial commit
    print("\n5. Amending initial commit with assets...")
    run_cmd(['git', 'commit', '--amend', '--no-edit'])
    
    new_initial_commit = run_cmd(['git', 'rev-parse', 'HEAD']).stdout.strip()
    print(f"New initial commit: {new_initial_commit}")
    
    # Rebase intermediate commit
    print("\n6. Rebasing intermediate commit...")
    run_cmd(['git', 'rebase', '--onto', new_initial_commit, initial_commit, intermediate_commit])
    
    new_intermediate_commit = run_cmd(['git', 'rev-parse', 'HEAD']).stdout.strip()
    print(f"New intermediate commit: {new_intermediate_commit}")
    
    # Rebase customization commit (but remove assets first)
    print("\n7. Rebasing customization commit (removing assets from it)...")
    
    # Checkout customization commit
    run_cmd(['git', 'checkout', customization_commit, '--detach'])
    
    # Remove assets from this commit
    run_cmd(['git', 'rm', '-r', '--cached'] + list(asset_dirs), check=False)
    
    # Check if there are other changes
    result = run_cmd(['git', 'status', '--porcelain'], check=False)
    if result.stdout.strip():
        # There are other changes, commit them
        run_cmd(['git', 'commit', '--amend', '--no-edit'])
        customization_without_assets = run_cmd(['git', 'rev-parse', 'HEAD']).stdout.strip()
    else:
        # No other changes, this commit would be empty
        print("Warning: Customization commit has no other changes besides assets")
        customization_without_assets = new_intermediate_commit
    
    # Rebase onto new intermediate
    if customization_without_assets != new_intermediate_commit:
        run_cmd(['git', 'rebase', '--onto', new_intermediate_commit, intermediate_commit, customization_without_assets])
    
    # Update main branch
    print("\n8. Updating main branch...")
    run_cmd(['git', 'checkout', current_branch])
    run_cmd(['git', 'reset', '--hard', 'HEAD'])
    
    print("\nDone! Assets have been moved to initial commit.")
    print(f"Backup branch created: backup-before-asset-move")
    print("\nTo verify, run:")
    print(f"  git diff {new_initial_commit} {new_intermediate_commit} | grep assets/ | wc -l")
    print("(should show 0 or very few asset changes)")

if __name__ == '__main__':
    main()

