#!/usr/bin/env python3
"""
Fix all URL-encoded filenames (%20) to use actual spaces
and update all HTML references accordingly
"""

import os
import re
import urllib.parse
from pathlib import Path

def find_files_with_encoding(base_dir):
    """Find all files with %20 in their names"""
    files_to_rename = []
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if '%20' in file:
                full_path = os.path.join(root, file)
                files_to_rename.append(full_path)
    
    return files_to_rename

def rename_file(old_path):
    """Rename file from %20 to space"""
    directory = os.path.dirname(old_path)
    old_name = os.path.basename(old_path)
    new_name = old_name.replace('%20', ' ')
    new_path = os.path.join(directory, new_name)
    
    if os.path.exists(old_path) and not os.path.exists(new_path):
        os.rename(old_path, new_path)
        return (old_path, new_path)
    return None

def update_html_references(html_file, file_mappings):
    """Update HTML to reference renamed files"""
    html_dir = os.path.dirname(html_file)
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Create mapping of old paths to new paths
    for old_path, new_path in file_mappings:
        # Get relative paths
        old_rel = os.path.relpath(old_path, html_dir)
        new_rel = os.path.relpath(new_path, html_dir)
        
        # Old path with %20
        old_path_encoded = old_rel.replace(' ', '%20')
        # New path should use %20 in HTML (browser will decode to space)
        new_path_encoded = new_rel.replace(' ', '%20')
        
        # Replace in content (handle both %20 and space versions)
        content = content.replace(old_path_encoded, new_path_encoded)
        # Also replace if HTML already has the space version
        content = content.replace(old_rel, new_path_encoded)
    
    if content != original_content:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    base_dir = 'webflow-site'
    
    print("🔍 Finding files with URL encoding issues...")
    files_to_fix = find_files_with_encoding(os.path.join(base_dir, 'assets'))
    
    if not files_to_fix:
        print("✅ No files with %20 encoding found!")
        return
    
    print(f"   Found {len(files_to_fix)} files with %20 encoding")
    
    print("\n📝 Renaming files...")
    file_mappings = []
    renamed_count = 0
    
    for file_path in files_to_fix:
        result = rename_file(file_path)
        if result:
            old_path, new_path = result
            file_mappings.append((old_path, new_path))
            renamed_count += 1
            print(f"   ✓ {os.path.basename(old_path)} → {os.path.basename(new_path)}")
    
    print(f"\n✅ Renamed {renamed_count} files")
    
    if not file_mappings:
        print("No files needed renaming.")
        return
    
    print("\n✏️  Updating HTML references...")
    html_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    updated_count = 0
    for html_file in html_files:
        if update_html_references(html_file, file_mappings):
            updated_count += 1
    
    print(f"✅ Updated {updated_count} HTML files")
    print("\n🎉 All URL encoding issues fixed!")

if __name__ == '__main__':
    main()

