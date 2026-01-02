#!/usr/bin/env python3
"""
Build HTML files from templates.

This script reads HTML files, extracts page-specific content, and rebuilds them
using the templates in the templates/ directory.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Optional

# Template directory
TEMPLATES_DIR = Path('templates')

# Load templates
def load_template(name: str) -> str:
    """Load a template file."""
    template_path = TEMPLATES_DIR / name
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    return template_path.read_text(encoding='utf-8')

def extract_page_metadata(html_content: str) -> Dict[str, str]:
    """Extract page-specific metadata from HTML content."""
    metadata = {}
    
    # Extract title
    title_match = re.search(r'<title>(.*?)</title>', html_content, re.DOTALL | re.IGNORECASE)
    if title_match:
        metadata['title'] = title_match.group(1).strip()
    
    # Extract description
    desc_match = re.search(r'<meta\s+content="([^"]*)"\s+name="description"', html_content, re.IGNORECASE)
    if desc_match:
        metadata['description'] = desc_match.group(1).strip()
    
    # Extract page ID
    page_id_match = re.search(r'data-wf-page="([^"]*)"', html_content, re.IGNORECASE)
    if page_id_match:
        metadata['page_id'] = page_id_match.group(1).strip()
    
    # Extract page-specific styles (between <style> tags that come after CSS link)
    # Look for style tags that contain data-w-id (page-specific animations)
    style_match = re.search(r'<link[^>]*css/gabe-clarke[^>]*>.*?<style[^>]*>(.*?)</style>', html_content, re.DOTALL | re.IGNORECASE)
    if style_match:
        styles = style_match.group(1).strip()
        if 'data-w-id' in styles:
            metadata['styles'] = f'  <style type="text/css">\n{styles}\n  </style>'
        else:
            metadata['styles'] = ''
    else:
        metadata['styles'] = ''
    
    return metadata

def extract_body_content(html_content: str) -> str:
    """Extract the main body content (excluding navigation and footer)."""
    # Find body tag
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL | re.IGNORECASE)
    if not body_match:
        return ''
    
    body = body_match.group(1)
    
    # Remove navigation (navbar)
    body = re.sub(r'<div[^>]*data-collapse="all"[^>]*class="navbar[^"]*"[^>]*>.*?</div>\s*</div>', '', body, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove footer (footer-1-meta-links and back-to-top)
    body = re.sub(r'<div[^>]*class="[^"]*footer-1-meta-links[^"]*"[^>]*>.*?</div>\s*</div>\s*</div>', '', body, flags=re.DOTALL | re.IGNORECASE)
    body = re.sub(r'<a[^>]*id="[^"]*back-to-top[^"]*"[^>]*>.*?</div>\s*</div>\s*</div>', '', body, flags=re.DOTALL | re.IGNORECASE)
    
    return body.strip()

def determine_asset_path(filepath: str) -> str:
    """Determine the asset path prefix based on file location."""
    depth = filepath.count('/') - (1 if filepath.startswith('./') else 0)
    if depth == 0:
        return ''  # Root level
    return '../' * depth

def determine_nav_variables(filepath: str, base_url: str) -> Dict[str, str]:
    """Determine navigation variables based on current page."""
    nav_vars = {
        'NAV_HOME_URL': 'index.html',
        'NAV_ABOUT_URL': 'about/about-1.html',
        'NAV_PROJECTS_URL': 'pages/works.html',
        'NAV_SHOP_URL': 'pages/shop.html',
        'NAV_CONTACT_URL': 'contact/contact-1.html',
        'NAV_HOME_ACTIVE': '',
        'NAV_ABOUT_ACTIVE': '',
        'NAV_PROJECTS_ACTIVE': '',
        'NAV_SHOP_ACTIVE': '',
        'NAV_CONTACT_ACTIVE': '',
        'NAV_HOME_CURRENT': '',
        'NAV_ABOUT_CURRENT': '',
        'NAV_PROJECTS_CURRENT': '',
        'NAV_SHOP_CURRENT': '',
        'NAV_CONTACT_CURRENT': '',
    }
    
    # Adjust URLs based on file depth
    depth = filepath.count('/') - (1 if filepath.startswith('./') else 0)
    if depth > 0:
        prefix = '../' * depth
        nav_vars['NAV_HOME_URL'] = prefix + 'index.html'
        nav_vars['NAV_ABOUT_URL'] = prefix + 'about/about-1.html'
        nav_vars['NAV_PROJECTS_URL'] = prefix + 'pages/works.html'
        nav_vars['NAV_SHOP_URL'] = prefix + 'pages/shop.html'
        nav_vars['NAV_CONTACT_URL'] = prefix + 'contact/contact-1.html'
    
    # Determine active page
    if 'index.html' in filepath or 'home/' in filepath:
        nav_vars['NAV_HOME_ACTIVE'] = 'aria-current="page"'
        nav_vars['NAV_HOME_CURRENT'] = ' w--current'
    elif 'about/' in filepath:
        nav_vars['NAV_ABOUT_ACTIVE'] = 'aria-current="page"'
        nav_vars['NAV_ABOUT_CURRENT'] = ' w--current'
    elif 'works' in filepath or 'work' in filepath:
        nav_vars['NAV_PROJECTS_ACTIVE'] = 'aria-current="page"'
        nav_vars['NAV_PROJECTS_CURRENT'] = ' w--current'
    elif 'shop' in filepath:
        nav_vars['NAV_SHOP_ACTIVE'] = 'aria-current="page"'
        nav_vars['NAV_SHOP_CURRENT'] = ' w--current'
    elif 'contact/' in filepath:
        nav_vars['NAV_CONTACT_ACTIVE'] = 'aria-current="page"'
        nav_vars['NAV_CONTACT_CURRENT'] = ' w--current'
    
    return nav_vars

def build_html_file(filepath: str, output_dir: Optional[str] = None) -> None:
    """Build an HTML file from templates."""
    # Read original file
    with open(filepath, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Extract metadata
    metadata = extract_page_metadata(original_content)
    
    # Extract body content
    body_content = extract_body_content(original_content)
    
    # Determine asset path
    asset_path = determine_asset_path(filepath)
    
    # Determine navigation variables
    nav_vars = determine_nav_variables(filepath, '')
    
    # Load templates
    header_template = load_template('header.html')
    nav_template = load_template('navigation.html')
    footer_template = load_template('footer.html')
    closing_template = load_template('closing.html')
    
    # Replace header variables
    header = header_template
    header = header.replace('{{PAGE_ID}}', metadata.get('page_id', ''))
    header = header.replace('{{PAGE_TITLE}}', metadata.get('title', ''))
    header = header.replace('{{PAGE_DESCRIPTION}}', metadata.get('description', ''))
    header = header.replace('{{PAGE_STYLES}}', metadata.get('styles', ''))
    header = header.replace('{{ASSET_PATH}}', asset_path)
    
    # Replace navigation variables
    nav = nav_template
    for key, value in nav_vars.items():
        nav = nav.replace(f'{{{{{key}}}}}', value)
    
    # Replace closing variables
    closing = closing_template
    closing = closing.replace('{{ASSET_PATH}}', asset_path)
    
    # Build final HTML
    final_html = header + '\n\n<body class="body">\n'
    
    # Add layout wrapper if present in original
    if '<div style="opacity:0" class="layout">' in original_content:
        final_html += '  <div style="opacity:0" class="layout">\n'
    
    final_html += body_content + '\n\n'
    
    # Add navigation
    final_html += '  ' + nav + '\n'
    
    # Close layout wrapper if opened
    if '<div style="opacity:0" class="layout">' in original_content:
        final_html += '  </div>\n'
    
    # Add footer
    final_html += '  ' + footer_template + '\n'
    
    # Add closing
    final_html += closing
    
    # Write output
    if output_dir:
        output_path = Path(output_dir) / filepath
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(final_html, encoding='utf-8')
        print(f"Built: {output_path}")
    else:
        # Write back to original file
        Path(filepath).write_text(final_html, encoding='utf-8')
        print(f"Rebuilt: {filepath}")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Build HTML files from templates')
    parser.add_argument('files', nargs='*', help='HTML files to build (default: all HTML files)')
    parser.add_argument('--output', '-o', help='Output directory (default: overwrite original files)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be built without writing')
    
    args = parser.parse_args()
    
    # Find HTML files
    if args.files:
        html_files = args.files
    else:
        html_files = []
        for root, dirs, files in os.walk('.'):
            if '.git' in root or 'ofelia-original' in root or 'webflow-site' in root or 'templates' in root:
                continue
            for file in files:
                if file.endswith('.html'):
                    html_files.append(os.path.join(root, file))
    
    print(f"Found {len(html_files)} HTML files to process\n")
    
    for filepath in html_files:
        try:
            if args.dry_run:
                print(f"Would build: {filepath}")
            else:
                build_html_file(filepath, args.output)
        except Exception as e:
            print(f"Error processing {filepath}: {e}")

if __name__ == '__main__':
    main()







