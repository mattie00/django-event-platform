from django.contrib import admin
from .models import Order, OrderItem, Ticket

class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    readonly_fields = ('ticket_number',)
    fields = ('first_name', 'last_name', 'ticket_number')
    can_delete = False

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price',)
    fields = ('ticket_pool', 'quantity', 'price')
    can_delete = False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ticket_pool')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'email', 'status', 'payment_method', 'display_total_price', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]

    def display_total_price(self, obj):
        return obj.calculate_total_price()
    display_total_price.short_description = "Łączna kwota"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('items')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'ticket_pool', 'quantity', 'price')
    list_filter = ('order__status', 'ticket_pool__event')
    search_fields = ('order__email', 'ticket_pool__name', 'ticket_pool__event__name')
    readonly_fields = ('price',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'ticket_pool')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_item', 'first_name', 'last_name', 'ticket_number')
    list_filter = ('order_item__order__status', 'order_item__ticket_pool__event')
    search_fields = ('first_name', 'last_name', 'ticket_number', 'order_item__order__email')
    readonly_fields = ('ticket_number',)
