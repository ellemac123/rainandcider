from django.shortcuts import redirect, render
from django.shortcuts import render_to_response

from .forms import CityForm
from .models import *


def home(request):
    if request.method == 'POST':
        cityform = CityForm(request.POST)
        if cityform.is_valid():
            citydata = cityform.cleaned_data
            cityInfo = City.objects.get(id=citydata['city'])

            # messages.success(request, 'Successfully Changed')
        return redirect('country:detail', country_code=cityInfo.country, city_code=citydata['city'])

    return render_to_response('home/home.html')


def detail(request, country_code, city_code):
    data = {'country': country_code, 'city': city_code, }
    return render(request, 'country/detail.html', data)
