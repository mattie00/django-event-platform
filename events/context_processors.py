from .models import Category
import random

def random_categories(request):
    if 'random_categories' not in request.session:
        categories = list(Category.objects.all())
        r_categories = random.sample(categories, min(len(categories), 5)) if categories else []
        request.session['random_categories'] = [category.id for category in r_categories]

    random_categories_ids = request.session['random_categories']
    categories = Category.objects.filter(id__in=random_categories_ids)

    return {'random_categories': categories}

def favorite_events(request):
    if request.user.is_authenticated:
        favs = request.user.favorites.select_related('event')
        fav_events = [f.event for f in favs]
    else:
        favorites = request.session.get('favorites', [])
        fav_events = []
        if favorites:
            from .models import Event
            fav_events = Event.objects.filter(id__in=favorites)
    return {'favorite_events': fav_events}
