# 📄 PDF Generator for Document AI Results

This package generates professional PDF reports from Document AI extraction results with configurable ordering and formatting.

## 🌟 Features

- **Configurable File Ordering**: Use `pdf_order_config.txt` to specify document order
- **Professional Formatting**: Clean, readable PDF layout with tables and headers
- **Automatic Table of Contents**: Generated with document summaries
- **Cover Page**: Summary statistics and processing information
- **Table Preservation**: Extracted tables formatted as proper PDF tables
- **Metadata Integration**: Processing details and statistics included

## 📦 Installation

Install the required dependency:

```bash
pip install reportlab
```

## 🚀 Quick Start

### Command Line Usage

```bash
# Generate PDF from default outputs folder (saves to reports/)
python3 pdf_generator/generate_pdf_report.py

# Generate PDF from specific folder
python3 pdf_generator/generate_pdf_report.py outputs/parallel

# Generate PDF with custom filename and location
python3 pdf_generator/generate_pdf_report.py outputs custom_report.pdf reports
python3 pdf_generator/generate_pdf_report.py outputs/parallel parallel_report.pdf custom_reports
```

### Python API Usage

```python
from pdf_generator import PDFGenerator

# Initialize generator
generator = PDFGenerator(config_file="pdf_generator/pdf_order_config.txt")

# Generate PDF (saves to reports/ folder by default)
pdf_path = generator.generate_pdf("outputs", "my_report.pdf")
print(f"PDF generated: {pdf_path}")

# Custom reports folder
pdf_path = generator.generate_pdf("outputs", "custom.pdf", "custom_reports")
print(f"PDF generated: {pdf_path}")
```

## ⚙️ Configuration

### File Order Configuration

Edit `pdf_order_config.txt` to specify the order of documents in the PDF:

```txt
# Priority files first
Sheets
project_data

# Finish schedule files in logical order
finish_schedule_acoustical_panel_ceiling
finish_schedule_applied_window_film
finish_schedule_Architecural_Millwork
# ... more files
```

**Configuration Rules:**
- Lines starting with `#` are comments
- Empty lines are ignored
- Files are processed in the order listed
- Use the base filename without `_extracted.txt` suffix
- Files not listed will be appended alphabetically

### Supported Input Files

The PDF generator works with files created by the Document AI extractor:
- `*_extracted.txt` files from any output folder
- Preserves all metadata (pages, tables found, processor info)
- Maintains table formatting and structure

## 📊 PDF Report Structure

### 1. Cover Page
- Report generation timestamp
- Summary statistics (files processed, tables found, pages)
- Processing method information

### 2. Table of Contents
- List of all documents
- Table count per document
- Document descriptions

### 3. Document Sections
- Each extracted file becomes a section
- Metadata summary for each document
- Formatted tables and content
- Page breaks between documents

## 🎨 Styling Features

- **Professional Layout**: Clean, corporate-style formatting
- **Color Coding**: Headers and tables with consistent color scheme
- **Table Formatting**: Proper table grids with headers
- **Typography**: Multiple font styles for different content types
- **Spacing**: Optimal spacing for readability

## 📁 Project Integration

### Usage with Document AI Processing

```bash
# 1. Process documents
python3 demo.py

# 2. Generate PDF report
python3 pdf_generator/generate_pdf_report.py outputs

# 3. Compare sequential vs parallel results
python3 pdf_generator/generate_pdf_report.py outputs/sequential sequential_report.pdf
python3 pdf_generator/generate_pdf_report.py outputs/parallel parallel_report.pdf
```

### Integration with Performance Benchmarks

```bash
# 1. Run performance benchmark
python3 performance_benchmark.py

# 2. Generate PDF from benchmark results
python3 pdf_generator/generate_pdf_report.py benchmarks/*/output_parallel_5
```

## 🔧 Advanced Configuration

### Custom Styling

Modify the `_create_styles()` method in `pdf_generator.py` to customize:
- Font sizes and families
- Colors and backgrounds
- Spacing and margins
- Table styles

### Custom Content Processing

Override the `_process_content_for_pdf()` method to:
- Add custom content parsing
- Modify table detection logic
- Include additional metadata
- Custom formatting rules

## 📝 Examples

### Basic Usage

```python
from pdf_generator import PDFGenerator

# Simple PDF generation
generator = PDFGenerator()
pdf_path = generator.generate_pdf("outputs")
print(f"Report saved to: {pdf_path}")
```

### Custom Configuration

```python
# Custom order configuration
generator = PDFGenerator(config_file="custom_order.txt")

# Custom filename with timestamp
import datetime
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"document_report_{timestamp}.pdf"

pdf_path = generator.generate_pdf("outputs/parallel", filename)
```

### Batch Processing Multiple Folders

```python
folders = ["outputs/sequential", "outputs/parallel"]

for folder in folders:
    folder_name = folder.split("/")[-1]
    filename = f"report_{folder_name}.pdf"
    
    pdf_path = generator.generate_pdf(folder, filename)
    print(f"Generated: {pdf_path}")
```

## 🐛 Troubleshooting

### Common Issues

**ReportLab Not Found**
```bash
pip install reportlab
```

**No Extracted Files Found**
- Ensure you've run Document AI processing first
- Check that `*_extracted.txt` files exist in the output folder

**Configuration File Not Found**
- The generator will work without config file (alphabetical order)
- Ensure `pdf_order_config.txt` exists in the same folder as the script

**Permission Errors**
- Ensure write permissions to the output directory
- Check that the PDF file isn't open in another application

### Debug Mode

Enable verbose output by modifying the logging level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

generator = PDFGenerator()
# ... rest of code
```

## 📈 Performance Considerations

- **Memory Usage**: Proportional to number and size of input files
- **Processing Time**: ~1-2 seconds per document for typical files
- **PDF Size**: Depends on content volume and table complexity
- **Concurrent Access**: Thread-safe for multiple generator instances

## 🤝 Integration Examples

### With Demo Scripts

Add PDF generation to existing demo scripts:

```python
# At end of demo.py
from pdf_generator import PDFGenerator

if success:
    try:
        generator = PDFGenerator("pdf_generator/pdf_order_config.txt")
        pdf_path = generator.generate_pdf("outputs")
        print(f"📄 PDF report generated: {pdf_path}")
    except Exception as e:
        print(f"⚠️  PDF generation failed: {e}")
```

### With Performance Benchmarks

```python
# After benchmark completion
def generate_benchmark_pdf(benchmark_dir):
    generator = PDFGenerator()
    
    # Find output folders in benchmark directory
    for folder in os.listdir(benchmark_dir):
        if folder.startswith("output_"):
            folder_path = os.path.join(benchmark_dir, folder)
            pdf_name = f"benchmark_{folder}.pdf"
            generator.generate_pdf(folder_path, pdf_name)
```

## 📋 API Reference

### PDFGenerator Class

#### `__init__(config_file="pdf_order_config.txt")`
Initialize PDF generator with configuration file.

#### `generate_pdf(output_folder, pdf_filename=None)`
Generate PDF report from extracted files.
- **Returns**: Path to generated PDF file
- **Raises**: ValueError if no files found, ImportError if ReportLab missing

#### `_load_order_config()`
Load file ordering from configuration file.

#### `_find_extracted_files(output_folder)`
Find and map all `*_extracted.txt` files in folder.

#### `_order_files(files_map)`
Order files according to configuration and return sorted list.

---

## 💡 Tips for Best Results

1. **Consistent Naming**: Use consistent file naming for better organization
2. **Order Configuration**: Customize `pdf_order_config.txt` for logical document flow
3. **File Descriptions**: Update `_get_file_description()` for better document descriptions
4. **Custom Styling**: Modify styles for branding or specific requirements
5. **Batch Processing**: Generate multiple PDFs for comparison (sequential vs parallel results)

This PDF generator provides a professional way to present Document AI extraction results in a consolidated, well-formatted report perfect for presentations, documentation, or archival purposes.
