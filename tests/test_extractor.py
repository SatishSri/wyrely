#!/usr/bin/env python3
"""
Test script for Document AI Table Extractor
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path so we can import src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.extractor import TableExtractor

load_dotenv()


def test_extractor():
    """Test the Document AI functionality with a sample image."""
    
    print("🧪 Testing Document AI Table Extractor")
    print("=" * 50)
    
    # Check environment variables
    project_id = os.getenv('PROJECT_ID')
    if not project_id:
        print("❌ Error: PROJECT_ID not set in environment variables")
        print("Please set your Google Cloud project ID in the .env file")
        return False
    
    location = os.getenv('LOCATION', 'us')
    print(f"📍 Using location: {location}")
    print(f"🔑 Project ID: {project_id}")
    
    # Check if we have a test image
    test_image_path = "../inputs/test_image.png"
    if not os.path.exists(test_image_path):
        print(f"⚠️  Test image not found: {test_image_path}")
        print("Please place a test image in the inputs/ directory")
        return False
    
    try:
        # Initialize extractor
        print("\n🚀 Initializing Document AI client...")
        extractor = TableExtractor()
        print("✅ Client initialized successfully")
        
        # Process the test image
        print(f"\n📸 Processing test image: {test_image_path}")
        result = extractor.extract_tables(test_image_path)
        
        if not result['success']:
            print(f"❌ Error processing image: {result.get('error', 'Unknown error')}")
            return False
        
        # Display results
        print("\n📊 Processing Results:")
        print(f"   Pages: {result['pages']}")
        print(f"   Tables found: {len(result['tables'])}")
        
        if result['tables']:
            total_rows = sum(table.get('row_count', 0) for table in result['tables'])
            print(f"   Total rows: {total_rows}")
        
        # Export results
        print("\n💾 Exporting results...")
        output_path = "test_output.txt"
        
        if extractor.save_to_text(result, output_path):
            print(f"✅ Text file exported: {output_path}")
        else:
            print("❌ Failed to export text file")
            return False
        
        print("\n🎉 Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    print("Document AI Table Extractor - Test Script")
    print("This script tests the basic functionality of the extractor.")
    print()
    
    success = test_extractor()
    
    if success:
        print("\n✅ All tests passed! Your setup is working correctly.")
        print("\nNext steps:")
        print("1. Run the demo: python3 demo.py")
        print("2. Use the extractor: python3 src/extractor.py")
        print("3. Check the output files for extracted data")
    else:
        print("\n❌ Tests failed. Please check your configuration and try again.")
        print("\nCommon issues:")
        print("1. Missing or incorrect PROJECT_ID in .env file")
        print("2. Google Cloud credentials not properly set up")
        print("3. Document AI API not enabled")
        print("4. Insufficient permissions on the service account")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
