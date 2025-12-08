#!/usr/bin/env python3
"""
Fix all malformed HTML entities and encoding issues for better readability in diffs
"""

import re
import sys
from pathlib import Path

def fix_encoding_issues_in_file(filepath):
    """Fix all encoding issues in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Fix malformed HTML entities BEFORE decoding
        # Replace &#194; (which is Â, often part of encoding errors) with space
        content = re.sub(r'&#194;', ' ', content)
        
        # Remove replacement characters (U+FFFD) that appear as
        content = content.replace('\ufffd', '')
        content = content.replace('', '')
        
        # Fix other common malformed entity patterns
        # These are often Windows-1252 to UTF-8 encoding errors
        malformed_replacements = {
            r'&#226;&#8364;&#8220;': '–',  # en dash
            r'&#226;&#8364;&#162;': '•',  # bullet
            r'&#226;&#8364;&#8482;': '™',  # trademark
            r'&#226;&#8364;&#8221;': '—',  # em dash
            r'&#195;&#8220;': 'Ö',
            r'&#195;&#164;': 'ä',
            r'&#195;&#188;': 'ü',
            r'&#195;&#179;': 'ó',
        }
        
        for pattern, replacement in malformed_replacements.items():
            content = re.sub(pattern, replacement, content)
        
        # Decode remaining HTML entities
        import html
        content = html.unescape(content)
        
        # Fix common mojibake patterns (garbled characters after decoding)
        mojibake_replacements = {
            'â€"': '–',  # en dash
            'â€"': '—',  # em dash
            'â€¢': '•',  # bullet
            'â€"': '™',  # trademark
            'â€™': ''',  # right single quotation mark
            'â€˜': ''',  # left single quotation mark
            'â€œ': '"',  # left double quotation mark
            'â€"': '"',  # right double quotation mark
            'â€¦': '…',  # ellipsis
            'Ã"': 'Ö',
            'Ã¤': 'ä',
            'Ã¼': 'ü',
            'Ã³': 'ó',
        }
        
        for garbled, correct in mojibake_replacements.items():
            content = content.replace(garbled, correct)
        
        # Remove any remaining replacement characters
        content = content.replace('\ufffd', '')
        content = content.replace('', '')
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False

def fix_all_html(directory='.'):
    """Fix encoding issues in all HTML files"""
    html_files = [
        p for p in Path(directory).rglob('*.html')
        if not any(part in p.parts for part in ['ofelia-original', 'webflow-site'])
    ]
    
    print(f"Found {len(html_files)} HTML files to process...")
    
    processed = 0
    failed = 0
    
    for html_file in html_files:
        if fix_encoding_issues_in_file(html_file):
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
    fix_all_html(directory)

