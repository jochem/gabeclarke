#!/usr/bin/env python3
"""
Deep comparison between Gabe Clarke version and original template
"""

import os
import hashlib
import json
from pathlib import Path
from collections import defaultdict

def get_file_hash(filepath):
    """Get MD5 hash of file"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def get_file_size(filepath):
    """Get file size"""
    try:
        return os.path.getsize(filepath)
    except:
        return 0

def scan_directory(base_dir):
    """Scan directory and return file structure"""
    files = {}
    structure = {
        'html_files': [],
        'css_files': [],
        'js_files': [],
        'image_files': [],
        'other_files': []
    }
    
    for root, dirs, filenames in os.walk(base_dir):
        # Skip assets for now (will compare separately)
        if 'assets' in root:
            continue
            
        for filename in filenames:
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, base_dir)
            
            file_info = {
                'path': rel_path,
                'size': get_file_size(filepath),
                'hash': get_file_hash(filepath)
            }
            
            files[rel_path] = file_info
            
            if filename.endswith('.html'):
                structure['html_files'].append(rel_path)
            elif filename.endswith('.css'):
                structure['css_files'].append(rel_path)
            elif filename.endswith('.js'):
                structure['js_files'].append(rel_path)
            elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp')):
                structure['image_files'].append(rel_path)
            else:
                structure['other_files'].append(rel_path)
    
    return files, structure

def compare_html_content(file1, file2):
    """Compare HTML content and extract differences"""
    try:
        with open(file1, 'r', encoding='utf-8') as f:
            content1 = f.read()
        with open(file2, 'r', encoding='utf-8') as f:
            content2 = f.read()
        
        if content1 == content2:
            return {'identical': True}
        
        # Extract text content (rough comparison)
        import re
        text1 = re.sub(r'<[^>]+>', ' ', content1)
        text1 = ' '.join(text1.split())
        text2 = re.sub(r'<[^>]+>', ' ', content2)
        text2 = ' '.join(text2.split())
        
        # Find unique text in each
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        unique_to_1 = words1 - words2
        unique_to_2 = words2 - words1
        
        # Extract key differences
        differences = {
            'identical': False,
            'size_diff': len(content1) - len(content2),
            'unique_words_gabe': len(unique_to_1),
            'unique_words_original': len(unique_to_2),
            'sample_unique_gabe': list(unique_to_1)[:10],
            'sample_unique_original': list(unique_to_2)[:10]
        }
        
        return differences
    except Exception as e:
        return {'error': str(e)}

def analyze_assets(base_dir):
    """Analyze assets directory"""
    assets_info = {
        'total_files': 0,
        'total_size': 0,
        'by_type': defaultdict(int),
        'by_size': defaultdict(int)
    }
    
    assets_dir = os.path.join(base_dir, 'assets')
    if not os.path.exists(assets_dir):
        return assets_info
    
    for root, dirs, files in os.walk(assets_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            size = get_file_size(filepath)
            ext = os.path.splitext(filename)[1].lower()
            
            assets_info['total_files'] += 1
            assets_info['total_size'] += size
            assets_info['by_type'][ext] += 1
            
            if size < 1024:
                assets_info['by_size']['<1KB'] += 1
            elif size < 1024 * 100:
                assets_info['by_size']['1-100KB'] += 1
            elif size < 1024 * 1024:
                assets_info['by_size']['100KB-1MB'] += 1
            else:
                assets_info['by_size']['>1MB'] += 1
    
    return assets_info

def main():
    print("🔍 Deep Comparison: Gabe Clarke vs Original Template")
    print("=" * 60)
    
    gabe_dir = 'webflow-site'
    original_dir = 'ofelia-original'
    
    print("\n1️⃣  Scanning file structures...")
    gabe_files, gabe_structure = scan_directory(gabe_dir)
    original_files, original_structure = scan_directory(original_dir)
    
    print(f"   Gabe Clarke: {len(gabe_files)} files")
    print(f"   Original: {len(original_files)} files")
    
    # Find common and unique files
    gabe_paths = set(gabe_files.keys())
    original_paths = set(original_files.keys())
    
    common_files = gabe_paths & original_paths
    only_gabe = gabe_paths - original_paths
    only_original = original_paths - gabe_paths
    
    print(f"\n   Common files: {len(common_files)}")
    print(f"   Only in Gabe Clarke: {len(only_gabe)}")
    print(f"   Only in Original: {len(only_original)}")
    
    # Compare common files
    print("\n2️⃣  Comparing common files...")
    identical = 0
    different = 0
    html_differences = []
    
    for rel_path in sorted(common_files):
        gabe_file = os.path.join(gabe_dir, rel_path)
        original_file = os.path.join(original_dir, rel_path)
        
        gabe_hash = gabe_files[rel_path]['hash']
        original_hash = original_files[rel_path]['hash']
        
        if gabe_hash == original_hash:
            identical += 1
        else:
            different += 1
            if rel_path.endswith('.html'):
                diff = compare_html_content(gabe_file, original_file)
                if not diff.get('identical', False):
                    html_differences.append({
                        'file': rel_path,
                        'diff': diff
                    })
    
    print(f"   Identical files: {identical}")
    print(f"   Different files: {different}")
    
    # Analyze HTML differences
    print("\n3️⃣  Analyzing HTML differences...")
    if html_differences:
        print(f"   Found {len(html_differences)} HTML files with differences:")
        for item in html_differences[:5]:  # Show first 5
            print(f"\n   📄 {item['file']}")
            diff = item['diff']
            if 'size_diff' in diff:
                print(f"      Size difference: {diff['size_diff']:,} bytes")
            if 'unique_words_gabe' in diff:
                print(f"      Unique words in Gabe: {diff['unique_words_gabe']}")
                if diff['sample_unique_gabe']:
                    print(f"      Sample: {', '.join(diff['sample_unique_gabe'][:5])}")
    
    # Analyze assets
    print("\n4️⃣  Analyzing assets...")
    gabe_assets = analyze_assets(gabe_dir)
    original_assets = analyze_assets(original_dir)
    
    print(f"\n   Gabe Clarke assets:")
    print(f"      Total files: {gabe_assets['total_files']}")
    print(f"      Total size: {gabe_assets['total_size'] / (1024*1024):.1f} MB")
    print(f"      File types: {dict(gabe_assets['by_type'])}")
    
    print(f"\n   Original assets:")
    print(f"      Total files: {original_assets['total_files']}")
    print(f"      Total size: {original_assets['total_size'] / (1024*1024):.1f} MB")
    print(f"      File types: {dict(original_assets['by_type'])}")
    
    # Find unique files
    print("\n5️⃣  Files unique to each version...")
    if only_gabe:
        print(f"\n   📁 Only in Gabe Clarke ({len(only_gabe)} files):")
        for f in sorted(list(only_gabe))[:10]:
            print(f"      - {f}")
        if len(only_gabe) > 10:
            print(f"      ... and {len(only_gabe) - 10} more")
    
    if only_original:
        print(f"\n   📁 Only in Original ({len(only_original)} files):")
        for f in sorted(list(only_original))[:10]:
            print(f"      - {f}")
        if len(only_original) > 10:
            print(f"      ... and {len(only_original) - 10} more")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Total customization level: {different}/{len(common_files)} files modified ({different*100//len(common_files) if common_files else 0}%)")
    print(f"Unique files in Gabe Clarke: {len(only_gabe)}")
    print(f"Unique files in Original: {len(only_original)}")
    print(f"Asset size difference: {abs(gabe_assets['total_size'] - original_assets['total_size']) / (1024*1024):.1f} MB")
    
    # Save detailed report
    report = {
        'comparison_date': str(Path(__file__).stat().st_mtime),
        'gabe_clarke': {
            'total_files': len(gabe_files),
            'html_files': len(gabe_structure['html_files']),
            'assets': gabe_assets
        },
        'original': {
            'total_files': len(original_files),
            'html_files': len(original_structure['html_files']),
            'assets': original_assets
        },
        'differences': {
            'common_files': len(common_files),
            'identical_files': identical,
            'different_files': different,
            'only_gabe': list(only_gabe),
            'only_original': list(only_original),
            'html_differences': html_differences[:20]  # Limit to 20
        }
    }
    
    with open('comparison-report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Detailed report saved to: comparison-report.json")

if __name__ == '__main__':
    main()

