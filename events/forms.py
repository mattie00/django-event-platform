from django import forms
from .models import Category, Event, Performer

class EventSearchForm(forms.Form):
    city = forms.ChoiceField(
        required=False,
        label="Miasto",
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    club_name = forms.ChoiceField(
        required=False,
        label="Nazwa Klubu",
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all() if Category.objects.exists() else Category.objects.none(),
        required=False,
        label="Kategoria",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False,
        label="Data od",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    date_to = forms.DateField(
        required=False,
        label="Data do",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    min_age = forms.IntegerField(
        required=False,
        label="Minimalny wiek uczestnika",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0})
    )
    is_featured = forms.BooleanField(
        required=False,
        label="Wyróżnione wydarzenia",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    is_archived = forms.BooleanField(
        required=False,
        label="Uwzględnij zarchiwizowane",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    sort_by = forms.ChoiceField(
        required=False,
        label="Sortowanie",
        choices=[
            ('price_asc', 'Cena: od najniższej'),
            ('price_desc', 'Cena: od najwyższej'),
            ('date_asc', 'Data: od najbliższych'),
            ('date_desc', 'Data: od najdawniejszych')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    performer = forms.ModelChoiceField(
        queryset=Performer.objects.all() if Performer.objects.exists() else Performer.objects.none(),
        required=False,
        label="Wykonawca",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].choices = [
            ('', 'Wybierz miasto')] + list(Event.objects.values_list('location', 'location').distinct())
        self.fields['club_name'].choices = [
            ('', 'Wybierz klub')] + list(Event.objects.values_list('club_name', 'club_name').distinct())

