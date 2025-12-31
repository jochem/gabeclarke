# HTML Templates

This directory contains reusable template components extracted from the HTML files.

## Template Files

### `header.html`
The HTML `<head>` section with common elements. Contains placeholders for:
- `{{PAGE_ID}}` - Webflow page ID (e.g., "670903a26ae4eb4eb6eb91ff")
- `{{PAGE_TITLE}}` - Page title
- `{{PAGE_DESCRIPTION}}` - Page meta description
- `{{PAGE_STYLES}}` - Page-specific inline styles (optional)
- `{{ASSET_PATH}}` - Asset path prefix (empty for root, "../" for subdirectories)

### `navigation.html`
The main navigation menu that appears on all pages. Includes:
- Logo/brand ("Gabe Clarke")
- Navigation links (Home, About, Projects, Shop, Contacts)
- Social media links (Instagram, Twitter, Behance)
- Mobile menu button

**Note**: The active page indicator (`w--current` class) should be added to the appropriate link based on the current page.

### `footer.html`
The footer section that appears at the bottom of pages. Includes:
- Back-to-top link
- Footer meta links (site by Fouroom, powered by Webflow)
- License and changelog links (if applicable)

### `closing.html`
Closing tags and scripts that appear after `</body>`. Includes:
- Preloader (if present)
- jQuery script
- Webflow JavaScript chunks
- Closing `</body>` and `</html>` tags

## Usage

### Option 1: Server-Side Includes (SSI)
If your server supports SSI, you can include templates like this:

```html
<!--#include virtual="templates/header.html" -->
<body>
  <!--#include virtual="templates/navigation.html" -->
  
  <!-- Page content here -->
  
  <!--#include virtual="templates/footer.html" -->
</body>
<!--#include virtual="templates/closing.html" -->
```

### Option 2: Build-Time Templating
Use a build script (Python, Node.js, etc.) to:
1. Read template files
2. Replace placeholders with actual values
3. Inject templates into HTML files
4. Output final HTML files

### Option 3: PHP Includes
If using PHP:

```php
<?php
$page_title = "Home #1 • Ofelia – Webflow Ecommerce website template";
$page_description = "Ofelia is a template made for every artist...";
$page_id = "670903a26ae4eb4eb6eb91ff";
$asset_path = ""; // or "../" for subdirectories
$page_styles = ""; // optional inline styles
include 'templates/header.php';
?>
```

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{PAGE_ID}}` | Webflow page ID | `670903a26ae4eb4eb6eb91ff` |
| `{{PAGE_TITLE}}` | Page title | `Home #1 • Ofelia – Webflow Ecommerce website template` |
| `{{PAGE_DESCRIPTION}}` | Meta description | `Ofelia is a template made for every artist...` |
| `{{PAGE_STYLES}}` | Page-specific inline CSS | `<style>...</style>` or empty |
| `{{ASSET_PATH}}` | Asset path prefix | `""` (root) or `"../"` (subdirectory) |

## Commonality Statistics

- **Header**: 90%+ commonality across all files
- **Navigation**: Appears in 100% of pages (32/32 files analyzed)
- **Footer**: Appears in 90%+ of pages (28/31 files analyzed)
- **Closing**: 100% commonality

## Next Steps

1. Create a build script to automate template injection
2. Extract page-specific content sections
3. Create a configuration file for page metadata
4. Set up a build process to generate final HTML files







