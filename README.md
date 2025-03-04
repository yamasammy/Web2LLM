# Web2LLM

An advanced Python tool for extracting data from websites, cleaning the content, and converting it to high-quality Markdown for optimal use by LLM systems.

## Features

- **Intelligent content extraction** from web pages with removal of non-relevant elements
- **Advanced content cleaning**:
  - Removal of headers, footers, navbars, and sidebars
  - Complete elimination of CSS and JavaScript
  - Intelligent detection of navigation elements through content analysis
- **Optimized Markdown conversion** with multiple cascading methods
- **REST API** for workflow integration
- **Local saving** to .md files with relevant name generation

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Scrape a URL and display the result
python run.py scrape https://example.com

# Scrape a URL and save as Markdown
python run.py scrape https://example.com --save

# Specify an output filename
python run.py scrape https://example.com --save --output my-file.md
```

### Start the API

```bash
python -m app.main
```

### Use as a Library

```python
from app.scraper import scrape_url
from app.converter import html_to_markdown

# Scrape a URL
result = scrape_url("https://example.com")
html_content = result["html"]

# Convert to markdown
markdown_content = html_to_markdown(html_content)

# Save to a file
with open("output.md", "w") as f:
    f.write(markdown_content)
```

## API Endpoints

- `POST /scrape`: Scrape a URL and return the content in Markdown
- `POST /scrape/save`: Scrape a URL and save the content as a Markdown file

## Major Improvements

### 1. Intelligent Content Extraction

- **Complete removal of headers and footers** via an exhaustive list of CSS selectors
- **Advanced detection of navbars and sidebars**:
  - By standard CSS selectors
  - By link density analysis (menus with numerous short links)
  - By textual content analysis (terms like "menu", "navigation")
  - By position in the page (first/last elements)
  - By CSS attributes (reduced width typical of sidebars)
- **Extraction of additional content** if Readability doesn't extract enough
- **Balanced and adaptive approach**:
  - Preservation of rich content (>1000 characters)
  - Conditional application of cleaning methods
  - Adjustable thresholds for different types of sites

### 2. Complete Elimination of CSS and JavaScript

- **Removal of all script and style tags** and their content
- **Elimination of JavaScript attributes** (onclick, onload, etc.)
- **Removal of inline styles** and JavaScript-related classes
- **Filtering of code blocks** resembling CSS or JavaScript
- **Cleaning of CDATA sections** that may contain code

### 3. Optimized Markdown Conversion

- **Multi-method cascading approach**:
  - Using html2markdown as the main method
  - Structured extraction with BeautifulSoup as backup
  - Raw text extraction as a last resort
- **Complete cleaning of residual HTML tags**
- **Specific processing** for tables, quotes, code blocks, images
- **Double cleaning** of spaces and line breaks

### 4. Robust Error Handling

- **Saving of raw HTML** in case of conversion failure
- **Text extraction** as an alternative if conversion fails
- **Better detection of encoding** of web pages
- **Generation of meaningful and robust filenames**

## Adjustable Parameters

To adapt the tool to specific sites, you can modify:

1. **Detection thresholds** in `detect_nav_by_content()`:
   - Number of links (currently 8)
   - Percentage of short links (currently 85%)
   - Text length considered significant (currently 50 characters per link)

2. **CSS selectors** in `remove_headers_footers()`:
   - Add specific selectors for certain sites
   - Modify the `header_selectors`, `footer_selectors`, etc. lists

3. **Content thresholds** in `clean_html()`:
   - Modify the 500 character threshold for additional extraction
   - Adjust the 70% threshold for applying advanced detection

## Result Examples

With these improvements, the scraper produces:
- Clean Markdown content without HTML tags
- No JavaScript scripts or CSS styles
- No navigation bars or sidebars
- Only informative main content

## Maintenance and Troubleshooting

If you encounter problems with certain sites:

1. **Check the HTML structure** of the site to identify particular elements
2. **Add specific CSS selectors** to the appropriate lists
3. **Adjust detection thresholds** to be more or less aggressive
4. **Use the raw HTML saving option** to analyze the original content

## Configuration

See the `.env.example` file for available configuration options. 
