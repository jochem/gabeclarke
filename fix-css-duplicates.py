#!/usr/bin/env python3
"""
Fix CSS duplicates and normalize formatting in <style> tags
"""

import re
import sys
from pathlib import Path

def normalize_and_format_css(css_text):
    """Normalize CSS by removing duplicates and formatting properly"""
    css_text = css_text.strip()
    if not css_text:
        return ''
    
    # First, remove duplicate property:value pairs that appear consecutively
    # This handles cases like "prop: val prop: val" on the same line
    # Process line by line to handle already-formatted CSS
    lines = css_text.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Check if this line has duplicate properties
        # Find all property:value patterns
        prop_value_pattern = r'([a-zA-Z][a-zA-Z0-9-]*)\s*:\s*([^;{}]+?)(?=\s+[a-zA-Z][a-zA-Z0-9-]*\s*:|;|{|}|$)'
        matches = list(re.finditer(prop_value_pattern, line))
        
        if len(matches) > 1:
            # Check for duplicates
            seen = {}
            result_parts = []
            last_pos = 0
            
            for match in matches:
                prop = match.group(1)
                val = match.group(2).strip()
                key = prop + ':' + val
                
                # Skip if duplicate
                if key in seen:
                    continue
                
                seen[key] = True
                if match.start() > last_pos:
                    result_parts.append(line[last_pos:match.start()])
                result_parts.append(match.group(0))
                last_pos = match.end()
            
            if last_pos < len(line):
                result_parts.append(line[last_pos:])
            
            if result_parts:
                line = ''.join(result_parts)
        
        fixed_lines.append(line)
    
    # Rejoin and normalize whitespace
    css_text = '\n'.join(fixed_lines)
    css_text = re.sub(r'\s+', ' ', css_text)
    
    # Now split by semicolons for formatting
    statements = css_text.split(';')
    normalized_statements = []
    
    for stmt in statements:
        stmt = stmt.strip()
        if not stmt:
            continue
        
        # Find all property:value pairs in this statement
        # Match property-name: value (value until next property or end)
        prop_pattern = r'([a-zA-Z][a-zA-Z0-9-]*)\s*:\s*([^;{}]+?)(?=\s*[a-zA-Z][a-zA-Z0-9-]*\s*:|;|{|}|$)'
        
        matches = list(re.finditer(prop_pattern, stmt))
        if len(matches) > 1:
            # Check for duplicates
            seen = {}
            result_parts = []
            last_pos = 0
            
            for match in matches:
                prop = match.group(1)
                val = match.group(2).strip()
                key = prop + ':' + val
                
                # Skip if we've seen this exact property:value
                if key in seen:
                    continue
                
                seen[key] = True
                # Add text from last position to start of this match
                if match.start() > last_pos:
                    result_parts.append(stmt[last_pos:match.start()])
                # Add this property:value
                result_parts.append(match.group(0))
                last_pos = match.end()
            
            # Add remaining text
            if last_pos < len(stmt):
                result_parts.append(stmt[last_pos:])
            
            if result_parts:
                stmt = ''.join(result_parts).strip()
        
        normalized_statements.append(stmt)
    
    # Rejoin with semicolons
    normalized_css = '; '.join(normalized_statements)
    if normalized_css and not normalized_css.endswith(';'):
        normalized_css += ';'
    
    # Now format with proper indentation
    result = []
    indent_level = 0
    i = 0
    in_string = False
    string_char = None
    current_line = []
    
    while i < len(normalized_css):
        char = normalized_css[i]
        
        # Handle strings
        if char in ['"', "'"] and (i == 0 or normalized_css[i-1] != '\\'):
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
    
    # Remove trailing whitespace
    lines = [line.rstrip() for line in formatted.split('\n')]
    formatted = '\n'.join(lines)
    
    return formatted.strip()

def fix_css_in_style_tags_in_file(filepath):
    """Fix CSS duplicates in <style> tags"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Find all <style> tags
        style_pattern = r'(<style[^>]*>)(.*?)(</style>)'
        
        def fix_style_tag(match):
            style_tag_start = match.group(1)
            css_content = match.group(2)
            style_tag_end = match.group(3)
            
            if css_content.strip():
                fixed_css = normalize_and_format_css(css_content)
                if fixed_css:
                    return f'{style_tag_start}\n{fixed_css}\n  {style_tag_end}'
            
            return match.group(0)
        
        content = re.sub(style_pattern, fix_style_tag, content, flags=re.DOTALL)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False

def fix_all_html(directory='.'):
    """Fix CSS in all HTML files"""
    html_files = [
        p for p in Path(directory).rglob('*.html')
        if not any(part in p.parts for part in ['ofelia-original', 'webflow-site'])
    ]
    
    print(f"Found {len(html_files)} HTML files to process...")
    
    processed = 0
    modified = 0
    
    for html_file in html_files:
        if fix_css_in_style_tags_in_file(html_file):
            modified += 1
        processed += 1
        if processed % 10 == 0:
            print(f"  Processed {processed} files... ({modified} modified)")
    
    print(f"\n✓ Processed {processed} files")
    print(f"  {modified} files modified")
    
    return processed, modified

if __name__ == '__main__':
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    fix_all_html(directory)
