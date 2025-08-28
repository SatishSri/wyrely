#!/usr/bin/env python3
"""
Generate PDF from Technical Architect Analysis document.
Creates a professional PDF report showcasing the complete technical journey.
"""

import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import re

class TechnicalArchitectPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom styles for the technical document."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#1f4e79'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=HexColor('#2e75b6'),
            fontName='Helvetica-Bold'
        ))
        
        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=15,
            textColor=HexColor('#4472c4'),
            fontName='Helvetica-Bold'
        ))
        
        # Code block style
        self.styles.add(ParagraphStyle(
            name='CodeBlock',
            parent=self.styles['Code'],
            fontSize=9,
            fontName='Courier',
            leftIndent=20,
            rightIndent=20,
            spaceAfter=10,
            spaceBefore=10,
            backColor=HexColor('#f8f9fa'),
            borderColor=HexColor('#dee2e6'),
            borderWidth=1,
            borderPadding=8
        ))
        
        # Highlight box style
        self.styles.add(ParagraphStyle(
            name='HighlightBox',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=15,
            rightIndent=15,
            spaceAfter=10,
            spaceBefore=10,
            backColor=HexColor('#e8f4fd'),
            borderColor=HexColor('#2e75b6'),
            borderWidth=1,
            borderPadding=10
        ))
        
        # Quote style
        self.styles.add(ParagraphStyle(
            name='Quote',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=30,
            rightIndent=30,
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Oblique',
            textColor=HexColor('#666666')
        ))

    def _clean_markdown_text(self, text):
        """Clean markdown formatting for PDF display."""
        # Remove markdown headers but keep the text
        text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
        
        # Convert **bold** to <b>bold</b>
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        
        # Convert *italic* to <i>italic</i>
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        
        # Convert `code` to monospace
        text = re.sub(r'`(.*?)`', r'<font name="Courier">\1</font>', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        return text

    def _parse_markdown_content(self, content):
        """Parse markdown content and return structured elements."""
        elements = []
        lines = content.split('\n')
        current_section = []
        in_code_block = False
        code_block_lines = []
        
        for line in lines:
            # Handle code blocks
            if line.strip().startswith('```'):
                if in_code_block:
                    # End code block
                    if code_block_lines:
                        code_text = '\n'.join(code_block_lines)
                        elements.append(('code', code_text))
                    code_block_lines = []
                    in_code_block = False
                else:
                    # Start code block
                    if current_section:
                        elements.append(('text', '\n'.join(current_section)))
                        current_section = []
                    in_code_block = True
                continue
            
            if in_code_block:
                code_block_lines.append(line)
                continue
            
            # Handle headers
            if line.startswith('# '):
                if current_section:
                    elements.append(('text', '\n'.join(current_section)))
                    current_section = []
                elements.append(('title', line[2:].strip()))
            elif line.startswith('## '):
                if current_section:
                    elements.append(('text', '\n'.join(current_section)))
                    current_section = []
                elements.append(('section', line[3:].strip()))
            elif line.startswith('### '):
                if current_section:
                    elements.append(('text', '\n'.join(current_section)))
                    current_section = []
                elements.append(('subsection', line[4:].strip()))
            else:
                current_section.append(line)
        
        # Add remaining content
        if current_section:
            elements.append(('text', '\n'.join(current_section)))
        
        return elements

    def _create_performance_table(self):
        """Create performance comparison table."""
        data = [
            ['Metric', 'Before', 'After', 'Improvement'],
            ['Processing Time', '27.71s', '4.36s', '6.36x faster'],
            ['Throughput', '43.2/hour', '275/hour', '537% increase'],
            ['CPU Utilization', '15%', '85%', '467% efficiency'],
            ['Time per Document', '2.31s', '0.36s', '541% improvement'],
            ['Error Rate', '0%', '0%', 'Maintained'],
            ['Resource Cost', 'Fixed', 'Variable', '84% reduction']
        ]
        
        table = Table(data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e75b6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f8f9fa')])
        ]))
        
        return table

    def _create_scaling_table(self):
        """Create scaling projections table."""
        data = [
            ['Configuration', 'Throughput', 'Monthly Cost', 'ROI'],
            ['Current (Single Machine)', '275 docs/hour', '$400', 'Baseline'],
            ['Small Cluster (3 nodes)', '825 docs/hour', '$800', '200%'],
            ['Medium Cluster (10 nodes)', '2,640 docs/hour', '$1,200', '350%'],
            ['Enterprise (25+ nodes)', '6,875 docs/hour', '$2,000', '400%']
        ]
        
        table = Table(data, colWidths=[2.2*inch, 1.5*inch, 1.3*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4472c4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f8f9fa')])
        ]))
        
        return table

    def generate_pdf(self, markdown_file, output_file):
        """Generate PDF from markdown file."""
        print(f"📄 Generating Technical Architect Analysis PDF...")
        print(f"📂 Source: {markdown_file}")
        print(f"🎯 Output: {output_file}")
        
        # Read markdown content
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_file,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # Parse content
        elements = self._parse_markdown_content(content)
        
        for element_type, element_content in elements:
            if element_type == 'title':
                # Main title
                story.append(Paragraph(self._clean_markdown_text(element_content), self.styles['CustomTitle']))
                story.append(Spacer(1, 20))
                
            elif element_type == 'section':
                # Section header
                story.append(Paragraph(self._clean_markdown_text(element_content), self.styles['SectionHeader']))
                story.append(Spacer(1, 10))
                
            elif element_type == 'subsection':
                # Subsection header
                story.append(Paragraph(self._clean_markdown_text(element_content), self.styles['SubsectionHeader']))
                story.append(Spacer(1, 8))
                
            elif element_type == 'code':
                # Code block
                story.append(Paragraph(element_content, self.styles['CodeBlock']))
                story.append(Spacer(1, 10))
                
            elif element_type == 'text':
                # Regular text content
                cleaned_text = self._clean_markdown_text(element_content)
                if cleaned_text.strip():
                    # Split into paragraphs
                    paragraphs = cleaned_text.split('\n\n')
                    for para in paragraphs:
                        para = para.strip()
                        if para:
                            # Check for special formatting
                            if para.startswith('**') and para.endswith('**'):
                                # Highlight box
                                story.append(Paragraph(para[2:-2], self.styles['HighlightBox']))
                            elif para.startswith('>'):
                                # Quote
                                story.append(Paragraph(para[1:].strip(), self.styles['Quote']))
                            else:
                                # Regular paragraph
                                story.append(Paragraph(para, self.styles['Normal']))
                            story.append(Spacer(1, 6))
            
            # Add special tables at appropriate sections
            if element_type == 'text' and 'Performance Results Achieved' in element_content:
                story.append(Spacer(1, 10))
                story.append(self._create_performance_table())
                story.append(Spacer(1, 15))
                
            if element_type == 'text' and 'Scaling Projections' in element_content:
                story.append(Spacer(1, 10))
                story.append(self._create_scaling_table())
                story.append(Spacer(1, 15))
        
        # Add footer information
        story.append(PageBreak())
        story.append(Paragraph("Technical Architect Analysis - Document AI Processing Platform", self.styles['SectionHeader']))
        story.append(Spacer(1, 10))
        
        footer_info = f"""
        <b>Generated:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br/>
        <b>Repository:</b> https://github.com/SatishSri/wyrely.git<br/>
        <b>Performance Achievement:</b> 6.36x speedup with parallel processing<br/>
        <b>Enterprise Vision:</b> 50x scaling potential with distributed architecture<br/>
        <b>Business Impact:</b> 84% cost reduction, 300% ROI projection
        """
        
        story.append(Paragraph(footer_info, self.styles['HighlightBox']))
        
        # Build PDF
        doc.build(story)
        
        # Get file size
        file_size = os.path.getsize(output_file) / (1024 * 1024)
        
        print(f"✅ PDF generated successfully!")
        print(f"📄 Location: {output_file}")
        print(f"📊 File size: {file_size:.2f} MB")
        print(f"🎯 Professional technical architect analysis ready for presentation!")
        
        return output_file

def main():
    """Main function."""
    print("🏗️ Technical Architect Analysis PDF Generator")
    print("=" * 50)
    
    # Paths
    markdown_file = "docs/TECHNICAL_ARCHITECT_ANALYSIS.md"
    output_dir = "reports"
    output_file = os.path.join(output_dir, "Technical_Architect_Analysis.pdf")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if markdown file exists
    if not os.path.exists(markdown_file):
        print(f"❌ Error: Markdown file not found: {markdown_file}")
        return 1
    
    try:
        # Generate PDF
        generator = TechnicalArchitectPDFGenerator()
        pdf_path = generator.generate_pdf(markdown_file, output_file)
        
        print(f"\n🎉 Success! Technical Architect Analysis PDF created:")
        print(f"   📁 {pdf_path}")
        print(f"\n💡 This PDF showcases your complete technical journey:")
        print(f"   • Sequential → Parallel → Distributed architecture evolution")
        print(f"   • 6.36x performance improvement with detailed analysis")
        print(f"   • Enterprise scaling strategy with Docker + Celery + Kubernetes")
        print(f"   • Technology comparison (Celery vs RabbitMQ vs Kafka)")
        print(f"   • Business impact analysis with ROI projections")
        print(f"   • Professional technical architect documentation")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
