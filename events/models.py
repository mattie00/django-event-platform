from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.conf import settings
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nazwa kategorii")

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Tag")
    popularity = models.PositiveIntegerField(default=0, verbose_name="Popularność tagu")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Liczba wyświetleń")

    def __str__(self):
        return self.name

    def update_popularity(self):
        active_event_count = self.events.filter(is_active=True).count()
        self.popularity = active_event_count
        self.save()

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['popularity']),
            models.Index(fields=['views_count']),
        ]

class Performer(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Nazwa wykonawcy")
    performer_image = models.ImageField(
        upload_to='performer/images/',
        null=True,
        blank=True,
        verbose_name="Zdjęcie artysty"
    )
    performer_views_count = models.PositiveIntegerField(default=0, verbose_name="Liczba wyświetleń")
    performer_popularity = models.PositiveIntegerField(default=0, verbose_name="Popularność")

    def __str__(self):
        return self.name

    def update_popularity(self):
        self.performer_popularity = self.events.filter(is_active=True).count()
        self.save()

    def get_primary_event(self):
        return self.events.filter(is_active=True).order_by('date').first()

    def get_related_events_count(self):
        return self.events.filter(is_active=True).count() - 1

class Event(models.Model):
    name = models.CharField(max_length=191, unique=True, verbose_name="Nazwa wydarzenia")
    short_description = models.CharField(max_length=255, verbose_name="Krótki opis wydarzenia", null=True, blank=True)
    description = models.TextField(verbose_name="Opis wydarzenia")
    date = models.DateTimeField(verbose_name="Data i godzina wydarzenia")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Data zakończenia wydarzenia")
    location = models.CharField(max_length=100, verbose_name="Miasto")
    address = models.CharField(max_length=255, verbose_name="Adres (ulica, numer budynku)", null=True, blank=True)
    club_name = models.CharField(max_length=255, verbose_name="Nazwa klubu", default="Nieznany klub")
    organizer = models.CharField(max_length=255, verbose_name="Organizator wydarzenia", null=True, blank=True)
    performers = models.ManyToManyField(
        'Performer',
        blank=True,
        related_name='events',
        verbose_name="Występują"
    )
    min_age = models.PositiveIntegerField(null=True, blank=True, verbose_name="Minimalny wiek uczestnika")
    is_recurring = models.BooleanField(default=False, verbose_name="Czy wydarzenie jest cykliczne?")
    recurrence_pattern = models.CharField(
        max_length=50,
        choices=[('DAILY', 'Codziennie'), ('WEEKLY', 'Co tydzień'), ('MONTHLY', 'Co miesiąc')],
        null=True,
        blank=True,
        verbose_name="Schemat powtarzania"
    )
    recurrence_end_date = models.DateTimeField(null=True, blank=True, verbose_name="Data zakończenia powtarzania")
    category = models.ForeignKey(
        'Category',
        on_delete=models.PROTECT,
        related_name='events',
        verbose_name="Kategoria wydarzenia"
    )
    tags = models.ManyToManyField(
        'Tag',
        blank=True,
        related_name='events',
        verbose_name="Tagi"
    )
    image = models.ImageField(
        upload_to='events/images/',
        null=True,
        blank=True,
        verbose_name="Zdjęcie wydarzenia"
    )
    ticket_sales_start = models.DateTimeField(null=True, blank=True, verbose_name="Początek sprzedaży biletów")
    ticket_sales_end = models.DateTimeField(null=True, blank=True, verbose_name="Koniec sprzedaży biletów")
    max_attendees = models.PositiveIntegerField(null=True, blank=True, verbose_name="Maksymalna liczba uczestników")
    is_active = models.BooleanField(default=True, verbose_name="Czy wydarzenie jest aktywne?")
    is_featured = models.BooleanField(default=False, verbose_name="Wyróżnione wydarzenie")
    is_archived = models.BooleanField(default=False, verbose_name="Czy wydarzenie jest zarchiwizowane?")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Liczba odwiedzin strony")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Utworzono")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Zaktualizowano")

    use_pool_logic = models.BooleanField(
        default=True,
        verbose_name="Używaj logiki zależnych pul biletów",
        help_text="Jeśli zaznaczone, kolejne pule pojawią się dopiero po wyprzedaniu wcześniejszych."
    )

    def __str__(self):
        return self.name

    def clean(self):
        if self.ticket_sales_end and self.ticket_sales_end > self.date:
            raise ValidationError("Koniec sprzedaży biletów nie może być po dacie wydarzenia.")

        if self.ticket_sales_start and self.ticket_sales_end:
            if self.ticket_sales_start > self.ticket_sales_end:
                raise ValidationError("Początek sprzedaży biletów nie może być po jej końcu.")

    def is_ticket_sales_active(self):
        if self.ticket_sales_start and self.ticket_sales_end:
            return self.ticket_sales_start <= now() <= self.ticket_sales_end
        return False

    def deactivate_if_past(self):
        if self.date < now() and self.is_active:
            self.is_active = False
            self.save()

    def save(self, *args, **kwargs):
        self.deactivate_if_past()
        super().save(*args, **kwargs)

    def get_event_status(self):
        if self.is_archived:
            return "Zarchiwizowane"
        elif self.date < now():
            return "Zakończone"
        elif self.is_ticket_sales_active():
            return "Aktywne"
        return "Planowane"

    def total_remaining_tickets(self):
        remaining = self.ticket_pools.aggregate(
            total_remaining=Sum('quantity_available') - Sum('quantity_sold')
        )['total_remaining']
        return max(0, remaining) if remaining else 0

    def get_available_ticket_pools(self):
        return self.ticket_pools.all()

    def get_lowest_price(self):
        # Najniższa cena wśród dostępnych i sprzedających się pul
        pools = self.get_available_ticket_pools()
        prices = [p.get_current_price() for p in pools if p.remaining_tickets() > 0 and p.is_sales_active()]
        return min(prices) if prices else None

    def has_promo(self):
        return any(p.is_last_minute_promo() and p.remaining_tickets() > 0 and p.is_sales_active()
                   for p in self.ticket_pools.all())

    def get_lowest_promo_price(self):
        promos = [p.promo_price for p in self.ticket_pools.all() if
                  p.is_last_minute_promo() and p.remaining_tickets() > 0 and p.is_sales_active()]
        return min(promos) if promos else None

    def get_earliest_promo_end_date(self):
        promo_end_dates = [
            p.promo_end_date for p in self.ticket_pools.all()
            if p.is_last_minute_promo() and p.remaining_tickets() > 0 and p.is_sales_active()
        ]
        return min(promo_end_dates) if promo_end_dates else None

    def get_lowest_promo_ticket_pool(self):
        promo_pools = [
            p for p in self.ticket_pools.all()
            if p.is_last_minute_promo() and p.remaining_tickets() > 0 and p.is_sales_active()
        ]
        if not promo_pools:
            return None
        return min(promo_pools, key=lambda p: p.promo_price)

class TicketPool(models.Model):
    event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE,
        related_name='ticket_pools',
        verbose_name="Wydarzenie"
    )
    name = models.CharField(max_length=100, verbose_name="Nazwa puli")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cena biletu")
    quantity_available = models.PositiveIntegerField(verbose_name="Ilość dostępnych biletów")
    quantity_sold = models.PositiveIntegerField(default=0, verbose_name="Ilość sprzedanych biletów")
    order = models.PositiveIntegerField(
        verbose_name="Kolejność puli",
        null=True, blank=True
    )
    is_independent = models.BooleanField(
        default=False,
        verbose_name="Niezależna pula",
        help_text="Jeśli zaznaczone, pula biletów będzie zawsze widoczna, niezależnie od innych."
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Utworzono")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Zaktualizowano")

    max_tickets_per_user = models.PositiveIntegerField(
        default=5,
        verbose_name="Maksymalna liczba biletów na użytkownika",
        help_text="Maksymalna liczba biletów, które jeden użytkownik może kupić dla tej puli."
    )

    is_promo_active = models.BooleanField(default=False, verbose_name="Czy promocja jest aktywna?")
    promo_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Cena promocyjna"
    )
    promo_end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data zakończenia promocji"
    )

    def __str__(self):
        return f"{self.name} - {self.event.name}"

    def clean(self):
        super().clean()
        if not self.is_independent and self.order is None:
            raise ValidationError("Jeśli pula nie jest niezależna (is_independent=False), musisz podać jej kolejność.")
        if self.is_independent and self.order is not None:
            raise ValidationError("Pula niezależna (is_independent=True) nie wymaga kolejności puli. Usuń wartość 'order'.")

        if self.quantity_sold > self.quantity_available:
            raise ValidationError("Nie można sprzedać więcej biletów niż dostępnych w tej puli.")

        if self.event and self.event.pk and self.event.max_attendees is not None:
            total_tickets = sum(pool.quantity_available for pool in self.event.ticket_pools.all())
            if total_tickets > self.event.max_attendees:
                raise ValidationError(
                    f"Suma biletów ({total_tickets}) przekracza maksymalną liczbę uczestników wydarzenia "
                    f"({self.event.max_attendees})."
                )

        if not self.is_independent:
            if self.event.ticket_pools.filter(order=self.order).exclude(id=self.id).exists():
                raise ValidationError("Kolejność puli biletów musi być unikalna w ramach wydarzenia.")

    @property
    def is_locked(self):
        if self.is_independent:
            return False

        if not self.event.use_pool_logic:
            return False

        previous_pools = self.event.ticket_pools.filter(order__lt=self.order)
        return not all(pool.is_sold_out() for pool in previous_pools)

    def current_price(self):
        if self.is_last_minute_promo():
            return self.promo_price
        return self.price

    def has_promo(self):
        return self.promo_price is not None

    def is_last_minute_promo(self):
        return (
                self.is_promo_active
                and self.promo_price is not None
                and self.promo_price < self.price
                and self.promo_end_date is not None
                and timezone.now() <= self.promo_end_date
        )

    def get_current_price(self):
        if self.is_last_minute_promo():
            return self.promo_price
        return self.price

    def remaining_tickets(self):
        available = self.quantity_available or 0
        sold = self.quantity_sold or 0
        return max(0, available - sold)

    def is_sold_out(self):
        return self.remaining_tickets() == 0

    def is_active(self):
        previous_pools = self.event.ticket_pools.filter(order__lt=self.order).order_by('order')
        all_previous_sold_out = all(pool.is_sold_out() for pool in previous_pools)
        return all_previous_sold_out and not self.is_sold_out()

    def is_sales_active(self):
        return (self.event.ticket_sales_start is None or self.event.ticket_sales_start <= now()) and \
               (self.event.ticket_sales_end is None or now() <= self.event.ticket_sales_end)

    def is_sales_pending(self):
        return self.event.ticket_sales_start and now() < self.event.ticket_sales_start

    def is_sales_ended(self):
        return self.event.ticket_sales_end and now() > self.event.ticket_sales_end


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.email} - {self.event.name}"
