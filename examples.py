"""
Example usage of the information extraction package.
"""

from extract import InformationExtractor


def example_simple_extraction():
    """Example of simple field extraction."""
    print("=" * 60)
    print("Example 1: Simple Field Extraction")
    print("=" * 60)
    
    # Initialize the extractor
    # Note: Make sure OPENAI_API_KEY is set in your environment or .env file
    extractor = InformationExtractor()
    
    # Example text
    text = """
    Dr. Maria Silva is a 35-year-old software engineer working at Tech Corp.
    She lives in São Paulo, Brazil, and has been with the company for 5 years.
    Her email is maria.silva@techcorp.com and phone number is +55 11 98765-4321.
    """
    
    # Extract specific fields
    result = extractor.extract(
        text=text,
        fields=["name", "age", "occupation", "company", "city", "email", "phone"]
    )
    
    if result.success:
        print("\n✓ Extraction successful!")
        print("\nExtracted data:")
        for field, value in result.data.items():
            print(f"  {field}: {value}")
    else:
        print(f"\n✗ Extraction failed: {result.error}")
    
    print()


def example_schema_extraction():
    """Example of extraction with schema."""
    print("=" * 60)
    print("Example 2: Extraction with Schema")
    print("=" * 60)
    
    extractor = InformationExtractor()
    
    # Example text about a product
    text = """
    The UltraPhone X Pro is a premium smartphone released in 2024.
    It features a 6.7-inch OLED display, 12GB RAM, and 256GB storage.
    The device is priced at $999 and available in Black, Silver, and Gold colors.
    Battery capacity is 5000mAh with fast charging support.
    """
    
    # Define a schema with field descriptions
    schema = {
        "product_name": "Name of the product",
        "category": "Product category (e.g., smartphone, laptop)",
        "release_year": "Year of release",
        "price": "Price in USD",
        "colors": "Available colors as a list",
        "specs": "Technical specifications as a nested object"
    }
    
    # Extract with schema
    result = extractor.extract_with_schema(
        text=text,
        schema=schema,
        instructions="For specs, include display, ram, storage, and battery as separate fields"
    )
    
    if result.success:
        print("\n✓ Extraction successful!")
        print("\nExtracted data:")
        import json
        print(json.dumps(result.data, indent=2))
    else:
        print(f"\n✗ Extraction failed: {result.error}")
    
    print()


def example_custom_instructions():
    """Example with custom instructions."""
    print("=" * 60)
    print("Example 3: Extraction with Custom Instructions")
    print("=" * 60)
    
    extractor = InformationExtractor()
    
    # Example text in Portuguese
    text = """
    O evento Tech Summit 2024 acontecerá nos dias 15 e 16 de março
    no Centro de Convenções de Lisboa. As inscrições custam €250
    para participantes individuais e €200 para grupos de 5 ou mais pessoas.
    """
    
    # Extract event information
    result = extractor.extract(
        text=text,
        fields=["event_name", "dates", "location", "price_individual", "price_group"],
        instructions="Text is in Portuguese. Convert prices to numeric values without currency symbols."
    )
    
    if result.success:
        print("\n✓ Extraction successful!")
        print("\nExtracted data:")
        for field, value in result.data.items():
            print(f"  {field}: {value}")
    else:
        print(f"\n✗ Extraction failed: {result.error}")
    
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Information Extraction with LLM - Examples")
    print("=" * 60 + "\n")
    
    print("Note: These examples require a valid OpenAI API key.")
    print("Set the OPENAI_API_KEY environment variable or create a .env file.\n")
    
    try:
        example_simple_extraction()
        example_schema_extraction()
        example_custom_instructions()
        
        print("=" * 60)
        print("All examples completed!")
        print("=" * 60)
        
    except ValueError as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print("or create a .env file with:")
        print("  OPENAI_API_KEY=your-api-key-here")
