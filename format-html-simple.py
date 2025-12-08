#!/usr/bin/env python3
"""
Simple HTML formatter using regex - no external dependencies
"""

import os
import re
import sys
from pathlib import Path

def format_html_simple(content):
    """Format HTML with basic indentation"""
    # Add newlines after tags
    content = re.sub(r'><', '>\n<', content)
    
    # Add newlines after closing tags
    content = re.sub(r'</([^>]+)>', r'</\1>\n', content)
    
    # Clean up multiple newlines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Basic indentation
    lines = content.split('\n')
    formatted = []
    indent = 0
    indent_size = 2
    
    for line in lines:
        line = line.strip()
        if not line:
            formatted.append('')
            continue
        
        # Decrease indent for closing tags
        if line.startswith('</'):
            indent = max(0, indent - indent_size)
        
        # Add indented line
        formatted.append(' ' * indent + line)
        
        # Increase indent for opening tags (but not self-closing)
        if line.startswith('<') and not line.startswith('</') and not line.endswith('/>') and not line.startswith('<!') and not line.startswith('<?'):
            # Don't indent for single-line elements
            if '>' in line and not line.startswith('<script') and not line.startswith('<style'):
                pass
            else:
                indent += indent_size
    
    return '\n'.join(formatted)

def format_html_file(filepath):
    """Format a single HTML file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Only format if it's minified (no newlines after tags)
        if '\n<' not in content[:500]:
            formatted = format_html_simple(content)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(formatted)
            
            return True
        return False
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
    skipped = 0
    
    for html_file in html_files:
        if format_html_file(html_file):
            formatted += 1
            if formatted % 10 == 0:
                print(f"  Formatted {formatted} files...")
        else:
            skipped += 1
    
    print(f"\n✓ Formatted {formatted} files")
    print(f"⊘ Skipped {skipped} files (already formatted)")
    
    return formatted, skipped

if __name__ == '__main__':
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    format_all_html(directory)

