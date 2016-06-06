from django import forms
from . import models
from django.forms import Select

"""
Creates a city form that will allow you to
select a city from the ones created by the
admin. Used by the home view and html.
"""
class CityForm(forms.ModelForm):
    class Meta:
        model = models.City
        fields = ('city',)
        args = models.City.objects.values_list('id', 'city')
        widgets = {'city': Select(choices=list(args))}
