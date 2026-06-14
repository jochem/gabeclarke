#!/usr/bin/env python3
"""
Export Flask app to static HTML files with only used assets.
"""

import os
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
from flask import Flask
from app import app

OUTPUT_DIR = Path('output')
ASSETS_DIR = Path('assets')
MEDIA_DIR = Path('media')

# Track all referenced assets
referenced_assets = set()
referenced_media = set()

def fix_relative_paths(html_content, depth):
    """Fix relative paths in HTML for static export and decode URL-encoded paths."""
    from urllib.parse import unquote
    
    # Pattern to match paths in href, src, data-full-image, etc.
    # Match: (../)* + (assets/|media/) + (path with possible URL encoding)
    # We need to capture the full path to decode it
    patterns = [
        # For href and src attributes
        (r'(href|src)=["\']((?:\.\./)+)(assets/|media/)([^"\']+)["\']', r'\1="\2\3'),
        # For data attributes
        (r'(data-[^=]+)=["\']((?:\.\./)+)(assets/|media/)([^"\']+)["\']', r'\1="\2\3'),
    ]
    
    def decode_and_fix_path(match, attr_name, prefix, folder, path_part):
        """Decode URL-encoded path and fix prefix."""
        # URL-decode the path part
        decoded_path = unquote(path_part)
        
        # Calculate correct prefix based on depth
        if depth == 0:
            correct_prefix = ''
        else:
            correct_prefix = '../' * depth
        
        return f'{attr_name}="{correct_prefix}{folder}{decoded_path}"'
    
    # Fix href and src attributes
    def fix_href_src(match):
        attr = match.group(1)
        old_prefix = match.group(2)
        folder = match.group(3)
        path = match.group(4)
        return decode_and_fix_path(match, attr, old_prefix, folder, path)
    
    html_content = re.sub(
        r'(href|src)=["\']((?:\.\./)+)(assets/|media/)([^"\']+)["\']',
        fix_href_src,
        html_content
    )
    
    # Fix data attributes (like data-full-image)
    def fix_data_attr(match):
        attr = match.group(1)
        old_prefix = match.group(2)
        folder = match.group(3)
        path = match.group(4)
        return decode_and_fix_path(match, attr, old_prefix, folder, path)
    
    html_content = re.sub(
        r'(data-[^=]+)=["\']((?:\.\./)+)(assets/|media/)([^"\']+)["\']',
        fix_data_attr,
        html_content
    )
    
    return html_content

def extract_asset_paths(html_content, output_path=''):
    """Extract all asset paths from HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all asset references
    for tag in soup.find_all(['img', 'link', 'script', 'source', 'video', 'audio']):
        # Images
        if tag.name == 'img' and tag.get('src'):
            src = tag.get('src')
            process_asset_path(src, output_path)
        
        # Stylesheets and other links
        if tag.name == 'link' and tag.get('href'):
            href = tag.get('href')
            process_asset_path(href, output_path)
        
        # Scripts
        if tag.name == 'script' and tag.get('src'):
            src = tag.get('src')
            process_asset_path(src, output_path)
        
        # Video/audio sources
        if tag.name in ['source', 'video', 'audio']:
            for attr in ['src', 'poster']:
                if tag.get(attr):
                    src = tag.get(attr)
                    process_asset_path(src, output_path)
    
    # Responsive image candidates: srcset (img/source) and imagesrcset (preload links)
    for attr in ['srcset', 'imagesrcset']:
        for tag in soup.find_all(attrs={attr: True}):
            for candidate in tag.get(attr, '').split(','):
                parts = candidate.split()
                if parts:
                    process_asset_path(parts[0], output_path)

    # Also check inline styles for background images
    for tag in soup.find_all(style=True):
        style = tag.get('style', '')
        # Find url(...) patterns
        urls = re.findall(r'url\(["\']?([^"\')]+)["\']?\)', style)
        for url in urls:
            process_asset_path(url, output_path)

def process_asset_path(path, output_path=''):
    """Process an asset path and add it to the referenced sets."""
    from urllib.parse import unquote
    
    # Remove query strings and fragments
    path = path.split('?')[0].split('#')[0]
    
    # Skip external URLs (including CDN URLs)
    if path.startswith(('http://', 'https://', '//', 'mailto:', 'tel:')):
        return
    
    # Handle relative paths (../)
    # Calculate how many levels up we need to go from output_path
    if path.startswith('../'):
        # Count how many ../ we have
        up_levels = len(re.findall(r'\.\./', path))
        # Remove all ../
        clean_path = re.sub(r'\.\./', '', path)
        # For now, just use the clean path - assets should be at root level
        path = clean_path
    elif path.startswith('/'):
        # Absolute path from root
        path = path.lstrip('/')
    
    # Normalize path
    path = path.lstrip('/')
    
    # URL-decode the path to get the actual filename
    # This handles cases like %20 (space), %28/%29 (parentheses)
    decoded_path = unquote(path)
    
    # Check if it's a media file
    if path.startswith('media/') or decoded_path.startswith('media/'):
        # Remove 'media/' prefix from both encoded and decoded paths
        media_path_encoded = path[6:] if path.startswith('media/') else path
        media_path_decoded = decoded_path[6:] if decoded_path.startswith('media/') else decoded_path
        
        # Try both encoded and decoded paths
        if (MEDIA_DIR / media_path_decoded).exists():
            referenced_media.add(media_path_decoded)
        elif (MEDIA_DIR / media_path_encoded).exists():
            referenced_media.add(media_path_encoded)
    # Check if it's an asset
    elif path.startswith('assets/') or decoded_path.startswith('assets/'):
        asset_path_encoded = path[7:] if path.startswith('assets/') else path
        asset_path_decoded = decoded_path[7:] if decoded_path.startswith('assets/') else decoded_path
        
        if (ASSETS_DIR / asset_path_decoded).exists():
            referenced_assets.add(asset_path_decoded)
        elif (ASSETS_DIR / asset_path_encoded).exists():
            referenced_assets.add(asset_path_encoded)
    # Direct asset reference (no assets/ prefix) - check if it exists in assets
    elif (ASSETS_DIR / decoded_path).exists():
        referenced_assets.add(decoded_path)
    elif (ASSETS_DIR / path).exists():
        referenced_assets.add(path)
    # Direct media reference (no media/ prefix) - check if it exists in media
    elif (MEDIA_DIR / decoded_path).exists():
        referenced_media.add(decoded_path)
    elif (MEDIA_DIR / path).exists():
        referenced_media.add(path)

def get_all_routes():
    """Get all routes from the Flask app."""
    routes = []
    
    with app.test_client() as client:
        # Live pages only (Webflow demo pages moved to webflow-demo/)
        routes.append(('/', 'index.html'))
        routes.append(('/index.html', 'index.html'))
        routes.append(('/about/', 'about/index.html'))
        routes.append(('/contact/', 'contact/index.html'))
        routes.append(('/contact', 'contact/index.html'))
        routes.append(('/performances/', 'performances/index.html'))
        routes.append(('/press/', 'press/index.html'))
        routes.append(('/press', 'press/index.html'))
        routes.append(('/media/', 'media/index.html'))

    return routes

def export_static():
    """Export all pages to static HTML."""
    # Clean output directory
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()
    
    # Create subdirectories
    (OUTPUT_DIR / 'assets').mkdir(parents=True)
    (OUTPUT_DIR / 'media').mkdir(parents=True)
    
    print("Exporting pages...")
    routes = get_all_routes()
    
    with app.test_client() as client:
        for route_path, output_path in routes:
            try:
                print(f"  Rendering {route_path} -> {output_path}")
                response = client.get(route_path)
                
                if response.status_code == 200:
                    html_content = response.data.decode('utf-8')
                    
                    # Extract asset paths from rendered HTML
                    extract_asset_paths(html_content, output_path)
                    
                    # Fix relative paths in HTML for static export
                    # Calculate depth of output file (how many directories deep from root)
                    # index.html = depth 0, about/about-1.html = depth 1, works/the-crash/index.html = depth 2
                    # Count the number of directory separators (not including the filename)
                    path_parts = output_path.split('/')
                    # Remove the filename to get just directories
                    directories = [p for p in path_parts if p and not p.endswith('.html')]
                    depth = len(directories)
                    
                    # Fix paths in HTML
                    html_content = fix_relative_paths(html_content, depth)
                    
                    # Save HTML file
                    output_file = OUTPUT_DIR / output_path
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    output_file.write_text(html_content, encoding='utf-8')
                elif response.status_code == 301:
                    # Handle redirects
                    location = response.headers.get('Location', '')
                    print(f"    Redirect: {route_path} -> {location}")
                else:
                    print(f"    Error {response.status_code}: {route_path}")
            except Exception as e:
                print(f"    Error rendering {route_path}: {e}")
    
    # Pull in assets referenced from within CSS files (e.g. @font-face url(...))
    for css_rel in [a for a in list(referenced_assets) if a.lower().endswith('.css')]:
        css_file = ASSETS_DIR / css_rel
        if not css_file.exists():
            continue
        css_dir = css_file.parent
        for u in re.findall(r'url\(\s*["\']?([^"\')]+)["\']?\s*\)', css_file.read_text(encoding='utf-8', errors='ignore')):
            u = u.split('?')[0].split('#')[0]
            if u.startswith(('http://', 'https://', 'data:', '//')):
                continue
            resolved = (css_dir / u).resolve()
            try:
                rel = resolved.relative_to(ASSETS_DIR.resolve())
            except ValueError:
                continue
            if resolved.exists():
                referenced_assets.add(str(rel))

    print(f"\nCopying {len(referenced_assets)} asset files...")
    for asset_path in referenced_assets:
        src = ASSETS_DIR / asset_path
        if src.exists():
            dst = OUTPUT_DIR / 'assets' / asset_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  {asset_path}")
        else:
            print(f"  WARNING: Asset not found: {asset_path}")
    
    print(f"\nCopying {len(referenced_media)} media files...")
    for media_path in referenced_media:
        # media_path is already decoded from process_asset_path
        src = MEDIA_DIR / media_path
        if src.exists():
            # Copy to output with the same (decoded) name
            dst = OUTPUT_DIR / 'media' / media_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  {media_path}")
        else:
            print(f"  WARNING: Media file not found: {media_path}")
    
    # Copy root-level static files (favicons, etc.) to the output root
    for root_file in ('favicon.svg', 'favicon-32.png', 'apple-touch-icon.png'):
        src = Path(root_file)
        if src.exists():
            shutil.copy2(src, OUTPUT_DIR / root_file)
            print(f"  {root_file}")
        else:
            print(f"  WARNING: root file not found: {root_file}")

    # Generate robots.txt + sitemap.xml (SEO)
    site_url = 'https://gabeclarke.com'
    sitemap_paths = []
    seen = set()
    for rp, op in routes:
        if op.endswith('index.html') and (rp == '/' or rp.endswith('/')) and rp not in seen:
            seen.add(rp)
            sitemap_paths.append(rp)
    (OUTPUT_DIR / 'robots.txt').write_text(
        "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % site_url,
        encoding='utf-8')
    urls = "".join("  <url><loc>%s%s</loc></url>\n" % (site_url, p) for p in sitemap_paths)
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + urls + '</urlset>\n')
    (OUTPUT_DIR / 'sitemap.xml').write_text(sitemap, encoding='utf-8')
    print(f"  Wrote robots.txt and sitemap.xml ({len(sitemap_paths)} URLs)")

    print(f"\nExport complete! Static site is in '{OUTPUT_DIR}' directory.")
    print(f"You can now create a zip file of the '{OUTPUT_DIR}' folder.")

if __name__ == '__main__':
    export_static()

