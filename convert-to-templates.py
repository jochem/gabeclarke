#!/usr/bin/env python3
"""
Convert HTML files to use Jinja2 templates.
Extracts content between <body> and footer/navigation, and wraps it in template includes.
"""

import os
import re
from pathlib import Path
from bs4 import BeautifulSoup

def get_asset_path(file_path):
    """Calculate asset path based on file depth."""
    depth = str(file_path).count('/') - 1  # Subtract 1 for the file itself
    if depth <= 0:
        return ''
    return '../' * depth

def extract_page_styles(html_content):
    """Extract page-specific styles from head."""
    soup = BeautifulSoup(html_content, 'html.parser')
    style_tags = soup.find_all('style', type='text/css')
    page_styles = []
    for style in style_tags:
        # Check if it's not the common body style
        style_text = style.get_text()
        if '@media' in style_text or 'data-w-id' in style_text:
            page_styles.append(style_text)
    return '\n'.join(page_styles)

def convert_html_to_template(html_file_path):
    """Convert an HTML file to use Jinja2 templates."""
    with open(html_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Extract metadata
    title_tag = soup.find('title')
    title = title_tag.get_text() if title_tag else 'Page'
    
    meta_desc = soup.find('meta', {'name': 'description'})
    description = meta_desc.get('content', '') if meta_desc else ''
    
    html_tag = soup.find('html')
    page_id = html_tag.get('data-wf-page', '670903a26ae4eb4eb6eb91ff') if html_tag else '670903a26ae4eb4eb6eb91ff'
    
    # Extract page-specific styles
    page_styles = extract_page_styles(content)
    
    # Find body content (between <body> and footer/navigation)
    body = soup.find('body')
    if not body:
        return None
    
    # Find footer and navigation
    footer = body.find('div', class_='footer-1')
    navbar = body.find('div', class_='navbar')
    preloader = body.find('div', class_='preloader')
    
    # Extract main content (everything between body start and footer/navbar)
    main_content = []
    for child in body.children:
        if child == footer or child == navbar or child == preloader:
            break
        if hasattr(child, 'prettify'):
            main_content.append(str(child))
        elif str(child).strip():
            main_content.append(str(child))
    
    main_content_html = '\n'.join(main_content)
    
    # Determine if layout has opacity style
    layout = body.find('div', class_='layout')
    layout_opacity = layout and layout.get('style', '').startswith('opacity:0')
    
    # Determine if preloader exists
    has_preloader = preloader is not None
    
    # Determine current page
    current_page = html_file_path.stem
    if html_file_path.parent.name in ['about', 'contact', 'home']:
        current_page = f"{html_file_path.parent.name}-{current_page}"
    
    # Create template
    template_content = f"""{{% extends "base.html" %}}

{{% block content %}}
{main_content_html}
{{% endblock %}}
"""
    
    if has_preloader:
        template_content = f"""{{% extends "base.html" %}}

{{% block preloader %}}
  <div class="preloader">
    <img src="https://cdn.prod.website-files.com/670903a26ae4eb4eb6eb91a2/670903a26ae4eb4eb6eb9218_loader_three-dots-white.svg" loading="lazy" alt="" class="preloader-image">
  </div>
{{% endblock %}}

{{% block content %}}
{main_content_html}
{{% endblock %}}
"""
    
    # Save template
    template_path = Path('templates') / html_file_path
    template_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    return {
        'page_id': page_id,
        'title': title,
        'description': description,
        'page_styles': page_styles,
        'layout_opacity': layout_opacity,
        'preloader': has_preloader,
        'current_page': current_page
    }

def main():
    """Convert all HTML files to templates."""
    # Files to convert (excluding ofelia-original and webflow-site)
    html_files = []
    for pattern in ['*.html', '*/*.html', '*/*/*.html']:
        html_files.extend(Path('.').glob(pattern))
    
    # Filter out excluded directories
    html_files = [f for f in html_files if not any(excluded in str(f) for excluded in ['ofelia-original', 'webflow-site', 'templates', '.git'])]
    
    metadata = {}
    for html_file in html_files:
        print(f"Converting {html_file}...")
        try:
            meta = convert_html_to_template(html_file)
            if meta:
                metadata[str(html_file)] = meta
        except Exception as e:
            print(f"Error converting {html_file}: {e}")
    
    print(f"\nConverted {len(metadata)} files to templates.")
    print("Templates saved in templates/ directory.")

if __name__ == '__main__':
    main()
