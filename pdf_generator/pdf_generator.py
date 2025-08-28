"""
PDF Generator for Document AI Extraction Results

This module creates consolidated PDF reports from multiple extracted text files
with configurable ordering and professional formatting.
"""

import os
import glob
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import Color, black, blue, red, green
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class PDFGenerator:
    """
    PDF Generator for Document AI extraction results.
    
    Creates professional PDF reports combining multiple extracted text files
    with configurable ordering and formatting.
    """
    
    def __init__(self, config_file: str = "pdf_order_config.txt"):
        """
        Initialize PDF generator.
        
        Args:
            config_file: Path to the file order configuration file
        """
        self.config_file = config_file
        self.order_config = self._load_order_config()
        
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "ReportLab is required for PDF generation. "
                "Install with: pip install reportlab"
            )
    
    def _load_order_config(self) -> List[str]:
        """
        Load file ordering configuration from text file.
        
        Returns:
            List of base filenames in preferred order
        """
        order = []
        
        if not os.path.exists(self.config_file):
            print(f"⚠️  Order config file not found: {self.config_file}")
            print("   Using alphabetical order as default.")
            return order
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        order.append(line)
            
            print(f"✅ Loaded order configuration: {len(order)} files specified")
            return order
            
        except Exception as e:
            print(f"❌ Error loading order config: {e}")
            return []
    
    def _find_extracted_files(self, output_folder: str) -> Dict[str, str]:
        """
        Find all extracted text files in the output folder.
        
        Args:
            output_folder: Path to folder containing extracted text files
            
        Returns:
            Dictionary mapping base filename to full file path
        """
        files_map = {}
        
        if not os.path.exists(output_folder):
            print(f"❌ Output folder not found: {output_folder}")
            return files_map
        
        # Find all *_extracted.txt files
        pattern = os.path.join(output_folder, "*_extracted.txt")
        extracted_files = glob.glob(pattern)
        
        for file_path in extracted_files:
            filename = os.path.basename(file_path)
            # Remove _extracted.txt suffix to get base name
            base_name = filename.replace('_extracted.txt', '')
            files_map[base_name] = file_path
        
        print(f"📁 Found {len(files_map)} extracted files in {output_folder}")
        return files_map
    
    def _order_files(self, files_map: Dict[str, str]) -> List[tuple]:
        """
        Order files according to configuration.
        
        Args:
            files_map: Dictionary mapping base filename to full path
            
        Returns:
            List of (base_name, file_path) tuples in preferred order
        """
        ordered_files = []
        used_files = set()
        
        # First, add files in configured order
        for base_name in self.order_config:
            if base_name in files_map:
                ordered_files.append((base_name, files_map[base_name]))
                used_files.add(base_name)
            else:
                print(f"⚠️  Configured file not found: {base_name}")
        
        # Then add remaining files alphabetically
        remaining_files = [(name, path) for name, path in files_map.items() 
                          if name not in used_files]
        remaining_files.sort(key=lambda x: x[0])
        ordered_files.extend(remaining_files)
        
        print(f"📋 File order: {[name for name, _ in ordered_files]}")
        return ordered_files
    
    def _read_file_content(self, file_path: str) -> tuple:
        """
        Read content from an extracted text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Tuple of (content, metadata) where metadata is extracted from header
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata from header if present
            metadata = {}
            lines = content.split('\n')
            
            if content.startswith('='):
                # Find the end of header section
                header_end = 0
                for i, line in enumerate(lines):
                    if 'FULL TEXT CONTENT:' in line:
                        header_end = i
                        break
                
                # Extract metadata from header
                for line in lines[:header_end]:
                    if ':' in line and not line.startswith('=') and not line.startswith('-'):
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
            
            return content, metadata
            
        except Exception as e:
            print(f"❌ Error reading file {file_path}: {e}")
            return f"Error reading file: {e}", {}
    
    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """Create custom paragraph styles for the PDF."""
        styles = getSampleStyleSheet()
        
        custom_styles = {
            'title': ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            ),
            'heading': ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                spaceBefore=20,
                textColor=colors.darkblue
            ),
            'subheading': ParagraphStyle(
                'CustomSubHeading',
                parent=styles['Heading3'],
                fontSize=14,
                spaceAfter=8,
                spaceBefore=12,
                textColor=colors.darkgreen
            ),
            'normal': ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                alignment=TA_JUSTIFY
            ),
            'code': ParagraphStyle(
                'CustomCode',
                parent=styles['Normal'],
                fontSize=9,
                fontName='Courier',
                leftIndent=20,
                rightIndent=20,
                spaceAfter=6,
                textColor=colors.darkgreen
            )
        }
        
        return custom_styles
    
    def _create_cover_page(self, styles: Dict, num_files: int, total_pages: int, total_tables: int) -> List:
        """Create cover page elements."""
        elements = []
        
        # Title
        title = Paragraph("Document AI Extraction Results", styles['title'])
        elements.append(title)
        elements.append(Spacer(1, 0.5*inch))
        
        # Summary table
        summary_data = [
            ['Report Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Files Processed', str(num_files)],
            ['Total Pages Extracted', str(total_pages)],
            ['Total Tables Found', str(total_tables)],
            ['Processing Method', 'Google Document AI'],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Table of contents header
        toc_heading = Paragraph("Table of Contents", styles['heading'])
        elements.append(toc_heading)
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_table_of_contents(self, ordered_files: List[tuple], styles: Dict) -> List:
        """Create table of contents."""
        elements = []
        
        toc_data = [['Document', 'Tables Found', 'Description']]
        
        for i, (base_name, file_path) in enumerate(ordered_files, 1):
            # Read file to get table count
            content, metadata = self._read_file_content(file_path)
            tables_count = metadata.get('Tables Found', 'Unknown')
            
            # Create human-readable name
            display_name = base_name.replace('_', ' ').title()
            if 'finish_schedule' in base_name.lower():
                display_name = display_name.replace('Finish Schedule ', 'Finish Schedule: ')
            
            description = self._get_file_description(base_name)
            toc_data.append([display_name, str(tables_count), description])
        
        toc_table = Table(toc_data, colWidths=[2.5*inch, 1*inch, 2.5*inch])
        toc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        elements.append(toc_table)
        elements.append(PageBreak())
        
        return elements
    
    def _get_file_description(self, base_name: str) -> str:
        """Get description for a file based on its name."""
        descriptions = {
            'Sheets': 'Overview and summary information',
            'project_data': 'Project-specific data and details',
            'finish_schedule_acoustical_panel_ceiling': 'Acoustical panels and ceiling specifications',
            'finish_schedule_applied_window_film': 'Window film application details',
            'finish_schedule_Architecural_Millwork': 'Architectural millwork specifications',
            'finish_schedule_concrete': 'Concrete finishing requirements',
            'finish_schedule_decorative_formed_metals': 'Decorative metal work specifications',
            'finish_schedule_glazing': 'Glazing and window specifications',
            'finish_schedule_resilient_base_and_accessories': 'Resilient flooring and accessories',
            'finish_schedule_tiling': 'Tile work and installation details',
            'finish_schedule_wood_flooring': 'Wood flooring specifications',
            'finish_schedule_wood_panelling': 'Wood paneling requirements'
        }
        
        return descriptions.get(base_name, 'Document content and extracted data')
    
    def _process_content_for_pdf(self, content: str, styles: Dict) -> List:
        """Process content and convert to PDF elements."""
        elements = []
        lines = content.split('\n')
        
        current_section = ""
        in_table = False
        table_data = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                if not in_table:
                    elements.append(Spacer(1, 6))
                continue
            
            # Header sections
            if line.startswith('='):
                if 'DOCUMENT AI TABLE EXTRACTION RESULTS' in line:
                    continue  # Skip main header
                else:
                    heading = Paragraph(line.replace('=', ''), styles['heading'])
                    elements.append(heading)
                    
            elif line.startswith('-'):
                if in_table and table_data:
                    # End of table, create table element
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP')
                    ]))
                    elements.append(table)
                    elements.append(Spacer(1, 12))
                    table_data = []
                    in_table = False
                
                subheading = Paragraph(line.replace('-', ''), styles['subheading'])
                elements.append(subheading)
                
            elif line.startswith('Table '):
                # Start of a new table
                in_table = True
                table_data = []
                table_heading = Paragraph(line, styles['subheading'])
                elements.append(table_heading)
                
            elif ' | ' in line and in_table:
                # Table row
                row_data = [cell.strip() for cell in line.split('|')]
                table_data.append(row_data)
                
            elif ':' in line and any(keyword in line for keyword in ['Processed:', 'Pages:', 'Tables Found:', 'Processor:']):
                # Metadata line
                para = Paragraph(line, styles['code'])
                elements.append(para)
                
            else:
                # Regular content
                if in_table and table_data:
                    # End table if we hit regular content
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP')
                    ]))
                    elements.append(table)
                    elements.append(Spacer(1, 12))
                    table_data = []
                    in_table = False
                
                # Regular paragraph
                para = Paragraph(line, styles['normal'])
                elements.append(para)
        
        # Handle remaining table data
        if in_table and table_data:
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            elements.append(table)
        
        return elements
    
    def generate_pdf(self, output_folder: str, pdf_filename: str = None, reports_folder: str = "reports") -> str:
        """
        Generate PDF report from extracted text files.
        
        Args:
            output_folder: Folder containing *_extracted.txt files
            pdf_filename: Output PDF filename (auto-generated if None)
            reports_folder: Folder to save PDF reports (default: "reports")
            
        Returns:
            Path to generated PDF file
        """
        print(f"🎯 Starting PDF generation from: {output_folder}")
        
        # Find and order files
        files_map = self._find_extracted_files(output_folder)
        if not files_map:
            raise ValueError(f"No extracted files found in {output_folder}")
        
        ordered_files = self._order_files(files_map)
        
        # Create reports folder if it doesn't exist
        os.makedirs(reports_folder, exist_ok=True)
        
        # Generate PDF filename if not provided
        if pdf_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Include source folder in filename for clarity
            folder_name = os.path.basename(output_folder.rstrip('/'))
            pdf_filename = f"document_ai_report_{folder_name}_{timestamp}.pdf"
        
        # Ensure .pdf extension
        if not pdf_filename.endswith('.pdf'):
            pdf_filename += '.pdf'
        
        pdf_path = os.path.join(reports_folder, pdf_filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Create styles
        styles = self._create_styles()
        
        # Build PDF content
        elements = []
        
        # Calculate summary statistics
        total_pages = 0
        total_tables = 0
        
        for base_name, file_path in ordered_files:
            content, metadata = self._read_file_content(file_path)
            total_pages += int(metadata.get('Pages', 0) or 0)
            total_tables += int(metadata.get('Tables Found', 0) or 0)
        
        # Add cover page
        cover_elements = self._create_cover_page(styles, len(ordered_files), total_pages, total_tables)
        elements.extend(cover_elements)
        
        # Add table of contents
        toc_elements = self._create_table_of_contents(ordered_files, styles)
        elements.extend(toc_elements)
        
        # Process each file
        for i, (base_name, file_path) in enumerate(ordered_files):
            print(f"📄 Processing file {i+1}/{len(ordered_files)}: {base_name}")
            
            # Create human-readable title
            display_name = base_name.replace('_', ' ').title()
            if 'finish_schedule' in base_name.lower():
                display_name = display_name.replace('Finish Schedule ', 'Finish Schedule: ')
            
            # Add document title
            title = Paragraph(f"{i+1}. {display_name}", styles['heading'])
            elements.append(title)
            elements.append(Spacer(1, 12))
            
            # Read and process content
            content, metadata = self._read_file_content(file_path)
            
            # Add metadata summary
            if metadata:
                meta_text = f"<b>Processing Details:</b> "
                meta_items = [f"{k}: {v}" for k, v in metadata.items() if k in ['Pages', 'Tables Found', 'Processor']]
                meta_text += " | ".join(meta_items)
                meta_para = Paragraph(meta_text, styles['code'])
                elements.append(meta_para)
                elements.append(Spacer(1, 12))
            
            # Process and add content
            content_elements = self._process_content_for_pdf(content, styles)
            elements.extend(content_elements)
            
            # Add page break between documents (except for last one)
            if i < len(ordered_files) - 1:
                elements.append(PageBreak())
        
        # Build PDF
        print(f"📄 Building PDF document...")
        doc.build(elements)
        
        print(f"✅ PDF generated successfully: {pdf_path}")
        print(f"📊 Report contains {len(ordered_files)} documents with {total_tables} tables from {total_pages} pages")
        
        return pdf_path


def main():
    """
    Main function to demonstrate PDF generation.
    """
    print("🎯 Document AI PDF Generator")
    print("=" * 50)
    
    # Check if reportlab is available
    if not REPORTLAB_AVAILABLE:
        print("❌ ReportLab library not found!")
        print("   Install with: pip install reportlab")
        return
    
    # Initialize PDF generator
    try:
        generator = PDFGenerator()
        
        # Look for output folders
        output_folders = []
        potential_folders = ['outputs', 'outputs/parallel', 'outputs/sequential']
        
        for folder in potential_folders:
            if os.path.exists(folder):
                files = [f for f in os.listdir(folder) if f.endswith('_extracted.txt')]
                if files:
                    output_folders.append(folder)
        
        if not output_folders:
            print("❌ No output folders with extracted files found!")
            print("   Run document processing first to generate extracted files.")
            return
        
        print(f"📁 Available output folders: {output_folders}")
        
        # Use the first available folder (or prompt user)
        output_folder = output_folders[0]
        print(f"📂 Using output folder: {output_folder}")
        
        # Generate PDF
        pdf_path = generator.generate_pdf(output_folder)
        
        print(f"\n🎉 PDF Report Generated Successfully!")
        print(f"📄 Location: {pdf_path}")
        print(f"💡 You can now view the consolidated report with all extracted data!")
        
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")


if __name__ == "__main__":
    main()
