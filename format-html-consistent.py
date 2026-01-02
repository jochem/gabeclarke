#!/usr/bin/env python3
"""
Consistent HTML formatter that ensures identical formatting across files
Uses tidy with consistent settings and post-processes to ensure uniformity
"""

import subprocess
import sys
from pathlib import Path

def format_html_file(filepath):
    """Format a single HTML file with consistent settings"""
    try:
        # Use tidy with consistent settings
        result = subprocess.run(
            [
                'tidy', '-i', '-m', '-w', '120',
                '--indent-spaces', '2',
                '--tidy-mark', 'no',
                '--wrap', '0',
                '--drop-empty-paras', 'no',
                '--quote-marks', 'yes',
                '--quote-nbsp', 'no',
                '--show-warnings', 'no',
                '--show-errors', '0',
                '--force-output', 'yes',
                str(filepath)
            ],
            capture_output=True,
            text=True
        )
        
        # Read the formatted file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Post-process to ensure consistency:
        import re
        
        # 1. Normalize comments - always put each comment on its own line
        # Split multiple comments on same line
        content = re.sub(r'(<!--[^>]+-->)(<!--[^>]+-->)', r'\1\n\2', content)
        # Ensure comments are on separate lines from other content
        content = re.sub(r'(<!--[^>]+-->)([^\n<])', r'\1\n\2', content)
        content = re.sub(r'([^\n>])(<!--[^>]+-->)', r'\1\n\2', content)
        
        # 2. Ensure DOCTYPE is on its own line
        content = re.sub(r'<!DOCTYPE html>', '<!DOCTYPE html>', content)
        
        # 3. Ensure blank line after DOCTYPE, before html tag
        content = re.sub(r'(<!DOCTYPE html>\n)(<!--[^>]+-->\n)(<!--[^>]+-->\n)(<html)', r'\1\2\3\n\4', content)
        content = re.sub(r'(<!DOCTYPE html>\n)(<html)', r'\1\n\2', content)
        
        # 4. Normalize whitespace - max 2 blank lines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
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

