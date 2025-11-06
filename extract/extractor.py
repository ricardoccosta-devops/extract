"""
Information extraction module using LLM.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv


class ExtractionResult(BaseModel):
    """Result of an information extraction operation."""
    
    success: bool = Field(description="Whether the extraction was successful")
    data: Dict[str, Any] = Field(default_factory=dict, description="Extracted data")
    error: Optional[str] = Field(default=None, description="Error message if extraction failed")
    raw_response: Optional[str] = Field(default=None, description="Raw LLM response")


class InformationExtractor:
    """
    Information extractor using LLM for structured data extraction from text.
    
    This class provides methods to extract structured information from unstructured
    text using Large Language Models.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the InformationExtractor.
        
        Args:
            api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY in environment.
            model: The OpenAI model to use for extraction. Default is 'gpt-3.5-turbo'.
        """
        load_dotenv()
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
    
    def _parse_json_response(self, raw_response: str) -> Dict[str, Any]:
        """
        Parse JSON from LLM response, handling markdown-wrapped JSON.
        
        Args:
            raw_response: The raw response string from the LLM.
        
        Returns:
            Parsed JSON as a dictionary.
        
        Raises:
            json.JSONDecodeError: If JSON cannot be parsed.
        """
        try:
            return json.loads(raw_response)
        except json.JSONDecodeError:
            # Try to extract JSON from the response if it's wrapped in markdown
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            raise
    
    def extract(
        self,
        text: str,
        fields: List[str],
        instructions: Optional[str] = None
    ) -> ExtractionResult:
        """
        Extract specified fields from the given text.
        
        Args:
            text: The text to extract information from.
            fields: List of field names to extract.
            instructions: Optional additional instructions for the extraction.
        
        Returns:
            ExtractionResult containing the extracted data or error information.
        
        Example:
            >>> extractor = InformationExtractor()
            >>> result = extractor.extract(
            ...     "John Doe is 30 years old and lives in New York.",
            ...     fields=["name", "age", "city"]
            ... )
            >>> print(result.data)
            {'name': 'John Doe', 'age': '30', 'city': 'New York'}
        """
        try:
            # Build the extraction prompt
            prompt = self._build_prompt(text, fields, instructions)
            
            # Call the LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that extracts structured information from text. "
                                   "Respond only with JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            raw_response = response.choices[0].message.content
            
            # Parse the response
            try:
                data = self._parse_json_response(raw_response)
            except json.JSONDecodeError:
                return ExtractionResult(
                    success=False,
                    error="Failed to parse JSON from LLM response",
                    raw_response=raw_response
                )
            
            return ExtractionResult(
                success=True,
                data=data,
                raw_response=raw_response
            )
            
        except Exception as e:
            return ExtractionResult(
                success=False,
                error=str(e)
            )
    
    def _build_prompt(
        self,
        text: str,
        fields: List[str],
        instructions: Optional[str] = None
    ) -> str:
        """
        Build the extraction prompt for the LLM.
        
        Args:
            text: The text to extract information from.
            fields: List of field names to extract.
            instructions: Optional additional instructions.
        
        Returns:
            The formatted prompt string.
        """
        prompt_parts = [
            "Extract the following information from the text below:",
            "",
            f"Fields to extract: {', '.join(fields)}",
            ""
        ]
        
        if instructions:
            prompt_parts.extend([
                f"Additional instructions: {instructions}",
                ""
            ])
        
        prompt_parts.extend([
            "Text:",
            text,
            "",
            "Provide the extracted information as a JSON object with the specified fields as keys. "
            "If a field cannot be found, use null as the value. "
            "Return only the JSON object, nothing else."
        ])
        
        return "\n".join(prompt_parts)
    
    def extract_with_schema(
        self,
        text: str,
        schema: Dict[str, str],
        instructions: Optional[str] = None
    ) -> ExtractionResult:
        """
        Extract information based on a schema with field descriptions.
        
        Args:
            text: The text to extract information from.
            schema: Dictionary mapping field names to their descriptions.
            instructions: Optional additional instructions for the extraction.
        
        Returns:
            ExtractionResult containing the extracted data or error information.
        
        Example:
            >>> extractor = InformationExtractor()
            >>> schema = {
            ...     "name": "Full name of the person",
            ...     "age": "Age in years",
            ...     "occupation": "Job or profession"
            ... }
            >>> result = extractor.extract_with_schema(
            ...     "Dr. Jane Smith, 45, is a renowned scientist.",
            ...     schema=schema
            ... )
        """
        try:
            # Build the extraction prompt with schema
            prompt = self._build_schema_prompt(text, schema, instructions)
            
            # Call the LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that extracts structured information from text. "
                                   "Respond only with JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            raw_response = response.choices[0].message.content
            
            # Parse the response
            try:
                data = self._parse_json_response(raw_response)
            except json.JSONDecodeError:
                return ExtractionResult(
                    success=False,
                    error="Failed to parse JSON from LLM response",
                    raw_response=raw_response
                )
            
            return ExtractionResult(
                success=True,
                data=data,
                raw_response=raw_response
            )
            
        except Exception as e:
            return ExtractionResult(
                success=False,
                error=str(e)
            )
    
    def _build_schema_prompt(
        self,
        text: str,
        schema: Dict[str, str],
        instructions: Optional[str] = None
    ) -> str:
        """
        Build the extraction prompt with schema for the LLM.
        
        Args:
            text: The text to extract information from.
            schema: Dictionary mapping field names to descriptions.
            instructions: Optional additional instructions.
        
        Returns:
            The formatted prompt string.
        """
        prompt_parts = [
            "Extract the following information from the text below:",
            "",
            "Fields to extract:"
        ]
        
        for field, description in schema.items():
            prompt_parts.append(f"- {field}: {description}")
        
        prompt_parts.append("")
        
        if instructions:
            prompt_parts.extend([
                f"Additional instructions: {instructions}",
                ""
            ])
        
        prompt_parts.extend([
            "Text:",
            text,
            "",
            "Provide the extracted information as a JSON object with the specified fields as keys. "
            "If a field cannot be found, use null as the value. "
            "Return only the JSON object, nothing else."
        ])
        
        return "\n".join(prompt_parts)
