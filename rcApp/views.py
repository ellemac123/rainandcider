"""
@author Laura Macaluso
@version 1.3, 06/3/2016

Views.py is is used to call the home page and the detail page.
The detail function will access and cache the data passed to
the detail.html file. This function calls other functions to make
its work easier.

The Twython Twitter API is used to grab 3 local tweets from the city the
user selects. These tweets are selected using the city's
latitude and longitude. The NYTimes API is used to access recent
NYTimes articles based upon the country name. If the country is
the United States of America, then it will grab the recent articles
for the State. Pywapi is used to get the current weather from Weather.com
based upon the city's location id (which is manually inputted from the
admin site by the user). Timezonefinder package is also used to fine the
timezone and thus get the current time for the location.
"""

import datetime

import pytz
from django.http import Http404
from django.shortcuts import redirect, render

from .city_utils import *
from .forms import CityForm
from .models import *

twitterHandle = ''
TWITTER_KEY = 'kkgJHe2AJCJ7TEumZa7WZ2pdR'
TWITTER_SECRET = 'z4fl2dFDDiLrV6w66Mpu2hu9lLSW0tEVkBAUTcyhgv2zaj4H6q'
CACHE_TIME_DAY = 86400
CACHE_TIME_FIVE = 60 * 5
logger = logging.getLogger(__name__)


def home(request):
    """
    @:param request

    The request to the home page. Uses the city form
    to get the city object that the user chooses.
    Uses the request.POST to use the home.html csrf
    token. Will also redirect the user to the detail
    page and the detail method based
    """
    logger.debug('The home page was called. ')
    cityform = CityForm()
    if request.method == 'POST':
        cityform = CityForm(request.POST)
        if cityform.is_valid():
            citydata = cityform.cleaned_data
            cityInfo = citydata['city']
            logger.info('request successfully changed')
            print(str(cityInfo.city))
            return redirect('detail', country_code=cityInfo.country, city_code=cityInfo.id)
    else:
        return render(request, 'home/home.html', {'cityform': cityform})


def detail(request, country_code, city_code):
    """
    @:param request        The request to be rendered upon return.
    @:param country_code   The country code of the given city object.
                                Used to create the country name.
    @:param city_code      The city id. This is the id automattically
                                created. Used to create a city object.
    The detail gets the data, checks if it has been cached, and if not
    it will cache the data. then it passes all that data to the
    detail.html file. The data is stored with a name, those names are
    used to access the data in detail.html
    """
    if country_code not in countries:
        logger.error('Invalid Country Code Error')
        raise Http404("Invalid Country Code")
    city_data = City.objects.get(id=city_code)

    current_weather = cache_current_weather_data(city_data)
    current_icon = cache_current_icon(city_data, current_weather)
    icons = cache_forecast_icons(city_data, current_weather)
    local_timezone = cache_timezone(city_data, current_weather)
    current_time = datetime.datetime.now(pytz.timezone(local_timezone))

    city_state = current_weather['location']['name']
    news = cache_news(country_code, city_data, city_state)
    state = cache_state(country_code, city_data, city_state)
    text = cache_twitter(city_data, current_weather)
    current_text = weather_error_check(current_weather)

    logger.info('data is stored to be passed to detail.html')
    data = {'country': Country(country_code), 'city': city_data, 'state': state,
            'current_conditions': current_text,
            'temperature_units': current_weather['units']['temperature'],
            'current_icon': current_icon,
            'chance_precip': current_weather['forecasts'][0]['day']['chance_precip'],
            'current_weather': current_weather['current_conditions'],
            'day_forecast': current_weather['forecasts'],
            'twitter_text': text,
            'speed_units': current_weather['units']['speed'],
            'timezone': local_timezone,
            'current_time': current_time,
            'news': news, 'icons': icons}
    return render(request, 'country/detail.html', data)


def update_city(country_code, city_code):
    """
    @param country_code  the country code of the given city
    @param city_code     the id of the given city. This is used to get
                            the city object.

    This method is used to update the caches for the city. This will
    make repeat calls to a city (with or without celery) much faster.
    This is the method called by the celery task. It will constantly
    update the cities in the background so that the user has no wait time.
    """
    city_data = City.objects.get(id=city_code)

    current_weather = cache_current_weather_data(city_data)
    cache_current_icon(city_data, current_weather)
    cache_forecast_icons(city_data, current_weather)
    local_timezone = cache_timezone(city_data, current_weather)
    datetime.datetime.now(pytz.timezone(local_timezone))

    city_state = current_weather['location']['name']
    cache_news(country_code, city_data, city_state)
    cache_state(country_code, city_data, city_state)
    cache_twitter(city_data, current_weather)
    weather_error_check(current_weather)
    print("inside update city method")
