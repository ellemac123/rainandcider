from django import forms
from . import models
from django.forms import Select


class CityForm(forms.ModelForm):
    class Meta:
        model = models.City
        fields = ('city',)
        args = models.City.objects.values_list('id', 'city')
        widgets = {'city': Select(choices = list(args))}
