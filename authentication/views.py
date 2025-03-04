from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from authentication.models import AppUser
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator as generate_token, default_token_generator
from django.utils.encoding import force_str
from orders.models import Order, OrderItem, Ticket, OrderStatus
from events.models import TicketPool
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

def user_register(request):
    if request.method == 'POST':
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone_number = request.POST['phone_number']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        terms = request.POST.get('terms', None)

        if not terms:
            messages.info(request, 'Musisz zaakceptować regulamin.', extra_tags='user_register error')
            return render(request, 'authentication/register.html')

        if password != confirm_password:
            messages.info(request, 'Hasła nie pasują.', extra_tags='user_register error')
        else:
            if AppUser.objects.filter(email=email).exists():
                messages.info(request, 'Użytkownik z tym adresem email już istnieje.', extra_tags='user_register error')
            elif AppUser.objects.filter(phone_number=phone_number).exists():
                messages.info(request, 'Użytkownik z tym numerem telefonu już istnieje.', extra_tags='user_register error')
            else:
                user = AppUser.objects.create_user(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    password=password
                )
                user.is_active = False
                user.save()

                messages.info(
                    request,
                    'Twoje konto zostało pomyślnie utworzone. Sprawdź maila w celu potwierdzenia rejestracji.',
                    extra_tags='user_register success'
                )

                subject = "Nazwa - Witamy w naszej platformie!"
                html_message = render_to_string('emails/user_welcome.html', {
                    'user': user,
                })
                email_msg = EmailMessage(
                    subject,
                    html_message,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[user.email],
                )
                email_msg.content_subtype = "html"
                email_msg.send(fail_silently=True)

                current_site = get_current_site(request)
                email_subject = "Nazwa - Potwierdź swój adres e-mail"
                message2 = render_to_string('emails/email_confirmation.html', {
                    'name': user.first_name,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': generate_token.make_token(user)
                })
                email2 = EmailMessage(
                    email_subject,
                    message2,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                )
                email2.content_subtype = "html"
                email2.send(fail_silently=True)

                return redirect('login')

    return render(request, 'authentication/register.html')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = AppUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, AppUser.DoesNotExist):
        user = None

    if user is not None and generate_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.info(request, "Twoje konto zostało aktywowane. Możesz teraz korzystać z aplikacji!",
                      extra_tags='activate success')
        return redirect('login')
    else:
        messages.info(request, "Link aktywacyjny jest nieprawidłowy lub wygasł.", extra_tags='activate error')
        return render(request, 'authentication/activation_failed.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            if not user.is_active:
                messages.info(request,
                              'Twoje konto nie zostało jeszcze zweryfikowane. Sprawdź swój e-mail, aby potwierdzić konto.',
                              extra_tags='user_login error')
                return render(request, 'authentication/login.html')
            login(request, user)

            if 'cart' in request.session:
                cart = request.session['cart']
                order, created = Order.objects.get_or_create(user=user, status='pending')

                for item in cart:
                    ticket_pool = TicketPool.objects.get(id=item['ticket_pool_id'])
                    order_item, item_created = OrderItem.objects.get_or_create(
                        order=order,
                        ticket_pool=ticket_pool,
                        defaults={'quantity': item['quantity'], 'price': ticket_pool.price}
                    )
                    if not item_created:
                        order_item.quantity += item['quantity']
                        order_item.save()

                order.total_price = sum([oi.price * oi.quantity for oi in order.items.all()])
                order.save()

                request.session['cart'] = []

            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)

            return redirect('home')
        else:
            messages.info(request, 'Nieprawidłowe dane logowania.', extra_tags='user_login error')

    return render(request, 'authentication/login.html')

def user_logout(request):
    if 'cart' in request.session:
        del request.session['cart']
    logout(request)
    messages.info(request, 'Zostałeś pomyślnie wylogowany.', extra_tags='user_logout success')
    return redirect('login')

@login_required
def profile(request):
    active_tab = request.GET.get('tab', 'your-data')
    user = request.user

    tickets = Ticket.objects.filter(
        order_item__order__user=user,
        order_item__order__status=OrderStatus.COMPLETED
    ).select_related('order_item__ticket_pool__event')

    context = {
        'active_tab': active_tab,
        'tickets': tickets,
    }
    return render(request, 'authentication/profile.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(old_password):
            messages.info(request, 'Podane stare hasło jest nieprawidłowe.',
                          extra_tags='change_password error password_reset')
            return redirect(reverse('profile') + '?tab=change-password')

        if new_password != confirm_password:
            messages.info(request, 'Nowe hasła nie są takie same.',
                          extra_tags='change_password error password_reset')
            return redirect(reverse('profile') + '?tab=change-password')

        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.info(request, 'Twoje hasło zostało pomyślnie zmienione.',
                      extra_tags='change_password success password_reset')
        return redirect(reverse('profile') + '?tab=change-password')

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user

        first_name = request.POST.get('first_name', user.first_name)
        last_name = request.POST.get('last_name', user.last_name)
        email = request.POST.get('email', user.email)
        phone_number = request.POST.get('phone_number', user.phone_number)

        if (user.first_name == first_name and
            user.last_name == last_name and
            user.email == email and
            user.phone_number == phone_number):
            messages.info(request, 'Nie wprowadzono żadnych zmian.',
                          extra_tags='update_profile warning profile')
            return redirect(reverse('profile') + '?tab=your-data')

        if email != user.email and user.__class__.objects.filter(email=email).exists():
            messages.info(request, 'Użytkownik z tym adresem email już istnieje.',
                          extra_tags='update_profile error profile')
            return redirect(reverse('profile') + '?tab=your-data')

        if phone_number != user.phone_number and user.__class__.objects.filter(phone_number=phone_number).exists():
            messages.info(request, 'Użytkownik z tym numerem telefonu już istnieje.',
                          extra_tags='update_profile error profile')
            return redirect(reverse('profile') + '?tab=your-data')

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone_number = phone_number
        user.save()

        messages.info(request, 'Twoje dane zostały zaktualizowane.',
                      extra_tags='update_profile success profile')
        return redirect(reverse('profile') + '?tab=your-data')

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if AppUser.objects.filter(email=email).exists():
            user = AppUser.objects.get(email=email)
            current_site = get_current_site(request)
            subject = "EventApp - Resetowanie hasła"
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            html_message = render_to_string('emails/password_reset_request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
                'protocol': 'https' if request.is_secure() else 'http'
            })
            email_msg = EmailMessage(
                subject,
                html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email_msg.content_subtype = "html"
            email_msg.send(fail_silently=True)

        messages.info(request,
                      "Jeśli podany adres e-mail istnieje w naszej bazie, otrzymasz wiadomość z linkiem do resetowania hasła.",
                      extra_tags='password_reset_request info')
        return redirect('password_reset_done_custom')
    return render(request, 'authentication/password_reset/password_reset_form.html')

def password_reset_done_custom(request):
    return render(request, 'authentication/password_reset/password_reset_done.html')

def password_reset_confirm_custom(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = AppUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, AppUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            new_password_confirm = request.POST.get('new_password_confirm')

            if new_password != new_password_confirm:
                messages.info(request, "Hasła nie są identyczne.",
                              extra_tags='password_reset_confirm_custom error')
                return render(request, 'authentication/password_reset/password_reset_confirm.html', {'validlink': True})

            user.set_password(new_password)
            user.save()
            messages.info(request, "Hasło zostało pomyślnie zmienione.",
                          extra_tags='password_reset_confirm_custom success')
            return redirect('password_reset_complete_custom')

        return render(request, 'authentication/password_reset/password_reset_confirm.html', {'validlink': True})
    else:
        messages.info(request, "Link do resetowania hasła jest nieprawidłowy lub wygasł.",
                      extra_tags='password_reset_confirm_custom error')
        return render(request, 'authentication/password_reset/password_reset_confirm.html', {'validlink': False})

def password_reset_complete_custom(request):
    if request.user.is_authenticated:
        subject = "EventApp - Hasło zresetowane"
        html_message = render_to_string('emails/password_reset_complete_email.html', {
            'user': request.user,
        })
        email_msg = EmailMessage(
            subject,
            html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[request.user.email]
        )
        email_msg.content_subtype = "html"
        email_msg.send(fail_silently=True)

    return render(request, 'authentication/password_reset/password_reset_complete.html')
