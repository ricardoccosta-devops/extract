# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-06

### Added
- Initial implementation of LLM-based information extraction system
- `InformationExtractor` class with OpenAI integration
- Two extraction methods: `extract()` for simple field-based extraction and `extract_with_schema()` for schema-based extraction
- `ExtractionResult` model for structured results
- Support for environment variable and .env file configuration
- Comprehensive test suite with 14 unit tests
- Example usage script demonstrating different use cases
- Complete documentation in README.md
- Quick start guide
- Setup.py for package installation

### Features
- Extract structured data from unstructured text
- Support for custom instructions
- Multilingual text support
- Robust JSON parsing with markdown handling
- Type hints and Pydantic models for validation
- Error handling and reporting

[0.1.0]: https://github.com/ricardoccosta-devops/extract/releases/tag/v0.1.0
