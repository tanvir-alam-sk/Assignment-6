from django import forms
from .models import Accommodation
from django.contrib.auth.models import User

class AccommodationForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=False, widget=forms.HiddenInput())
    
    class Meta:
        model = Accommodation
        fields = ['title', 'location', 'bedroom_count', 'usd_rate', 'center', 'amenities', 'published']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # Pop the user from kwargs
        super(AccommodationForm, self).__init__(*args, **kwargs)
        
        # Set the initial value and filter the queryset of the user field
        self.fields['user'].queryset = User.objects.filter(id=user.id)  
        self.fields['user'].initial = user  # Set initial user value


class LocationImportForm(forms.Form):
    csv_file = forms.FileField()

