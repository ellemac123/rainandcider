import json
import urllib2
import pywapi
import pytz
import datetime
import us

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django_countries import countries
from django_countries.fields import Country
from timezonefinder import TimezoneFinder
from twython import Twython
from django.core.cache import cache, caches
from django.views.decorators.cache import cache_page
from .forms import CityForm
from .models import *

twitterHandle = ''
TWITTER_KEY = 'kkgJHe2AJCJ7TEumZa7WZ2pdR'
TWITTER_SECRET = 'z4fl2dFDDiLrV6w66Mpu2hu9lLSW0tEVkBAUTcyhgv2zaj4H6q'

@cache_page(60 * 5)
def home(request):
    cityform = CityForm()

    if request.method == 'POST':
        cityform = CityForm(request.POST)
        if cityform.is_valid():
            citydata = cityform.cleaned_data
            cityInfo = City.objects.get(id=citydata['city'])

            messages.success(request, 'Successfully Changed')
            return redirect('detail', country_code=cityInfo.country, city_code=citydata['city'])
    else:
        cityform = CityForm()
        return render(request, 'home/home.html', {'cityform': cityform})


def detail(request, country_code, city_code):
    if country_code not in countries:
        raise Http404("Invalid Country Code")
    cityData = City.objects.get(id=city_code)


    current_weather = cache.get('weather_{}_{}'.format(country_code, city_code))
    if current_weather is None:
        current_weather = pywapi.get_weather_from_weather_com(cityData.location_id)
        cache.set('weather_{}_{}'.format(country_code, city_code), current_weather)



    # this is to handle errors occuring from Queenstown - no current conditions so gets forecast for the day
    if current_weather['current_conditions']['text'] == '':
        currentText = current_weather['forecasts'][0]['day']['brief_text']
        if currentText == '':
            currentText = 'information is currently unavailable'
    else:
        currentText = current_weather['current_conditions']['text'] + ' and'


    icon_num = current_weather['current_conditions']['icon']
    # error handling -- stupid queenstown never has current conditions, so just get their forecast for today
    if icon_num == '':
        icon_num = current_weather['forecasts'][0]['day']['icon']

    current_icon = 'http://l.yimg.com/a/i/us/we/52/{}.gif'.format(icon_num)
    cityAndState = current_weather['location']['name']



    #Cache the news here
    print("this is the caches instances : " + str(caches.all()))
    print(" ")
    print("this is what cache value is :    " + str(cache.get('news')))
    news = cache.get('news')
    if cache.get('news') is None:
        news = getNews(cityAndState, countryName=str(Country(country_code).name))
        cache.set('news', news, 280000) #timeout is a :day - then the news will refresh
        print("This is the cache value AFTER 'caching' : " + str(cache.get('news')))
        print("caching the news")

    #cache state
    print("state cash is " + str(cache.get('state')))
    state = cache.get('state')
    if state is None:
        state = getState(str(Country(country_code).name), cityAndState)
        cache.set('state', state, 280000)

    icon1_num = current_weather['forecasts'][1]['day']['icon']
    day1_icon = 'http://l.yimg.com/a/i/us/we/52/{}.gif'.format(icon1_num)
    icon2_num = current_weather['forecasts'][2]['day']['icon']
    day2_icon = 'http://l.yimg.com/a/i/us/we/52/{}.gif'.format(icon2_num)
    icon3_num = current_weather['forecasts'][3]['day']['icon']
    day3_icon = 'http://l.yimg.com/a/i/us/we/52/{}.gif'.format(icon3_num)

    #cache twitter
    text = cache.get('twitter')
    if text is None:
        text = tryTwitter(current_weather['location']['lat'], current_weather['location']['lon'])
        cache.set('twitter', text, 280000)


    local_timezone = findTimezone(current_weather['location']['lat'], current_weather['location']['lon'])
    current_time = datetime.datetime.now(pytz.timezone(local_timezone))


    data = {'country': Country(country_code), 'city': cityData, 'state': state,
            'current_conditions': currentText,
            'current_temperature': current_weather['current_conditions']['temperature'],
            'temperature_units': current_weather['units']['temperature'], 'current_icon': current_icon,
            'last_update': current_weather['current_conditions']['last_updated'],
            'feels_like': current_weather['current_conditions']['feels_like'],
            'chance_precip': current_weather['forecasts'][0]['day']['chance_precip'],
            'wind_direction': current_weather['current_conditions']['wind']['text'],
            'wind': current_weather['current_conditions']['wind']['speed'],
            'humidity': current_weather['current_conditions']['humidity'],
            'day0_high': current_weather['forecasts'][0]['high'],
            'day0_low': current_weather['forecasts'][0]['low'],
            'speed_units': current_weather['units']['speed'], 'twitterText': text[0], 'twitterHandle': text[1],
            'twitterText1': text[2], 'twitterHandle1': text[3], 'twitterText2': text[4], 'twitterHandle2': text[5],
            'timezone': local_timezone, 'current_time': current_time,
            'tommDate': current_weather['forecasts'][1]['date'],
            'news': news,
            'date2': current_weather['forecasts'][2]['date'], 'date3': current_weather['forecasts'][3]['date'],
            'day1forecast': current_weather['forecasts'][1]['day']['brief_text'], 'day1Icon': day1_icon,
            'day1_precip': current_weather['forecasts'][1]['day']['chance_precip'],
            'day1_high': current_weather['forecasts'][1]['high'],
            'day1_low': current_weather['forecasts'][1]['low'],
            'day2forecast': current_weather['forecasts'][2]['day']['brief_text'], 'day2Icon': day2_icon,
            'day2_precip': current_weather['forecasts'][2]['day']['chance_precip'],
            'day2_high': current_weather['forecasts'][2]['high'],
            'day2_low': current_weather['forecasts'][2]['low'],
            'day3forecast': current_weather['forecasts'][3]['day']['brief_text'], 'day3Icon': day3_icon,
            'day3_precip': current_weather['forecasts'][3]['day']['chance_precip'],
            'day3_high': current_weather['forecasts'][3]['high'],
            'day3_low': current_weather['forecasts'][3]['low'],
            'wind1': current_weather['forecasts'][1]['day']['wind']['speed'],
            'wind2': current_weather['forecasts'][2]['day']['wind']['speed'],
            'wind3': current_weather['forecasts'][3]['day']['wind']['speed'],
            'wind1_direction': current_weather['forecasts'][1]['day']['wind']['text'],
            'wind2_direction': current_weather['forecasts'][2]['day']['wind']['text'],
            'wind3_direction': current_weather['forecasts'][3]['day']['wind']['text']}
    return render(request, 'country/detail.html', data)
