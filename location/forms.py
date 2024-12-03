from django import forms
from .models import Accommodation
from django.contrib.auth.models import User

class AccommodationForm(forms.ModelForm):
    class Meta:
        model = Accommodation
        fields = ['title', 'location', 'bedroom_count', 'usd_rate', 'center', 'amenities', 'published']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # Pop the user from kwargs
        super(AccommodationForm, self).__init__(*args, **kwargs)
        # Filter the location queryset if necessary
        self.fields['user'].queryset = User.objects.filter(id=user.id)  # Only show logged-in user
        self.fields['user'].initial = user  # Set initial user value
