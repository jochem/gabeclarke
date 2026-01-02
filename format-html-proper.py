#!/usr/bin/env python3
"""
Proper HTML formatter that respects HTML structure and indentation
Uses html.parser to properly format HTML with correct indentation
"""

import html.parser
import re
import sys
from pathlib import Path

class HTMLFormatter(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.output = []
        self.indent_level = 0
        self.indent_size = 2
        self.in_script = False
        self.in_style = False
        self.current_tag = None
        
    def handle_starttag(self, tag, attrs):
        # Check if we're entering script or style
        if tag in ('script', 'style'):
            self.in_script = (tag == 'script')
            self.in_style = (tag == 'style')
        
        # Format attributes
        attrs_str = ' '.join(f'{k}="{v}"' if v else k for k, v in attrs)
        if attrs_str:
            tag_str = f'<{tag} {attrs_str}>'
        else:
            tag_str = f'<{tag}>'
        
        # Self-closing tags
        self_closing = tag in ('meta', 'link', 'img', 'br', 'hr', 'input', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr')
        
        if not self_closing:
            self.output.append(' ' * self.indent_level + tag_str)
            self.indent_level += self.indent_size
            self.current_tag = tag
        else:
            self.output.append(' ' * self.indent_level + tag_str)
    
    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.in_script = False
            self.in_style = False
        
        # Don't decrease indent for self-closing tags
        if tag not in ('meta', 'link', 'img', 'br', 'hr', 'input'):
            self.indent_level = max(0, self.indent_level - self.indent_size)
            self.output.append(' ' * self.indent_level + f'</{tag}>')
            self.current_tag = None
    
    def handle_data(self, data):
        if self.in_script or self.in_style:
            # Preserve script/style content as-is but indent it
            lines = data.split('\n')
            for line in lines:
                if line.strip():
                    self.output.append(' ' * self.indent_level + line)
        else:
            # Format text content
            data = data.strip()
            if data:
                # Check if this is inline text (should be on same line as tag)
                if self.current_tag and data and len(data) < 100:
                    # Try to put on same line if short
                    if self.output and not self.output[-1].strip().endswith('>'):
                        self.output[-1] += data
                    else:
                        self.output.append(' ' * self.indent_level + data)
                else:
                    # Multi-line text
                    for line in data.split('\n'):
                        if line.strip():
                            self.output.append(' ' * self.indent_level + line.strip())
    
    def handle_comment(self, data):
        self.output.append(' ' * self.indent_level + f'<!--{data}-->')
    
    def handle_decl(self, decl):
        self.output.append(decl)

def format_html_file(filepath):
    """Format a single HTML file with proper indentation"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already formatted (has proper line breaks)
        if '\n<' in content[:500] and content.count('\n') > 10:
            # Might already be formatted, but let's reformat it properly
            pass
        
        # Parse and format
        formatter = HTMLFormatter()
        formatter.feed(content)
        formatted = '\n'.join(formatter.output)
        
        # Clean up extra blank lines
        formatted = re.sub(r'\n{3,}', '\n\n', formatted)
        
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
