from orders.models import Order

def cart_item_count(request):
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, status='pending').first()
        return {'cart_item_count': sum(item.quantity for item in order.items.all())} if order else {'cart_item_count': 0}
    else:
        cart = request.session.get('cart', [])
        return {'cart_item_count': sum(item['quantity'] for item in cart)}
