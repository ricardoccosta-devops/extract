"""
Tests for the information extractor.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from extract import InformationExtractor, ExtractionResult


class TestExtractionResult:
    """Tests for ExtractionResult model."""
    
    def test_successful_result(self):
        """Test creation of successful result."""
        result = ExtractionResult(
            success=True,
            data={"name": "John Doe", "age": "30"}
        )
        assert result.success is True
        assert result.data == {"name": "John Doe", "age": "30"}
        assert result.error is None
    
    def test_failed_result(self):
        """Test creation of failed result."""
        result = ExtractionResult(
            success=False,
            error="Test error"
        )
        assert result.success is False
        assert result.error == "Test error"
        assert result.data == {}


class TestInformationExtractor:
    """Tests for InformationExtractor."""
    
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        extractor = InformationExtractor(api_key="test-key")
        assert extractor.api_key == "test-key"
        assert extractor.model == "gpt-3.5-turbo"
    
    def test_init_with_custom_model(self):
        """Test initialization with custom model."""
        extractor = InformationExtractor(api_key="test-key", model="gpt-4")
        assert extractor.model == "gpt-4"
    
    def test_init_without_api_key_raises_error(self):
        """Test that initialization without API key raises ValueError."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key is required"):
                InformationExtractor()
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'env-test-key'})
    def test_init_from_environment(self):
        """Test initialization from environment variable."""
        extractor = InformationExtractor()
        assert extractor.api_key == "env-test-key"
    
    def test_build_prompt(self):
        """Test prompt building."""
        extractor = InformationExtractor(api_key="test-key")
        
        prompt = extractor._build_prompt(
            text="Test text",
            fields=["field1", "field2"],
            instructions=None
        )
        
        assert "field1, field2" in prompt
        assert "Test text" in prompt
        assert "JSON" in prompt
    
    def test_build_prompt_with_instructions(self):
        """Test prompt building with instructions."""
        extractor = InformationExtractor(api_key="test-key")
        
        prompt = extractor._build_prompt(
            text="Test text",
            fields=["field1"],
            instructions="Special instructions"
        )
        
        assert "Special instructions" in prompt
    
    def test_build_schema_prompt(self):
        """Test schema prompt building."""
        extractor = InformationExtractor(api_key="test-key")
        
        schema = {
            "name": "Person's name",
            "age": "Person's age"
        }
        
        prompt = extractor._build_schema_prompt(
            text="Test text",
            schema=schema,
            instructions=None
        )
        
        assert "name: Person's name" in prompt
        assert "age: Person's age" in prompt
        assert "Test text" in prompt
    
    @patch('extract.extractor.OpenAI')
    def test_extract_success(self, mock_openai):
        """Test successful extraction."""
        # Mock the OpenAI client response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"name": "John Doe", "age": "30"}'
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        extractor = InformationExtractor(api_key="test-key")
        result = extractor.extract(
            text="John Doe is 30 years old",
            fields=["name", "age"]
        )
        
        assert result.success is True
        assert result.data == {"name": "John Doe", "age": "30"}
        assert result.error is None
    
    @patch('extract.extractor.OpenAI')
    def test_extract_with_markdown_json(self, mock_openai):
        """Test extraction when response has JSON wrapped in markdown."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '```json\n{"name": "Jane Smith"}\n```'
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        extractor = InformationExtractor(api_key="test-key")
        result = extractor.extract(
            text="Jane Smith",
            fields=["name"]
        )
        
        assert result.success is True
        assert result.data == {"name": "Jane Smith"}
    
    @patch('extract.extractor.OpenAI')
    def test_extract_invalid_json(self, mock_openai):
        """Test extraction with invalid JSON response."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = 'This is not JSON'
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        extractor = InformationExtractor(api_key="test-key")
        result = extractor.extract(
            text="Test",
            fields=["field"]
        )
        
        assert result.success is False
        assert "Failed to parse JSON" in result.error
    
    @patch('extract.extractor.OpenAI')
    def test_extract_api_error(self, mock_openai):
        """Test extraction when API raises an error."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        extractor = InformationExtractor(api_key="test-key")
        result = extractor.extract(
            text="Test",
            fields=["field"]
        )
        
        assert result.success is False
        assert "API Error" in result.error
    
    @patch('extract.extractor.OpenAI')
    def test_extract_with_schema_success(self, mock_openai):
        """Test successful extraction with schema."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"name": "John", "occupation": "Engineer"}'
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        extractor = InformationExtractor(api_key="test-key")
        schema = {
            "name": "Person's name",
            "occupation": "Person's job"
        }
        
        result = extractor.extract_with_schema(
            text="John is an engineer",
            schema=schema
        )
        
        assert result.success is True
        assert result.data == {"name": "John", "occupation": "Engineer"}
