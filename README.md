<div align="center">

![Project Logo](./public/Zom.png)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Package](https://img.shields.io/badge/GitHub-Package-green.svg)](https://github.com/features/packages)

*A powerful web scraping and content analysis tool with AI integration*

</div>

## 📋 Table of Contents

- [📋 Table of Contents](#-table-of-contents)
- [Overview](#overview)
- [📦 Releases](#-releases)
  - [Version 1.2.0 (Latest)](#version-120-latest)
  - [Version 1.1.0](#version-110)
  - [Version 1.0.0](#version-100)
  - [Version 0.9.0 (Beta)](#version-090-beta)
  - [Version 0.5.0 (Alpha)](#version-050-alpha)
- [🚀 Key Features](#-key-features)
  - [🌐 Web Scraping Capabilities](#-web-scraping-capabilities)
  - [🔒 Security and Compliance](#-security-and-compliance)
  - [📝 Content Processing](#-content-processing)
  - [🤖 Content Analysis](#-content-analysis)
  - [📊 Output Formats](#-output-formats)
- [📁 Project Structure](#-project-structure)
  - [Core Components](#core-components)
- [Installation](#installation)
- [Running the Tool](#running-the-tool)
  - [1. Standard Version (No API Required)](#1-standard-version-no-api-required)
  - [2. API Version (Requires Mistral API Key)](#2-api-version-requires-mistral-api-key)
  - [3. Advanced Version (Crew4lX64.py)](#3-advanced-version-crew4lx64py)
- [Running the Tool](#running-the-tool-1)
  - [1. Standard Version (No API Required)](#1-standard-version-no-api-required-1)
  - [2. API Version (Requires Mistral API Key)](#2-api-version-requires-mistral-api-key-1)
  - [Choosing the Right Version](#choosing-the-right-version)
  - [Web Interface](#web-interface)
  - [3. Advanced Version (Crew4lX64.py)](#3-advanced-version-crew4lx64py-1)
- [Publishing to GitHub Packages](#publishing-to-github-packages)
- [📤 Output Directory Structure](#-output-directory-structure)
- [🔍 Features in Detail](#-features-in-detail)
  - [Advanced Scraping Capabilities (Crew4lX64.py)](#advanced-scraping-capabilities-crew4lx64py)
    - [📝 Markdown Generation](#-markdown-generation)
    - [📊 Structured Data Extraction](#-structured-data-extraction)
    - [🌐 Browser Integration](#-browser-integration)
    - [🔎 Media and Content Extraction](#-media-and-content-extraction)
  - [GitHub Repository Handling](#github-repository-handling)
  - [Content Processing Pipeline](#content-processing-pipeline)
  - [Error Handling](#error-handling)
- [🤖 Content Analysis](#-content-analysis-1)
  - [API Version (CrewAPIX64)](#api-version-crewapix64)
  - [Standard Version (CrewNormalX64)](#standard-version-crewnormalx64)
- [🌐 Web Interface Features](#-web-interface-features)
- [⚠️ Important Notes](#️-important-notes)
- [🔄 Future Improvements](#-future-improvements)
- [👥 Contributing](#-contributing)
- [Star History](#star-history)
- [📄 License](#-license)

## Overview

**Crewzombitx64** is a comprehensive web scraping and content analysis tool designed to extract, process, and analyze web content efficiently. It supports both command-line and web-based interfaces, with special handling for GitHub repositories and integration with Mistral AI for advanced content summarization.

**Key Features:**
- Intelligent content extraction with BeautifulSoup4
- Advanced proxy management and rate limiting
- Robust security and compliance features
- Multiple output formats (JSON, Markdown)
- Integration with Mistral AI for content analysis
- User-friendly web interface for easy access and configuration

## 📦 Releases

### Version 1.2.0 (Latest)

- **Enhanced Security and Legal Compliance**:
  - Improved sensitive data detection (API keys, passwords, tokens)
  - Strict URL validation and hostname checking
  - Advanced robots.txt compliance system
  - Protected access to sensitive paths and admin panels
  - Extended internal network protection

- **Advanced Proxy Management**:
  - Intelligent proxy rotation based on performance
  - Proxy health monitoring and scoring
  - Automatic removal of poor performers
  - Response time tracking
  - Proxy anonymity verification

- **Adaptive Rate Limiting**:
  - Domain-specific rate controls
  - Automatic backoff on errors
  - Burst control with configurable limits
  - Response time monitoring
  - Per-domain request tracking

- **Enhanced Configuration System**:
  - Comprehensive security defaults
  - Privacy-focused settings
  - Legal compliance options
  - Random user agent rotation
  - Input validation and sanitization
  - Request limits and error thresholds

### Version 1.1.0

- **Google Colab Integration**:
  - Easy-to-use notebook interface
  - Cloud-based execution support
  - Interactive examples and tutorials

- **Advanced Web Scraping Implementation**:
  - LLM-powered schema generation using OpenAI/Ollama
  - Automatic CSS and XPath schema generation
  - Comprehensive documentation and examples
  - Parallel processing and performance optimizations
  - Enhanced JSON extraction with JSONPath support
  - Complex JSONPath, JSON-CSS, and Microdata extraction
  - SSL certificate handling with custom paths
  - Enhanced security features
  - Async/await support for better concurrency
  - Improved media extraction
  - Document type detection
  - Lazy loading support
  - Responsive image handling

### Version 1.0.0

- **Initial Release**:
  - Core web scraping functionality
  - Mistral AI integration
  - Web interface implementation
  - GitHub repository handling
  - JSON and Markdown export
  - Basic HTML content extraction
  - Markdown formatting
  - File output handling

### Version 0.9.0 (Beta)

- **Beta Release**:
  - Core web scraping features
  - Basic content processing pipeline
  - Command-line interface

### Version 0.5.0 (Alpha)

- **Alpha Release**:
  - Basic HTML parsing
  - File output handling
  - Error handling implementation

## 🚀 Key Features

### 🌐 Web Scraping Capabilities

- **Intelligent Content Extraction**:
  - HTML parsing with BeautifulSoup4
  - Special handling for GitHub repositories
  - Raw markdown file processing
  - Advanced robots.txt compliance system
  - Strict URL validation and hostname checking
  - Protected access controls for sensitive paths

### 🔒 Security and Compliance

- **Data Protection**:
  - Advanced sensitive data detection and redaction
  - Automatic detection of API keys, passwords, and tokens
  - Secure handling of credentials and sensitive information

- **Access Control**:
  - Extended internal network protection
  - Strict URL validation and filtering
  - Protected access to sensitive paths

- **Network Security**:
  - Intelligent proxy rotation with performance scoring
  - Automatic removal of poor-performing proxies
  - Response time monitoring and optimization

- **Legal Compliance**:
  - Advanced robots.txt compliance system
  - Rate limiting with domain-specific controls
  - Privacy-focused configuration defaults

### 📝 Content Processing

- **Smart Content Analysis**:
  - Automatic content structure detection
  - Preservation of header hierarchy
  - List formatting (ordered and unordered)
  - Code block preservation
  - Link extraction and formatting

### 🤖 Content Analysis

- **Multiple Analysis Options**:
  - **API Version (CrewAPIX64)**:
    - Mistral AI-powered summarization
    - Intelligent chunking for large content
    - Adaptive processing based on content size
  - **Standard Version (CrewNormalX64)**:
    - Local text summarization using NLTK
    - Sentence importance scoring
    - Position-based content analysis
    - Keyword-based content evaluation

### 📊 Output Formats

- **Flexible Export Options**:
  - JSON output with metadata
  - Formatted Markdown output
  - Timestamped file organization
  - Structured content hierarchy

## 📁 Project Structure

### Core Components

1. **CrewColabX64.ipynb**:
   - **Description**: This Jupyter Notebook is designed for Google Colab, providing an interactive and cloud-based environment to run Crewzombitx64.
   - **Features**:
     - Google Colab Integration: Seamless execution in the cloud.
     - Interactive Interface: Utilizes Jupyter Notebook for code execution and visualization.
     - Cloud-Based Execution: No local setup required, run directly in your browser.
     - Tutorial and Examples: Includes practical examples and tutorials for new users.
     - Built-in Documentation: Integrated documentation within the notebook for easy access to information.
     - Ideal Use Case: Users who prefer a cloud-based, interactive environment and want to quickly get started with web scraping and content analysis.

2. **CrewNormalX64.py**:
   - **Description**: This Python script represents the standard version of Crewzombitx64, focusing on core web scraping functionalities without requiring an API key.
   - **Features**:
     - Basic Web Scraping: Extracts content from web pages using BeautifulSoup4.
     - HTML Content Extraction: Focuses on parsing and extracting information from HTML.
     - Markdown Formatting: Converts extracted content into Markdown for readability.
     - File Output Handling: Saves scraped data to local files in JSON or Markdown format.
     - No API Key Required: Operates independently without needing external API access.
     - Local Text Summarization: Uses NLTK for basic text summarization.
     - GitHub Repository Handling: Includes specific functionalities for processing GitHub repositories.
     - Ideal Use Case: Users who need a simple, locally runnable web scraper without AI summarization and advanced features.

3. **CrewAPIX64.py**:
   - **Description**: This script enhances the standard version by integrating Mistral AI for advanced content analysis and summarization, requiring an API key.
   - **Features**:
     - Enhanced Scraping: Builds upon the capabilities of CrewNormalX64 with improved scraping logic.
     - Mistral AI Integration: Leverages Mistral AI for advanced content summarization.
     - Intelligent Content Chunking: Automatically breaks down large content for AI processing.
     - Enhanced Summary Quality: Provides more detailed and context-aware summaries using AI.
     - GitHub-Specific Parsing: Improved handling for GitHub repository content.
     - Advanced Error Handling: Robust error management and recovery mechanisms.
     - Ideal Use Case: Users who need AI-powered content summarization and are willing to configure an API key for enhanced analysis.

4. **Crew4lX64.py**:
   - **Description**: The advanced version of Crewzombitx64, offering comprehensive web scraping and content analysis features, including browser integration and advanced data extraction techniques.
   - **Features**:
     - Advanced Markdown Generation: Creates clean, structured Markdown with BM25 filtering.
     - Structured Data Extraction: Employs multiple strategies for extracting structured data.
     - Full Browser Integration: Uses a managed browser for dynamic content rendering and lazy-load handling.
     - Comprehensive Media Extraction: Extracts images, videos, and audio from web pages.
     - Enhanced Security and Proxy Management: Includes robust security features and proxy rotation.
     - Adaptive Rate Limiting: Dynamically adjusts request rates to avoid blocking.
     - Legal Compliance and Privacy Controls: Adheres to robots.txt and offers privacy-focused settings.
     - Advanced Data Protection: Implements measures for sensitive data detection and handling.
     - Ideal Use Case: Users who require advanced scraping capabilities, need to handle dynamic content, extract media, and ensure legal compliance and data protection.

5. **Web Interface**:
   - **Description**: A user-friendly web interface built using Flask, providing easy access to Crewzombitx64's functionalities through a browser.
   - **Features**:
     - User-Friendly Interface: Simple and intuitive design for easy navigation.
     - Real-Time Scraping Feedback: Provides live updates during the scraping process.
     - Content Preview: Allows users to preview extracted content directly in the browser.
     - Direct File Download: Offers options to download output in JSON and Markdown formats.
     - Easy URL Input: Simple form for users to input target URLs and configure scraping options.
     - Ideal Use Case: Users who prefer a graphical interface over command-line tools and need quick access to the tool's features via a web browser.

## Installation

To get started with zombitx64, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/zombitx64.git
   cd zombitx64
   ```

2. **Create a Virtual Environment (Recommended)**:
   It is recommended to create a virtual environment to isolate project dependencies.
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/macOS
   venv\Scripts\activate  # On Windows
   ```
   Ensure you have Python 3.8 or higher installed. You can check your Python version using: `python --version`

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Tool**:
   - Create a `.env` file in the project root and add your configuration settings, such as API keys.

## Running the Tool

The tool provides three main versions with different capabilities:

### 1. Standard Version (No API Required)

```bash
python CrewNormalX64.py
```

**Features**:
- Web scraping with BeautifulSoup
- Local text summarization using NLTK
- GitHub repository handling
- JSON and Markdown output
- No API key required

### 2. API Version (Requires Mistral API Key)

```bash
python CrewAPIX64.py
```

**Features**:
- All standard version features
- Advanced AI-powered summarization
- Intelligent content chunking
- Enhanced summary quality
- Requires Mistral API key


### 3. Advanced Version (Crew4lX64.py)

```bash
python Crew4lX64/main.py --url <target_url> [options]
```

**Features**:
- Advanced web scraping with browser integration
- Markdown and structured data extraction
- Comprehensive media and content extraction
- Enhanced security and proxy management
- Adaptive rate limiting

**Options**:
- `--url <target_url>`:  Specify the URL to crawl. (Required)
- `--depth <integer>`:  Specify the maximum depth for crawling. (Optional, default: 1)
- `--browser`: Enable browser mode for dynamic content rendering. (Optional)
- `--headless`: Run browser in headless mode (no GUI). (Optional, requires `--browser`)
- `--scroll`: Enable auto-scrolling for full page load. (Optional, requires `--browser`)
- `--output-format <format>`:  Specify output format ('json' or 'md'). (Optional, default: 'json')
- `--output-file <filename>`: Specify the output filename. (Optional, default: based on URL and timestamp)
- `--rate-limit <float>`:  Set requests per second rate limit. (Optional, default: 1.0)
- `--wait-time <float>`:  Set wait time between requests in seconds. (Optional, default: 0.5)
- `--proxy <proxy_url>`:  Specify a proxy URL. (Optional)
- `--user-agent <user_agent>`:  Specify a custom user agent. (Optional)
- `--timestamp`:  Include timestamp in output filename. (Optional)
- `--verbose`:  Enable verbose output. (Optional)

**Examples**:

- Crawl a website and save output in Markdown format:
  ```bash
  python Crew4lX64/main.py --url https://example.com --output-format md
  ```

- Crawl a website in browser mode with auto-scrolling and headless option:
  ```bash
  python Crew
<div align="center">

![Project Logo](./public/Zom.png)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Package](https://img.shields.io/badge/GitHub-Package-green.svg)](https://github.com/features/packages)

*A powerful web scraping and content analysis tool with AI integration*

</div>

## 📋 Table of Contents

- [📋 Table of Contents](#-table-of-contents)
- [Overview](#overview)
- [📦 Releases](#-releases)
  - [Version 1.2.0 (Latest)](#version-120-latest)
  - [Version 1.1.0](#version-110)
  - [Version 1.0.0](#version-100)
  - [Version 0.9.0 (Beta)](#version-090-beta)
  - [Version 0.5.0 (Alpha)](#version-050-alpha)
- [🚀 Key Features](#-key-features)
  - [🌐 Web Scraping Capabilities](#-web-scraping-capabilities)
  - [🔒 Security and Compliance](#-security-and-compliance)
  - [📝 Content Processing](#-content-processing)
  - [🤖 Content Analysis](#-content-analysis)
  - [📊 Output Formats](#-output-formats)
- [📁 Project Structure](#-project-structure)
  - [Core Components](#core-components)
- [Installation](#installation)
- [Running the Tool](#running-the-tool)
  - [1. Standard Version (No API Required)](#1-standard-version-no-api-required)
  - [2. API Version (Requires Mistral API Key)](#2-api-version-requires-mistral-api-key)
  - [3. Advanced Version (Crew4lX64.py)](#3-advanced-version-crew4lx64py)
- [Running the Tool](#running-the-tool-1)
  - [1. Standard Version (No API Required)](#1-standard-version-no-api-required-1)
  - [2. API Version (Requires Mistral API Key)](#2-api-version-requires-mistral-api-key-1)
  - [Choosing the Right Version](#choosing-the-right-version)
  - [Web Interface](#web-interface)
  - [3. Advanced Version (Crew4lX64.py)](#3-advanced-version-crew4lx64py-1)
- [Publishing to GitHub Packages](#publishing-to-github-packages)
- [📤 Output Directory Structure](#-output-directory-structure)
- [🔍 Features in Detail](#-features-in-detail)
  - [Advanced Scraping Capabilities (Crew4lX64.py)](#advanced-scraping-capabilities-crew4lx64py)
    - [📝 Markdown Generation](#-markdown-generation)
    - [📊 Structured Data Extraction](#-structured-data-extraction)
    - [🌐 Browser Integration](#-browser-integration)
    - [🔎 Media and Content Extraction](#-media-and-content-extraction)
  - [GitHub Repository Handling](#github-repository-handling)
  - [Content Processing Pipeline](#content-processing-pipeline)
  - [Error Handling](#error-handling)
- [🤖 Content Analysis](#-content-analysis-1)
  - [API Version (CrewAPIX64)](#api-version-crewapix64)
  - [Standard Version (CrewNormalX64)](#standard-version-crewnormalx64)
- [🌐 Web Interface Features](#-web-interface-features)
- [⚠️ Important Notes](#️-important-notes)
- [🔄 Future Improvements](#-future-improvements)
- [👥 Contributing](#-contributing)
- [Star History](#star-history)
- [📄 License](#-license)

## Overview

**Crewzombitx64** is a comprehensive web scraping and content analysis tool designed to extract, process, and analyze web content efficiently. It supports both command-line and web-based interfaces, with special handling for GitHub repositories and integration with Mistral AI for advanced content summarization.

**Key Features:**
- Intelligent content extraction with BeautifulSoup4
- Advanced proxy management and rate limiting
- Robust security and compliance features
- Multiple output formats (JSON, Markdown)
- Integration with Mistral AI for content analysis
- User-friendly web interface for easy access and configuration

## 📦 Releases

### Version 1.2.0 (Latest)

- **Enhanced Security and Legal Compliance**:
  - Improved sensitive data detection (API keys, passwords, tokens)
  - Strict URL validation and hostname checking
  - Advanced robots.txt compliance system
  - Protected access to sensitive paths and admin panels
  - Extended internal network protection

- **Advanced Proxy Management**:
  - Intelligent proxy rotation based on performance
  - Proxy health monitoring and scoring
  - Automatic removal of poor performers
  - Response time tracking
  - Proxy anonymity verification

- **Adaptive Rate Limiting**:
  - Domain-specific rate controls
  - Automatic backoff on errors
  - Burst control with configurable limits
  - Response time monitoring
  - Per-domain request tracking

- **Enhanced Configuration System**:
  - Comprehensive security defaults
  - Privacy-focused settings
  - Legal compliance options
  - Random user agent rotation
  - Input validation and sanitization
  - Request limits and error thresholds

### Version 1.1.0

- **Google Colab Integration**:
  - Easy-to-use notebook interface
  - Cloud-based execution support
  - Interactive examples and tutorials

- **Advanced Web Scraping Implementation**:
  - LLM-powered schema generation using OpenAI/Ollama
  - Automatic CSS and XPath schema generation
  - Comprehensive documentation and examples
  - Parallel processing and performance optimizations
  - Enhanced JSON extraction with JSONPath support
  - Complex JSONPath, JSON-CSS, and Microdata extraction
  - SSL certificate handling with custom paths
  - Enhanced security features
  - Async/await support for better concurrency
  - Improved media extraction
  - Document type detection
  - Lazy loading support
  - Responsive image handling

### Version 1.0.0

- **Initial Release**:
  - Core web scraping functionality
  - Mistral AI integration
  - Web interface implementation
  - GitHub repository handling
  - JSON and Markdown export
  - Basic HTML content extraction
  - Markdown formatting
  - File output handling

### Version 0.9.0 (Beta)

- **Beta Release**:
  - Core web scraping features
  - Basic content processing pipeline
  - Command-line interface

### Version 0.5.0 (Alpha)

- **Alpha Release**:
  - Basic HTML parsing
  - File output handling
  - Error handling implementation

## 🚀 Key Features

### 🌐 Web Scraping Capabilities

- **Intelligent Content Extraction**:
  - HTML parsing with BeautifulSoup4
  - Special handling for GitHub repositories
  - Raw markdown file processing
  - Advanced robots.txt compliance system
  - Strict URL validation and hostname checking
  - Protected access controls for sensitive paths

### 🔒 Security and Compliance

- **Data Protection**:
  - Advanced sensitive data detection and redaction
  - Automatic detection of API keys, passwords, and tokens
  - Secure handling of credentials and sensitive information

- **Access Control**:
  - Extended internal network protection
  - Strict URL validation and filtering
  - Protected access to sensitive paths

- **Network Security**:
  - Intelligent proxy rotation with performance scoring
  - Automatic removal of poor-performing proxies
  - Response time monitoring and optimization

- **Legal Compliance**:
  - Advanced robots.txt compliance system
  - Rate limiting with domain-specific controls
  - Privacy-focused configuration defaults

### 📝 Content Processing

- **Smart Content Analysis**:
  - Automatic content structure detection
  - Preservation of header hierarchy
  - List formatting (ordered and unordered)
  - Code block preservation
  - Link extraction and formatting

### 🤖 Content Analysis

- **Multiple Analysis Options**:
  - **API Version (CrewAPIX64)**:
    - Mistral AI-powered summarization
    - Intelligent chunking for large content
    - Adaptive processing based on content size
  - **Standard Version (CrewNormalX64)**:
    - Local text summarization using NLTK
    - Sentence importance scoring
    - Position-based content analysis
    - Keyword-based content evaluation

### 📊 Output Formats

- **Flexible Export Options**:
  - JSON output with metadata
  - Formatted Markdown output
  - Timestamped file organization
  - Structured content hierarchy

## 📁 Project Structure

### Core Components

1. **CrewColabX64.ipynb**:
   - **Description**: This Jupyter Notebook is designed for Google Colab, providing an interactive and cloud-based environment to run Crewzombitx64.
   - **Features**:
     - Google Colab Integration: Seamless execution in the cloud.
     - Interactive Interface: Utilizes Jupyter Notebook for code execution and visualization.
     - Cloud-Based Execution: No local setup required, run directly in your browser.
     - Tutorial and Examples: Includes practical examples and tutorials for new users.
     - Built-in Documentation: Integrated documentation within the notebook for easy access to information.
     - Ideal Use Case: Users who prefer a cloud-based, interactive environment and want to quickly get started with web scraping and content analysis.

2. **CrewNormalX64.py**:
   - **Description**: This Python script represents the standard version of Crewzombitx64, focusing on core web scraping functionalities without requiring an API key.
   - **Features**:
     - Basic Web Scraping: Extracts content from web pages using BeautifulSoup4.
     - HTML Content Extraction: Focuses on parsing and extracting information from HTML.
     - Markdown Formatting: Converts extracted content into Markdown for readability.
     - File Output Handling: Saves scraped data to local files in JSON or Markdown format.
     - No API Key Required: Operates independently without needing external API access.
     - Local Text Summarization: Uses NLTK for basic text summarization.
     - GitHub Repository Handling: Includes specific functionalities for processing GitHub repositories.
     - Ideal Use Case: Users who need a simple, locally runnable web scraper without AI summarization and advanced features.

3. **CrewAPIX64.py**:
   - **Description**: This script enhances the standard version by integrating Mistral AI for advanced content analysis and summarization, requiring an API key.
   - **Features**:
     - Enhanced Scraping: Builds upon the capabilities of CrewNormalX64 with improved scraping logic.
     - Mistral AI Integration: Leverages Mistral AI for advanced content summarization.
     - Intelligent Content Chunking: Automatically breaks down large content for AI processing.
     - Enhanced Summary Quality: Provides more detailed and context-aware summaries using AI.
     - GitHub-Specific Parsing: Improved handling for GitHub repository content.
     - Advanced Error Handling: Robust error management and recovery mechanisms.
     - Ideal Use Case: Users who need AI-powered content summarization and are willing to configure an API key for enhanced analysis.

4. **Crew4lX64.py**:
   - **Description**: The advanced version of Crewzombitx64, offering comprehensive web scraping and content analysis features, including browser integration and advanced data extraction techniques.
   - **Features**:
     - Advanced Markdown Generation: Creates clean, structured Markdown with BM25 filtering.
     - Structured Data Extraction: Employs multiple strategies for extracting structured data.
     - Full Browser Integration: Uses a managed browser for dynamic content rendering and lazy-load handling.
     - Comprehensive Media Extraction: Extracts images, videos, and audio from web pages.
     - Enhanced Security and Proxy Management: Includes robust security features and proxy rotation.
     - Adaptive Rate Limiting: Dynamically adjusts request rates to avoid blocking.
     - Legal Compliance and Privacy Controls: Adheres to robots.txt and offers privacy-focused settings.
     - Advanced Data Protection: Implements measures for sensitive data detection and handling.
     - Ideal Use Case: Users who require advanced scraping capabilities, need to handle dynamic content, extract media, and ensure legal compliance and data protection.

5. **Web Interface**:
   - **Description**: A user-friendly web interface built using Flask, providing easy access to Crewzombitx64's functionalities through a browser.
   - **Features**:
     - User-Friendly Interface: Simple and intuitive design for easy navigation.
     - Real-Time Scraping Feedback: Provides live updates during the scraping process.
     - Content Preview: Allows users to preview extracted content directly in the browser.
     - Direct File Download: Offers options to download output in JSON and Markdown formats.
     - Easy URL Input: Simple form for users to input target URLs and configure scraping options.
     - Ideal Use Case: Users who prefer a graphical interface over command-line tools and need quick access to the tool's features via a web browser.

## Installation

To get started with zombitx64, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/zombitx64.git
   cd zombitx64
   ```

2. **Create a Virtual Environment (Recommended)**:
   It is recommended to create a virtual environment to isolate project dependencies.
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/macOS
   venv\Scripts\activate  # On Windows
   ```
   Ensure you have Python 3.8 or higher installed. You can check your Python version using: `python --version`

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Tool**:
   - Create a `.env` file in the project root and add your configuration settings, such as API keys.

## Running the Tool

The tool provides two versions with different capabilities:

### 1. Standard Version (No API Required)

```bash
python CrewNormalX64.py
```

**Features**:
- Web scraping with BeautifulSoup
- Local text summarization using NLTK
- GitHub repository handling
- JSON and Markdown output
- No API key required

### 2. API Version (Requires Mistral API Key)

```bash
python CrewAPIX64.py
```

**Features**:
- All standard version features
- Advanced AI-powered summarization
- Intelligent content chunking
- Enhanced summary quality
- Requires Mistral API key

### Choosing the Right Version

To help you select the best version of Crewzombitx64 for your needs, here’s a breakdown of each version and its ideal use cases:

- **CrewNormalX64.py (Standard Version)**
  - **Ideal For**: Basic web scraping tasks where AI-powered summarization is not needed. Users who prefer a simple, locally runnable tool without external API dependencies.
  - **Key Features**:
    - Web scraping with BeautifulSoup4.
    - Local text summarization using NLTK.
    - GitHub repository handling.
    - JSON and Markdown output formats.
    - No API key required, fully functional offline.

- **CrewAPIX64.py (API Version)**
  - **Ideal For**: Tasks that require advanced content summarization using AI. Users who need more context-aware and detailed summaries and are comfortable setting up an API key.
  - **Key Features**:
    - Includes all features of the Standard Version.
    - Advanced AI-powered summarization using Mistral AI.
    - Intelligent content chunking for efficient AI processing.
    - Enhanced summary quality and context understanding.

- **Crew4lX64.py (Advanced Version)**
  - **Ideal For**: Complex web scraping projects that require browser interaction, media extraction, and robust handling of dynamic content. Users who need comprehensive scraping capabilities and advanced security features.
  - **Key Features**:
    - Advanced web scraping with browser integration (dynamic content, lazy loading).
    - Markdown and structured data extraction.
    - Comprehensive media and content extraction (images, videos, audio).
    - Enhanced security and proxy management.
    - Adaptive rate limiting for responsible scraping.

- **CrewColabX64.ipynb (Google Colab Version)**
  - **Ideal For**: Users who prefer a cloud-based, interactive environment for web scraping. Great for collaborative projects, tutorials, and running the tool without local installation.
  - **Key Features**:
    - Google Colab integration for cloud-based execution.
    - Interactive Jupyter Notebook interface.
    - Includes tutorials and examples for easy learning.
    - Suitable for users who want to avoid local setup and leverage cloud resources.

### Web Interface

To start the web interface, run:
```bash
python -m zombitx64.app
```

### 3. Advanced Version (Crew4lX64.py)

```bash
python Crew4lX64/main.py --url <target_url> [options]
```

**Features**:
- Advanced web scraping with browser integration
- Markdown and structured data extraction
- Comprehensive media and content extraction
- Enhanced security and proxy management
- Adaptive rate limiting

**Options**:
- `--url <target_url>`:  Specify the URL to crawl. (Required)
- `--depth <integer>`:  Specify the maximum depth for crawling. (Optional, default: 1)
- `--browser`: Enable browser mode for dynamic content rendering. (Optional)
- `--headless`: Run browser in headless mode (no GUI). (Optional, requires `--browser`)
- `--scroll`: Enable auto-scrolling for full page load. (Optional, requires `--browser`)
- `--output-format <format>`:  Specify output format ('json' or 'md'). (Optional, default: 'json')
- `--output-file <filename>`: Specify the output filename. (Optional, default: based on URL and timestamp)
- `--rate-limit <float>`:  Set requests per second rate limit. (Optional, default: 1.0)
- `--wait-time <float>`:  Set wait time between requests in seconds. (Optional, default: 0.5)
- `--proxy <proxy_url>`:  Specify a proxy URL. (Optional)
- `--user-agent <user_agent>`:  Specify a custom user agent. (Optional)
- `--timestamp`:  Include timestamp in output filename. (Optional)
- `--verbose`:  Enable verbose output. (Optional)

**Examples**:

- Crawl a website and save output in Markdown format:
  ```bash
  python Crew4lX64/main.py --url https://example.com --output-format md
  ```

- Crawl a website in browser mode with auto-scrolling and headless option:
  ```bash
  python Crew4lX64/main.py --url https://example.com --browser --headless --scroll
  ```

- Crawl with depth 2 and rate limit of 2 requests per second:
  ```bash
  python Crew4lX64/main.py --url https://example.com --depth 2 --rate-limit 2.0
  ```

- Crawl and save output to a specific file:
  ```bash
  python Crew4lX64/main.py --url https://example.com --output-file my_output.json
  ```

## Publishing to GitHub Packages

For contributors who want to publish new versions:

1. **Update Version**:
   - Update the version number in `setup.py`.

2. **Build the Package**:
   ```bash
   python -m build
   ```

3. **Publish to GitHub Packages**:
   ```bash
   python -m twine upload --repository github dist/*
   ```

**Note**: You need appropriate permissions and a PAT with `write:packages` scope to publish.

![Example](./public/imageReame.png)

## 📤 Output Directory Structure

```
scraped_output/
├── scraped_[timestamp].json  # JSON format output
└── scraped_[timestamp].md    # Markdown format output
```

## 🔍 Features in Detail

### Advanced Scraping Capabilities (Crew4lX64.py)

#### 📝 Markdown Generation

- Clean, structured Markdown with accurate formatting
- BM25-based content filtering for relevance
- Intelligent citation and reference management
- Multiple generation strategies
- Customizable content filtering

#### 📊 Structured Data Extraction

- Topic-based chunking strategies
- Cosine similarity for content relevance
- Schema-based data extraction using CSS selectors
- Flexible data extraction patterns

#### 🌐 Browser Integration

- Managed browser with anti-detection features
- Remote browser control capabilities
- Session management for complex workflows
- Proxy support with authentication
- Dynamic viewport adjustment
- Multi-browser compatibility

#### 🔎 Media and Content Extraction

- Comprehensive media support (images, video, audio)
- Responsive image format handling
- Lazy-load content detection
- Full-page content scanning
- Metadata extraction
- IFrame content processing
- Caching system for improved performance

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

## 🤖 Content Analysis

The tool offers two approaches for content analysis:

### API Version (CrewAPIX64)

- Uses Mistral AI for advanced summarization
- Automatic content chunking for large texts
- Progressive summarization for multi-chunk content
- Detailed progress tracking
- Error recovery mechanisms
- Requires API key configuration

### Standard Version (CrewNormalX64)

- Uses NLTK for local text summarization
- Sentence scoring based on position and length
- Keyword-based importance analysis
- No external API dependencies
- Works offline
- No API key required

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

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=JonusNattapong/Crewzombitx64&type=Date)](https://star-history.com/#JonusNattapong/Crewzombitx64&Date)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
