from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.db.models import F, Q, Min, Max
from .models import Event, Category, Favorite, Performer, Tag

def event_list(request):
    events = Event.objects.filter(is_active=True)
    query = request.GET.get('query', '')
    city = request.GET.get('city', '')
    category_id = request.GET.get('category', '')
    performer_id = request.GET.get('performer', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    club_name = request.GET.get('club_name', '')
    sort_by = request.GET.get('sort_by', 'date')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    tag_id = request.GET.get('tag', '')

    if query:
        events = events.filter(
            Q(name__icontains=query) |
            Q(club_name__icontains=query) |
            Q(performers__name__icontains=query) |
            Q(short_description__icontains=query)
        ).distinct()

    if city:
        events = events.filter(location__icontains=city)
    if category_id:
        events = events.filter(category_id=category_id)
    if club_name:
        events = events.filter(club_name__icontains=club_name)

    if date_from:
        events = events.filter(date__gte=date_from)
    if date_to:
        events = events.filter(date__lte=date_to)

    if price_min:
        events = events.filter(ticket_pools__price__gte=price_min)
    if price_max:
        events = events.filter(ticket_pools__price__lte=price_max)

    if tag_id:
        events = events.filter(tags__id=tag_id)

    if sort_by == 'price_asc':
        events = events.order_by('ticket_pools__price')
    elif sort_by == 'price_desc':
        events = events.order_by('-ticket_pools__price')
    elif sort_by == 'date':
        events = events.order_by('date')
    elif sort_by == '-date':
        events = events.order_by('-date')

    paginator = Paginator(events.distinct(), 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    cities = Event.objects.values_list('location', flat=True).distinct()
    categories = Category.objects.all()
    club_names = Event.objects.values_list('club_name', flat=True).distinct()
    tags = Tag.objects.all()

    price_range = Event.objects.aggregate(
        min_price=Min('ticket_pools__price'),
        max_price=Max('ticket_pools__price')
    )

    context = {
        'events': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': page_obj,
        'cities': cities,
        'categories': categories,
        'club_names': club_names,
        'tags': tags,
        'price_range': price_range,
        'performer_id': performer_id,
        'filters': {
            'query': query,
            'city': city,
            'category_id': category_id,
            'club_name': club_name,
            'date_from': date_from,
            'date_to': date_to,
            'sort_by': sort_by,
            'price_min': price_min,
            'price_max': price_max,
            'tag_id': tag_id,
        }
    }
    return render(request, 'events/list.html', context)

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    ticket_pools = event.ticket_pools.order_by('order')
    event.tags.update(views_count=F('views_count') + 1)

    for tag in event.tags.all():
        tag.update_popularity()

    dependent_pools = [pool for pool in ticket_pools if not pool.is_independent]
    independent_pools = [pool for pool in ticket_pools if pool.is_independent]
    event.views_count += 1
    event.save()

    return render(request, 'events/detail.html', {
        'event': event,
        'dependent_pools': dependent_pools,
        'independent_pools': independent_pools,
    })

def add_to_favorites(request):
    event_id = request.POST.get('event_id')
    event = get_object_or_404(Event, id=event_id)

    if request.user.is_authenticated:
        favorite, created = Favorite.objects.get_or_create(user=request.user, event=event)
    else:
        favorites = request.session.get('favorites', [])
        if event_id not in favorites:
            favorites.append(event_id)
            request.session['favorites'] = favorites

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    return redirect('events:list')

def remove_from_favorites(request):
    event_id = request.POST.get('event_id')
    event = get_object_or_404(Event, id=event_id)

    if request.user.is_authenticated:
        Favorite.objects.filter(user=request.user, event=event).delete()
    else:
        favorites = request.session.get('favorites', [])
        if event_id in favorites:
            favorites = [fav for fav in favorites if fav != event_id]
            request.session['favorites'] = favorites
    return redirect('events:favorites')

def favorites_view(request):
    if request.user.is_authenticated:
        favorites_qs = Favorite.objects.filter(user=request.user)
        favorite_events = [fav.event for fav in favorites_qs]
    else:
        favorites = request.session.get('favorites', [])
        favorite_events = Event.objects.filter(id__in=favorites)

    return render(request, 'events/favorites.html', {
        'favorite_events': favorite_events
    })

def performer_detail(request, performer_id):
    performer = get_object_or_404(Performer, id=performer_id)
    Performer.objects.filter(id=performer.id).update(performer_views_count=F('performer_views_count') + 1)

    related_events = performer.events.filter(is_active=True).order_by('date')
    event_count = related_events.count()

    context = {
        'performer': performer,
        'related_events': related_events,
        'event_count': event_count,
    }
    return render(request, 'events/performer_detail.html', context)
