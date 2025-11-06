"""
Extract - Information extraction with LLM

A Python package for extracting structured information from text using Large Language Models.
"""

__version__ = "0.1.0"

from .extractor import InformationExtractor, ExtractionResult

__all__ = ["InformationExtractor", "ExtractionResult"]
