#!/usr/bin/env python3
"""
Format HTML files to make diffs readable
Uses BeautifulSoup to parse and format HTML
"""

import os
import sys
from pathlib import Path
from bs4 import BeautifulSoup

def format_html_file(filepath):
    """Format a single HTML file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        # Format with indentation
        formatted = soup.prettify(indent_width=2)
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted)
        
        return True
    except Exception as e:
        print(f"Error formatting {filepath}: {e}", file=sys.stderr)
        return False

def format_all_html(directory='.'):
    """Format all HTML files in directory and subdirectories"""
    html_files = list(Path(directory).rglob('*.html'))
    
    # Exclude backup directories
    html_files = [f for f in html_files if 'ofelia-original' not in str(f) and 'webflow-site' not in str(f)]
    
    print(f"Found {len(html_files)} HTML files to format...")
    
    formatted = 0
    failed = 0
    
    for html_file in html_files:
        if format_html_file(html_file):
            formatted += 1
            if formatted % 10 == 0:
                print(f"  Formatted {formatted} files...")
        else:
            failed += 1
    
    print(f"\n✓ Formatted {formatted} files")
    if failed > 0:
        print(f"✗ Failed to format {failed} files")
    
    return formatted, failed

if __name__ == '__main__':
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    format_all_html(directory)

