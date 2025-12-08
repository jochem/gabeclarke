#!/usr/bin/env python3
"""
Webflow Offline Asset Downloader
Downloads all CSS, JS, images, and fonts from CDN and updates HTML to use local paths
"""

import os
import re
import urllib.request
import urllib.parse
from pathlib import Path
import json

def extract_urls(html_content):
    """Extract all external resource URLs from HTML"""
    urls = set()
    
    # CSS files
    css_pattern = r'href=["\'](https?://[^"\']+\.css[^"\']*)["\']'
    urls.update(re.findall(css_pattern, html_content))
    
    # JavaScript files
    js_pattern = r'src=["\'](https?://[^"\']+\.js[^"\']*)["\']'
    urls.update(re.findall(js_pattern, html_content))
    
    # Images
    img_pattern = r'src=["\'](https?://[^"\']+\.(jpg|jpeg|png|gif|svg|webp|ico)[^"\']*)["\']'
    urls.update(re.findall(img_pattern, html_content))
    
    # srcset images
    srcset_pattern = r'srcset=["\']([^"\']+)["\']'
    srcsets = re.findall(srcset_pattern, html_content)
    for srcset in srcsets:
        # Parse srcset (format: url width, url width, ...)
        for item in srcset.split(','):
            url = item.strip().split()[0]
            if url.startswith('http'):
                urls.add(url)
    
    # Fonts
    font_pattern = r'url\(["\']?(https?://[^"\')]+\.(woff|woff2|ttf|eot|otf)[^"\')]*)["\']?\)'
    urls.update(re.findall(font_pattern, html_content))
    
    # Background images in CSS
    bg_pattern = r'url\(["\']?(https?://[^"\')]+\.(jpg|jpeg|png|gif|svg|webp)[^"\')]*)["\']?\)'
    urls.update(re.findall(bg_pattern, html_content))
    
    return urls

def download_file(url, local_path):
    """Download a file from URL to local path"""
    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        urllib.request.urlretrieve(url, local_path)
        return True
    except Exception as e:
        print(f"  ⚠️  Failed to download {url}: {e}")
        return False

def get_local_path(url, base_dir):
    """Convert CDN URL to local file path"""
    # Parse URL
    parsed = urllib.parse.urlparse(url)
    path = parsed.path
    
    # Remove leading slash
    if path.startswith('/'):
        path = path[1:]
    
    # Create local path
    local_path = os.path.join(base_dir, 'assets', path)
    return local_path

def update_html_references(html_content, url_mapping, html_file_path):
    """Update HTML to use local file paths"""
    updated = html_content
    html_dir = os.path.dirname(html_file_path)
    
    # Sort by length (longest first) to avoid partial replacements
    for url, local_path in sorted(url_mapping.items(), key=lambda x: -len(x[0])):
        # Make path relative to HTML file location
        if html_dir:
            relative_path = os.path.relpath(local_path, html_dir)
        else:
            relative_path = os.path.relpath(local_path, 'webflow-site')
        # Normalize path separators for web
        relative_path = relative_path.replace('\\', '/')
        # Replace all occurrences
        updated = updated.replace(url, relative_path)
    
    return updated

def main():
    base_dir = 'webflow-site'
    assets_dir = os.path.join(base_dir, 'assets')
    
    print("🔍 Scanning HTML files for external assets...")
    
    # Find all HTML files
    html_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    print(f"   Found {len(html_files)} HTML files")
    
    # Extract all URLs
    all_urls = set()
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            urls = extract_urls(content)
            all_urls.update(urls)
    
    print(f"   Found {len(all_urls)} unique external resources")
    
    # Filter to only Webflow CDN and related domains
    cdn_domains = [
        'cdn.prod.website-files.com',
        'd3e54v103j8qbb.cloudfront.net',
        'fonts.googleapis.com',
        'fonts.gstatic.com',
        'ajax.googleapis.com'
    ]
    
    cdn_urls = [url for url in all_urls if any(domain in url for domain in cdn_domains)]
    other_urls = [url for url in all_urls if not any(domain in url for domain in cdn_domains)]
    
    print(f"   {len(cdn_urls)} from CDN domains")
    if other_urls:
        print(f"   {len(other_urls)} from other domains (skipping)")
    
    # Create URL mapping
    url_mapping = {}
    for url in cdn_urls:
        local_path = get_local_path(url, base_dir)
        url_mapping[url] = local_path
    
    # Download assets
    print("\n📥 Downloading assets...")
    downloaded = 0
    failed = 0
    
    for i, (url, local_path) in enumerate(url_mapping.items(), 1):
        print(f"   [{i}/{len(url_mapping)}] {os.path.basename(local_path)}")
        if download_file(url, local_path):
            downloaded += 1
        else:
            failed += 1
    
    print(f"\n✅ Downloaded {downloaded} files")
    if failed > 0:
        print(f"⚠️  Failed to download {failed} files")
    
    # Update HTML files
    print("\n✏️  Updating HTML files to use local paths...")
    updated_count = 0
    
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        updated_content = update_html_references(content, url_mapping, html_file)
        
        if content != updated_content:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            updated_count += 1
            print(f"   Updated {html_file}")
    
    print(f"\n✅ Updated {updated_count} HTML files")
    print(f"\n🎉 Done! Your site should now work fully offline.")
    print(f"   Assets saved to: {assets_dir}/")

if __name__ == '__main__':
    main()

