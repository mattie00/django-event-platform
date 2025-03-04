from django.urls import path
from .views import add_to_cart, cart_view, remove_from_cart, checkout_view, simulate_payment, payment_confirmation

app_name = 'orders'

urlpatterns = [
    path('add-to-cart/', add_to_cart, name='add_to_cart'),
    path('cart/', cart_view, name='cart'),
    path('remove-from-cart/<int:ticket_pool_id>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout_view, name='checkout'),
    path('simulate_payment/<int:order_id>/', simulate_payment, name='simulate_payment'),
    path('payment_confirmation/', payment_confirmation, name='payment_confirmation'),
]

