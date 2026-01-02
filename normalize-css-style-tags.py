#!/usr/bin/env python3
"""
Normalize CSS indentation inside <style> tags and remove blank lines after opening tag
"""

import re
import sys
from pathlib import Path

def normalize_style_tags(content):
    """Normalize CSS inside <style> tags"""
    # Pattern to match <style> tags and their content
    style_pattern = r'(<style[^>]*>)(.*?)(</style>)'
    
    def normalize_style(match):
        open_tag = match.group(1)
        css_content = match.group(2)
        close_tag = match.group(3)
        
        # Remove leading/trailing whitespace and blank lines
        css_content = css_content.strip()
        
        # Remove blank line immediately after opening tag
        # Split into lines and process
        lines = css_content.split('\n')
        
        # Remove leading blank lines
        while lines and not lines[0].strip():
            lines.pop(0)
        
        # Normalize indentation - find minimum indentation (excluding blank lines)
        non_blank_lines = [line for line in lines if line.strip()]
        if non_blank_lines:
            min_indent = min(len(line) - len(line.lstrip()) for line in non_blank_lines)
            # Normalize to 2 spaces
            normalized_lines = []
            for line in lines:
                if line.strip():
                    # Remove existing indentation and add 2 spaces
                    normalized_lines.append('  ' + line.lstrip())
                else:
                    normalized_lines.append('')
            css_content = '\n'.join(normalized_lines)
        else:
            css_content = ''
        
        return open_tag + '\n' + css_content + '\n' + close_tag
    
    # Replace all <style> tags
    return re.sub(style_pattern, normalize_style, content, flags=re.DOTALL)

def normalize_file(filepath):
    """Normalize CSS in a single HTML file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        normalized = normalize_style_tags(content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(normalized)
        
        return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False

def normalize_all_html(directory='.'):
    """Normalize CSS in all HTML files"""
    print(f"Normalizing CSS in <style> tags in {directory}...")
    processed_count = 0
    skipped_count = 0
    
    # Find all HTML files, excluding those in 'ofelia-original' and 'webflow-site' subdirectories
    html_files = [
        p for p in Path(directory).rglob('*.html')
        if not any(part in p.parts for part in ['ofelia-original', 'webflow-site'])
    ]

    for filepath in html_files:
        print(f"Processing {filepath}...")
        if normalize_file(filepath):
            processed_count += 1
        else:
            skipped_count += 1
    print(f"\n✓ Processed {processed_count} files")
    print(f"⊘ Skipped {skipped_count} files (error)")

if __name__ == "__main__":
    normalize_all_html()







