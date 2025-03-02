# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2025-03-03

### Added
- Dark mode versions for all main scripts:
  - `CrewAPIDarkX64.py`: API version with enhanced dark mode interface
  - `CrewNormalDarkX64.py`: Local version with dark mode support
  - `CrewColabDarkX64.ipynb`: Google Colab version with dark mode
- Enhanced warnings and disclaimers in both English and Thai
- Improved visual feedback with emojis and progress indicators

## [1.2.3] - 2025-03-03

### Added
- Enhanced legal compliance features
  - Added can_scrape() method in security_manager.py
  - Implemented robots.txt checking with detailed error handling
  - Added Terms of Service warning system
  - Added PDF permission warnings
  - Added GDPR compliance warnings
  - Added copyright protection warnings
  - Enhanced personal data detection
  - Added content scanning for copyrighted material
  - Implemented one-time warning system to avoid duplicates

### Changed
- Updated security_manager.py with improved robots.txt handling
- Enhanced content_extractor.py with PDF detection
- Improved data_exporter.py with GDPR and copyright checks

## [1.2.2] - 2025-03-01

### Added
- Enhanced GitHub repository integration
  - Intelligent path type detection (root/tree/blob)
  - Repository metadata extraction (languages, stars, forks, topics)
  - Improved README parsing with markdown structure preservation
  - Directory tree visualization with file/folder icons
  - File content extraction with proper formatting
  - Repository description and metadata handling
  - GitHub-specific selectors and path patterns
  - Smart repository navigation system

### Changed
- Improved content extraction in content_extractor.py
  - Added GitHub-specific selectors and content handlers
  - Enhanced markdown structure preservation
  - Better metadata organization
- Enhanced web crawler in web_crawler.py
  - Added GitHub path pattern recognition
  - Smarter link filtering for repositories
  - Improved navigation handling
- Updated CrewAPIX64.py
  - Added specialized GitHub content handlers
  - Improved error recovery and fallbacks
  - Better content organization in output

## [1.2.1] - 2025-03-01

### Fixed
- Resolved issues with browser mode in web crawler
  - Fixed "await expression" errors
  - Improved browser setup and navigation
  - Correctly handled async/sync operations
  - Enhanced error handling and resource cleanup

## [1.2.0] - 2025-02-28

### Added
- Enhanced security and legal compliance features
  - Improved sensitive data detection (API keys, passwords, tokens)
  - Strict URL validation and hostname checking
  - Advanced robots.txt compliance system
  - Protected access to sensitive paths and admin panels
  - Extended internal network protection
- Advanced proxy management
  - Intelligent proxy rotation based on performance
  - Proxy health monitoring and scoring
  - Automatic removal of poor performers
  - Response time tracking
  - Proxy anonymity verification
- Adaptive rate limiting
  - Domain-specific rate controls
  - Automatic backoff on errors
  - Burst control with configurable limits
  - Response time monitoring
  - Per-domain request tracking
- Enhanced configuration system
  - Comprehensive security defaults
  - Privacy-focused settings
  - Legal compliance options
  - Random user agent rotation
  - Input validation and sanitization
  - Request limits and error thresholds

### Changed
- Updated default configuration for better security
- Improved proxy handling system
- Enhanced rate limiting algorithm
- Strengthened data protection measures

## [1.1.0] - 2025-02-28

### Added
- CrewColabX64.ipynb: Google Colab integration
  - Easy-to-use notebook interface
  - Cloud-based execution support
  - Interactive examples and tutorials
- Crew4lX64.py: Advanced web scraping implementation
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

### Changed
- Improved error handling and logging
- Enhanced browser integration
- Better proxy support with authentication
- Optimized caching system

## [1.0.0] - 2025-02-28

### Added
- Initial release with core functionality
- Web scraping capabilities
- Mistral AI integration (CrewAPIX64.py)
- Web interface implementation
- GitHub repository handling
- JSON and Markdown export
- Basic web scraping functionality (CrewNormalX64.py)
- HTML content extraction
- Markdown formatting
- File output handling

## [0.9.0] - Beta

### Added
- Beta release with core features
- Basic web scraping
- Content processing pipeline
- Command-line interface

## [0.5.0] - Alpha

### Added
- Alpha release for testing
- Basic HTML parsing
- File output handling
- Error handling implementation

## [0.1.0] - Initial Commit

### Added
- Project scaffolding
- Basic file structure
- Initial documentation
