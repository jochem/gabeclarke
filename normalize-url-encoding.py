#!/usr/bin/env python3
"""
Normalize URL encoding in HTML files for consistency in diffs.
Ensures all spaces in URLs are encoded as %20.
"""

import re
import sys
from pathlib import Path
from urllib.parse import quote, unquote

def normalize_url_encoding_in_file(filepath):
    """Normalize URL encoding in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Find all URL attributes (src, href, srcset, etc.)
        # Pattern matches: attribute="value" or attribute='value'
        url_attributes = ['src', 'href', 'srcset', 'data-src', 'data-href', 'action', 'formaction']
        
        for attr in url_attributes:
            # Match attribute="value" or attribute='value'
            # This regex handles both quoted and unquoted values
            pattern = rf'({attr}\s*=\s*["\'])([^"\']+)(["\'])'
            
            def normalize_url(match):
                quote_char = match.group(1)
                url = match.group(2)
                closing_quote = match.group(3)
                
                # Decode any existing encoding, then re-encode consistently
                # This ensures %20 is used for spaces, not + or other encodings
                try:
                    decoded = unquote(url)
                    # Re-encode, using %20 for spaces (not +)
                    normalized = quote(decoded, safe='/')
                    return f'{quote_char}{normalized}{closing_quote}'
                except:
                    # If decoding fails, return as-is
                    return match.group(0)
            
            content = re.sub(pattern, normalize_url, content)
        
        # Also handle srcset attribute which has a special format:
        # srcset="url1 width1, url2 width2, ..."
        srcset_pattern = r'(srcset\s*=\s*["\'])([^"\']+)(["\'])'
        
        def normalize_srcset(match):
            quote_char = match.group(1)
            srcset_value = match.group(2)
            closing_quote = match.group(3)
            
            # Split by comma, normalize each URL
            parts = srcset_value.split(',')
            normalized_parts = []
            
            for part in parts:
                part = part.strip()
                # Split URL and descriptor (e.g., "url 500w" or "url 500w, 2x")
                url_match = re.match(r'^(.+?)(\s+\d+[wx]?)$', part)
                if url_match:
                    url = url_match.group(1).strip()
                    descriptor = url_match.group(2)
                    try:
                        decoded = unquote(url)
                        normalized_url = quote(decoded, safe='/')
                        normalized_parts.append(f'{normalized_url}{descriptor}')
                    except:
                        normalized_parts.append(part)
                else:
                    # No descriptor, just normalize the URL
                    try:
                        decoded = unquote(part)
                        normalized_url = quote(decoded, safe='/')
                        normalized_parts.append(normalized_url)
                    except:
                        normalized_parts.append(part)
            
            return f'{quote_char}{", ".join(normalized_parts)}{closing_quote}'
        
        content = re.sub(srcset_pattern, normalize_srcset, content)
        
        # Only write if content changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False

def normalize_all_html(directory='.'):
    """Normalize URL encoding in all HTML files"""
    html_files = [
        p for p in Path(directory).rglob('*.html')
        if not any(part in p.parts for part in ['ofelia-original', 'webflow-site'])
    ]
    
    print(f"Found {len(html_files)} HTML files to process...")
    
    processed = 0
    modified = 0
    failed = 0
    
    for html_file in html_files:
        if normalize_url_encoding_in_file(html_file):
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
    normalize_all_html(directory)

