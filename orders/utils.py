import qrcode
import base64
from io import BytesIO
from django.template.loader import render_to_string
from xhtml2pdf import pisa

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()

def render_pdf(html_content):
    result = BytesIO()
    pisa.CreatePDF(BytesIO(html_content.encode('utf-8')), dest=result)
    return result.getvalue()

def generate_tickets_pdf(order):
    tickets = []
    for item in order.items.all():
        for t in item.tickets.all():
            qr_data = str(t.ticket_number)
            qr_image = generate_qr_code(qr_data)
            qr_base64 = base64.b64encode(qr_image).decode('utf-8')
            tickets.append({
                'ticket': t,
                'qr_code': qr_base64,
                'event': t.order_item.ticket_pool.event
            })
    html = render_to_string('orders/tickets/ticket_pdf_template.html', {'tickets': tickets})
    return render_pdf(html)

def generate_invoice_pdf(order):
    total_price = 0.0
    for item in order.items.all():
        total_price += float(item.price) * item.quantity
    vat_amount = total_price * 0.23
    net_price = total_price - vat_amount

    context = {
        'order': order,
        'total_price': total_price,
        'vat_amount': vat_amount,
        'net_price': net_price,
    }

    html = render_to_string('orders/tickets/invoice_pdf_template.html', context)

    return render_pdf(html)
