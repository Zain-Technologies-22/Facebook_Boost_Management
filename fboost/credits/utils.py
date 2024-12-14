# credits/utils.py

from reportlab.pdfgen import canvas
from io import BytesIO
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

def generate_invoice_pdf(transaction):
    """
    Generates a PDF invoice for the given billing transaction.
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    
    # Basic PDF layout; customize as needed
    p.setFont("Helvetica-Bold", 20)
    p.drawString(100, 800, "Invoice")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, 770, f"Transaction ID: {transaction.transaction_id}")
    p.drawString(100, 750, f"Date: {transaction.timestamp.strftime('%Y-%m-%d')}")
    p.drawString(100, 730, f"User: {transaction.user.username} ({transaction.user.email})")
    p.drawString(100, 710, f"Description: {transaction.description}")
    p.drawString(100, 690, f"Amount: ৳{transaction.amount}")
    p.drawString(100, 670, f"Payment Method: {transaction.get_payment_method_display()}")
    p.drawString(100, 650, f"Status: {transaction.get_status_display()}")
    
    # Additional details or branding can be added here
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer

def upload_invoice(transaction, pdf_buffer):
    """
    Saves the generated invoice PDF to the media storage and returns its URL.
    """
    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'invoices'))
    invoice_directory = 'invoices/'
    filename = f"invoices/invoice_{transaction.transaction_id}.pdf"
    
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'invoices')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'invoices'), exist_ok=True)
    
    fs.save(filename, pdf_buffer)
    return fs.url(filename)