#!/usr/bin/env python3
"""
Fix paths and URL encoding for original template
"""

import os
import re

# Fix paths
base_dir = 'ofelia-original'
html_files = []

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith('.html'):
            html_files.append(os.path.join(root, file))

print(f"Fixing {len(html_files)} HTML files...")

# Fix paths (webflow-site/assets -> assets)
for html_file in html_files:
    html_dir = os.path.dirname(html_file)
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Fix absolute paths to relative
    if html_dir == base_dir:
        asset_prefix = 'assets'
    else:
        depth = html_dir.replace(base_dir, '').count(os.sep)
        asset_prefix = '../' * depth + 'assets'
    
    asset_prefix = asset_prefix.replace('\\', '/')
    content = re.sub(r'ofelia-original/assets/', f'{asset_prefix}/', content)
    
    if content != original:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)

print("✅ Paths fixed!")

# Fix URL encoding (rename files and update HTML)
print("\nFixing URL encoding...")
import subprocess
result = subprocess.run(['python3', 'fix-all-url-encoding.py'], 
                       cwd='ofelia-original' if os.path.exists('ofelia-original') else '.',
                       capture_output=True, text=True)
print(result.stdout)

print("\n✅ Original template is ready!")
