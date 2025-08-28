# Document AI Table Extractor

Extract tabular data from images using Google Document AI and save as text files.

## 🎯 Interview Assignment Solution

This project demonstrates:
- Google Cloud Document AI integration
- Table detection and extraction from images
- **Parallel processing with 6.36x speedup**
- Clean, professional code structure
- Environment-based configuration
- Comprehensive error handling
- Performance benchmarking and optimization

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Setup Google Cloud
```bash
python3 setup_env.py --help  # View setup instructions
python3 setup_env.py         # Create .env file interactively
```

### 3. Run Demo
```bash
python3 demo.py                    # Smart demo with parallel/sequential options
python3 demo.py document.pdf       # Process specific PDF in inputs/ folder  
python3 demo.py image.png          # Process specific image in inputs/ folder
python3 demo.py path/to/file.pdf   # Process PDF at specific path

# Performance Analysis
python3 parallel_demo.py           # Compare sequential vs parallel processing
python3 performance_benchmark.py   # Comprehensive performance analysis

# PDF Report Generation (saves to reports/ folder)
python3 pdf_generator/generate_pdf_report.py        # Generate consolidated PDF report
python3 pdf_generator/generate_pdf_report.py outputs/parallel  # From specific folder
python3 pdf_generator/generate_pdf_report.py outputs custom_report.pdf reports  # Custom location

# Interactive Mode
python3 src/extractor.py           # Interactive mode with menu options
```

## 📁 Project Structure

```
wyrely/
├── src/                    # Core extraction logic
│   ├── extractor.py        # Sequential processing implementation
│   ├── parallel_extractor.py  # Parallel processing (6.36x faster!)
│   └── __init__.py
├── pdf_generator/          # PDF report generation
│   ├── pdf_generator.py    # PDF generation engine
│   ├── generate_pdf_report.py  # CLI script for PDF generation
│   ├── pdf_order_config.txt    # Configurable file ordering
│   ├── __init__.py
│   └── README.md           # PDF generator documentation
├── inputs/                 # Test images (12 real project files)
├── outputs/                # Extracted text files
├── reports/                # Generated PDF reports
├── benchmarks/             # Performance analysis results
├── tests/                  # Test scripts
│   └── test_extractor.py   # Functionality tests
├── docs/                   # Comprehensive documentation
│   ├── INTERVIEW_GUIDE.md  # Interview demo guide
│   ├── PARALLEL_PROCESSING_ANALYSIS.md  # Technical analysis
│   └── SUBMISSION_SUMMARY.md  # Complete submission guide
├── demo.py                 # Smart demo (parallel/sequential options)
├── parallel_demo.py        # Performance comparison demo
├── performance_benchmark.py  # Comprehensive benchmarking
├── setup_env.py           # Environment setup helper
├── requirements.txt       # Dependencies (includes ReportLab)
└── .env                   # Your credentials (create this)
```

## 🎯 For Interview Demo

### Show the Working Solution:
```bash
# Smart demo - automatically detects what to do:
python3 demo.py                    # → Batch mode (all images in inputs/)
python3 demo.py image.png          # → Single mode (specific image)
python3 demo.py path/to/file.png   # → Single mode (full path)

# Alternative demos:
python3 batch_demo.py              # → Always batch mode
python3 src/extractor.py           # → Interactive mode with menu
```

### Demo Modes Explained:
- **Batch Mode**: No arguments → processes ALL images in `inputs/` folder
- **Single Mode**: Specify image name or path → processes only that image
- **Smart Detection**: Automatically chooses the right mode based on arguments

### Explain the Code:
- `src/extractor.py` - Core implementation
- Clean, modular design
- Environment-based configuration
- Comprehensive error handling

### Discuss Improvements:
- ✅ **Batch processing for multiple images** (Already implemented!)
- ✅ **Parallel processing with 6.36x speedup** (Already implemented!)
- ✅ **Performance benchmarking and analysis** (Already implemented!)
- Additional output formats (CSV, JSON)
- Web interface for non-technical users  
- Confidence scoring and validation
- Kubernetes deployment and auto-scaling

## 🔧 Configuration

Create a `.env` file with just these 3 essential variables:
```bash
GOOGLE_APPLICATION_CREDENTIALS=./your-service-account-key.json
PROJECT_ID=your-google-cloud-project-id
LOCATION=us
```

**That's it!** The code will automatically:
- Find suitable Document AI processors
- Create output directories as needed
- Handle all other configuration

## ⚡ Parallel Processing Performance

### 🚀 **Performance Improvements**
- **Sequential Processing:** 27.71s for 12 files
- **Parallel Processing:** 4.36s for 12 files  
- **Speedup:** **6.36x faster**
- **Time Saved:** 23.35 seconds (84% reduction)

### 📊 **Scaling Results**
| Workers | Time (s) | Speedup | Efficiency |
|---------|----------|---------|------------|
| 1       | 27.71    | 1.00x   | 100%       |
| 3       | 10.35    | 2.68x   | 89%        |
| 5       | 7.35     | 3.77x   | 75%        |
| 10      | 4.36     | 6.36x   | 64%        |

### 💡 **Why It Works**
- **I/O-Bound Operations:** Document AI API calls benefit from parallelism
- **Thread-Based:** Optimal for network-intensive operations
- **Error Isolation:** Individual file failures don't stop the batch
- **Resource Efficient:** Shared client instances reduce overhead

### 🔬 **How to Test Performance**
```bash
# Quick comparison demo
python3 parallel_demo.py

# Comprehensive benchmark analysis
python3 performance_benchmark.py

# View detailed report
cat benchmarks/*/PERFORMANCE_REPORT.md
```

## 📄 PDF Report Generation

### 🎯 **Consolidated PDF Reports**
Generate professional PDF reports combining all extracted data:

```bash
# Generate PDF from outputs folder (saves to reports/)
python3 pdf_generator/generate_pdf_report.py

# Generate from specific results
python3 pdf_generator/generate_pdf_report.py outputs/parallel
python3 pdf_generator/generate_pdf_report.py outputs/sequential

# Custom filename and location
python3 pdf_generator/generate_pdf_report.py outputs my_report.pdf reports
python3 pdf_generator/generate_pdf_report.py outputs/parallel parallel_report.pdf custom_reports
```

### ⚙️ **Configurable File Ordering**
Customize document order in `pdf_generator/pdf_order_config.txt`:
```txt
# Priority files first
Sheets
project_data

# Finish schedule files in logical order
finish_schedule_acoustical_panel_ceiling
finish_schedule_applied_window_film
# ... more files
```

### 🎨 **PDF Features**
- **Professional Layout**: Clean, corporate-style formatting
- **Table of Contents**: Auto-generated with document summaries
- **Cover Page**: Processing statistics and metadata
- **Preserved Tables**: Extracted tables formatted as proper PDF tables
- **Configurable Order**: Customize document sequence via config file

## 📋 Supported File Formats

Your system processes multiple document formats:

### ✅ **Image Formats:**
- PNG, JPG, JPEG
- GIF, BMP, TIFF

### ✅ **Document Formats:**
- **PDF** (Multi-page support!)

### 🔧 **No Additional Setup Required:**
PDF processing works out-of-the-box with your existing Google Document AI configuration. The system automatically:
- Detects file type by extension
- Uses appropriate MIME type (`application/pdf`)
- Processes all pages in multi-page PDFs
- Extracts tables from each page

## 📊 Sample Output

The extracted text file contains:
- All detected text from the document/image
- Structured table data (headers and rows)
- Processing metadata (pages, tables found, processor info)

### Single Image Output:
```
image_extracted.txt - Processed from inputs/image.png
```

### Batch Processing Output:
```
outputs/
├── image_extracted.txt          # From image.png
├── inventory_extracted.txt      # From inventory.png (if present)
└── sales_extracted.txt          # From sales.png (if present)
```

## 🚨 Troubleshooting

- **No processor found**: Enable Document AI API
- **Permission denied**: Check service account roles
- **Credentials not found**: Verify .env file path

## 🎉 Success Metrics

✅ Image processes without errors  
✅ Tables are detected and extracted  
✅ Text file is generated with structured data  
✅ Code is clean and well-documented  
