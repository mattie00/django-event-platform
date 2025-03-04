from django.urls import path
from django.views.generic import TemplateView

from additional import views

app_name = 'additional'

urlpatterns = [
    path('about/', TemplateView.as_view(template_name='others/help_center/about.html'), name='about'),
    path('faq/', TemplateView.as_view(template_name='others/help_center/faq.html'), name='faq'),
    path('terms/', TemplateView.as_view(template_name='others/help_center/terms.html'), name='terms'),
    path('payment-methods/', TemplateView.as_view(template_name='others/help_center/payment_methods.html'), name='payment_methods'),
    path('privacy-policy/', TemplateView.as_view(template_name='others/help_center/privacy_policy.html'), name='privacy_policy'),
    path('contact/', TemplateView.as_view(template_name='others/help_center/contact.html'), name='contact'),
    path('organizers/', TemplateView.as_view(template_name='others/for_business/organizers.html'), name='organizers'),
    path('partnership/', TemplateView.as_view(template_name='others/for_business/partnership.html'), name='partnership'),
    path('advertising/', TemplateView.as_view(template_name='others/for_business/advertising.html'), name='advertising'),
    path('business-solutions/', TemplateView.as_view(template_name='others/for_business/business_solutions.html'), name='business_solutions'),
    path('affiliate-program/', TemplateView.as_view(template_name='others/for_business/affiliate_program.html'), name='affiliate_program'),
    path('events/', TemplateView.as_view(template_name='others/meet/events.html'), name='events'),
    path('categories/', TemplateView.as_view(template_name='others/meet/categories.html'), name='categories'),
    path('promotions/', TemplateView.as_view(template_name='others/meet/promotions.html'), name='promotions'),
    path('blog/', TemplateView.as_view(template_name='others/meet/blog.html'), name='blog'),
    path('', views.newsletter_page, name='page'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('newsletter_terms/', views.terms, name='newsletter_terms'),
]
