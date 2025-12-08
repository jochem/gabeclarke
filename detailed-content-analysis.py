#!/usr/bin/env python3
"""
Detailed content analysis - extract actual text differences
"""

import os
import re
from html.parser import HTMLParser
from collections import Counter

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip_tags = {'script', 'style', 'meta', 'link'}
        self.in_skip = False
    
    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags:
            self.in_skip = True
    
    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.in_skip = False
    
    def handle_data(self, data):
        if not self.in_skip:
            text = data.strip()
            if text and len(text) > 2:
                self.text.append(text)

def extract_text_content(html_file):
    """Extract readable text from HTML"""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        parser = TextExtractor()
        parser.feed(content)
        return ' '.join(parser.text)
    except:
        return ""

def analyze_key_pages():
    """Analyze key pages in detail"""
    gabe_dir = 'webflow-site'
    original_dir = 'ofelia-original'
    
    key_pages = ['index.html', 'about/about-2.html', 'pages/works.html']
    
    print("📝 Detailed Content Analysis")
    print("=" * 60)
    
    for page in key_pages:
        gabe_file = os.path.join(gabe_dir, page)
        original_file = os.path.join(original_dir, page)
        
        if not (os.path.exists(gabe_file) and os.path.exists(original_file)):
            continue
        
        print(f"\n📄 {page}")
        print("-" * 60)
        
        gabe_text = extract_text_content(gabe_file)
        original_text = extract_text_content(original_file)
        
        # Extract key phrases
        gabe_words = set(gabe_text.lower().split())
        original_words = set(original_text.lower().split())
        
        unique_gabe = gabe_words - original_words
        unique_original = original_words - gabe_words
        
        # Filter out common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'where', 'when', 'why', 'how'}
        
        unique_gabe = {w for w in unique_gabe if w not in common_words and len(w) > 3}
        unique_original = {w for w in unique_original if w not in common_words and len(w) > 3}
        
        print(f"Unique content in Gabe Clarke ({len(unique_gabe)} significant words):")
        if unique_gabe:
            # Show most relevant
            sample = sorted(list(unique_gabe))[:15]
            print(f"   {', '.join(sample)}")
        
        print(f"\nUnique content in Original ({len(unique_original)} significant words):")
        if unique_original:
            sample = sorted(list(unique_original))[:15]
            print(f"   {', '.join(sample)}")
        
        # Character count
        print(f"\nText length: Gabe={len(gabe_text):,} chars, Original={len(original_text):,} chars")

def compare_images():
    """Compare image usage"""
    print("\n\n🖼️  Image Analysis")
    print("=" * 60)
    
    gabe_dir = 'webflow-site/assets'
    original_dir = 'ofelia-original/assets'
    
    def get_image_files(base_dir):
        images = []
        if os.path.exists(base_dir):
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp')):
                        images.append(file.lower())
        return set(images)
    
    gabe_images = get_image_files(gabe_dir)
    original_images = get_image_files(original_dir)
    
    common_images = gabe_images & original_images
    only_gabe = gabe_images - original_images
    only_original = original_images - gabe_images
    
    print(f"Gabe Clarke images: {len(gabe_images)}")
    print(f"Original images: {len(original_images)}")
    print(f"Common images: {len(common_images)}")
    print(f"Only in Gabe Clarke: {len(only_gabe)}")
    print(f"Only in Original: {len(only_original)}")
    
    # Sample unique images
    if only_gabe:
        print(f"\nSample unique Gabe images:")
        for img in sorted(list(only_gabe))[:10]:
            # Extract meaningful part
            if 'jonathanballliet' in img or 'crash' in img or 'whatsapp' in img:
                print(f"   - {img[:80]}...")
    
    if only_original:
        print(f"\nSample unique Original images:")
        for img in sorted(list(only_original))[:10]:
            print(f"   - {img[:80]}...")

def main():
    analyze_key_pages()
    compare_images()
    
    print("\n" + "=" * 60)
    print("✅ Analysis complete!")

if __name__ == '__main__':
    main()

