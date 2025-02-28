# ZombithX64 - Advanced Web Scraping Tool

<div align="center">

![Project Logo](Zom.png)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

*A powerful web scraping and content analysis tool with AI integration*

</div>

## 📋 Table of Contents
- [ZombithX64 - Advanced Web Scraping Tool](#zombithx64---advanced-web-scraping-tool)
  - [📋 Table of Contents](#-table-of-contents)
  - [Overview](#overview)
  - [🚀 Key Features](#-key-features)
    - [🌐 Web Scraping Capabilities](#-web-scraping-capabilities)
    - [📝 Content Processing](#-content-processing)
    - [🤖 AI Integration](#-ai-integration)
    - [📊 Output Formats](#-output-formats)
  - [📁 Project Structure](#-project-structure)
    - [Core Components](#core-components)
  - [🛠️ Setup and Usage](#️-setup-and-usage)
  - [📤 Output Directory Structure](#-output-directory-structure)
  - [🔍 Features in Detail](#-features-in-detail)
    - [GitHub Repository Handling](#github-repository-handling)
    - [Content Processing Pipeline](#content-processing-pipeline)
    - [Error Handling](#error-handling)
  - [🤖 AI Integration](#-ai-integration-1)
  - [🌐 Web Interface Features](#-web-interface-features)
  - [⚠️ Important Notes](#️-important-notes)
  - [🔄 Future Improvements](#-future-improvements)
  - [👥 Contributing](#-contributing)
  - [📄 License](#-license)

## Overview
ZombithX64 is a comprehensive web scraping and content analysis tool that combines multiple approaches to extract, process, and analyze web content. The project features both command-line and web-based interfaces, with special handling for GitHub repositories and integration with Mistral AI for content summarization.

## 🚀 Key Features

### 🌐 Web Scraping Capabilities
- **Intelligent Content Extraction**
  - HTML parsing with BeautifulSoup4
  - Special handling for GitHub repositories
  - Raw markdown file processing
  - Robots.txt compliance checking

### 📝 Content Processing
- **Smart Content Analysis**
  - Automatic content structure detection
  - Preservation of header hierarchy
  - List formatting (ordered and unordered)
  - Code block preservation
  - Link extraction and formatting

### 🤖 AI Integration
- **Mistral AI Integration**
  - Content summarization
  - Intelligent chunking for large content
  - Adaptive processing based on content size
  - Error handling with informative messages

### 📊 Output Formats
- **Flexible Export Options**
  - JSON output with metadata
  - Formatted Markdown output
  - Timestamped file organization
  - Structured content hierarchy

## 📁 Project Structure

### Core Components
1. **CrewNormalX64.py**
   - Basic web scraping functionality
   - HTML content extraction
   - Markdown formatting
   - File output handling

2. **CrewAPIX64.py**
   - Enhanced scraping capabilities
   - Mistral AI integration
   - GitHub-specific parsing
   - Advanced error handling

3. **Web Interface**
   - User-friendly interface for URL input
   - Result display with content preview
   - Download options for JSON/Markdown
   - Error feedback

## 🛠️ Setup and Usage

1. **Installation**
   ```bash
   # Clone the repository
   git clone [repository-url]
   cd [repository-name]

   # Install required packages
   pip install -r requirements.txt
   ```

2. **Environment Setup**
   - Create a `.env` file in the project root
   - Add your Mistral AI API key:
     ```
     MISTRAL_API_KEY=your_api_key_here
     ```

3. **Running the Tool**

   a. Command Line Interface:
   ```bash
   # Basic scraping
   python CrewNormalX64.py

   # Advanced scraping with AI
   python CrewAPIX64.py
   ```

   b. Web Interface:
   ```bash
   # Start the web server
   python app.py
   ```

## 📤 Output Directory Structure
```
scraped_output/
├── scraped_[timestamp].json  # JSON format output
└── scraped_[timestamp].md    # Markdown format output
```

## 🔍 Features in Detail

### GitHub Repository Handling
- Repository metadata extraction
- README.md content parsing
- Description and structure preservation
- Support for both main and master branches

### Content Processing Pipeline
1. URL validation and robots.txt checking
2. Content extraction and structure analysis
3. AI-powered summarization (when enabled)
4. Formatted output generation

### Error Handling
- Comprehensive error catching
- Informative error messages
- Fallback mechanisms for different scenarios
- API rate limit handling

## 🤖 AI Integration

The tool uses Mistral AI for content summarization with the following features:
- Automatic content chunking for large texts
- Progressive summarization for multi-chunk content
- Detailed progress tracking
- Error recovery mechanisms

## 🌐 Web Interface Features
- Clean and intuitive user interface
- Real-time scraping feedback
- Content preview functionality
- Direct file download options

## ⚠️ Important Notes
- Ensure proper API key configuration in `.env`
- Respect robots.txt guidelines
- Monitor rate limits for API calls
- Check output directory permissions

## 🔄 Future Improvements
- Additional output format support
- Enhanced error recovery
- Multiple AI provider support

## 👥 Contributing
Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
