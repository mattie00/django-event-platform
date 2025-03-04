from django.db.models import Sum
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.signals import user_logged_in
from django.contrib import messages
from django.dispatch import receiver
from django.forms import formset_factory
from authentication.models import AppUser
from events.models import TicketPool
from .forms import TicketForm
from .models import OrderItem, Ticket, PaymentMethod, Order, OrderStatus
from django.conf import settings
from django.urls import reverse
from django.core.mail import EmailMessage
from .utils import generate_tickets_pdf, generate_invoice_pdf
import os

def add_to_cart(request):
    if request.method == "POST":
        ticket_pool_id = request.POST.get('ticket_pool')
        requested_quantity = int(request.POST.get('quantity', '1') or 1)

        ticket_pool = get_object_or_404(TicketPool, id=ticket_pool_id)

        if ticket_pool.is_promo_active and ticket_pool.remaining_tickets() <= 0:
            messages.info(request,
                          f"Bilety promocyjne dla puli '{ticket_pool.name}' są wyprzedane.",
                          extra_tags="add_to_cart error")
            return redirect('events:detail', event_id=ticket_pool.event.id)

        if ticket_pool.is_sales_pending():
            messages.info(request,
                          "Sprzedaż biletów dla tej puli jeszcze się nie rozpoczęła.",
                          extra_tags="add_to_cart error")
            return redirect('events:detail', event_id=ticket_pool.event.id)

        if ticket_pool.is_sales_ended():
            messages.info(request,
                          "Sprzedaż biletów dla tej puli została zakończona.",
                          extra_tags="add_to_cart error")
            return redirect('events:detail', event_id=ticket_pool.event.id)

        if not ticket_pool.is_independent:
            previous_pools = ticket_pool.event.ticket_pools.filter(order__lt=ticket_pool.order).order_by('order')
            if not all(pool.is_sold_out() for pool in previous_pools):
                messages.info(
                    request,
                    "Biletów z tej puli nie można jeszcze kupić. Najpierw muszą zostać wyprzedane bilety z wcześniejszych pul.",
                    extra_tags="add_to_cart error")
                return redirect('events:detail', event_id=ticket_pool.event.id)

        available = ticket_pool.remaining_tickets()
        if requested_quantity > available:
            messages.info(request,
                          f"Dostępnych jest tylko {available} biletów. Dodano maksymalną dostępną ilość.",
                          extra_tags="add_to_cart warning")
            requested_quantity = available

        if request.user.is_authenticated:
            order, _ = Order.objects.get_or_create(user=request.user, status=OrderStatus.PENDING)
            existing_quantity = order.items.filter(ticket_pool=ticket_pool).aggregate(
                total=Sum('quantity'))['total'] or 0
            if existing_quantity + requested_quantity > ticket_pool.max_tickets_per_user:
                messages.info(
                    request,
                    f"Możesz kupić maksymalnie {ticket_pool.max_tickets_per_user} biletów dla tej puli.",
                    extra_tags="add_to_cart error")
                return redirect('events:detail', event_id=ticket_pool.event.id)
        else:
            cart = request.session.get('cart', [])
            existing_quantity = sum(item['quantity'] for item in cart if item['ticket_pool_id'] == ticket_pool.id)
            if existing_quantity + requested_quantity > ticket_pool.max_tickets_per_user:
                messages.info(
                    request,
                    f"Możesz kupić maksymalnie {ticket_pool.max_tickets_per_user} biletów dla tej puli.",
                    extra_tags="add_to_cart error")
                return redirect('events:detail', event_id=ticket_pool.event.id)

        if request.user.is_authenticated:
            order, _ = Order.objects.get_or_create(user=request.user, status='pending')
            item, created = OrderItem.objects.get_or_create(
                order=order,
                ticket_pool=ticket_pool,
                defaults={'quantity': requested_quantity, 'price': ticket_pool.current_price()}
            )
            if not created:
                item.quantity += requested_quantity
                item.price = ticket_pool.current_price()
                item.save()
        else:
            cart = request.session.get('cart', [])
            for it in cart:
                if it['ticket_pool_id'] == ticket_pool.id:
                    it['quantity'] += requested_quantity
                    break
            else:
                cart.append({'ticket_pool_id': ticket_pool.id, 'quantity': requested_quantity})
            request.session['cart'] = cart

        messages.info(request,
                      "Dodano do koszyka.",
                      extra_tags="add_to_cart success")
        return redirect('events:detail', event_id=ticket_pool.event.id)

    messages.error(request, "Nieprawidłowe żądanie.")
    return redirect('home')

def cart_view(request):
    cart_items = []
    total_price = 0

    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, status=OrderStatus.PENDING).first()
        if order:
            cart_items = order.items.all()
            valid_items = []
            for item in cart_items:
                try:
                    if item.ticket_pool is None:
                        item.delete()
                        messages.info(request,
                                      "Jeden z przedmiotów w Twoim koszyku był już niedostępny i został usunięty.",
                                      extra_tags="cart_view warning")
                        continue
                except TicketPool.DoesNotExist:
                    item.delete()
                    messages.info(request,
                                  "Jeden z przedmiotów w Twoim koszyku był już niedostępny i został usunięty.",
                                  extra_tags="cart_view warning")
                    continue

                current_price = item.ticket_pool.current_price()
                if item.price != current_price:
                    item.price = current_price
                    item.save()
                valid_items.append(item)

            cart_items = valid_items
            total_price = (sum(item.quantity * item.price for item in cart_items))

    else:
        cart = request.session.get('cart', [])
        new_cart = []
        for item in cart:
            try:
                ticket_pool = TicketPool.objects.get(id=item['ticket_pool_id'])
                current_price = ticket_pool.current_price()
                if item.get('price') != float(current_price):
                    item['price'] = float(current_price)
            except TicketPool.DoesNotExist:
                messages.info(request,
                              "Jeden z przedmiotów w Twoim koszyku jest już niedostępny i został usunięty.",
                              extra_tags="cart_view warning")
                continue

            new_cart.append(item)
            cart_items.append({
                'ticket_pool': ticket_pool,
                'quantity': item['quantity'],
                'total_price': item['quantity'] * float(ticket_pool.current_price()),  # Konwersja na float
            })
            total_price += item['quantity'] * float(ticket_pool.current_price())

        request.session['cart'] = new_cart

    return render(request, 'orders/cart.html', {'cart_items': cart_items, 'total_price': total_price})

def remove_from_cart(request, ticket_pool_id):
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, status='pending').first()
        if order:
            order.items.filter(ticket_pool_id=ticket_pool_id).delete()
    else:
        cart = request.session.get('cart', [])
        cart = [item for item in cart if item['ticket_pool_id'] != int(ticket_pool_id)]
        request.session['cart'] = cart

    messages.info(request,
                  "Przedmiot usunięty z koszyka.",
                  extra_tags="remove_from_cart success")
    return redirect('orders:cart')


@csrf_exempt
def checkout_view(request):
    order = None
    cart = []
    cart_items = []
    total_price = 0
    total_tickets = 0

    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, status='PENDING').first()
        if order:
            cart_items = order.items.all()
            for item in cart_items:
                current_price = item.ticket_pool.current_price()
                if item.price != current_price:
                    item.price = current_price
                    item.save()
                    messages.info(
                        request,
                        f"Cena biletu w puli '{item.ticket_pool.name}' została zaktualizowana na {current_price} zł.",
                        extra_tags="checkout info")
            total_price = sum(item.quantity * item.price for item in cart_items)
            total_tickets = sum(item.quantity for item in cart_items)
    else:
        cart = request.session.get('cart', [])
        cart_items = []
        total_price = 0
        total_tickets = 0
        for cart_item in cart:
            ticket_pool = get_object_or_404(TicketPool, id=cart_item['ticket_pool_id'])
            current_price = ticket_pool.current_price()
            if cart_item.get('price') != current_price:
                cart_item['price'] = current_price
                messages.info(
                    request,
                    f"Cena biletu w puli '{ticket_pool.name}' została zaktualizowana na {current_price} zł.",
                    extra_tags="checkout info")
            cart_items.append({
                'ticket_pool': ticket_pool,
                'quantity': cart_item['quantity'],
                'total_price': cart_item['quantity'] * ticket_pool.current_price(),
            })
            total_price += cart_item['quantity'] * ticket_pool.current_price()
            total_tickets += cart_item['quantity']

        request.session['cart'] = cart

    ticket_form_set = formset_factory(TicketForm, extra=total_tickets if total_tickets > 0 else 0)
    formset = ticket_form_set(prefix='tickets')

    if request.method == "POST":
        payment_method = request.POST.get('payment_method')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone')

        formset = ticket_form_set(request.POST, prefix='tickets')

        if payment_method not in [PaymentMethod.TRANSFER, PaymentMethod.CARD]:
            messages.info(request,
                          "Wybierz metodę płatności.",
                          extra_tags="checkout error")
            return redirect('orders:checkout')

        if request.user.is_authenticated:
            if not order:
                messages.info(request,
                              "Brak aktywnego zamówienia.",
                              extra_tags="checkout error")
                return redirect('orders:cart')
            for item in order.items.all():
                available = item.ticket_pool.remaining_tickets()
                if item.quantity > available:
                    messages.info(
                        request,
                        f"Zbyt wiele biletów w puli '{item.ticket_pool.name}'. Dostępne jest tylko {available} sztuk.",
                        extra_tags="checkout error")
                    return redirect('orders:cart')
        else:
            if email and AppUser.objects.filter(email=email).exists():
                messages.info(request,
                              "Ten adres e-mail jest już używany przez zarejestrowanego użytkownika. Zaloguj się lub użyj innego adresu.",
                              extra_tags="checkout error")
                return redirect('orders:checkout')

            if not cart:
                messages.info(request,
                              "Twój koszyk jest pusty.",
                              extra_tags="checkout error")
                return redirect('orders:cart')
            for cart_item in cart:
                ticket_pool = get_object_or_404(TicketPool, id=cart_item['ticket_pool_id'])
                available = ticket_pool.remaining_tickets()
                if cart_item['quantity'] > available:
                    messages.info(
                        request,
                        f"Zbyt wiele biletów w puli '{ticket_pool.name}'. Dostępne jest tylko {available} sztuk.",
                        extra_tags="checkout error")
                    return redirect('orders:cart')

        if total_tickets > 0 and not formset.is_valid():
            messages.info(request,
                          "Proszę poprawnie uzupełnić dane dla wszystkich biletów.",
                          extra_tags="checkout error")
            return render(request, 'orders/checkout.html', {
                'user': request.user if request.user.is_authenticated else None,
                'cart_items': cart_items,
                'total_price': total_price,
                'total_tickets': total_tickets,
                'formset': formset,
            })

        if request.user.is_authenticated:
            order.payment_method = payment_method
            if email: order.email = email
            if first_name: order.first_name = first_name
            if last_name: order.last_name = last_name
            if phone_number: order.phone_number = phone_number
            order.save()
        else:
            order = Order.objects.create(
                session_id=request.session.session_key,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                status=OrderStatus.PENDING,
                payment_method=payment_method
            )
            for cart_item in cart:
                ticket_pool = get_object_or_404(TicketPool, id=cart_item['ticket_pool_id'])
                OrderItem.objects.create(
                    order=order,
                    ticket_pool=ticket_pool,
                    quantity=cart_item['quantity'],
                    price=ticket_pool.current_price()
                )

        all_order_items = list(order.items.all())
        form_index = 0
        for item in all_order_items:
            for i in range(item.quantity):
                f = formset.forms[form_index]
                Ticket.objects.create(
                    order_item=item,
                    first_name=f.cleaned_data['first_name'],
                    last_name=f.cleaned_data['last_name']
                )
                form_index += 1

        request.session['order_id'] = order.id
        send_payment_link(order, request)
        messages.info(request,
                      "Link do płatności został wysłany na Twój adres e-mail.",
                      extra_tags="checkout success")
        return redirect('orders:simulate_payment', order_id=order.id)

    tickets_with_forms = []
    form_index = 0
    for item in cart_items:
        if request.user.is_authenticated:
            event_name = f"{item.ticket_pool.event.name} ({item.ticket_pool.name})"
            quantity = item.quantity
        else:
            event_name = f"{item['ticket_pool'].event.name} ({item['ticket_pool'].name})"
            quantity = item['quantity']

        for _ in range(quantity):
            tickets_with_forms.append({
                'form': formset.forms[form_index],
                'event_name': event_name,
            })
            form_index += 1

    context = {
        'user': request.user if request.user.is_authenticated else None,
        'cart_items': cart_items,
        'total_price': total_price,
        'total_tickets': total_tickets,
        'tickets_with_forms': tickets_with_forms,
        'formset': formset,
    }
    return render(request, 'orders/checkout.html', context)

@receiver(user_logged_in)
def sync_cart_after_login(request, user, **kwargs):
    session_cart = request.session.get('cart', [])
    if not session_cart:
        return

    order, created = Order.objects.get_or_create(user=user, status=OrderStatus.PENDING)

    for item in session_cart:
        ticket_pool_id = item['ticket_pool_id']
        quantity = item['quantity']

        ticket_pool = TicketPool.objects.get(id=ticket_pool_id)

        existing_item = order.items.filter(ticket_pool=ticket_pool).first()
        if existing_item:
            existing_item.quantity += quantity
            if existing_item.price is None:
                existing_item.price = ticket_pool.price
            existing_item.save()
        else:
            OrderItem.objects.create(
                order=order,
                ticket_pool=ticket_pool,
                quantity=quantity,
                price=ticket_pool.price,
            )

    del request.session['cart']

def save_pdf_to_file(pdf_bytes, filename):
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, filename)
    with open(pdf_path, 'wb') as f:
        f.write(pdf_bytes)
    return pdf_path

def send_payment_link(order, request):
    payment_url = request.build_absolute_uri(reverse('orders:simulate_payment', args=[order.id]))
    subject = "Opłać swoje zamówienie"
    message = render_to_string('emails/payment_link.html', {
        'order': order,
        'payment_url': payment_url,
    })
    email_message = EmailMessage(subject, message, to=[order.email])
    email_message.content_subtype = 'html'
    email_message.send()

@csrf_exempt
def simulate_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status == OrderStatus.COMPLETED:
        messages.info(request,
                      "To zamówienie zostało już opłacone.",
                      extra_tags="simulate_payment info")
        return render(request, 'orders/payment_already_done.html', {'order': order})

    if order.status == OrderStatus.CANCELLED:
        messages.info(request,
                      "To zamówienie zostało anulowane.",
                      extra_tags="simulate_payment error")
        return redirect('orders:checkout')

    vat_rate = 0.23

    total_price = float(
        sum(item.quantity * (item.price or item.ticket_pool.current_price()) for item in order.items.all()))
    vat_amount = round(total_price * vat_rate, 2)
    net_price = round(total_price - vat_amount, 2)

    if request.method == "POST":
        payment_code = request.POST.get('payment_code')

        if payment_code == "123456":
            for item in order.items.all():
                if item.quantity > item.ticket_pool.remaining_tickets():
                    messages.info(
                        request,
                        f"Bilety w puli '{item.ticket_pool.name}' są wyprzedane lub liczba dostępnych biletów zmniejszyła się.",
                        extra_tags="simulate_payment error")
                    order.status = OrderStatus.CANCELLED
                    order.save()
                    return redirect('orders:cart')

                item.ticket_pool.quantity_sold += item.quantity
                item.ticket_pool.save()

            order.status = OrderStatus.COMPLETED
            order.save()

            if not request.user.is_authenticated:
                if 'cart' in request.session:
                    del request.session['cart']

            tickets_pdf = generate_tickets_pdf(order)
            tickets_pdf_path = save_pdf_to_file(tickets_pdf, f"bilety_{order.id}.pdf")

            invoice_pdf = generate_invoice_pdf(order)
            invoice_pdf_path = save_pdf_to_file(invoice_pdf, f"faktura_{order.id}_.pdf")

            subject = "Twoje bilety na wydarzenie"
            message = render_to_string('emails/tickets_email.html', {'order': order})
            email_message = EmailMessage(subject, message, to=[order.email])
            email_message.content_subtype = 'html'
            email_message.attach_file(tickets_pdf_path)
            email_message.attach_file(invoice_pdf_path)
            email_message.send()

            messages.info(request,
                          "Płatność została pomyślnie zrealizowana! Bilety i faktura zostały przesłane na Twój e-mail.",
                          extra_tags="simulate_payment success")
            return redirect('orders:payment_confirmation')

        else:
            messages.info(request,
                          "Nieprawidłowy kod płatności. Spróbuj ponownie.",
                          extra_tags="simulate_payment error")

    return render(request, 'orders/payment_page.html', {
        'order': order,
        'total_price': total_price,
        'vat_amount': vat_amount,
        'net_price': net_price,
        'items': order.items.all(),
    })

def payment_confirmation(request):
    return render(request, 'orders/payment_confirmation.html')
