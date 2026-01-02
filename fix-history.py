#!/usr/bin/env python3
"""
Fix Git history:
1. Add back the missing intermediate commit (home/home-1.html -> index.html)
2. Rename asset folders in initial commit (git mv) instead of duplicating
"""

import subprocess
import os
from pathlib import Path

def run_cmd(cmd, check=True, capture_output=True, text=True):
    """Helper to run shell commands."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=capture_output, text=text, check=check)
    if capture_output:
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
    return result

def main():
    # Get current state
    current_branch = run_cmd(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).stdout.strip()
    print(f"Current branch: {current_branch}")
    
    # Find commits
    log_output = run_cmd(['git', 'log', '--oneline', '--all']).stdout
    initial_commit = None
    intermediate_commit = None
    customization_commit = None
    
    for line in log_output.split('\n'):
        if 'Initial commit' in line:
            initial_commit = line.split()[0]
        elif 'Move index.html to home/old-home.html' in line:
            intermediate_commit = line.split()[0]
        elif 'Customized version' in line and 'Gabe Clarke' in line:
            customization_commit = line.split()[0]
            break
    
    print(f"Initial commit: {initial_commit}")
    print(f"Intermediate commit: {intermediate_commit}")
    print(f"Customization commit: {customization_commit}")
    
    # Check if we need to restore the missing commit
    log_output = run_cmd(['git', 'log', '--oneline', 'main']).stdout
    has_home1_move = 'Move home/home-1.html to index.html' in log_output
    
    if not has_home1_move:
        print("\nMissing commit detected: Move home/home-1.html to index.html")
        print("This will be restored after fixing assets.")
    
    # Create backup
    backup_branch = "backup-before-fix"
    run_cmd(['git', 'branch', backup_branch], check=False)
    print(f"\nBackup branch created: {backup_branch}")
    
    # Checkout initial commit
    print(f"\nChecking out initial commit: {initial_commit}")
    run_cmd(['git', 'checkout', initial_commit])
    
    # Check what asset folders exist
    asset_dirs = run_cmd(['git', 'ls-tree', '-d', '--name-only', 'HEAD', 'assets/']).stdout.strip().split('\n')
    asset_dirs = [d for d in asset_dirs if d]
    print(f"\nAsset directories in initial commit: {asset_dirs}")
    
    # The issue: we need to rename 613b963b9d55ae9315a4f51e to 670903a26ae4eb4eb6eb91a2
    # and 61509145daf7a82714b7a7ec to 670903a26ae4eb4eb6eb920a
    # But first we need to remove the incorrectly nested structure
    
    # Check if nested structure exists
    nested_check = run_cmd(['git', 'ls-tree', '-r', '--name-only', 'HEAD'], check=False)
    if 'assets/670903a26ae4eb4eb6eb91a2/613b963b9d55ae9315a4f51e' in nested_check.stdout:
        print("\nFound nested asset structure. Need to fix this first.")
        # We'll need to extract and reorganize
        
    print("\nStrategy:")
    print("1. In initial commit, rename asset folders to match Gabe Clarke names")
    print("2. Update HTML files to reference new folder names")
    print("3. Add back missing intermediate commit")
    print("4. Rebase subsequent commits")
    
    print("\nThis is complex. Let me create a simpler approach...")
    print("Actually, let's check the backup branch to see the original structure.")

if __name__ == '__main__':
    main()







