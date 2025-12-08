#!/usr/bin/env python3
"""
Fix relative paths in HTML files
"""

import os
import re
from pathlib import Path

def fix_paths_in_html(html_file):
    """Fix paths to be relative to the HTML file location"""
    html_dir = os.path.dirname(html_file)
    base_dir = 'webflow-site'
    
    # Calculate relative path from HTML file to assets
    if html_dir == base_dir:
        # HTML is in root, assets are in assets/
        asset_prefix = 'assets'
    else:
        # HTML is in subdirectory, need to go up then into assets
        depth = html_dir.replace(base_dir, '').count(os.sep)
        asset_prefix = '../' * depth + 'assets'
    
    # Normalize for web
    asset_prefix = asset_prefix.replace('\\', '/')
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace absolute paths with relative paths
    # Pattern: webflow-site/assets/... -> assets/... or ../assets/...
    pattern = r'webflow-site/assets/'
    replacement = f'{asset_prefix}/'
    
    updated = re.sub(pattern, replacement, content)
    
    if content != updated:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(updated)
        return True
    return False

def main():
    base_dir = 'webflow-site'
    html_files = []
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    print(f"Fixing paths in {len(html_files)} HTML files...")
    
    fixed_count = 0
    for html_file in html_files:
        if fix_paths_in_html(html_file):
            fixed_count += 1
            print(f"  Fixed {html_file}")
    
    print(f"\n✅ Fixed paths in {fixed_count} files")

if __name__ == '__main__':
    main()

