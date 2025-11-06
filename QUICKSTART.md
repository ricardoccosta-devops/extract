# Quick Start Guide

## Installation

```bash
pip install -r requirements.txt
```

## Basic Setup

1. Get an OpenAI API key from https://platform.openai.com/api-keys

2. Set the environment variable:
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

   Or create a `.env` file:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## Simple Example

```python
from extract import InformationExtractor

# Initialize
extractor = InformationExtractor()

# Extract information
text = "John Doe, age 30, lives in New York and works as an engineer."
result = extractor.extract(
    text=text,
    fields=["name", "age", "city", "occupation"]
)

# Check results
if result.success:
    print(result.data)
    # Output: {'name': 'John Doe', 'age': '30', 'city': 'New York', 'occupation': 'engineer'}
else:
    print(f"Error: {result.error}")
```

## More Examples

See `examples.py` for comprehensive examples including:
- Simple field extraction
- Schema-based extraction
- Custom instructions
- Multilingual support

Run the examples:
```bash
python examples.py
```

## Running Tests

```bash
pytest
```

## Common Use Cases

### Extract Contact Information
```python
text = "Contact Sarah Johnson at sarah.j@example.com or call (555) 123-4567"
result = extractor.extract(text, fields=["name", "email", "phone"])
```

### Extract Product Details
```python
schema = {
    "name": "Product name",
    "price": "Price as a number",
    "features": "List of key features"
}
result = extractor.extract_with_schema(text, schema=schema)
```

### Extract Event Information
```python
text = "Tech Conference 2024 - March 15-16 at Convention Center, tickets $299"
result = extractor.extract(
    text,
    fields=["event_name", "dates", "location", "price"]
)
```

## API Reference

### InformationExtractor

**Constructor:**
- `api_key` (optional): Your OpenAI API key
- `model` (optional): Model to use (default: "gpt-3.5-turbo")

**Methods:**
- `extract(text, fields, instructions=None)` - Extract specified fields
- `extract_with_schema(text, schema, instructions=None)` - Extract with field descriptions

### ExtractionResult

**Attributes:**
- `success` (bool): Whether extraction succeeded
- `data` (dict): Extracted information
- `error` (str): Error message if failed
- `raw_response` (str): Raw LLM response

## Tips

1. **Be specific with field names**: Use descriptive names like "customer_email" instead of just "email"

2. **Use custom instructions**: Add context to improve accuracy
   ```python
   result = extractor.extract(
       text,
       fields=["date"],
       instructions="Convert dates to YYYY-MM-DD format"
   )
   ```

3. **Use schema for complex extractions**: Provide descriptions to guide the LLM
   ```python
   schema = {
       "price": "Numeric price without currency symbol",
       "currency": "Three-letter currency code (USD, EUR, etc.)"
   }
   ```

4. **Handle errors gracefully**: Always check `result.success` before using the data

5. **Choose the right model**: Use GPT-4 for better accuracy (costs more)
   ```python
   extractor = InformationExtractor(model="gpt-4")
   ```

## Troubleshooting

**Error: "OpenAI API key is required"**
- Make sure you've set the OPENAI_API_KEY environment variable or created a .env file

**Poor extraction quality**
- Try using GPT-4 instead of GPT-3.5-turbo
- Add more specific instructions
- Use schema with detailed field descriptions

**Rate limit errors**
- Add delays between requests
- Check your OpenAI API usage limits

## Support

For issues and questions, please refer to the main README.md file.
