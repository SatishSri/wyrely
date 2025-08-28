#!/usr/bin/env python3
"""
Document AI Table Extractor - Core Module
Simple and focused implementation for extracting tabular data from images.
"""

import os
import sys
from google.cloud import documentai_v1 as documentai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TableExtractor:
    """Simple table extractor using Google Document AI."""
    
    def __init__(self, project_id=None, location=None):
        """
        Initialize the extractor.
        
        Args:
            project_id: Google Cloud project ID (from .env if not provided)
            location: Document AI processor location (from .env if not provided)
        """
        self.project_id = project_id or os.getenv('PROJECT_ID')
        self.location = location or os.getenv('LOCATION', 'us')
        
        if not self.project_id:
            raise ValueError("Project ID must be set in .env file or provided as parameter")
        
        self.client = documentai.DocumentProcessorServiceClient()
        self.parent = f"projects/{self.project_id}/locations/{self.location}"
        
        # Find a suitable processor
        self.processor_id = self._find_processor()
        if not self.processor_id:
            raise Exception("No suitable Document AI processor found")
    
    def _find_processor(self):
        """Find a Document AI processor that can handle documents."""
        try:
            request = documentai.ListProcessorsRequest(parent=self.parent)
            page_result = self.client.list_processors(request=request)
            
            for processor in page_result:
                # Look for document processors
                if processor.type_ in ['DOCUMENT_OCR_PROCESSOR', 'FORM_PARSER_PROCESSOR']:
                    return processor.name.split('/')[-1]
            
            return None
        except Exception as e:
            print(f"Warning: Could not list processors: {e}")
            return None
    
    def extract_tables(self, image_path):
        """
        Extract tables from an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with extracted data
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Read the image
        with open(image_path, "rb") as image:
            image_content = image.read()
        
        # Create raw document for processing
        raw_document = documentai.RawDocument(
            content=image_content,
            mime_type=self._get_mime_type(image_path)
        )
        
        # Process request
        request = documentai.ProcessRequest(
            name=f"{self.parent}/processors/{self.processor_id}",
            raw_document=raw_document
        )
        
        try:
            # Process the document
            result = self.client.process_document(request=request)
            document = result.document
            
            # Extract data
            extracted_data = self._extract_data(document)
            
            return {
                'success': True,
                'text': document.text,
                'tables': extracted_data['tables'],
                'pages': len(document.pages),
                'processor': self.processor_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'tables': [],
                'pages': 0
            }
    
    def _get_mime_type(self, file_path):
        """Get MIME type based on file extension."""
        ext = file_path.lower().split('.')[-1]
        mime_types = {
            'pdf': 'application/pdf',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'bmp': 'image/bmp',
            'tiff': 'image/tiff'
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    def _extract_data(self, document):
        """Extract table data from the processed document."""
        tables = []
        
        for page in document.pages:
            for table in page.tables:
                table_data = self._extract_table(table, document)
                if table_data:
                    tables.append(table_data)
        
        return {'tables': tables}
    
    def _extract_table(self, table, document):
        """Extract data from a single table."""
        try:
            # Get headers
            headers = []
            if table.header_rows:
                for cell in table.header_rows[0].cells:
                    text = self._get_text_from_layout(cell.layout, document)
                    headers.append(text)
            
            # Get rows
            rows = []
            for row in table.body_rows:
                row_data = []
                for cell in row.cells:
                    text = self._get_text_from_layout(cell.layout, document)
                    row_data.append(text)
                rows.append(row_data)
            
            return {
                'headers': headers,
                'rows': rows,
                'row_count': len(rows),
                'column_count': len(headers) if headers else 0
            }
            
        except Exception as e:
            print(f"Error extracting table: {e}")
            return None
    
    def _get_text_from_layout(self, layout, document):
        """Extract text from a layout element."""
        try:
            if layout.text_anchor and layout.text_anchor.text_segments:
                start_index = layout.text_anchor.text_segments[0].start_index
                end_index = layout.text_anchor.text_segments[0].end_index
                return document.text[start_index:end_index]
            return ""
        except:
            return ""
    
    def process_folder(self, input_folder="inputs", output_folder="outputs"):
        """
        Process all images in a folder.
        
        Args:
            input_folder: Folder containing input images
            output_folder: Folder to save output files
            
        Returns:
            Dictionary with processing results
        """
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Supported image extensions
        supported_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.pdf'}
        
        # Find all image files
        image_files = []
        if os.path.exists(input_folder):
            for filename in os.listdir(input_folder):
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in supported_extensions:
                    image_files.append(os.path.join(input_folder, filename))
        
        if not image_files:
            return {
                'success': False,
                'error': f'No supported image files found in {input_folder}',
                'processed': 0,
                'results': []
            }
        
        print(f"Found {len(image_files)} image(s) to process...")
        
        results = []
        successful = 0
        
        for i, image_path in enumerate(image_files, 1):
            filename = os.path.basename(image_path)
            print(f"\n[{i}/{len(image_files)}] Processing: {filename}")
            
            try:
                # Process the image
                result = self.extract_tables(image_path)
                
                if result['success']:
                    # Generate output filename
                    base_name = os.path.splitext(filename)[0]
                    output_filename = f"{base_name}_extracted.txt"
                    output_path = os.path.join(output_folder, output_filename)
                    
                    # Save to text file
                    if self.save_to_text(result, output_path):
                        print(f"   ✅ Saved to: {output_filename}")
                        successful += 1
                        
                        results.append({
                            'input_file': filename,
                            'output_file': output_filename,
                            'success': True,
                            'tables_found': len(result['tables']),
                            'pages': result['pages']
                        })
                    else:
                        print(f"   ❌ Failed to save output")
                        results.append({
                            'input_file': filename,
                            'success': False,
                            'error': 'Failed to save output file'
                        })
                else:
                    print(f"   ❌ Processing failed: {result.get('error', 'Unknown error')}")
                    results.append({
                        'input_file': filename,
                        'success': False,
                        'error': result.get('error', 'Unknown error')
                    })
                    
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
                results.append({
                    'input_file': filename,
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'success': successful > 0,
            'processed': successful,
            'total': len(image_files),
            'results': results
        }
    
    def save_to_text(self, data, output_path):
        """
        Save extracted data to a text file.
        
        Args:
            data: Extracted data from Document AI
            output_path: Path for the output file
            
        Returns:
            True if successful
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("EXTRACTED TABLE DATA\n")
                f.write("=" * 50 + "\n\n")
                
                # Write main text
                if data.get('text'):
                    f.write("TEXT CONTENT:\n")
                    f.write("-" * 20 + "\n")
                    f.write(data['text'])
                    f.write("\n\n")
                
                # Write tables
                if data.get('tables'):
                    f.write("TABLE DATA:\n")
                    f.write("-" * 20 + "\n")
                    
                    for i, table in enumerate(data['tables'], 1):
                        f.write(f"\nTable {i}:\n")
                        
                        # Headers
                        if table.get('headers'):
                            f.write("Headers: " + " | ".join(table['headers']) + "\n")
                        
                        # Rows
                        if table.get('rows'):
                            for j, row in enumerate(table['rows'], 1):
                                f.write(f"Row {j}: " + " | ".join(row) + "\n")
                
                # Metadata
                f.write(f"\nMETADATA:\n")
                f.write(f"-" * 20 + "\n")
                f.write(f"Pages: {data.get('pages', 0)}\n")
                f.write(f"Tables found: {len(data.get('tables', []))}\n")
                f.write(f"Processor: {data.get('processor', 'Unknown')}\n")
            
            return True
            
        except Exception as e:
            print(f"Error saving to text: {e}")
            return False


def main():
    """Main function for the interview assignment."""
    
    print("🧪 Document AI Table Extractor - Interview Assignment")
    print("=" * 60)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please create a .env file with your Google Cloud configuration:")
        print("   GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json")
        print("   PROJECT_ID=your-google-cloud-project-id")
        print("   LOCATION=us")
        return 1
    
    # Check required environment variables
    project_id = os.getenv('PROJECT_ID')
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if not project_id:
        print("❌ PROJECT_ID not set in .env file")
        return 1
    
    if not creds_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set in .env file")
        return 1
    
    if not os.path.exists(creds_path):
        print(f"❌ Credentials file not found: {creds_path}")
        return 1
    
    print(f"✅ Configuration loaded from .env file")
    print(f"   Project ID: {project_id}")
    print(f"   Location: {os.getenv('LOCATION', 'us')}")
    print(f"   Credentials: {creds_path}")
    
    # Ask for processing mode
    print(f"\n📋 Processing Options:")
    print(f"   1. Single image")
    print(f"   2. Batch process all images in inputs/ folder")
    
    mode = input("\nChoose processing mode (1 or 2): ").strip()
    
    if mode == "2":
        # Batch processing mode
        print(f"\n📁 Batch Processing Mode")
        input_folder = input("Enter input folder (default: inputs): ").strip() or "inputs"
        output_folder = input("Enter output folder (default: outputs): ").strip() or "outputs"
        
        try:
            print(f"\n🚀 Initializing Document AI client...")
            extractor = TableExtractor()
            print(f"✅ Using processor: {extractor.processor_id}")
            
            print(f"\n📸 Processing all images in {input_folder}/...")
            batch_result = extractor.process_folder(input_folder, output_folder)
            
            if batch_result['success']:
                print(f"\n📊 Batch Processing Results:")
                print(f"   Processed: {batch_result['processed']}/{batch_result['total']} files")
                
                # Show individual results
                for result in batch_result['results']:
                    if result['success']:
                        print(f"   ✅ {result['input_file']} → {result['output_file']} ({result['tables_found']} tables)")
                    else:
                        print(f"   ❌ {result['input_file']} → Error: {result['error']}")
                
                print(f"\n🎉 Batch processing completed! Check {output_folder}/ folder for results.")
                return 0
            else:
                print(f"❌ Batch processing failed: {batch_result.get('error', 'Unknown error')}")
                return 1
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return 1
    
    else:
        # Single image processing mode
        print(f"\n📸 Single Image Processing Mode")
        
        # Get image path
        image_path = input("Enter path to your image file: ").strip()
        if not image_path or not os.path.exists(image_path):
            print("❌ Valid image file path is required")
            return 1
        
        # Get output path
        output_path = input("Enter output text file path (default: output.txt): ").strip()
        if not output_path:
            output_path = "output.txt"
    
    try:
        print(f"\n🚀 Initializing Document AI client...")
        extractor = TableExtractor()
        print(f"✅ Using processor: {extractor.processor_id}")
        
        print(f"\n📸 Processing image: {image_path}")
        result = extractor.extract_tables(image_path)
        
        if not result['success']:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return 1
        
        # Display results
        print(f"\n📊 Results:")
        print(f"   Pages: {result['pages']}")
        print(f"   Tables found: {len(result['tables'])}")
        
        if result['tables']:
            total_rows = sum(table.get('row_count', 0) for table in result['tables'])
            print(f"   Total rows: {total_rows}")
        
        # Save to text file
        print(f"\n💾 Saving to: {output_path}")
        if extractor.save_to_text(result, output_path):
            print("✅ Data saved successfully!")
            
            # Show file size
            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                print(f"   File size: {size} bytes")
        else:
            print("❌ Failed to save data")
            return 1
        
        print(f"\n🎉 Success! Check {output_path} for extracted data.")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
