from django.contrib import admin
from .models import Event, TicketPool, Category, Tag, Performer
from django.forms.models import BaseInlineFormSet

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'popularity', 'views_count']
    search_fields = ['name']
    readonly_fields = ['popularity']

@admin.register(Performer)
class PerformerAdmin(admin.ModelAdmin):
    list_display = ['name', 'performer_views_count', 'performer_popularity_dynamic']
    search_fields = ['name']
    readonly_fields = ['performer_views_count', 'performer_popularity_dynamic']
    fields = ['name', 'performer_image', 'performer_views_count']
    ordering = ['name']

    @admin.display(description='Popularność')
    def performer_popularity_dynamic(self, obj):
        return obj.events.filter(is_active=True).count()

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.update_popularity()

class BaseTicketPoolInlineFormSet(BaseInlineFormSet):
    def save_new(self, form, commit=True):
        obj = super().save_new(form, commit=False)
        if not self.instance.pk:
            self.instance.save()
        obj.event = self.instance
        if commit:
            obj.save()
        return obj

class TicketPoolInline(admin.TabularInline):
    model = TicketPool
    formset = BaseTicketPoolInlineFormSet
    extra = 1
    fields = [
        'name',
        'price',
        'promo_price',
        'is_promo_active',
        'promo_end_date',
        'quantity_available',
        'quantity_sold',
        'order',
        'is_independent',
        'remaining_tickets_display',
        'max_tickets_per_user',
    ]
    readonly_fields = ['remaining_tickets_display']

    def remaining_tickets_display(self, obj):
        return obj.remaining_tickets()
    remaining_tickets_display.short_description = "Pozostałe bilety"

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj:
            use_pool_logic = getattr(obj, 'use_pool_logic', True)

            if 'is_independent' in formset.form.base_fields:
                formset.form.base_fields['is_independent'].help_text = (
                    "Jeśli zaznaczone, pula jest niezależna i wyświetlana zawsze osobno (VIP/Premium). "
                    "Nie wymaga podania kolejności."
                )

            if 'order' in formset.form.base_fields:
                if use_pool_logic:
                    formset.form.base_fields['order'].help_text = (
                        "Kolejność puli biletów ma znaczenie przy aktywnej logice zależności (use_pool_logic=True). "
                        "Pule z wyższą kolejnością pojawią się dopiero po wyprzedaniu wcześniejszych."
                    )
                else:
                    formset.form.base_fields['order'].help_text = (
                        "Logika zależnych pul jest wyłączona (use_pool_logic=False). Kolejność nie blokuje sprzedaży, "
                        "ale musi być unikalna dla pul zależnych."
                    )

        return formset

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'date', 'location', 'club_name', 'category', 'is_active', 'is_archived',
        'get_ticket_sales_active', 'total_remaining_tickets_display', 'has_last_minute_promo',
    ]
    list_filter = ['category', 'is_active', 'is_archived', 'is_featured', 'date']
    search_fields = ['name', 'location', 'address', 'description', 'performers__name']
    readonly_fields = ['created_at', 'updated_at', 'total_remaining_tickets_display']
    autocomplete_fields = ['performers', 'tags']
    inlines = [TicketPoolInline]
    fieldsets = (
        (None, {
            'fields': (
                'name', 'short_description', 'description', 'date', 'end_date', 'location', 'address', 'club_name',
                'organizer', 'category', 'tags', 'performers', 'image', 'min_age', 'is_recurring',
                'recurrence_pattern', 'recurrence_end_date',
            )
        }),
        ("Sprzedaż biletów", {
            'fields': (
                'ticket_sales_start', 'ticket_sales_end', 'max_attendees', 'is_active', 'is_featured', 'is_archived',
                'use_pool_logic',
            )
        }),
        ("Czasy i statystyki", {
            'fields': (
                'views_count', 'created_at', 'updated_at'
            )
        }),
    )

    def get_ticket_sales_active(self, obj):
        return obj.is_ticket_sales_active()
    get_ticket_sales_active.boolean = True
    get_ticket_sales_active.short_description = "Sprzedaż aktywna"

    def total_remaining_tickets_display(self, obj):
        return obj.total_remaining_tickets()
    total_remaining_tickets_display.short_description = "Pozostałe bilety"

    def has_last_minute_promo(self, obj):
        return any(pool.is_last_minute_promo() for pool in obj.ticket_pools.all())
    has_last_minute_promo.boolean = True
    has_last_minute_promo.short_description = "Last minute"
