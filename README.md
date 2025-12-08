# Webflow Template Local Development

This repository contains your exported Webflow template for local development.

## Getting Started

### Step 1: Download Your Published Site

Since code export requires a paid Webflow plan, here are **free alternatives** to download your site:

#### Option A: Browser Extension (Easiest) ⭐ Recommended

1. **Install a site downloader extension**:
   - **Chrome/Edge**: "Save Page WE" or "SingleFile"
   - **Firefox**: "Save Page WE" or "SingleFile"
   
2. **Download your site**:
   - Publish your Webflow site (or use the template's published version)
   - Visit your published site URL (e.g., `https://yoursite.webflow.io`)
   - Use the extension to save the page
   - Repeat for each page you want to download

#### Option B: HTTrack Website Copier (Best for Full Sites)

1. **Download HTTrack**: https://www.httrack.com/ (free, cross-platform)
2. **Set up the download**:
   - Enter your published Webflow site URL
   - Choose this directory as the download location
   - Start the download
   - HTTrack will download all pages, CSS, JS, and images

#### Option C: Command Line (wget) ⚡ Fast & Complete

**Quick Answer**: wget downloads everything that's **published and visible** on your site - all HTML, CSS, JS, images, and assets. It won't get editor-only features or unpublished content, but for local development of styling and structure, it's perfect!

**Install wget** (if needed):
```bash
brew install wget
```

**Use the provided script** (recommended):
```bash
./download-webflow.sh https://yoursite.webflow.io
```

**Or use wget directly**:
```bash
wget --mirror --convert-links --adjust-extension --page-requisites --no-parent https://yoursite.webflow.io
```

#### Option D: Manual Browser Method

1. **Open your published site** in a browser
2. **Right-click → "Save Page As"** (or `Cmd+S` / `Ctrl+S`)
3. **Choose "Web Page, Complete"** to save HTML + assets
4. **Repeat for each page** you need
5. **Copy saved files** into this directory

#### Option E: Browser Developer Tools

1. **Open your published site** and press `F12` (or `Cmd+Option+I` on Mac)
2. **Go to Network tab** and reload the page
3. **Right-click → "Save all as HAR"** (optional, for reference)
4. **Manually save** HTML, CSS, and JS files from the Sources/Network tab

### Step 2: Organize Downloaded Files

After downloading, organize your files:
- Ensure `index.html` is in the root directory
- CSS files should be in a `css/` folder (or keep as-is)
- JavaScript files should be in a `js/` folder (or keep as-is)
- Images should be in an `images/` or `assets/` folder

### Step 3: Set Up Local Development

Once you've downloaded your site files:

1. **Install a Local Server** (choose one):
   - **Node.js**: `npm run dev` (already configured) or `npx serve .`
   - **Python**: `python3 -m http.server 8000`
   - **VS Code**: Use the "Live Server" extension
   - **PHP**: `php -S localhost:8000`

2. **View Your Site**:
   - Open `http://localhost:8000` (or the port your server uses)
   - Navigate to `index.html` to see your homepage

> **Note**: Some downloaded sites may have broken links or missing assets. You may need to adjust file paths after downloading.

## Important Notes

⚠️ **What wget Downloads vs. What's in the Editor**:

**✅ What you WILL get** (everything published):
- All HTML pages (structure and content)
- All CSS stylesheets (custom styles, animations, responsive breakpoints)
- All JavaScript files (interactions, custom code)
- Images and assets (logos, photos, icons)
- Font files (if self-hosted)
- Layout, spacing, colors, typography - everything visual!

**❌ What you WON'T get** (editor-only):
- Unpublished pages or draft content
- CMS content that's not published
- Editor metadata/settings
- Assets on external CDNs (may need manual download)
- Dynamic features (forms, CMS, ecommerce functionality)
- Editor-specific interactions in development

**💡 Bottom Line**: For local development of **design, styling, and structure**, wget gets you 95%+ of what you need! The visual design, CSS, and HTML structure will be identical to what's published.

## Local Development Workflow

1. Make changes to HTML, CSS, or JavaScript files locally
2. Test changes in your local server
3. If you want to sync back to Webflow, you'll need to manually recreate changes in the Designer

## Project Structure

After extraction, your project should look like:
```
.
├── index.html          # Homepage
├── css/               # Stylesheets
├── js/                # JavaScript files
├── images/            # Image assets
└── [other pages].html # Additional pages
```

## Next Steps

- Review the downloaded code structure
- Fix any broken links or missing assets
- Set up version control (Git): `git init`
- Configure a build process if needed
- Set up a deployment pipeline

## Troubleshooting

**Broken links or missing images?**
- Check that all asset folders were downloaded
- Verify file paths are relative (not absolute Webflow URLs)
- Some assets might be hosted on Webflow CDN - you may need to download them separately

**CSS/JS not loading?**
- Check browser console for 404 errors
- Ensure file paths match your folder structure
- Some Webflow scripts may need to be replaced with local alternatives

