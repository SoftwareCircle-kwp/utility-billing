import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, inch
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.frames import Frame
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, PageTemplate
from functools import partial
from PyPDF2 import PdfFileMerger
import tempfile



class InvoiceGenerator:
    def __init__(self, billings_df, bpsd, bped, logo_file, property_dataframe, name):
        self.name = name
        self.df = billings_df
        self.billing_period_start_date = bpsd
        self.billing_period_end_date = bped
        self.property_df = property_dataframe
        self.groups = self.df.groupby('Resident')
        self.logo = Image(logo_file, width=0.5*inch, height=0.5*inch, kind='direct', hAlign='LEFT')


    def generate_invoices(self):
        # Create a new PDF document for all invoices
        filename = self.name
        doc = SimpleDocTemplate(filename, pagesize=letter, logo=self.logo)

        # Define the styles for the document
        styles = getSampleStyleSheet()
        if 'Justify' not in styles:
            styles.add(ParagraphStyle(name='Justify', alignment=TA_LEFT, fontSize=10, leading=12))
        if 'Centered' not in styles:
            styles.add(ParagraphStyle(name='Centered', alignment=TA_CENTER, fontSize=10, leading=12))
        if 'Header' not in styles:
            styles.add(ParagraphStyle(name='Header', alignment=TA_CENTER, fontSize=16, leading=16))
        if 'CustomTitle' not in styles:
            styles.add(ParagraphStyle(name='CustomTitle', alignment=TA_LEFT, fontSize=14, leading=14))
        if 'CustomLogoTitle' not in styles:
            styles.add(ParagraphStyle(name='CustomLogoTitle', alignment=TA_LEFT, fontSize=14, leading=16))

    
        # Define the content of the document
        content = []
        for index, group in self.groups:
            # Add the logo to the document
            content.append(self.logo)
            content.append(Spacer(1, 0.3*inch))
            #Add the logo text
            logo_text = "Utility Allocation Services" 
            logo = Paragraph(logo_text, styles["CustomLogoTitle"])
            content.append(logo)  
            content.append(Spacer(1, 0.4*inch))
            # Add the company name and tenant name to the document
            header_text = "Invoice for Utility Services"
            header = Paragraph(header_text, styles["Header"])
            content.append(header)
            content.append(Spacer(1, 0.2*inch))

            bp_sd=self.billing_period_start_date.strftime('%m/%d/%Y')
            bp_ed=self.billing_period_end_date.strftime('%m/%d/%Y')
            bp_text = f"Billing Period:         {str(bp_sd)} to {str(bp_ed)}"
            bp = Paragraph(bp_text, styles["Justify"])
            content.append(bp)
            content.append(Spacer(1, 0.2*inch))

            resident_text = f"Resident:         {str(group['Resident'].iloc[0])}        {str(group['Name'].iloc[0])}"
            resident = Paragraph(resident_text, styles["Justify"])
            content.append(resident)
            content.append(Spacer(1, 0.2*inch))


            # Add the property information to the document
            unit_text = f"Unit: {group['Unit'].iloc[0]}"
            unit = Paragraph(unit_text, styles["Justify"])
            content.append(unit)
            property_text = f"Property: {self.property_df['property_name'].iloc[0]}"
            property_info = Paragraph(property_text, styles["Justify"])
            content.append(property_info)
            address_text = f"Address: {self.property_df['address1'].iloc[0]} apt: {group['Unit'].iloc[0]}"
            address = Paragraph(address_text, styles["Justify"])
            content.append(address)
            city_state_zip_text = f"{self.property_df['city'].iloc[0]} {self.property_df['state'].iloc[0]} {self.property_df['zip'].iloc[0]}"
            city_state_zip = Paragraph(city_state_zip_text, styles["Justify"])
            content.append(city_state_zip)
            content.append(Spacer(1, 0.2*inch))

            # Add the billing information to the document
            data = []
            for _, row in group.iterrows():
                code_text = f"{row['code']}"
                notes_text = f"{row['gl_notes']}"
                gl_code_text = f"" #"{row['gl_code']}"
                amount_text = f"${round(row['amount'], 2):.2f}"
                data.append([code_text,  notes_text, gl_code_text, amount_text])
            table = Table(data)
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('LEFTPADDING', (0, 0), (-1, -1), 2),
                ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
            ]))
            content.append(table)
            content.append(Spacer(1, 0.3*inch))

            # Add the total due to the document
            total_due_text = f"Total Due: ${round(group['amount'].sum(), 2):.2f}"
            total_due = Paragraph(total_due_text, styles["Justify"])
            content.append(total_due)
            content.append(Spacer(1, 0.2*inch))
            # due date
            date_due_text = f"Due Date: {str(group['bill_due_date'].iloc[0].strftime('%m/%d/%Y'))}"
            date_due = Paragraph(date_due_text, styles["Justify"])
            content.append(date_due)
            content.append(Spacer(1, 0.2*inch))

            footer1_text = f"Please submit payment to: {self.property_df['property_name'].iloc[0]}, {self.property_df['city'].iloc[0]}, {self.property_df['state'].iloc[0]} {self.property_df['zip'].iloc[0]}"
            footer1 = Paragraph(footer1_text, styles["Justify"])
            content.append(footer1)
            content.append(Spacer(1, 0.5*inch))
            footer2_text = "*This account statement is generated by Utility Allocation Services. Some charges appearing on this"+\
                " statement may be allocated from master property bills from the respective utility provider(s). This bill is not"+\
                " from City of "+self.property_df['city'].iloc[0]+". Charges are billed to residents based upon their lease agreements. For details on"+\
                " rate calculations, refer to your resident portal or contact the property's management staff. Property"+\
                " Charges reflect data in the resident ledger as of the date bills were printed and mailed. Please contact"+\
                " your leasing office at "+self.property_df['phone'].iloc[0]+" or via email at "+self.property_df['email'].iloc[0]+" for billing inquires or disputes."
            
            footer2 = Paragraph(footer2_text, styles["Normal"])
            content.append(footer2)
            
            content.append(PageBreak())

        # Build the document and save it
        doc.build(content)

