#!/usr/bin/env python3
"""
Fix URL-encoded filenames in HTML references
Some files were downloaded with %20 in the filename, but HTML references need proper encoding
"""

import os
import re
import urllib.parse
from pathlib import Path

def fix_url_encoded_paths(html_file):
    """Fix paths with URL-encoded characters to work properly"""
    html_dir = os.path.dirname(html_file)
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Find all src and href attributes with assets paths
    # Pattern: src="assets/.../filename%20with%20spaces.ext"
    patterns = [
        (r'src="(assets/[^"]*%20[^"]*)"', 'src'),
        (r'href="(assets/[^"]*%20[^"]*)"', 'href'),
        (r'srcset="([^"]*%20[^"]*)"', 'srcset'),
    ]
    
    for pattern, attr_type in patterns:
        def replace_match(match):
            path = match.group(1)
            # Check if file exists with %20
            full_path = os.path.join(html_dir, path)
            if os.path.exists(full_path):
                # File exists with %20, keep it as is (browsers handle %20 in URLs)
                return match.group(0)
            else:
                # Try with decoded space
                decoded_path = urllib.parse.unquote(path)
                decoded_full_path = os.path.join(html_dir, decoded_path)
                if os.path.exists(decoded_full_path):
                    # Use decoded path
                    if attr_type == 'src':
                        return f'src="{decoded_path}"'
                    elif attr_type == 'href':
                        return f'href="{decoded_path}"'
                    else:  # srcset
                        return f'srcset="{decoded_path}"'
            return match.group(0)
        
        content = re.sub(pattern, replace_match, content)
    
    if content != original_content:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    base_dir = 'webflow-site'
    html_files = []
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    print(f"Checking {len(html_files)} HTML files for URL-encoding issues...")
    
    fixed_count = 0
    for html_file in html_files:
        if fix_url_encoded_paths(html_file):
            fixed_count += 1
            print(f"  Fixed {html_file}")
    
    if fixed_count == 0:
        print("No URL-encoding issues found.")
    else:
        print(f"\n✅ Fixed {fixed_count} files")

if __name__ == '__main__':
    main()
