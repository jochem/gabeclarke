#!/usr/bin/env python3
"""
Decode HTML entities to their actual Unicode characters for better readability in diffs
"""

import html
import re
import sys
from pathlib import Path

def decode_html_entities_in_file(filepath):
    """Decode HTML entities in a file and fix common encoding issues"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Decode all HTML entities
        decoded_content = html.unescape(content)
        
        # Fix common double-encoded/malformed entities
        # These are Windows-1252 to UTF-8 encoding errors
        # &#226;&#8364;&#8220; = "â€"" which should be em dash "—" or en dash "–"
        # &#226;&#8364;&#162; = "â€¢" which should be bullet "•"
        # &#226;&#8364;&#8482; = "â€"" which should be trademark "™"
        # &#195;&#8220; = "Ã"" which should be "Ö"
        # &#195;&#164; = "Ã¤" which should be "ä"
        # &#195;&#188; = "Ã¼" which should be "ü"
        # &#195;&#179; = "Ã³" which should be "ó"
        # &#39; = apostrophe "'"
        
        # Replace common malformed entities with correct characters
        replacements = {
            'â€"': '–',  # en dash (most common in titles)
            'â€"': '—',  # em dash
            'â€¢': '•',  # bullet
            'â€"': '™',  # trademark
            'Ã"': 'Ö',
            'Ã¤': 'ä',
            'Ã¼': 'ü',
            'Ã³': 'ó',
            '&#39;': "'",  # apostrophe
        }
        
        for old, new in replacements.items():
            decoded_content = decoded_content.replace(old, new)
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(decoded_content)
        
        return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False

def decode_all_html(directory='.'):
    """Decode HTML entities in all HTML files"""
    html_files = list(Path(directory).rglob('*.html'))
    
    # Exclude backup directories
    html_files = [f for f in html_files if 'ofelia-original' not in str(f) and 'webflow-site' not in str(f)]
    
    print(f"Found {len(html_files)} HTML files to process...")
    
    processed = 0
    failed = 0
    
    for html_file in html_files:
        if decode_html_entities_in_file(html_file):
            processed += 1
            if processed % 10 == 0:
                print(f"  Processed {processed} files...")
        else:
            failed += 1
    
    print(f"\n✓ Processed {processed} files")
    if failed > 0:
        print(f"✗ Failed to process {failed} files")
    
    return processed, failed

if __name__ == '__main__':
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    decode_all_html(directory)

