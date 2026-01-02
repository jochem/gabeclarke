#!/usr/bin/env python3
"""
Update HTML files to use %20 encoding for files with spaces
Simple and fast approach
"""

import os
import re

def update_html_file(html_file):
    """Update HTML to use %20 for spaces in asset paths"""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Find all asset paths and replace spaces with %20
        # Match: assets/.../filename with spaces.ext
        def replace_spaces_in_path(match):
            path = match.group(1)
            # Only replace spaces in the filename part, not in the directory structure
            parts = path.split('/')
            if len(parts) > 0:
                # Last part is the filename
                filename = parts[-1]
                if ' ' in filename:
                    parts[-1] = filename.replace(' ', '%20')
                    return match.group(0).replace(path, '/'.join(parts))
            return match.group(0)
        
        # Replace in src, href, and srcset attributes
        patterns = [
            (r'(src="assets/[^"]+")', replace_spaces_in_path),
            (r'(href="assets/[^"]+")', replace_spaces_in_path),
            (r'(srcset="[^"]+")', lambda m: m.group(0).replace(' ', '%20') if 'assets/' in m.group(0) else m.group(0)),
        ]
        
        for pattern, replacer in patterns:
            content = re.sub(pattern, replacer, content)
        
        if content != original:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {html_file}: {e}")
        return False

def main():
    base_dir = 'webflow-site'
    html_files = []
    
    print("Finding HTML files...")
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    print(f"Found {len(html_files)} HTML files")
    print("Updating paths...")
    
    updated = 0
    for i, html_file in enumerate(html_files, 1):
        if update_html_file(html_file):
            updated += 1
            if i % 5 == 0:
                print(f"  Processed {i}/{len(html_files)}...")
    
    print(f"\n✅ Updated {updated} HTML files")

if __name__ == '__main__':
    main()
