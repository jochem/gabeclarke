#!/usr/bin/env python3
"""
Format CSS inside <style> tags for better readability in diffs
"""

import re
import sys
from pathlib import Path

def format_css(css_text):
    """Format CSS with proper indentation and line breaks"""
    css_text = css_text.strip()
    if not css_text:
        return ''
    
    # Normalize: remove all existing formatting first
    # Replace all whitespace with single spaces
    css_text = re.sub(r'\s+', ' ', css_text)
    
    # Now format properly
    result = []
    i = 0
    indent_level = 0
    in_string = False
    string_char = None
    current_line = []
    
    while i < len(css_text):
        char = css_text[i]
        
        # Handle strings (don't format inside strings)
        if char in ['"', "'"] and (i == 0 or css_text[i-1] != '\\'):
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                in_string = False
                string_char = None
            current_line.append(char)
            i += 1
            continue
        
        if in_string:
            current_line.append(char)
            i += 1
            continue
        
        # Handle opening brace
        if char == '{':
            # Output current line if any
            if current_line:
                line_text = ''.join(current_line).strip()
                if line_text:
                    result.append('  ' * indent_level + line_text)
                current_line = []
            result.append('  ' * indent_level + '{')
            indent_level += 1
            i += 1
        
        # Handle closing brace
        elif char == '}':
            # Output current line if any
            if current_line:
                line_text = ''.join(current_line).strip()
                if line_text:
                    result.append('  ' * indent_level + line_text)
                current_line = []
            indent_level = max(0, indent_level - 1)
            result.append('  ' * indent_level + '}')
            i += 1
        
        # Handle semicolon
        elif char == ';':
            current_line.append(';')
            line_text = ''.join(current_line).strip()
            if line_text:
                result.append('  ' * indent_level + line_text)
            current_line = []
            i += 1
        
        # Regular character
        else:
            current_line.append(char)
            i += 1
    
    # Output any remaining line
    if current_line:
        line_text = ''.join(current_line).strip()
        if line_text:
            result.append('  ' * indent_level + line_text)
    
    formatted = '\n'.join(result)
    
    # Clean up multiple blank lines
    formatted = re.sub(r'\n{3,}', '\n\n', formatted)
    
    # Remove trailing whitespace from each line
    lines = [line.rstrip() for line in formatted.split('\n')]
    formatted = '\n'.join(lines)
    
    return formatted.strip()

def format_css_in_style_tags_in_file(filepath):
    """Format CSS inside <style> tags in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Find all <style> tags (with or without type attribute)
        style_pattern = r'(<style[^>]*>)(.*?)(</style>)'
        
        def format_style_tag(match):
            style_tag_start = match.group(1)
            css_content = match.group(2)
            style_tag_end = match.group(3)
            
            # Only format if there's actual CSS (not empty or just whitespace)
            if css_content.strip():
                formatted_css = format_css(css_content)
                if formatted_css:
                    return f'{style_tag_start}\n{formatted_css}\n  {style_tag_end}'
                else:
                    return match.group(0)
            else:
                return match.group(0)
        
        content = re.sub(style_pattern, format_style_tag, content, flags=re.DOTALL)
        
        # Only write if content changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False

def format_all_html(directory='.'):
    """Format CSS in style tags in all HTML files"""
    html_files = [
        p for p in Path(directory).rglob('*.html')
        if not any(part in p.parts for part in ['ofelia-original', 'webflow-site'])
    ]
    
    print(f"Found {len(html_files)} HTML files to process...")
    
    processed = 0
    modified = 0
    failed = 0
    
    for html_file in html_files:
        if format_css_in_style_tags_in_file(html_file):
            modified += 1
        processed += 1
        if processed % 10 == 0:
            print(f"  Processed {processed} files... ({modified} modified)")
    
    print(f"\n✓ Processed {processed} files")
    print(f"  {modified} files modified")
    if failed > 0:
        print(f"✗ Failed to process {failed} files")
    
    return processed, modified, failed

if __name__ == '__main__':
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    format_all_html(directory)
