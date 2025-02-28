# Web Scraping Tool Documentation

## Files Overview

### 1. Web Content Scraper (app.py)
A basic web scraping utility that extracts content from web pages. Features include:
- Basic robots.txt compliance checking
- HTML content extraction with BeautifulSoup
- Support for headers, lists, and code blocks
- Content saving in both JSON and Markdown formats
- Simple error handling

### 2. Advanced Content Analyzer (main.py)
An enhanced version with additional capabilities:
- Comprehensive GitHub repository content extraction
  - Repository descriptions
  - README content parsing
  - Support for multiple content formats
- Integration with Mistral AI for content summarization
- Advanced error handling and detailed logging
- Organized output with timestamped files
- Support for large content processing through chunking
- Structured output directory management

## Key Features
- Web content scraping with respect for robots.txt
- Markdown and JSON output formats
- AI-powered content summarization
- Support for various content types (HTML, Markdown, GitHub repos)
- Extensive error handling and logging
