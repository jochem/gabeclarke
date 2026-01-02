#!/usr/bin/env python3
"""
Fix all malformed HTML entities in HTML files
"""

import html
import re
import sys
from pathlib import Path

def fix_malformed_entities_in_file(filepath):
    """Fix all malformed HTML entities in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        original_content = content
        
        # Map of malformed entity sequences to their correct Unicode characters
        # These are common double-encoded or malformed entities
        malformed_entity_map = {
            # Apostrophes and quotes
            '&#226;&#8222;&#162;': "'",  # Right single quotation mark / apostrophe
            '&#226;&#8364;&#162;': "'",  # Another variant
            '&#226;&#8364;&#8220;': '"',  # Left double quotation mark
            '&#226;&#8364;&#8221;': '"',  # Right double quotation mark
            '&#226;&#8364;&#8222;': '"',  # Another variant
            
            # Accented characters (double-encoded)
            '&#195;&#169;': 'é',  # é
            '&#195;&#8211;': 'Ó',  # Ó
            '&#195;&#164;': 'ä',  # ä
            '&#195;&#188;': 'ü',  # ü
            '&#195;&#161;': 'á',  # á
            '&#195;&#173;': 'í',  # í
            '&#195;&#179;': 'ó',  # ó
            '&#195;&#186;': 'ú',  # ú
            '&#195;&#177;': 'ñ',  # ñ
            '&#195;&#167;': 'ç',  # ç
            '&#195;&#160;': 'à',  # à
            '&#195;&#168;': 'è',  # è
            '&#195;&#172;': 'ì',  # ì
            '&#195;&#178;': 'ò',  # ò
            '&#195;&#185;': 'ù',  # ù
            
            # Other common malformed entities
            '&#226;&#8364;&#8220;': '–',  # En dash
            '&#226;&#8364;&#8221;': '—',  # Em dash
            '&#226;&#8364;&#8222;': '…',  # Ellipsis
            '&#226;&#8364;&#162;': '•',  # Bullet
            '&#226;&#8364;&#8482;': '™',  # Trademark
            '&#226;&#8364;&#174;': '®',  # Registered trademark
            '&#226;&#8364;&#169;': '©',  # Copyright
        }
        
        # Replace all malformed entity sequences
        for malformed, correct in malformed_entity_map.items():
            content = content.replace(malformed, correct)
        
        # Also handle patterns like &#226;&#8222;&#162; (three separate entities)
        # These are often the result of double encoding
        
        # Fix common patterns of malformed entities
        # Pattern: &#226; followed by &#8222; followed by &#162; = apostrophe
        content = re.sub(r'&#226;&#8222;&#162;', "'", content)
        content = re.sub(r'&#226;&#8364;&#162;', "'", content)
        content = re.sub(r'&#226;&#8364;&#8220;', '"', content)
        content = re.sub(r'&#226;&#8364;&#8221;', '"', content)
        
        # Fix accented characters (double-encoded)
        content = re.sub(r'&#195;&#169;', 'é', content)
        content = re.sub(r'&#195;&#8211;', 'Ó', content)
        content = re.sub(r'&#195;&#164;', 'ä', content)
        content = re.sub(r'&#195;&#188;', 'ü', content)
        content = re.sub(r'&#195;&#161;', 'á', content)
        content = re.sub(r'&#195;&#173;', 'í', content)
        content = re.sub(r'&#195;&#179;', 'ó', content)
        content = re.sub(r'&#195;&#186;', 'ú', content)
        content = re.sub(r'&#195;&#177;', 'ñ', content)
        content = re.sub(r'&#195;&#167;', 'ç', content)
        content = re.sub(r'&#195;&#160;', 'à', content)
        content = re.sub(r'&#195;&#168;', 'è', content)
        content = re.sub(r'&#195;&#172;', 'ì', content)
        content = re.sub(r'&#195;&#178;', 'ò', content)
        content = re.sub(r'&#195;&#185;', 'ù', content)
        
        # Now decode any remaining valid HTML entities
        # But be careful - we want to decode valid entities like &#39; but not break what we just fixed
        # Use html.unescape() which will handle standard entities
        decoded_content = html.unescape(content)
        
        # Fix any mojibake that might have resulted from the decoding
        # Common mojibake patterns
        mojibake_fixes = {
            'â€"': '–',  # En dash
            'â€"': '—',  # Em dash
            'â€¢': '•',  # Bullet
            'â„¢': '™',  # Trademark
            'â€™': "'",  # Right single quotation mark
            'â€œ': '"',  # Left double quotation mark
            'â€': '"',  # Right double quotation mark
            'â€¦': '…',  # Ellipsis
        }
        
        for mojibake, correct in mojibake_fixes.items():
            decoded_content = decoded_content.replace(mojibake, correct)
        
        # Only write if content changed
        if decoded_content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(decoded_content)
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False

def fix_all_html(directory='.'):
    """Fix malformed entities in all HTML files"""
    html_files = [
        p for p in Path(directory).rglob('*.html')
        if not any(part in p.parts for part in ['ofelia-original', 'webflow-site'])
    ]
    
    print(f"Found {len(html_files)} HTML files to process...")
    
    processed = 0
    modified = 0
    failed = 0
    
    for html_file in html_files:
        if fix_malformed_entities_in_file(html_file):
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







