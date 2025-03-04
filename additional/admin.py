from django.contrib import admin
from .models import Carousel, CarouselSlide, NewsletterSubscriber

class CarouselSlideInline(admin.TabularInline):
    model = CarouselSlide
    extra = 1

@admin.register(Carousel)
class CarouselAdmin(admin.ModelAdmin):
    inlines = [CarouselSlideInline]

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subscribed_at', 'accepted_terms')
    search_fields = ('name', 'email')
    list_filter = ('subscribed_at', 'accepted_terms')
