#!/usr/bin/env python3
"""
Normalize CSS indentation inside <style> tags to be consistent
"""

import re
import sys
from pathlib import Path

def normalize_css_in_style_tags(content):
    """Normalize CSS indentation inside <style> tags"""
    # Pattern to match <style> tags and their content
    style_pattern = r'(<style[^>]*>)(.*?)(</style>)'
    
    def normalize_style(match):
        open_tag = match.group(1)
        css_content = match.group(2)
        close_tag = match.group(3)
        
        # Skip if CSS is minified (no newlines or very long lines)
        if '\n' not in css_content.strip() or len(css_content.strip()) > 500:
            return match.group(0)  # Return as-is for minified CSS
        
        # Split CSS into lines
        lines = css_content.split('\n')
        
        # Find the base indentation level (from the <style> tag)
        # Count leading spaces/tabs from the line containing <style>
        base_indent = 0
        for i, line in enumerate(lines):
            if '<style' in line:
                base_indent = len(line) - len(line.lstrip())
                break
        
        # Normalize CSS indentation to 2 spaces per level
        normalized_lines = []
        indent_level = 0
        indent_size = 2
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                normalized_lines.append('')
                continue
            
            # Decrease indent for closing braces
            if stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)
            
            # Add normalized indentation
            normalized_indent = ' ' * (base_indent + indent_level * indent_size)
            normalized_lines.append(normalized_indent + stripped)
            
            # Increase indent for opening braces (but not if it's on the same line as a selector)
            if '{' in stripped and not stripped.endswith('{'):
                # Opening brace on same line, increase indent for next line
                indent_level += 1
            elif stripped.endswith('{'):
                # Opening brace at end, increase indent for next line
                indent_level += 1
        
        normalized_css = '\n'.join(normalized_lines)
        return open_tag + normalized_css + close_tag
    
    # Apply normalization to all <style> tags
    normalized_content = re.sub(style_pattern, normalize_style, content, flags=re.DOTALL)
    
    return normalized_content

def normalize_file(filepath):
    """Normalize CSS indentation in a single HTML file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        normalized = normalize_css_in_style_tags(content)
        
        if normalized != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(normalized)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False

def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    html_files = list(Path(directory).rglob('*.html'))
    
    # Exclude subdirectories
    html_files = [f for f in html_files if 'ofelia-original' not in str(f) and 'webflow-site' not in str(f)]
    
    normalized_count = 0
    for html_file in html_files:
        if normalize_file(html_file):
            normalized_count += 1
    
    print(f"Normalized CSS indentation in {normalized_count} files")

if __name__ == "__main__":
    main()

