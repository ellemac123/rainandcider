from django.shortcuts import redirect, render
from django.contrib import messages

from .forms import CityForm
from .models import *


def home(request):
    cityform = CityForm()

    if request.method == 'POST':
        cityform = CityForm(request.POST)
        if cityform.is_valid():
            citydata = cityform.cleaned_data
            cityInfo = City.objects.get(id=citydata['city'])

            messages.success(request, 'Successfully Changed')
            return redirect('country:detail', country_code=cityInfo.country, city_code=citydata['city'])
    else:
        cityform = CityForm()
    return render(request, 'index.html', {'cityform': cityform})


def detail(request, country_code, city_code):
    data = {'country': country_code, 'city': city_code, }
    return render(request, 'country/detail.html', data)
