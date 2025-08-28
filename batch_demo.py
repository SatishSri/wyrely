#!/usr/bin/env python3
"""
Batch processing demo for Document AI Table Extractor
Processes all images in the inputs folder.
"""

import os
import sys
from dotenv import load_dotenv
from src.extractor import TableExtractor

# Load environment variables
load_dotenv()


def batch_demo():
    """
    Demonstrate batch processing functionality.
    """
    
    print("🎯 BATCH DEMO: Document AI Table Extraction")
    print("=" * 60)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please create a .env file with your Google Cloud configuration")
        return 1
    
    # Check required environment variables
    project_id = os.getenv('PROJECT_ID')
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if not project_id:
        print("❌ PROJECT_ID not set in .env file")
        return 1
    
    if not creds_path or not os.path.exists(creds_path):
        print(f"❌ Credentials file not found: {creds_path}")
        return 1
    
    print(f"✅ Configuration loaded from .env file")
    print(f"   Project ID: {project_id}")
    print(f"   Location: {os.getenv('LOCATION', 'us')}")
    
    input_folder = "inputs"
    output_folder = "outputs"
    
    # Check if inputs folder exists and has images
    if not os.path.exists(input_folder):
        print(f"❌ Input folder '{input_folder}' not found!")
        return 1
    
    # Count images in input folder
    supported_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.pdf'}
    image_files = [f for f in os.listdir(input_folder) 
                   if os.path.splitext(f)[1].lower() in supported_extensions]
    
    if not image_files:
        print(f"❌ No supported image files found in '{input_folder}' folder!")
        print("Supported formats: PNG, JPG, JPEG, GIF, BMP, TIFF, PDF")
        return 1
    
    print(f"\n📁 Found {len(image_files)} image(s) in '{input_folder}' folder:")
    for img in image_files:
        print(f"   • {img}")
    
    try:
        # Initialize extractor
        print(f"\n🚀 Initializing Document AI client...")
        extractor = TableExtractor()
        print(f"✅ Using processor: {extractor.processor_id}")
        
        # Process all images in batch
        print(f"\n📸 Processing all images...")
        batch_result = extractor.process_folder(input_folder, output_folder)
        
        if batch_result['success']:
            print(f"\n📊 Batch Processing Summary:")
            print(f"   Successfully processed: {batch_result['processed']}/{batch_result['total']} files")
            print(f"   Output folder: {output_folder}/")
            
            # Show detailed results
            print(f"\n📋 Detailed Results:")
            for result in batch_result['results']:
                if result['success']:
                    print(f"   ✅ {result['input_file']}")
                    print(f"      → Output: {result['output_file']}")
                    print(f"      → Tables found: {result['tables_found']}")
                    print(f"      → Pages: {result['pages']}")
                else:
                    print(f"   ❌ {result['input_file']}")
                    print(f"      → Error: {result['error']}")
                print()
            
            print(f"🎉 Batch processing completed successfully!")
            print(f"Check the '{output_folder}/' folder for all extracted text files.")
            return 0
            
        else:
            print(f"❌ Batch processing failed: {batch_result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        return 1


def main():
    """Main function."""
    
    print("Document AI Table Extractor - Batch Processing Demo")
    print("This demo processes ALL images in the inputs/ folder")
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Usage: python3 batch_demo.py")
        print()
        print("This script will:")
        print("1. Find all supported images in inputs/ folder")
        print("2. Process each image with Document AI")
        print("3. Save extracted data to outputs/ folder")
        print()
        print("Supported formats: PNG, JPG, JPEG, GIF, BMP, TIFF, PDF")
        return 0
    
    return batch_demo()


if __name__ == "__main__":
    sys.exit(main())
