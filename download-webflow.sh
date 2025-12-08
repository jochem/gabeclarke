#!/bin/bash

# Webflow Site Downloader using wget
# This script downloads your published Webflow site for local development

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Webflow Site Downloader${NC}"
echo "================================"
echo ""

# Check if URL is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Please provide your Webflow site URL${NC}"
    echo ""
    echo "Usage: ./download-webflow.sh <your-site-url>"
    echo "Example: ./download-webflow.sh https://yoursite.webflow.io"
    echo ""
    exit 1
fi

SITE_URL=$1

# Check if wget is installed
if ! command -v wget &> /dev/null; then
    echo -e "${RED}Error: wget is not installed${NC}"
    echo ""
    echo "Install wget on macOS:"
    echo "  brew install wget"
    echo ""
    exit 1
fi

echo -e "${YELLOW}What wget WILL download:${NC}"
echo "  ✓ All published HTML pages"
echo "  ✓ CSS stylesheets"
echo "  ✓ JavaScript files"
echo "  ✓ Images and assets"
echo "  ✓ Fonts (if hosted on your domain)"
echo ""
echo -e "${YELLOW}What wget WON'T download:${NC}"
echo "  ✗ Unpublished pages or draft content"
echo "  ✗ CMS content that's not published"
echo "  ✗ Editor-specific settings/metadata"
echo "  ✗ Assets hosted on external CDNs (may need manual download)"
echo "  ✗ Dynamic features (forms, CMS, ecommerce)"
echo ""
echo -e "${GREEN}Starting download...${NC}"
echo ""

# Create download directory
DOWNLOAD_DIR="webflow-site"
mkdir -p "$DOWNLOAD_DIR"

# wget command optimized for Webflow sites
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
    --limit-rate=200k \
    --directory-prefix="$DOWNLOAD_DIR" \
    "$SITE_URL"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Download complete!${NC}"
    echo ""
    echo "Files downloaded to: $DOWNLOAD_DIR/"
    echo ""
    echo "Next steps:"
    echo "  1. Review the downloaded files"
    echo "  2. Move files to project root if needed"
    echo "  3. Run 'npm run dev' to start local server"
    echo ""
else
    echo ""
    echo -e "${RED}✗ Download failed${NC}"
    echo "Please check the URL and try again"
    exit 1
fi

