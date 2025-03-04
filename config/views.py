from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils.timezone import now
from datetime import timedelta, datetime
import random
from django.db.models import Count, F
from additional.models import Carousel
from events.models import Event, Category, Tag, TicketPool, Performer
from django.utils import timezone
from django.utils.timezone import make_aware
from django.db.models import Q

def home(request):
    upcoming_events = Event.objects.filter(is_active=True, date__gte=now()).order_by('date')[:8]
    popular_events = Event.objects.filter(is_active=True).order_by('-views_count')[:10]
    popular_cities = (
        Event.objects.filter(is_active=True)
        .values('location')
        .annotate(event_count=Count('id'))
        .order_by('-event_count')[:10]
    )
    popular_tags = Tag.objects.annotate(event_count=Count('events')).order_by('-event_count')[:10]
    total_events_count = Event.objects.filter(is_active=True).count()
    featured_events = Event.objects.filter(is_active=True, is_featured=True).order_by('?')[:14]
    categories = Category.objects.all()

    random_category = random.choice(list(categories)) if categories else None
    category_events = Event.objects.filter(is_active=True, category=random_category).order_by('?')[:4] if random_category else []

    cities = Event.objects.values_list('location', flat=True).distinct()

    selected_city = request.GET.get('city')
    if selected_city and selected_city in cities:
        city_for_events = selected_city
    else:
        city_for_events = random.choice(list(cities)) if cities else None

    city_events = (
        Event.objects.filter(location=city_for_events, is_active=True).order_by('?')[:4]
        if city_for_events
        else []
    )

    popular_tag = Tag.objects.order_by('-views_count').first()
    tag_events = (
        Event.objects.filter(tags=popular_tag, is_active=True).order_by('?')[:8]
        if popular_tag
        else []
    )

    upcoming_week_events = Event.objects.filter(
        is_active=True,
        date__gte=now(),
        date__lte=now() + timedelta(days=7),
    ).order_by('?')[:8]

    newly_added_events = Event.objects.filter(is_active=True).order_by('?')[:14]

    kids_category = Category.objects.filter(name="Dla dzieci").first()
    kids_events = (
        Event.objects.filter(category=kids_category, is_active=True).order_by('?')[:10]
        if kids_category
        else []
    )

    carousel = Carousel.objects.prefetch_related('slides').first()

    last_minute_events = Event.objects.filter(
        ticket_pools__is_promo_active=True,
        ticket_pools__promo_end_date__gte=timezone.now()
    ).distinct().order_by('?')[:6]

    promo_tickets = TicketPool.objects.filter(
        is_promo_active=True,
        promo_price__isnull=False,
        promo_end_date__gte=timezone.now(),
        quantity_sold__lt=F('quantity_available')
    ).select_related('event').order_by('?')[:8]

    performers = Performer.objects.all()

    popular_performers = Performer.objects.annotate(
        event_count=Count('events', filter=Q(events__is_active=True))
    ).order_by('-event_count', '-performer_views_count')[:10]

    context = {
        'upcoming_events': upcoming_events,
        'total_events_count': total_events_count,
        'popular_cities': popular_cities,
        'popular_events': popular_events,
        'popular_tags': popular_tags,
        'featured_events': featured_events,
        'random_category': random_category,
        'category_events': category_events,
        'city_for_events': city_for_events,
        'city_events': city_events,
        'popular_tag': popular_tag,
        'tag_events': tag_events,
        'upcoming_week_events': upcoming_week_events,
        'newly_added_events': newly_added_events,
        'kids_events': kids_events,
        'categories': categories,
        'cities': cities,
        'carousel': carousel,
        'last_minute_events': last_minute_events,
        'promo_tickets': promo_tickets,
        'performers': performers,
        'popular_performers': popular_performers,
    }
    return render(request, 'main/home.html', context)

def ajax_events_by_period(request):
    period = request.GET.get('period')
    now_time = now()
    today = now_time.date()
    events = Event.objects.none()

    if period == 'today':
        events = Event.objects.filter(is_active=True, date__date=today)[:4]
    elif period == 'tomorrow':
        tomorrow = today + timedelta(days=1)
        tomorrow_aware = make_aware(datetime.combine(tomorrow, datetime.min.time()))
        tomorrow_end_aware = make_aware(datetime.combine(tomorrow, datetime.max.time()))
        events = Event.objects.filter(is_active=True, date__range=(tomorrow_aware, tomorrow_end_aware))[:4]
    elif period == 'day_after_tomorrow':
        day_after_tomorrow = today + timedelta(days=2)
        day_after_aware = make_aware(datetime.combine(day_after_tomorrow, datetime.min.time()))
        day_after_end_aware = make_aware(datetime.combine(day_after_tomorrow, datetime.max.time()))
        events = Event.objects.filter(is_active=True, date__range=(day_after_aware, day_after_end_aware))[:4]
    elif period == 'weekend':
        weekend_start = today + timedelta(days=(5 - today.weekday()))
        weekend_end = weekend_start + timedelta(days=1)
        weekend_start_aware = make_aware(datetime.combine(weekend_start, datetime.min.time()))
        weekend_end_aware = make_aware(datetime.combine(weekend_end, datetime.max.time()))
        events = Event.objects.filter(is_active=True, date__range=(weekend_start_aware, weekend_end_aware))[:4]
    elif period == 'next_week':
        next_week_start = today + timedelta(days=(7 - today.weekday()))
        next_week_end = next_week_start + timedelta(days=6)
        next_week_start_aware = make_aware(datetime.combine(next_week_start, datetime.min.time()))
        next_week_end_aware = make_aware(datetime.combine(next_week_end, datetime.max.time()))
        events = Event.objects.filter(is_active=True, date__range=(next_week_start_aware, next_week_end_aware))[:4]

    if events.exists():
        html = render_to_string('main/partials/events_period_partial.html', {'events': events})
        return JsonResponse({'success': True, 'html': html})
    else:
        return JsonResponse({'success': False, 'html': '<p class="text-muted">Brak wydarzeń dla wybranego okresu.</p>'})

def ajax_category_events(request):
    category_id = request.GET.get('category')
    if category_id:
        try:
            category = Category.objects.get(id=category_id)
            category_events = Event.objects.filter(category=category, is_active=True).order_by('?')[:10]
        except Category.DoesNotExist:
            category_events = Event.objects.none()
    else:
        categories = Category.objects.all()
        random_category = random.choice(list(categories)) if categories else None
        category_events = Event.objects.filter(category=random_category, is_active=True).order_by('?')[:10] if random_category else []

    html = render_to_string('main/partials/category_events_partial.html', {
        'category_events': category_events,
    })
    return HttpResponse(html)

def ajax_tag_events(request):
    tag_id = request.GET.get('tag')
    if tag_id:
        try:
            tag = Tag.objects.get(id=tag_id)
            tag_events = Event.objects.filter(tags=tag, is_active=True).order_by('?')[:10]
        except Tag.DoesNotExist:
            tag_events = Event.objects.none()
    else:
        tags = Tag.objects.all()
        random_tag = random.choice(list(tags)) if tags else None
        tag_events = Event.objects.filter(tags=random_tag, is_active=True).order_by('?')[:10] if random_tag else []

    html = render_to_string('main/partials/tag_events_partial.html', {
        'tag_events': tag_events,
    })
    return HttpResponse(html)

def ajax_artist_events(request):
    artist_id = request.GET.get('artist')
    if artist_id:
        try:
            artist = Performer.objects.get(id=artist_id)
            artist_events = Event.objects.filter(performers=artist, is_active=True).order_by('?')[:4]
        except Performer.DoesNotExist:
            artist_events = Event.objects.none()
    else:
        artists = Performer.objects.all()
        random_artist = random.choice(list(artists)) if artists.exists() else None
        artist_events = Event.objects.filter(performers=random_artist, is_active=True).order_by('?')[:4] if random_artist else []

    html = render_to_string('main/partials/artist_events_partial.html', {
        'artist_events': artist_events,
    })
    return HttpResponse(html)

def ajax_city_events(request):
    city = request.GET.get('city')
    cities = Event.objects.values_list('location', flat=True).distinct()
    if city and city in cities:
        city_for_events = city
    else:
        city_for_events = random.choice(list(cities)) if cities else None

    city_events = (
        Event.objects.filter(location=city_for_events, is_active=True).order_by('?')[:10]
        if city_for_events
        else []
    )

    html = render_to_string('main/partials/city_events_partial.html', {
        'city_for_events': city_for_events,
        'city_events': city_events
    })
    return HttpResponse(html)