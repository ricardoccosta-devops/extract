# Extract

**Extração de informações com LLM** (Information extraction with LLM)

A Python package for extracting structured information from unstructured text using Large Language Models (LLM).

## Features

- 🤖 Extract structured data from unstructured text using LLM
- 📋 Simple field-based extraction
- 🔧 Schema-based extraction with field descriptions
- 🌐 Support for multiple languages
- ⚡ Easy to use API
- 🔒 Secure API key management with environment variables

## Installation

```bash
pip install -r requirements.txt
```

For development:

```bash
pip install -e .
```

## Configuration

The package requires an OpenAI API key to function. You can provide it in two ways:

### Option 1: Environment Variable

```bash
export OPENAI_API_KEY='your-api-key-here'
```

### Option 2: .env File

Create a `.env` file in your project root:

```
OPENAI_API_KEY=your-api-key-here
```

You can use `.env.example` as a template.

## Usage

### Basic Field Extraction

Extract specific fields from text:

```python
from extract import InformationExtractor

# Initialize the extractor
extractor = InformationExtractor()

# Example text
text = """
Dr. Maria Silva is a 35-year-old software engineer working at Tech Corp.
She lives in São Paulo, Brazil.
"""

# Extract fields
result = extractor.extract(
    text=text,
    fields=["name", "age", "occupation", "city"]
)

if result.success:
    print(result.data)
    # Output: {'name': 'Dr. Maria Silva', 'age': '35', 'occupation': 'software engineer', 'city': 'São Paulo'}
```

### Schema-Based Extraction

Use a schema to provide detailed descriptions for each field:

```python
from extract import InformationExtractor

extractor = InformationExtractor()

text = """
The UltraPhone X Pro is a premium smartphone released in 2024.
It features a 6.7-inch OLED display and is priced at $999.
"""

# Define schema
schema = {
    "product_name": "Name of the product",
    "category": "Product category",
    "price": "Price in USD",
    "specs": "Technical specifications"
}

result = extractor.extract_with_schema(
    text=text,
    schema=schema
)

if result.success:
    print(result.data)
```

### Custom Instructions

Provide additional instructions for extraction:

```python
result = extractor.extract(
    text="O evento acontecerá dia 15 de março em Lisboa",
    fields=["event_date", "location"],
    instructions="Text is in Portuguese. Convert dates to ISO format."
)
```

### Custom Model

Use a different OpenAI model:

```python
extractor = InformationExtractor(model="gpt-4")
```

## Examples

Run the examples file to see the package in action:

```bash
python examples.py
```

The examples demonstrate:
1. Simple field extraction
2. Schema-based extraction with nested objects
3. Extraction with custom instructions for multilingual text

## Testing

Run the test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=extract tests/
```

## API Reference

### `InformationExtractor`

Main class for information extraction.

#### Constructor

```python
InformationExtractor(api_key: Optional[str] = None, model: str = "gpt-3.5-turbo")
```

- `api_key`: OpenAI API key (optional if set in environment)
- `model`: OpenAI model to use (default: "gpt-3.5-turbo")

#### Methods

##### `extract(text, fields, instructions=None)`

Extract specified fields from text.

**Parameters:**
- `text` (str): Text to extract information from
- `fields` (List[str]): List of field names to extract
- `instructions` (Optional[str]): Additional instructions

**Returns:** `ExtractionResult`

##### `extract_with_schema(text, schema, instructions=None)`

Extract information using a schema with field descriptions.

**Parameters:**
- `text` (str): Text to extract information from
- `schema` (Dict[str, str]): Field names mapped to descriptions
- `instructions` (Optional[str]): Additional instructions

**Returns:** `ExtractionResult`

### `ExtractionResult`

Result object from extraction operations.

**Attributes:**
- `success` (bool): Whether extraction was successful
- `data` (Dict[str, Any]): Extracted data as a dictionary
- `error` (Optional[str]): Error message if failed
- `raw_response` (Optional[str]): Raw LLM response

## Use Cases

- **Contact Information Extraction**: Extract names, emails, phone numbers from documents
- **Product Information**: Parse product specifications from descriptions
- **Event Details**: Extract dates, locations, and details from event announcements
- **Resume Parsing**: Extract skills, experience, education from resumes
- **Invoice Processing**: Extract amounts, dates, vendor information
- **Article Summarization**: Extract key facts and entities from articles

## Requirements

- Python >= 3.8
- openai >= 1.0.0
- python-dotenv >= 1.0.0
- pydantic >= 2.0.0

## License

This project is open source.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

