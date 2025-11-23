from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import io
import pandas as pd

class PDFGenerator:
    def __init__(self):
        # Register Japanese font
        try:
            pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
            self.font_name = 'HeiseiKakuGo-W5'
        except Exception:
            # Fallback if Japanese font is not available (though it should be with reportlab)
            self.font_name = 'Helvetica'

    def generate_report(self, df, insights_data):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Custom Styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontName=self.font_name,
            fontSize=24,
            spaceAfter=20
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=self.font_name,
            fontSize=16,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.blue
        )
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName=self.font_name,
            fontSize=10,
            leading=14
        )

        # 1. Title
        elements.append(Paragraph("AI Business Insight Report", title_style))
        elements.append(Spacer(1, 10))
        
        date_range = f"{df['注文日時'].min().date()} ~ {df['注文日時'].max().date()}"
        elements.append(Paragraph(f"分析期間: {date_range}", normal_style))
        elements.append(Spacer(1, 20))

        # 2. Sales Summary Table
        elements.append(Paragraph("売上サマリー", heading_style))
        
        total_sales = int((df['数量'] * df['単価（税込）']).sum())
        total_customers = df['注文番号'].nunique()
        avg_customer_spend = int(total_sales / total_customers) if total_customers else 0
        
        data = [
            ['項目', '値'],
            ['総売上', f"¥{total_sales:,}"],
            ['総客数', f"{total_customers:,} 人"],
            ['客単価', f"¥{avg_customer_spend:,}"]
        ]
        
        table = Table(data, colWidths=[200, 200])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

        # 3. AI Insights
        if insights_data and 'insights' in insights_data:
            elements.append(Paragraph("AI インサイト (気づき)", heading_style))
            for insight in insights_data['insights']:
                elements.append(Paragraph(f"• {insight}", normal_style))
                elements.append(Spacer(1, 5))
        
        elements.append(Spacer(1, 10))

        # 4. Recommended Actions
        if insights_data and 'actions' in insights_data:
            elements.append(Paragraph("推奨アクション", heading_style))
            for action in insights_data['actions']:
                elements.append(Paragraph(f"-> {action}", normal_style))
                elements.append(Spacer(1, 5))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
