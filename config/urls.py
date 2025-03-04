from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from config import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('', include('authentication.urls')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('events/', include('events.urls', namespace='events')),
    path('add/', include('additional.urls', namespace='add')),
    path('ajax/city_events/', views.ajax_city_events, name='ajax_city_events'),
    path('ajax/events_by_period/', views.ajax_events_by_period, name='ajax_events_by_period'),
    path('ajax-category-events/', views.ajax_category_events, name='ajax_category_events'),
    path('ajax-tag-events/', views.ajax_tag_events, name='ajax_tag_events'),
    path('ajax/artist-events/', views.ajax_artist_events, name='ajax_artist_events'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)