from django.shortcuts import render, redirect
from django.contrib import messages
from .models import NewsletterSubscriber
from django.utils.timezone import now

def subscribe(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        newsletter_terms = request.POST.get('terms') == 'on'

        if not newsletter_terms:
            messages.error(request, "Musisz zaakceptować regulamin, aby się zapisać.")
            return redirect('newsletter:page')

        if NewsletterSubscriber.objects.filter(email=email).exists():
            messages.info(request, "Ten e-mail jest już zapisany do newslettera.")
        else:
            NewsletterSubscriber.objects.create(name=name, email=email, accepted_terms=newsletter_terms)
            messages.success(request, "Dziękujemy za zapisanie się do newslettera!")
        return redirect('home')

def newsletter_page(request):
    return render(request, 'others/newsletter/newsletter_page.html')

def terms(request):
    return render(request, 'others/newsletter/newsletter_terms.html', {'current_date': now()})
