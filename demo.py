#!/usr/bin/env python3
"""
Demo script for Document AI Table Extractor - Interview Assignment

Usage:
    python3 demo.py                    # Process all images in inputs/ folder
    python3 demo.py [image_name]       # Process specific image in inputs/ folder
    python3 demo.py [full_path]        # Process image at specific path
"""

import os
import sys
import time
from dotenv import load_dotenv
from src.extractor import TableExtractor
from src.parallel_extractor import ParallelTableExtractor

# Load environment variables
load_dotenv()


def demo_parallel_batch_processing(input_folder="inputs", output_folder="outputs", max_workers=5):
    """
    Demonstrate parallel batch processing of all images in a folder.
    
    Args:
        input_folder: Input folder containing images
        output_folder: Output folder for extracted text files
        max_workers: Number of parallel workers
    """
    
    print(f"🚀 DEMO: Parallel Batch Processing - All Images ({max_workers} workers)")
    print("=" * 60)
    
    try:
        # Initialize parallel extractor
        extractor = ParallelTableExtractor(max_workers=max_workers)
        
        # Process folder
        start_time = time.time()
        result = extractor.process_folder_parallel(input_folder, output_folder)
        total_time = time.time() - start_time
        
        if result['success']:
            print(f"\n🎉 Parallel processing completed successfully!")
            print(f"⏱️  Total time: {total_time:.2f} seconds")
            print(f"📊 Files processed: {result['successful']}/{result['total_files']}")
            print(f"📈 Throughput: {result['throughput']:.2f} files/second")
            print(f"👥 Workers used: {result['max_workers']}")
            
            if result['failed'] > 0:
                print(f"⚠️  Failed files: {result['failed']}")
            
            print(f"\n📁 Results saved to: {output_folder}/")
            print("🔍 Check the output folder for extracted table data!")
            
            # Show speedup if we have processing time data
            total_processing_time = result.get('total_processing_time', 0)
            if total_processing_time > 0:
                efficiency = (total_processing_time / total_time) * 100
                print(f"⚡ Processing efficiency: {efficiency:.1f}%")
            
        else:
            print(f"\n❌ Parallel processing failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n💥 Error during parallel processing: {e}")
        return False
    
    return True


def demo_batch_processing(input_folder="inputs", output_folder="outputs"):
    """
    Demonstrate sequential batch processing of all images in a folder.
    
    Args:
        input_folder: Input folder containing images
        output_folder: Output folder for extracted text files
    """
    
    print("🎯 DEMO: Sequential Batch Processing - All Images")
    print("=" * 55)
    
    try:
        # Initialize extractor
        print("1️⃣ Initializing Document AI client...")
        extractor = TableExtractor()
        print(f"   ✅ Processor: {extractor.processor_id}")
        
        # Process all images
        print(f"\n2️⃣ Processing all images in: {input_folder}/")
        result = extractor.process_folder(input_folder, output_folder)
        
        if not result['success']:
            print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
            return False
        
        # Show results
        print(f"\n3️⃣ Batch Processing Results:")
        print(f"   📁 Processed: {result['processed']}/{result['total']} files")
        print(f"   📂 Output folder: {output_folder}/")
        
        # Show individual results
        for file_result in result['results']:
            if file_result['success']:
                print(f"   ✅ {file_result['input_file']} → {file_result['output_file']}")
                if 'tables_found' in file_result:
                    print(f"      📊 Tables found: {file_result['tables_found']}")
            else:
                print(f"   ❌ {file_result['input_file']}: {file_result.get('error', 'Failed')}")
        
        print(f"\n🎉 Batch processing completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Batch processing failed: {str(e)}")
        return False


def demo_single_image(image_path, output_path=None):
    """
    Demonstrate single image processing.
    
    Args:
        image_path: Path to image file
        output_path: Output text file path (optional)
    """
    
    if output_path is None:
        # Generate output filename based on input
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = f"{base_name}_extracted.txt"
    
    print("🎯 DEMO: Single Image Processing")
    print("=" * 50)
    
    try:
        # Initialize extractor
        print("1️⃣ Initializing Document AI client...")
        extractor = TableExtractor()
        print(f"   ✅ Processor: {extractor.processor_id}")
        
        # Process image
        print(f"\n2️⃣ Processing image: {image_path}")
        result = extractor.extract_tables(image_path)
        
        if not result['success']:
            print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
            return False
        
        # Show results
        print(f"\n3️⃣ Extraction Results:")
        print(f"   📄 Pages: {result['pages']}")
        print(f"   📊 Tables found: {len(result['tables'])}")
        
        if result['tables']:
            total_rows = sum(table.get('row_count', 0) for table in result['tables'])
            print(f"   📝 Total rows: {total_rows}")
            
            # Show table preview
            for i, table in enumerate(result['tables'][:2], 1):  # Show first 2 tables
                print(f"   📋 Table {i}: {table.get('row_count', 0)} rows × {table.get('column_count', 0)} columns")
        
        # Save to file
        print(f"\n4️⃣ Saving results to: {output_path}")
        if extractor.save_to_text(result, output_path):
            print("   ✅ Data saved successfully!")
            
            # Show file info
            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                print(f"   📁 File size: {size} bytes")
                
                # Show preview of saved content
                with open(output_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    print(f"\n📖 Output Preview (first 10 lines):")
                    for i, line in enumerate(lines[:10]):
                        print(f"   {i+1:2d}: {line}")
                    if len(lines) > 10:
                        print(f"   ... and {len(lines) - 10} more lines")
        else:
            print("   ❌ Failed to save data")
            return False
        
        print(f"\n🎉 Single image processing completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Single image processing failed: {str(e)}")
        return False


def main():
    """Main demo function with intelligent mode selection."""
    
    print("🚀 Document AI Table Extractor - Smart Demo")
    print("=" * 50)
    
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
    print(f"   Credentials: {os.path.basename(creds_path)}")
    
    # Determine mode based on command line arguments
    if len(sys.argv) > 1:
        # Single image mode - argument provided
        arg = sys.argv[1]
        
        # Check if it's a filename in inputs/ folder or a full path
        if os.path.exists(arg):
            # Full path provided
            image_path = arg
        elif os.path.exists(os.path.join("inputs", arg)):
            # Image name in inputs/ folder
            image_path = os.path.join("inputs", arg)
        else:
            print(f"❌ Image file not found: {arg}")
            print("Checked:")
            print(f"   • {arg}")
            print(f"   • inputs/{arg}")
            return 1
        
        print(f"\n🎯 Mode: Single Image Processing")
        print(f"   📸 Target: {image_path}")
        success = demo_single_image(image_path)
        
        if success:
            print(f"\n📋 Summary:")
            print(f"   • Project ID: {project_id}")
            print(f"   • Input image: {image_path}")
            print(f"   • Status: ✅ Success")
            return 0
        else:
            return 1
    
    else:
        # Batch mode - no arguments, process all images in inputs/
        if not os.path.exists("inputs"):
            print("❌ No inputs/ folder found!")
            print("Please create an inputs/ folder and add some images, or specify an image path:")
            print("\nUsage:")
            print("   python3 demo.py                    # Process all images in inputs/")
            print("   python3 demo.py image.png          # Process inputs/image.png")
            print("   python3 demo.py path/to/image.png  # Process specific path")
            return 1
        
        # Check for images in inputs folder
        image_files = []
        supported_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.pdf'}
        
        if os.path.exists("inputs"):
            for filename in os.listdir("inputs"):
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in supported_extensions:
                    image_files.append(filename)
        
        if not image_files:
            print("❌ No supported files found in inputs/ folder!")
            print("Supported formats: PNG, JPG, JPEG, GIF, BMP, TIFF, PDF")
            print("\nUsage:")
            print("   python3 demo.py                    # Process all files in inputs/")
            print("   python3 demo.py document.pdf       # Process inputs/document.pdf")
            print("   python3 demo.py image.png          # Process inputs/image.png")
            print("   python3 demo.py path/to/file.pdf   # Process specific path")
            return 1
        
        print(f"\n🎯 Mode: Batch Processing")
        print(f"   📁 Found {len(image_files)} image(s) in inputs/ folder")
        for img in image_files:
            print(f"      • {img}")
        
        # Offer processing options
        print(f"\n⚡ Processing Options:")
        print(f"   1. Sequential Processing (traditional)")
        print(f"   2. Parallel Processing (faster for multiple files)")
        print(f"   3. Performance Comparison (both methods)")
        
        choice = input("\nSelect processing method (1/2/3) [default: 2]: ").strip()
        
        if choice == "1":
            success = demo_batch_processing("inputs", "outputs")
        elif choice == "3":
            print(f"\n🏁 Running Performance Comparison...")
            print(f"This will process files twice to compare performance.\n")
            
            # Sequential first
            print("1️⃣ Sequential Processing:")
            start_time = time.time()
            success1 = demo_batch_processing("inputs", "outputs/sequential")
            sequential_time = time.time() - start_time
            
            print("\n" + "="*60)
            
            # Parallel second
            print("2️⃣ Parallel Processing:")
            start_time = time.time()
            success2 = demo_parallel_batch_processing("inputs", "outputs/parallel", max_workers=5)
            parallel_time = time.time() - start_time
            
            print(f"\n📊 PERFORMANCE COMPARISON RESULTS")
            print("=" * 50)
            print(f"Sequential Time: {sequential_time:.2f}s")
            print(f"Parallel Time:   {parallel_time:.2f}s")
            
            if sequential_time > 0 and parallel_time > 0:
                speedup = sequential_time / parallel_time
                time_saved = sequential_time - parallel_time
                improvement = (speedup - 1) * 100
                
                print(f"Speedup:         {speedup:.2f}x")
                print(f"Time Saved:      {time_saved:.2f}s")
                print(f"Improvement:     {improvement:.1f}%")
                
                if speedup > 2:
                    print("🎉 Excellent parallel performance!")
                elif speedup > 1.5:
                    print("✅ Good parallel performance!")
                else:
                    print("⚠️  Limited parallel benefit")
            
            success = success1 and success2
        else:
            # Default to parallel processing
            success = demo_parallel_batch_processing("inputs", "outputs", max_workers=5)
        
        if success:
            print(f"\n📋 Summary:")
            print(f"   • Project ID: {project_id}")
            print(f"   • Mode: Batch Processing")
            print(f"   • Images processed: {len(image_files)}")
            print(f"   • Output folder: outputs/")
            print(f"   • Status: ✅ Success")
            
            print(f"\n🚀 Next steps for your interview:")
            print(f"   1. Show the extracted text files in outputs/ folder")
            print(f"   2. Explain the Google Document AI integration")
            print(f"   3. Demonstrate both sequential and parallel processing")
            print(f"   4. Run 'python3 performance_benchmark.py' for detailed analysis")
            print(f"   5. Generate PDF report: python3 pdf_generator/generate_pdf_report.py")
            print(f"   6. Discuss scalability and Kubernetes deployment potential")
            
            # Offer to generate PDF report
            print(f"\n📄 Would you like to generate a PDF report now? (y/N): ", end="")
            try:
                response = input().strip().lower()
                if response in ['y', 'yes']:
                    print(f"\n📄 Generating PDF report...")
                    try:
                        import subprocess
                        result = subprocess.run([
                            'python3', 'pdf_generator/generate_pdf_report.py', 'outputs', '', 'reports'
                        ], capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            print(f"✅ PDF report generated successfully!")
                            # Extract PDF path from output
                            for line in result.stdout.split('\n'):
                                if 'Location:' in line:
                                    pdf_path = line.split('Location:')[1].strip()
                                    print(f"📄 PDF saved to: {pdf_path}")
                                    break
                        else:
                            print(f"⚠️  PDF generation failed: {result.stderr}")
                    except Exception as e:
                        print(f"⚠️  Could not generate PDF: {e}")
                        print(f"   You can generate it manually with:")
                        print(f"   python3 pdf_generator/generate_pdf_report.py outputs '' reports")
            except KeyboardInterrupt:
                print(f"\n   You can generate PDF later with:")
                print(f"   python3 pdf_generator/generate_pdf_report.py outputs '' reports")
            
            return 0
        else:
            return 1


if __name__ == "__main__":
    sys.exit(main())
