from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/done/', views.password_reset_done_custom, name='password_reset_done_custom'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm_custom, name='password_reset_confirm_custom'),
    path('password-reset-complete/', views.password_reset_complete_custom, name='password_reset_complete_custom'),
]