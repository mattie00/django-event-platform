from django import forms

class TicketForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=True, label="Imię")
    last_name = forms.CharField(max_length=100, required=True, label="Nazwisko")
