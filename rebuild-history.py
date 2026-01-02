#!/usr/bin/env python3
"""
Fix Git history:
1. Start from initial commit with original assets.
2. Add a commit that renames asset folders to Gabe Clarke names.
3. Cherry-pick the two intermediate file-rename commits.
4. Cherry-pick the customization commit.
5. Add .gitignore commit.
"""

import subprocess
import os
import shutil
from pathlib import Path

def run_cmd(cmd, check=True, capture_output=True, text=True, cwd=None):
    """Helper to run shell commands."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=capture_output, text=text, check=check, cwd=cwd)
    if capture_output:
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
    return result

def get_commit_hash(commit_message_substring):
    """Get the hash of a commit based on a substring of its message."""
    result = run_cmd(['git', 'log', '--all', '--grep', commit_message_substring, '--format=%H'], check=False)
    if result.returncode != 0 or not result.stdout.strip():
        raise ValueError(f"Could not find commit with message containing: '{commit_message_substring}'")
    # Take the first one (most recent)
    return result.stdout.strip().split('\n')[0]

def main():
    # Ensure we are on a clean state
    run_cmd(['git', 'reset', '--hard'])
    run_cmd(['git', 'clean', '-fdx'])

    # Get current branch
    current_branch = run_cmd(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).stdout.strip()
    print(f"Current branch: {current_branch}")

    # Identify commits from the backup branch
    print("\nIdentifying commits from backup-before-asset-move...")
    run_cmd(['git', 'checkout', 'backup-before-asset-move'])
    
    initial_commit = get_commit_hash("Initial commit: Original Ofelia template")
    move_index_to_old_home = get_commit_hash("Move index.html to home/old-home.html")
    move_home1_to_index = get_commit_hash("Move home/home-1.html to index.html")
    customization_commit = get_commit_hash("Customized version: Gabe Clarke portfolio")
    gitignore_commit = get_commit_hash("Add .gitignore for Python scripts")
    
    print(f"Initial commit: {initial_commit}")
    print(f"Move index.html to home/old-home.html: {move_index_to_old_home}")
    print(f"Move home/home-1.html to index.html: {move_home1_to_index}")
    print(f"Customization commit: {customization_commit}")
    print(f".gitignore commit: {gitignore_commit}")

    # 1. Start from the initial commit
    print(f"\nChecking out initial commit: {initial_commit}...")
    run_cmd(['git', 'checkout', initial_commit])

    # Create a new branch for the rewritten history
    new_main_branch = "main-new-history"
    run_cmd(['git', 'branch', '-D', new_main_branch], check=False) # Delete if exists
    run_cmd(['git', 'checkout', '-b', new_main_branch])

    # 2. Rename asset folders in a new commit
    print("\nRenaming asset folders...")
    # First, ensure the target directories don't exist in the working tree to allow git mv
    run_cmd(['rm', '-rf', 'assets/670903a26ae4eb4eb6eb91a2'], check=False)
    run_cmd(['rm', '-rf', 'assets/670903a26ae4eb4eb6eb920a'], check=False)
    
    # Check if source directories exist
    if not os.path.exists('assets/613b963b9d55ae9315a4f51e'):
        print("Warning: assets/613b963b9d55ae9315a4f51e does not exist, skipping rename")
    else:
        run_cmd(['git', 'mv', 'assets/613b963b9d55ae9315a4f51e', 'assets/670903a26ae4eb4eb6eb91a2'])
    
    if not os.path.exists('assets/61509145daf7a82714b7a7ec'):
        print("Warning: assets/61509145daf7a82714b7a7ec does not exist, skipping rename")
    else:
        run_cmd(['git', 'mv', 'assets/61509145daf7a82714b7a7ec', 'assets/670903a26ae4eb4eb6eb920a'])
    
    # Update HTML references
    print("Updating HTML references...")
    # Use Python to update files instead of sed for better cross-platform compatibility
    import glob
    html_files = []
    for pattern in ['**/*.html']:
        html_files.extend(glob.glob(pattern, recursive=True))
    
    # Filter out files in excluded directories
    html_files = [f for f in html_files if not any(excluded in f for excluded in ['.git', 'webflow-site', 'ofelia-original'])]
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace('assets/613b963b9d55ae9315a4f51e', 'assets/670903a26ae4eb4eb6eb91a2')
            content = content.replace('assets/61509145daf7a82714b7a7ec', 'assets/670903a26ae4eb4eb6eb920a')
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"Warning: Could not update {html_file}: {e}")

    run_cmd(['git', 'add', '-A'])
    run_cmd(['git', 'commit', '-m', 'Rename asset folders to match Gabe Clarke version'])

    # 3. Cherry-pick the intermediate commits
    print("\nCherry-picking intermediate commits...")
    run_cmd(['git', 'cherry-pick', move_index_to_old_home])
    run_cmd(['git', 'cherry-pick', move_home1_to_index])

    # 4. Cherry-pick the customization commit
    print("\nCherry-picking customization commit...")
    try:
        run_cmd(['git', 'cherry-pick', customization_commit])
    except subprocess.CalledProcessError:
        print("Conflict detected during cherry-pick of customization commit. Resolving...")
        # Resolve conflicts by taking 'theirs' (customization version)
        run_cmd(['git', 'checkout', '--theirs', '.'])
        run_cmd(['git', 'add', '-A'])
        run_cmd(['git', 'commit', '--no-edit'])
        print("Conflicts resolved, cherry-pick continued.")

    # 5. Cherry-pick the .gitignore commit
    print("\nCherry-picking .gitignore commit...")
    try:
        run_cmd(['git', 'cherry-pick', gitignore_commit])
    except subprocess.CalledProcessError:
        print("Conflict or issue with .gitignore commit. Checking if .gitignore already exists...")
        if os.path.exists('.gitignore'):
            print(".gitignore already exists, skipping cherry-pick")
        else:
            # Try to get just the .gitignore file from that commit
            run_cmd(['git', 'show', f'{gitignore_commit}:.gitignore'], check=False)
            result = run_cmd(['git', 'show', f'{gitignore_commit}:.gitignore'], check=False)
            if result.returncode == 0:
                with open('.gitignore', 'w') as f:
                    f.write(result.stdout)
                run_cmd(['git', 'add', '.gitignore'])
                run_cmd(['git', 'commit', '-m', 'Add .gitignore for Python scripts'])
            else:
                print("Could not extract .gitignore from commit, skipping")
    
    print("\nHistory rebuilt successfully.")
    print(f"New history on branch '{new_main_branch}':")
    run_cmd(['git', 'log', '--oneline', '-6'])

    print("\nTo update your main branch, run:")
    print(f"git checkout main")
    print(f"git reset --hard {new_main_branch}")
    print(f"git push origin main --force")

if __name__ == '__main__':
    main()
