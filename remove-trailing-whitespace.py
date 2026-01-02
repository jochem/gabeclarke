#!/usr/bin/env python3
"""
Remove trailing whitespace from HTML files
"""

import sys
from pathlib import Path

def remove_trailing_whitespace(filepath):
    """Remove trailing whitespace from each line"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        modified_lines = []
        modified = False
        
        for line in lines:
            # Remove trailing whitespace (spaces and tabs)
            original_line = line
            line = line.rstrip()
            
            # If line had trailing whitespace, add back newline
            if original_line != line:
                line += '\n'
                modified = True
            
            modified_lines.append(line)
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(modified_lines)
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False

def fix_all_html(directory='.'):
    """Remove trailing whitespace from all HTML files"""
    html_files = [
        p for p in Path(directory).rglob('*.html')
        if not any(part in p.parts for part in ['ofelia-original', 'webflow-site', '.git'])
    ]
    
    print(f"Found {len(html_files)} HTML files to process...")
    
    processed = 0
    modified = 0
    failed = 0
    
    for html_file in html_files:
        try:
            if remove_trailing_whitespace(html_file):
                modified += 1
            processed += 1
            if processed % 10 == 0:
                print(f"  Processed {processed} files... ({modified} modified)")
        except Exception as e:
            print(f"Error processing {html_file}: {e}", file=sys.stderr)
            failed += 1
    
    print(f"\n✓ Processed {processed} files")
    print(f"  {modified} files modified")
    if failed > 0:
        print(f"✗ Failed to process {failed} files")
    
    return processed, modified, failed

if __name__ == '__main__':
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    fix_all_html(directory)







