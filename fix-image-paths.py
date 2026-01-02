#!/usr/bin/env python3
"""
Fix image paths to ensure they match the actual files on disk
Handles URL encoding issues with %20 in filenames
"""

import os
import re
import urllib.parse
from pathlib import Path

def fix_image_paths(html_file):
    """Fix image src paths to match actual files"""
    html_dir = os.path.dirname(html_file)
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Find all img src attributes
    def fix_src(match):
        full_tag = match.group(0)
        src_path = match.group(1)
        
        # Check if path contains %20
        if '%20' in src_path:
            # Try to find the actual file
            # First, try with %20 as-is
            test_path = os.path.join(html_dir, src_path)
            if os.path.exists(test_path):
                return full_tag  # Already correct
            
            # Try with decoded space
            decoded_path = urllib.parse.unquote(src_path)
            test_path_decoded = os.path.join(html_dir, decoded_path)
            if os.path.exists(test_path_decoded):
                # File exists with space, update HTML to use space (properly encoded)
                new_src = urllib.parse.quote(decoded_path, safe='/')
                return full_tag.replace(src_path, new_src)
            
            # Try with double-encoded %20 (%2520)
            double_encoded = src_path.replace('%20', '%2520')
            test_path_double = os.path.join(html_dir, urllib.parse.unquote(double_encoded))
            if os.path.exists(test_path_double):
                return full_tag.replace(src_path, double_encoded)
        
        return full_tag
    
    # Fix src attributes
    content = re.sub(r'src="(assets/[^"]+)"', fix_src, content)
    
    # Fix srcset attributes (they contain multiple URLs)
    def fix_srcset(match):
        full_attr = match.group(0)
        srcset_value = match.group(1)
        
        # Split srcset into individual sources
        sources = re.split(r',\s*', srcset_value)
        fixed_sources = []
        
        for source in sources:
            parts = source.strip().split()
            url = parts[0] if parts else source.strip()
            
            if '%20' in url:
                test_path = os.path.join(html_dir, url)
                if not os.path.exists(test_path):
                    # Try decoded
                    decoded_url = urllib.parse.unquote(url)
                    test_path_decoded = os.path.join(html_dir, decoded_url)
                    if os.path.exists(test_path_decoded):
                        url = urllib.parse.quote(decoded_url, safe='/')
            
            if len(parts) > 1:
                fixed_sources.append(f"{url} {' '.join(parts[1:])}")
            else:
                fixed_sources.append(url)
        
        return f'srcset="{", ".join(fixed_sources)}"'
    
    content = re.sub(r'srcset="([^"]+)"', fix_srcset, content)
    
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
    
    print(f"Checking {len(html_files)} HTML files for image path issues...")
    
    fixed_count = 0
    for html_file in html_files:
        if fix_image_paths(html_file):
            fixed_count += 1
            print(f"  Fixed {html_file}")
    
    if fixed_count == 0:
        print("No image path issues found.")
    else:
        print(f"\n✅ Fixed {fixed_count} files")

if __name__ == '__main__':
    main()
