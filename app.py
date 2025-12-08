#!/usr/bin/env python3
"""
Flask server with Jinja2 templates for Gabe Clarke portfolio site.
"""

from flask import Flask, render_template, send_from_directory, url_for, request
import os
import json
from pathlib import Path
from bs4 import BeautifulSoup

app = Flask(__name__, template_folder='templates', static_folder='.')
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Cache for page metadata
_page_metadata_cache = None

def load_page_metadata():
    """Load page metadata from original HTML files."""
    global _page_metadata_cache
    if _page_metadata_cache is not None:
        return _page_metadata_cache
    
    metadata = {}
    for html_file in Path('.').rglob('*.html'):
        if any(excluded in str(html_file) for excluded in ['ofelia-original', 'webflow-site', 'templates', '.git']):
            continue
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            title = soup.find('title')
            title_text = title.get_text() if title else 'Page'
            meta_desc = soup.find('meta', {'name': 'description'})
            desc = meta_desc.get('content', '') if meta_desc else ''
            html_tag = soup.find('html')
            page_id = html_tag.get('data-wf-page', '670903a26ae4eb4eb6eb91ff') if html_tag else '670903a26ae4eb4eb6eb91ff'
            body = soup.find('body')
            layout = body.find('div', class_='layout') if body else None
            layout_opacity = layout and 'opacity:0' in layout.get('style', '')
            preloader = body.find('div', class_='preloader') if body else None
            has_preloader = preloader is not None
            
            rel_path = str(html_file).replace('\\', '/')
            metadata[rel_path] = {
                'title': title_text,
                'description': desc,
                'page_id': page_id,
                'layout_opacity': layout_opacity,
                'preloader': has_preloader
            }
        except Exception as e:
            print(f'Error processing {html_file}: {e}')
    
    _page_metadata_cache = metadata
    return metadata

def get_page_metadata(template_path):
    """Get metadata for a template based on its path."""
    metadata = load_page_metadata()
    # Try to find matching original HTML file
    for orig_path, meta in metadata.items():
        # Convert template path to original path
        if template_path.replace('templates/', '') in orig_path or orig_path.endswith(template_path.replace('templates/', '')):
            return meta
    # Default values
    return {
        'title': 'Page • Gabe Clarke',
        'description': 'Gabe Clarke portfolio site.',
        'page_id': '670903a26ae4eb4eb6eb91ff',
        'layout_opacity': False,
        'preloader': False
    }

# Calculate asset path based on request path depth
def get_asset_path(request_path):
    """Calculate the relative asset path based on the request path depth."""
    depth = request_path.strip('/').count('/')
    if depth == 0:
        return ''
    return '../' * depth

@app.context_processor
def inject_asset_path():
    """Inject asset_path into all templates."""
    def asset_path_func(path=''):
        request_path = request.path if request else ''
        return get_asset_path(request_path) + path
    return dict(asset_path=asset_path_func())

@app.route('/')
def index():
    """Home page."""
    meta = get_page_metadata('index.html')
    return render_template('index.html',
                         page_id=meta['page_id'],
                         title=meta['title'],
                         description=meta['description'],
                         layout_opacity=meta['layout_opacity'],
                         preloader=meta['preloader'])

@app.route('/about/about-<int:num>.html')
def about(num):
    """About pages."""
    meta = get_page_metadata(f'about/about-{num}.html')
    return render_template(f'about/about-{num}.html',
                         page_id=meta['page_id'],
                         title=meta['title'],
                         description=meta['description'],
                         layout_opacity=meta['layout_opacity'],
                         preloader=meta['preloader'])

@app.route('/contact/contact-<int:num>.html')
def contact(num):
    """Contact pages."""
    meta = get_page_metadata(f'contact/contact-{num}.html')
    return render_template(f'contact/contact-{num}.html',
                         page_id=meta['page_id'],
                         title=meta['title'],
                         description=meta['description'],
                         layout_opacity=meta['layout_opacity'],
                         preloader=meta['preloader'])

@app.route('/pages/<path:filename>')
def pages(filename):
    """Pages like shop.html, works.html."""
    meta = get_page_metadata(f'pages/{filename}')
    return render_template(f'pages/{filename}',
                         page_id=meta['page_id'],
                         title=meta['title'],
                         description=meta['description'],
                         layout_opacity=meta['layout_opacity'],
                         preloader=meta['preloader'])

@app.route('/category/<path:filename>')
def category(filename):
    """Category pages."""
    meta = get_page_metadata(f'category/{filename}')
    return render_template(f'category/{filename}',
                         page_id=meta['page_id'],
                         title=meta['title'],
                         description=meta['description'],
                         layout_opacity=meta['layout_opacity'],
                         preloader=meta['preloader'])

@app.route('/product/<path:filename>')
def product(filename):
    """Product pages."""
    meta = get_page_metadata(f'product/{filename}')
    return render_template(f'product/{filename}',
                         page_id=meta['page_id'],
                         title=meta['title'],
                         description=meta['description'],
                         layout_opacity=meta['layout_opacity'],
                         preloader=meta['preloader'])

@app.route('/project/<path:filename>')
def project(filename):
    """Project pages."""
    meta = get_page_metadata(f'project/{filename}')
    return render_template(f'project/{filename}',
                         page_id=meta['page_id'],
                         title=meta['title'],
                         description=meta['description'],
                         layout_opacity=meta['layout_opacity'],
                         preloader=meta['preloader'])

@app.route('/home/<path:filename>')
def home(filename):
    """Home variant pages."""
    meta = get_page_metadata(f'home/{filename}')
    return render_template(f'home/{filename}',
                         page_id=meta['page_id'],
                         title=meta['title'],
                         description=meta['description'],
                         layout_opacity=meta['layout_opacity'],
                         preloader=meta['preloader'])

@app.route('/template-settings/<path:filename>')
def template_settings(filename):
    """Template settings pages."""
    meta = get_page_metadata(f'template-settings/{filename}')
    return render_template(f'template-settings/{filename}',
                         page_id=meta['page_id'],
                         title=meta['title'],
                         description=meta['description'],
                         layout_opacity=meta['layout_opacity'],
                         preloader=meta['preloader'])

@app.route('/checkout.html')
def checkout():
    """Checkout page."""
    meta = get_page_metadata('checkout.html')
    return render_template('checkout.html',
                         page_id=meta['page_id'],
                         title=meta['title'],
                         description=meta['description'],
                         layout_opacity=meta['layout_opacity'],
                         preloader=meta['preloader'])

# Serve static files (assets, etc.)
@app.route('/assets/<path:filename>')
def assets(filename):
    """Serve asset files."""
    return send_from_directory('assets', filename)

@app.route('/<path:filename>')
def static_files(filename):
    """Serve other static files."""
    if os.path.isfile(filename):
        return send_from_directory('.', filename)
    return f"File not found: {filename}", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

