#!/bin/bash

# Complete Webflow Site Downloader
# Downloads HTML pages AND all external assets (CSS, JS, images from CDN)

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SITE_URL=$1

if [ -z "$SITE_URL" ]; then
    echo -e "${RED}Error: Please provide your Webflow site URL${NC}"
    echo "Usage: ./download-webflow-complete.sh <your-site-url>"
    exit 1
fi

if ! command -v wget &> /dev/null; then
    echo -e "${RED}Error: wget is not installed${NC}"
    echo "Install: brew install wget"
    exit 1
fi

echo -e "${GREEN}Complete Webflow Site Downloader${NC}"
echo "=========================================="
echo ""
echo -e "${YELLOW}Step 1: Downloading HTML pages...${NC}"

DOWNLOAD_DIR="webflow-site"
mkdir -p "$DOWNLOAD_DIR"

# First, download all HTML pages
wget \
    --mirror \
    --convert-links \
    --adjust-extension \
    --page-requisites \
    --no-parent \
    --no-host-directories \
    --cut-dirs=0 \
    --user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
    --wait=1 \
    --random-wait \
    --directory-prefix="$DOWNLOAD_DIR" \
    --domains="gabe-clarke.webflow.io" \
    "$SITE_URL"

echo ""
echo -e "${YELLOW}Step 2: Extracting CDN URLs and downloading assets...${NC}"

# Extract unique CDN URLs from HTML files
CDN_DOMAINS=(
    "cdn.prod.website-files.com"
    "d3e54v103j8qbb.cloudfront.net"
    "fonts.googleapis.com"
    "fonts.gstatic.com"
    "ajax.googleapis.com"
)

# Download assets from Webflow CDN
for domain in "${CDN_DOMAINS[@]}"; do
    echo "  Downloading from $domain..."
    wget \
        --recursive \
        --level=1 \
        --no-parent \
        --no-host-directories \
        --cut-dirs=0 \
        --page-requisites \
        --convert-links \
        --adjust-extension \
        --directory-prefix="$DOWNLOAD_DIR" \
        --accept=css,js,jpg,jpeg,png,gif,svg,woff,woff2,ttf,eot,ico,webp \
        --domains="$domain" \
        --wait=0.5 \
        "$SITE_URL" 2>/dev/null || true
done

echo ""
echo -e "${GREEN}✓ Download complete!${NC}"
echo ""
echo "Files downloaded to: $DOWNLOAD_DIR/"
echo ""
echo "Note: Some assets may still reference CDN URLs."
echo "For a fully offline version, you may need to:"
echo "  1. Download remaining assets manually"
echo "  2. Update file paths in HTML files"
echo "  3. Or use HTTrack for a more complete download"

