#!/usr/bin/env python3
"""
Create a standalone Celery architecture diagram PDF.
This creates a large, clear diagram perfect for presentations.
"""

import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Spacer
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus.flowables import Flowable

class LargeCeleryDiagram(Flowable):
    """Large, presentation-quality Celery architecture diagram."""
    
    def __init__(self, width=10*inch, height=7*inch):
        self.width = width
        self.height = height
    
    def wrap(self, availWidth, availHeight):
        return self.width, self.height
    
    def draw(self):
        """Draw comprehensive Celery architecture for Document AI."""
        canvas = self.canv
        
        # Title
        canvas.setFont("Helvetica-Bold", 18)
        canvas.drawString(2*inch, self.height - 0.5*inch, "Celery Architecture for Document AI Processing")
        
        # Subtitle
        canvas.setFont("Helvetica", 12)
        canvas.drawString(2*inch, self.height - 0.8*inch, "Distributed Task Queue with Auto-scaling Kubernetes Workers")
        
        # Main architecture container
        canvas.setStrokeColor(HexColor('#2e75b6'))
        canvas.setFillColor(HexColor('#f8f9fa'))
        canvas.setLineWidth(2)
        canvas.rect(0.5*inch, 0.5*inch, 9*inch, 5.5*inch, fill=1, stroke=1)
        
        # === TOP ROW: Client & API Layer ===
        
        # Web Client
        canvas.setFillColor(HexColor('#6c757d'))
        canvas.rect(1*inch, 5.2*inch, 1.5*inch, 0.6*inch, fill=1, stroke=1)
        canvas.setFillColor(white)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(1.1*inch, 5.6*inch, "Web Client")
        canvas.setFont("Helvetica", 9)
        canvas.drawString(1.1*inch, 5.4*inch, "Document Upload")
        canvas.drawString(1.1*inch, 5.25*inch, "Status Monitor")
        
        # Web API / FastAPI
        canvas.setFillColor(HexColor('#4472c4'))
        canvas.rect(3*inch, 5.2*inch, 1.8*inch, 0.6*inch, fill=1, stroke=1)
        canvas.setFillColor(white)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(3.1*inch, 5.6*inch, "Web API")
        canvas.setFont("Helvetica", 9)
        canvas.drawString(3.1*inch, 5.4*inch, "(FastAPI/Flask)")
        canvas.drawString(3.1*inch, 5.25*inch, "REST Endpoints")
        
        # Celery Producer
        canvas.setFillColor(HexColor('#2e75b6'))
        canvas.rect(5.2*inch, 5.2*inch, 1.8*inch, 0.6*inch, fill=1, stroke=1)
        canvas.setFillColor(white)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(5.3*inch, 5.6*inch, "Celery Producer")
        canvas.setFont("Helvetica", 9)
        canvas.drawString(5.3*inch, 5.4*inch, "Task Creation")
        canvas.drawString(5.3*inch, 5.25*inch, "Job Submission")
        
        # Load Balancer
        canvas.setFillColor(HexColor('#ff9800'))
        canvas.rect(7.5*inch, 5.2*inch, 1.5*inch, 0.6*inch, fill=1, stroke=1)
        canvas.setFillColor(white)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(7.6*inch, 5.6*inch, "Load Balancer")
        canvas.setFont("Helvetica", 9)
        canvas.drawString(7.6*inch, 5.4*inch, "K8s Ingress")
        canvas.drawString(7.6*inch, 5.25*inch, "Auto-scaling")
        
        # === MIDDLE ROW: Message Broker & Queue ===
        
        # Message Broker (Redis/RabbitMQ) - Highlighted
        canvas.setFillColor(HexColor('#ff9ff3'))
        canvas.setLineWidth(2)
        canvas.rect(3.5*inch, 4*inch, 2.5*inch, 0.8*inch, fill=1, stroke=1)
        canvas.setFillColor(black)
        canvas.setFont("Helvetica-Bold", 14)
        canvas.drawString(3.7*inch, 4.6*inch, "Message Broker")
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(3.7*inch, 4.4*inch, "(Redis Cluster)")
        canvas.setFont("Helvetica", 9)
        canvas.drawString(3.7*inch, 4.2*inch, "• Task Queue Management")
        canvas.drawString(3.7*inch, 4.05*inch, "• Priority Queues")
        
        # Queue Types
        queue_types = [
            ("High Priority", 1*inch, 3.5*inch, HexColor('#dc3545')),
            ("Normal Queue", 1*inch, 3*inch, HexColor('#28a745')),
            ("Batch Queue", 1*inch, 2.5*inch, HexColor('#6f42c1'))
        ]
        
        for name, x, y, color in queue_types:
            canvas.setFillColor(color)
            canvas.rect(x, y, 1.3*inch, 0.35*inch, fill=1, stroke=1)
            canvas.setFillColor(white)
            canvas.setFont("Helvetica", 9)
            canvas.drawString(x + 0.1*inch, y + 0.15*inch, name)
        
        # === WORKER ROW: Kubernetes Pods ===
        
        # Kubernetes cluster indicator
        canvas.setStrokeColor(HexColor('#326ce5'))
        canvas.setFillColor(HexColor('#e3f2fd'))
        canvas.setLineWidth(2)
        canvas.rect(0.8*inch, 1.5*inch, 8.4*inch, 1.3*inch, fill=1, stroke=1)
        canvas.setFillColor(black)
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(0.9*inch, 2.6*inch, "Kubernetes Cluster - Auto-scaling Worker Pods")
        
        # Worker Pods
        worker_positions = [
            (1.2*inch, 1.8*inch), (2.8*inch, 1.8*inch), 
            (4.4*inch, 1.8*inch), (6*inch, 1.8*inch), (7.6*inch, 1.8*inch)
        ]
        
        for i, (x, y) in enumerate(worker_positions):
            # Worker pod container
            canvas.setFillColor(HexColor('#54a0ff'))
            canvas.rect(x, y, 1.2*inch, 0.6*inch, fill=1, stroke=1)
            canvas.setFillColor(white)
            canvas.setFont("Helvetica-Bold", 9)
            canvas.drawString(x + 0.05*inch, y + 0.45*inch, f"Worker Pod {i+1}")
            canvas.setFont("Helvetica", 8)
            canvas.drawString(x + 0.05*inch, y + 0.3*inch, "Celery Worker")
            canvas.drawString(x + 0.05*inch, y + 0.15*inch, "Document AI SDK")
            canvas.drawString(x + 0.05*inch, y + 0.02*inch, "Auto-restart")
        
        # === BOTTOM ROW: External Services & Storage ===
        
        # Google Document AI API
        canvas.setFillColor(HexColor('#feca57'))
        canvas.rect(1.5*inch, 0.8*inch, 2.5*inch, 0.5*inch, fill=1, stroke=1)
        canvas.setFillColor(black)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(1.6*inch, 1.15*inch, "Google Document AI API")
        canvas.setFont("Helvetica", 9)
        canvas.drawString(1.6*inch, 0.95*inch, "Shared External Service")
        
        # Result Backend
        canvas.setFillColor(HexColor('#54a0ff'))
        canvas.rect(4.5*inch, 0.8*inch, 2*inch, 0.5*inch, fill=1, stroke=1)
        canvas.setFillColor(white)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(4.6*inch, 1.15*inch, "Result Backend")
        canvas.setFont("Helvetica", 9)
        canvas.drawString(4.6*inch, 0.95*inch, "(Redis/PostgreSQL)")
        
        # Monitoring & Management
        canvas.setFillColor(HexColor('#00d2d3'))
        canvas.rect(7*inch, 0.8*inch, 1.8*inch, 0.5*inch, fill=1, stroke=1)
        canvas.setFillColor(white)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(7.1*inch, 1.15*inch, "Celery Flower")
        canvas.setFont("Helvetica", 9)
        canvas.drawString(7.1*inch, 0.95*inch, "Monitoring UI")
        
        # === ARROWS AND CONNECTIONS ===
        canvas.setStrokeColor(black)
        canvas.setLineWidth(2)
        
        # Client to API
        canvas.line(2.5*inch, 5.5*inch, 3*inch, 5.5*inch)
        
        # API to Producer
        canvas.line(4.8*inch, 5.5*inch, 5.2*inch, 5.5*inch)
        
        # Producer to Message Broker
        canvas.line(6*inch, 5.2*inch, 5*inch, 4.8*inch)
        
        # Message Broker to Workers
        for x, y in worker_positions:
            canvas.line(5*inch, 4*inch, x + 0.6*inch, y + 0.6*inch)
        
        # Queue types to Message Broker
        for _, x, y, _ in queue_types:
            canvas.line(x + 1.3*inch, y + 0.175*inch, 3.5*inch, 4.4*inch)
        
        # Workers to Document AI
        for x, y in worker_positions:
            canvas.line(x + 0.6*inch, y, 2.75*inch, 1.3*inch)
        
        # Workers to Result Backend
        for x, y in worker_positions:
            canvas.line(x + 0.6*inch, y, 5.5*inch, 1.3*inch)
        
        # Performance metrics box
        canvas.setFillColor(HexColor('#28a745'))
        canvas.rect(0.5*inch, 6.2*inch, 2*inch, 0.6*inch, fill=1, stroke=1)
        canvas.setFillColor(white)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(0.6*inch, 6.6*inch, "Performance Targets")
        canvas.setFont("Helvetica", 9)
        canvas.drawString(0.6*inch, 6.4*inch, "• 1,000+ docs/hour")
        canvas.drawString(0.6*inch, 6.25*inch, "• Auto-scale 1-50 pods")
        
        # Scaling info box
        canvas.setFillColor(HexColor('#6f42c1'))
        canvas.rect(7.5*inch, 6.2*inch, 2*inch, 0.6*inch, fill=1, stroke=1)
        canvas.setFillColor(white)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(7.6*inch, 6.6*inch, "Auto-scaling Logic")
        canvas.setFont("Helvetica", 9)
        canvas.drawString(7.6*inch, 6.4*inch, "• Queue length > 100")
        canvas.drawString(7.6*inch, 6.25*inch, "• CPU usage > 70%")

def main():
    """Generate large Celery architecture diagram."""
    print("🎯 Creating Large Celery Architecture Diagram")
    print("=" * 45)
    
    output_dir = "reports"
    output_file = os.path.join(output_dir, "Celery_Architecture_Diagram.pdf")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Use landscape orientation for better diagram layout
    doc = SimpleDocTemplate(
        output_file,
        pagesize=landscape(A4),
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    story = []
    
    # Add the large diagram
    story.append(LargeCeleryDiagram(width=10.5*inch, height=7*inch))
    story.append(Spacer(1, 0.5*inch))
    
    # Build PDF
    doc.build(story)
    
    # Get file size
    file_size = os.path.getsize(output_file) / (1024 * 1024)
    
    print(f"✅ Celery Architecture Diagram created!")
    print(f"📄 Location: {output_file}")
    print(f"📊 File size: {file_size:.2f} MB")
    print(f"🎯 Perfect for technical presentations and architecture reviews!")
    print(f"\n💡 This diagram shows:")
    print(f"   • Complete Celery task queue architecture")
    print(f"   • Kubernetes auto-scaling worker pods")
    print(f"   • Message broker with priority queues")
    print(f"   • Integration with Google Document AI")
    print(f"   • Monitoring and result storage systems")
    print(f"   • Performance targets and scaling logic")
    
    return output_file

if __name__ == "__main__":
    main()
