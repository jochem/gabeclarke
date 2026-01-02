#!/usr/bin/env python3
"""
Fix URL encoding in HTML attributes (href, src, etc.)
Decodes things like https%3A// to https://
"""

import re
import sys
from pathlib import Path
from urllib.parse import unquote

def fix_url_encoding_in_file(filepath):
    """Fix URL encoding in HTML attributes"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Find all URL attributes (href, src, srcset, action, formaction, data-src, data-href)
        url_attributes = ['href', 'src', 'srcset', 'action', 'formaction', 'data-src', 'data-href']
        
        for attr in url_attributes:
            # Match attribute="value" or attribute='value'
            # Pattern: attr="..." or attr='...'
            pattern = rf'({attr}\s*=\s*["\'])([^"\']+)(["\'])'
            
            def decode_url(match):
                quote_char = match.group(1)
                url = match.group(2)
                closing_quote = match.group(3)
                
                # Decode URL encoding (like %3A to :)
                try:
                    decoded = unquote(url)
                    return f'{quote_char}{decoded}{closing_quote}'
                except:
                    # If decoding fails, return as-is
                    return match.group(0)
            
            content = re.sub(pattern, decode_url, content)
        
        # Also handle srcset which has format: "url1 width1, url2 width2"
        srcset_pattern = r'(srcset\s*=\s*["\'])([^"\']+)(["\'])'
        
        def decode_srcset(match):
            quote_char = match.group(1)
            srcset_value = match.group(2)
            closing_quote = match.group(3)
            
            # Split by comma, decode each URL
            parts = srcset_value.split(',')
            decoded_parts = []
            
            for part in parts:
                part = part.strip()
                # Split URL and descriptor (e.g., "url 500w" or "url 500w, 2x")
                url_match = re.match(r'^(.+?)(\s+\d+[wx]?)$', part)
                if url_match:
                    url = url_match.group(1).strip()
                    descriptor = url_match.group(2)
                    try:
                        decoded_url = unquote(url)
                        decoded_parts.append(f'{decoded_url}{descriptor}')
                    except:
                        decoded_parts.append(part)
                else:
                    # No descriptor, just decode the URL
                    try:
                        decoded_url = unquote(part)
                        decoded_parts.append(decoded_url)
                    except:
                        decoded_parts.append(part)
            
            return f'{quote_char}{", ".join(decoded_parts)}{closing_quote}'
        
        content = re.sub(srcset_pattern, decode_srcset, content)
        
        # Only write if content changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False

def fix_all_html(directory='.'):
    """Fix URL encoding in all HTML files"""
    html_files = [
        p for p in Path(directory).rglob('*.html')
        if not any(part in p.parts for part in ['ofelia-original', 'webflow-site'])
    ]
    
    print(f"Found {len(html_files)} HTML files to process...")
    
    processed = 0
    modified = 0
    failed = 0
    
    for html_file in html_files:
        if fix_url_encoding_in_file(html_file):
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
    fix_all_html(directory)







