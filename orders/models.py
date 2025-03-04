from django.db import models
from django.conf import settings
from events.models import TicketPool
from django.db.models import Sum, F
import uuid
import qrcode
import base64
from io import BytesIO

class OrderStatus:
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

    CHOICES = [
        (PENDING, 'Oczekujące'),
        (COMPLETED, 'Zakończone'),
        (CANCELLED, 'Anulowane'),
    ]

class PaymentMethod:
    TRANSFER = 'transfer'
    CARD = 'card'

    CHOICES = [
        (TRANSFER, 'Przelew'),
        (CARD, 'Karta'),
    ]

class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='orders'
    )
    email = models.EmailField(null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=OrderStatus.CHOICES, default=OrderStatus.PENDING)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.CHOICES, default=PaymentMethod.TRANSFER)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.get_status_display()}"

    def calculate_total_price(self):
        total = self.items.aggregate(
            total_price=Sum(F('quantity') * F('ticket_pool__price'))
        )['total_price']
        return total or 0

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    ticket_pool = models.ForeignKey(TicketPool, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0)

    def __str__(self):
        return f"{self.quantity} x {self.ticket_pool.name} ({self.order.id})"

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.ticket_pool.price
        super().save(*args, **kwargs)

class Ticket(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='tickets')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    ticket_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"Ticket {self.ticket_number} for {self.first_name} {self.last_name}"

    @property
    def qr_code(self):
        qr = qrcode.QRCode(version=1, box_size=2, border=2)
        qr.add_data(str(self.ticket_number))
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return qr_base64
