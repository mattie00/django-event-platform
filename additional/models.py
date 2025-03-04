from django.db import models

class Carousel(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nazwa slajdera")

    def __str__(self):
        return self.name

class CarouselSlide(models.Model):
    carousel = models.ForeignKey(Carousel, related_name="slides", on_delete=models.CASCADE)
    headline = models.CharField(max_length=255, verbose_name="Nagłówek")
    description = models.TextField(verbose_name="Opis")
    image = models.ImageField(upload_to="carousel/images/", verbose_name="Zdjęcie")
    event = models.ForeignKey('events.Event', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Powiązane wydarzenie")
    order = models.PositiveIntegerField(default=0, verbose_name="Kolejność")
    button_text = models.CharField(max_length=50, default="Zobacz więcej", verbose_name="Tekst przycisku")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.headline} ({self.carousel.name})"

class NewsletterSubscriber(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    accepted_terms = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.email}"
