# Template Commonality Analysis

## Overview
This document summarizes the commonality analysis performed on the HTML files to identify reusable template components.

## Files Analyzed
- **Total HTML files**: 31
- **Reference file**: `index.html`

## Template Components Identified

### 1. Header Template (`templates/header.html`)
**Commonality**: High (90%+ match across all files)

**Structure**:
- **Common prefix**: DOCTYPE, HTML opening tag, meta charset, common meta tags
- **Page-specific section**: 
  - Title tag
  - Meta description
  - Open Graph tags
  - Twitter card tags
  - Page-specific inline styles (with data-w-id attributes)
- **Common suffix**: 
  - Font preconnect links
  - WebFont script
  - Webflow detection script
  - Favicon links
  - Body font smoothing styles
  - Webflow currency settings script
  - Closing `</head>` tag

**Variations**:
- Asset paths differ (root files use `assets/`, subdirectory files use `../assets/`)
- Page-specific inline styles vary by page
- Title and meta content are page-specific

### 2. Navigation Template (`templates/navigation.html`)
**Commonality**: High (appears in most pages)

**Structure**:
- Navbar with collapse functionality
- Logo/brand section ("Gabe Clarke")
- Navigation menu with numbered links:
  - Home (01)
  - About (02)
  - Projects (03)
  - Shop (04)
  - Contacts (05)
- Social media links (Instagram, Twitter, Behance)
- Buy/Webflow link
- Menu button for mobile

**Variations**:
- Active page indicator (`w--current` class)
- Some pages may have different navigation structures

### 3. Footer Template (`templates/footer.html`)
**Commonality**: High (appears in most pages)

**Structure**:
- Back-to-top link
- Footer meta links section with:
  - "site by/ Fouroom" link
  - "powered by/ Webflow" link
- License and changelog links (if applicable)

**Variations**:
- Some pages may have additional footer content
- Link structure is consistent

### 4. Closing Template (`templates/closing.html`)
**Commonality**: Very High (100% match)

**Structure**:
- Preloader div (if present)
- jQuery script
- Webflow JavaScript chunks
- Closing `</body>` and `</html>` tags

## Template Usage Strategy

### Recommended Approach
1. **Header**: Extract common prefix and suffix, use placeholders for page-specific content
2. **Navigation**: Use as-is, but make active page indicator configurable
3. **Footer**: Use as-is, minimal variations
4. **Closing**: Use as-is, very consistent

### Implementation Options
1. **Server-side includes** (SSI): Use `<!--#include virtual="..." -->`
2. **Build-time templating**: Use a static site generator or build script
3. **JavaScript includes**: Load templates via JavaScript (not recommended for SEO)
4. **PHP includes**: If using PHP: `<?php include '...'; ?>`

## Next Steps
1. Create a build script to inject templates into HTML files
2. Identify page-specific content sections
3. Create a template system with variable substitution
4. Document the template variables and their usage







