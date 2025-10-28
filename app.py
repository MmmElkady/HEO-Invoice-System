from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import io
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///invoices.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(200), nullable=False)
    client_address = db.Column(db.String(500), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_item = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    invoice_type = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Invoice {self.id}>'

# Create database tables
with app.app_context():
    db.create_all()

# Register Arabic-capable fonts
pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))

# Helper function to process Arabic text for PDF
def process_arabic_text(text):
    reshaped_text = reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

# PDF Generation Function
def generate_pdf(invoice):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Title with both English and Arabic - Use DejaVu for potential Arabic content
    c.setFont("DejaVuSans-Bold", 24)
    processed_invoice_type = process_arabic_text(invoice.invoice_type) if invoice.invoice_type else invoice.invoice_type
    c.drawString(1 * inch, height - 1 * inch, f"{processed_invoice_type} Invoice")
    
    # Invoice Details
    c.setFont("DejaVuSans-Bold", 12)
    c.drawString(1 * inch, height - 1.5 * inch, f"Invoice #: {invoice.id}")
    c.drawString(1 * inch, height - 1.8 * inch, f"Date: {invoice.date_created.strftime('%Y-%m-%d %H:%M')}")
    
    # Client Information (Bilingual) - Process all user input
    c.setFont("DejaVuSans-Bold", 14)
    c.drawString(1 * inch, height - 2.5 * inch, f"Client Information / {process_arabic_text('معلومات العميل')}")
    c.setFont("DejaVuSans", 12)
    processed_client_name = process_arabic_text(invoice.client_name)
    c.drawString(1 * inch, height - 2.8 * inch, f"Name / {process_arabic_text('الاسم')}: {processed_client_name}")
    processed_client_address = process_arabic_text(invoice.client_address)
    c.drawString(1 * inch, height - 3.1 * inch, f"Address / {process_arabic_text('العنوان')}: {processed_client_address}")
    
    # Invoice Items Header
    c.setFont("DejaVuSans-Bold", 14)
    c.drawString(1 * inch, height - 4 * inch, f"Invoice Items / {process_arabic_text('بنود الفاتورة')}:")
    
    # Table Header (Bilingual)
    c.setFont("DejaVuSans-Bold", 11)
    y_position = height - 4.4 * inch
    c.drawString(1 * inch, y_position, f"Item / {process_arabic_text('المنتج')}")
    c.drawString(3 * inch, y_position, f"Qty / {process_arabic_text('الكمية')}")
    c.drawString(4 * inch, y_position, f"Price / {process_arabic_text('السعر')}")
    c.drawString(5 * inch, y_position, f"Total / {process_arabic_text('المجموع')}")
    
    # Table Line
    c.line(1 * inch, y_position - 5, 6.5 * inch, y_position - 5)
    
    # Table Data - Process item name for Arabic support
    c.setFont("DejaVuSans", 11)
    y_position -= 0.3 * inch
    processed_item_name = process_arabic_text(invoice.item_name)
    c.drawString(1 * inch, y_position, processed_item_name)
    c.drawString(3 * inch, y_position, str(invoice.quantity))
    c.drawString(4 * inch, y_position, f"${invoice.price_per_item:.2f}")
    c.drawString(5 * inch, y_position, f"${invoice.total:.2f}")
    
    # Total
    c.line(1 * inch, y_position - 5, 6.5 * inch, y_position - 5)
    c.setFont("DejaVuSans-Bold", 12)
    y_position -= 0.4 * inch
    c.drawString(4 * inch, y_position, f"Grand Total / {process_arabic_text('المجموع الكلي')}:")
    c.drawString(5.5 * inch, y_position, f"${invoice.total:.2f}")
    
    # Thank You Note in English and Arabic
    c.setFont("DejaVuSans", 11)
    y_position -= 1 * inch
    c.drawString(1 * inch, y_position, "Thank you for your business!")
    
    arabic_thanks = "شكراً لتعاملكم معنا"
    processed_arabic = process_arabic_text(arabic_thanks)
    c.setFont("DejaVuSans", 11)
    c.drawString(1 * inch, y_position - 0.3 * inch, processed_arabic)
    
    # Footer
    c.setFont("Helvetica", 9)
    c.drawString(1 * inch, 0.5 * inch, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    c.save()
    buffer.seek(0)
    return buffer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['POST'])
def create_invoice():
    client_name = request.form['client_name']
    client_address = request.form['client_address']
    item_name = request.form['item_name']
    quantity = int(request.form['quantity'])
    price_per_item = float(request.form['price_per_item'])
    invoice_type = request.form['invoice_type']
    
    # Calculate total
    total = quantity * price_per_item
    
    # Create invoice
    invoice = Invoice(
        client_name=client_name,
        client_address=client_address,
        item_name=item_name,
        quantity=quantity,
        price_per_item=price_per_item,
        total=total,
        invoice_type=invoice_type
    )
    
    db.session.add(invoice)
    db.session.commit()
    
    return redirect(url_for('list_invoices'))

@app.route('/invoices')
def list_invoices():
    invoices = Invoice.query.order_by(Invoice.date_created.desc()).all()
    return render_template('list.html', invoices=invoices)

@app.route('/download/<int:invoice_id>')
def download_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    pdf_buffer = generate_pdf(invoice)
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f'invoice_{invoice.id}_{invoice.invoice_type}.pdf',
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
