# Web2LLM

An advanced Python tool for extracting data from websites, cleaning the content, and converting it to high-quality Markdown for optimal use by LLM systems.

## Features

- **LLM-Optimized Content Extraction**: Intelligently extracts and cleans web content specifically formatted for Large Language Models and AI-powered IDEs like Cursor
- **AI-Ready Documentation Generation**: Creates markdown files that can be used to feed AI tools with the latest framework documentation, API references, or technical guides
- **Context Window Optimization**: Removes non-essential elements (headers, footers, navbars) to maximize the useful information within LLM context windows
- **Knowledge Base Enhancement**: Generates clean, structured markdown perfect for building custom knowledge bases to augment AI capabilities
- **Framework Documentation Updates**: Easily capture the latest documentation for programming frameworks to keep your AI tools up-to-date
- **Intelligent Content Processing**:
  - Removal of distracting UI elements that confuse AI parsers
  - Complete elimination of CSS and JavaScript that waste token space
  - Smart detection of navigation elements through semantic analysis
- **Multiple Output Formats** optimized for different AI consumption patterns
- **REST API** for seamless integration into AI workflows
- **Automatic File Management** with intelligent naming for organized knowledge repositories

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

### 1. AI-Optimized Content Extraction

- **Token Efficiency**: Removes headers, footers, and navigation elements to maximize useful content within LLM context windows
- **Advanced AI-Confusing Element Detection**:
  - Identifies and removes elements by standard CSS selectors
  - Uses link density analysis to detect navigation menus
  - Employs semantic content analysis to identify non-essential sections
  - Recognizes positional patterns typical of UI elements
  - Detects sidebar elements through structural analysis
- **Smart Content Preservation**:
  - Retains information-rich sections (>1000 characters)
  - Applies adaptive cleaning based on content type
  - Uses configurable thresholds for different website categories

### 2. LLM Context Window Optimization

- **Complete removal of token-wasting elements** like scripts, styles, and decorative markup
- **Elimination of interactive JavaScript attributes** irrelevant to AI processing
- **Removal of styling information** that consumes valuable context space
- **Filtering of code snippets** not relevant to the main content
- **Cleaning of metadata sections** that don't contribute to understanding

### 3. AI-Ready Markdown Generation

- **Multi-layered conversion strategy**:
  - Primary conversion optimized for AI readability
  - Structured extraction fallback for complex layouts
  - Plain text preservation when structure is less important
- **Enhanced semantic structure** for better AI comprehension
- **Special handling** for data-rich elements like tables, quotes, and code blocks
- **Optimized whitespace** for improved token efficiency

### 4. LLM Integration Reliability

- **Fallback mechanisms** to ensure content is always retrievable
- **Format consistency** for predictable AI processing
- **Encoding normalization** for cross-platform compatibility
- **Intelligent file organization** for systematic knowledge management

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

## AI Integration Use Cases

### Enhancing AI-Powered IDEs like Cursor

- **Framework Documentation Updates**: Keep your AI coding assistant up-to-date with the latest framework documentation by scraping official docs
- **API Reference Integration**: Create clean markdown files from API documentation for more accurate code suggestions
- **Tutorial Conversion**: Transform web tutorials into markdown for better context when asking for implementation help
- **Error Solution Repository**: Build a collection of cleaned Stack Overflow or GitHub issue solutions for common errors

### Augmenting LLM Knowledge

- **Technical Documentation**: Feed your LLM with the latest technical documentation that may not be in its training data
- **Research Papers**: Convert academic papers and research findings into clean markdown for better AI comprehension
- **Product Documentation**: Create markdown versions of product documentation for more accurate product-specific assistance
- **Custom Knowledge Base**: Build specialized knowledge repositories for domain-specific AI applications

### Practical Examples

```python
# Update your AI IDE with the latest React documentation
python run.py scrape https://reactjs.org/docs/getting-started.html --save --output react_latest.md

# Create a knowledge base from multiple pages
from app.scraper import scrape_url
from app.converter import html_to_markdown

urls = [
    "https://docs.python.org/3/library/asyncio.html",
    "https://docs.python.org/3/library/concurrent.futures.html"
]

for url in urls:
    result = scrape_url(url)
    markdown = html_to_markdown(result["html"])
    filename = f"python_async_{url.split('/')[-1].replace('.html', '.md')}"
    with open(filename, "w") as f:
        f.write(markdown)
```

## Result Examples

With these improvements, Web2LLM produces:

- **AI-Optimized Content**: Clean, structured markdown without distracting elements
- **Token-Efficient Format**: No wasted tokens on JavaScript, CSS, or UI elements
- **Context Window Maximization**: Only the most informative content is preserved
- **Semantic Structure**: Properly formatted headings, lists, and code blocks for better AI comprehension
- **Consistent Formatting**: Predictable structure for reliable AI processing

### Before & After Example

**Before processing (raw HTML):**
```html
<html>
<head>
  <title>API Documentation</title>
  <style>/* 250KB of CSS */</style>
  <script>/* 500KB of JavaScript */</script>
</head>
<body>
  <header>
    <nav><!-- Complex navigation menu --></nav>
    <div class="search"><!-- Search form --></div>
  </header>
  <aside><!-- Sidebar with links --></aside>
  <main>
    <h1>API Reference</h1>
    <p>This documentation describes the REST API...</p>
    <!-- Actual valuable content -->
  </main>
  <footer><!-- Copyright, links, etc. --></footer>
</body>
</html>
```

**After processing (markdown for LLM consumption):**
```markdown
# API Reference

This documentation describes the REST API...

## Endpoints

### GET /users

Returns a list of users.

**Parameters:**
- `limit`: Maximum number of results (default: 20)
- `offset`: Pagination offset (default: 0)

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "name": "Example User"
    }
  ],
  "total": 100
}
```
```

## Maintenance and Troubleshooting

If you encounter problems with certain sites:

1. **Check the HTML structure** of the site to identify particular elements
2. **Add specific CSS selectors** to the appropriate lists
3. **Adjust detection thresholds** to be more or less aggressive
4. **Use the raw HTML saving option** to analyze the original content

## Configuration

See the `.env.example` file for available configuration options. 
