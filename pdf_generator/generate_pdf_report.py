#!/usr/bin/env python3
"""
PDF Report Generator Script

This script generates consolidated PDF reports from Document AI extraction results
with configurable file ordering and professional formatting.

Usage:
    python3 pdf_generator/generate_pdf_report.py [output_folder] [pdf_filename] [reports_folder]
    
Examples:
    python3 pdf_generator/generate_pdf_report.py outputs
    python3 pdf_generator/generate_pdf_report.py outputs/parallel custom_report.pdf
    python3 pdf_generator/generate_pdf_report.py outputs/sequential report.pdf reports
"""

import sys
import os
from pathlib import Path
from pdf_generator import PDFGenerator


def print_banner():
    """Print script banner."""
    print("📄 Document AI PDF Report Generator")
    print("=" * 50)
    print("Generate consolidated PDF reports from extracted Document AI results")
    print("with configurable ordering and professional formatting.\n")


def find_output_folders():
    """Find available output folders with extracted files."""
    potential_folders = [
        'outputs',
        'outputs/parallel', 
        'outputs/sequential',
        'outputs/demo_parallel',
        'outputs/demo_sequential'
    ]
    
    available_folders = []
    
    for folder in potential_folders:
        if os.path.exists(folder):
            files = [f for f in os.listdir(folder) if f.endswith('_extracted.txt')]
            if files:
                available_folders.append((folder, len(files)))
    
    return available_folders


def interactive_folder_selection(available_folders):
    """Allow user to select output folder interactively."""
    if len(available_folders) == 1:
        return available_folders[0][0]
    
    print("📁 Available output folders:")
    for i, (folder, file_count) in enumerate(available_folders, 1):
        print(f"   {i}. {folder} ({file_count} files)")
    
    while True:
        try:
            choice = input(f"\nSelect folder (1-{len(available_folders)}) [1]: ").strip()
            if not choice:
                choice = "1"
            
            index = int(choice) - 1
            if 0 <= index < len(available_folders):
                return available_folders[index][0]
            else:
                print(f"❌ Please enter a number between 1 and {len(available_folders)}")
        except ValueError:
            print("❌ Please enter a valid number")


def main():
    """Main function."""
    print_banner()
    
    # Parse command line arguments
    output_folder = None
    pdf_filename = None
    reports_folder = "reports"  # Default reports folder
    
    if len(sys.argv) > 1:
        output_folder = sys.argv[1]
    
    if len(sys.argv) > 2:
        pdf_filename = sys.argv[2]
    
    if len(sys.argv) > 3:
        reports_folder = sys.argv[3]
    
    # Find available output folders if not specified
    if not output_folder:
        available_folders = find_output_folders()
        
        if not available_folders:
            print("❌ No output folders with extracted files found!")
            print("\n💡 Available commands to generate extracted files:")
            print("   python3 demo.py                    # Run Document AI processing")
            print("   python3 parallel_demo.py           # Run parallel processing demo")
            print("   python3 performance_benchmark.py   # Run comprehensive benchmarks")
            return 1
        
        print(f"📊 Found {len(available_folders)} folders with extracted files")
        output_folder = interactive_folder_selection(available_folders)
    
    # Validate output folder
    if not os.path.exists(output_folder):
        print(f"❌ Output folder not found: {output_folder}")
        return 1
    
    extracted_files = [f for f in os.listdir(output_folder) if f.endswith('_extracted.txt')]
    if not extracted_files:
        print(f"❌ No extracted files found in: {output_folder}")
        return 1
    
    print(f"✅ Using output folder: {output_folder}")
    print(f"📄 Found {len(extracted_files)} extracted files")
    
    # Check for ReportLab dependency
    try:
        import reportlab
        print("✅ ReportLab library available")
    except ImportError:
        print("❌ ReportLab library not found!")
        print("   Install with: pip install reportlab")
        return 1
    
    try:
        # Initialize PDF generator
        config_path = os.path.join(os.path.dirname(__file__), "pdf_order_config.txt")
        generator = PDFGenerator(config_file=config_path)
        
        # Generate PDF
        print(f"\n🎯 Generating PDF report...")
        print(f"📂 Source folder: {output_folder}")
        print(f"📁 Reports folder: {reports_folder}")
        pdf_path = generator.generate_pdf(output_folder, pdf_filename, reports_folder)
        
        # Success message
        print(f"\n🎉 PDF Report Generated Successfully!")
        print(f"📄 Location: {pdf_path}")
        print(f"📊 Report includes all {len(extracted_files)} processed documents")
        
        # Additional info
        file_size = os.path.getsize(pdf_path) / (1024 * 1024)  # MB
        print(f"💾 File size: {file_size:.2f} MB")
        
        print(f"\n💡 Next steps:")
        print(f"   • Open the PDF to review the consolidated report")
        print(f"   • Use this for presentations or documentation")
        print(f"   • Modify pdf_order_config.txt to change file ordering")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
