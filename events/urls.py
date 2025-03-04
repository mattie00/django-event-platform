from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='list'),
    path('<int:event_id>/', views.event_detail, name='detail'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('add-to-favorites/', views.add_to_favorites, name='add_to_favorites'),
    path('remove-from-favorites/', views.remove_from_favorites, name='remove_from_favorites'),
    path('performer/<int:performer_id>/', views.performer_detail, name='performer_detail'),
]
