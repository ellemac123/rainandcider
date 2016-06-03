"""
@author Laura Macaluso
@version 1.3, 06/3/2016

Views.py is is used to call the home page and the detail page.
The detail function will access and cache the data passed to
the detail.html file. This function calls other functions to make
its work easier.

The Twitter API is used to grab 3 local tweets from the city the
user selects. These tweets are selected using the city's
latitude and longitude. The NYTimes API is used to access recent
NYTimes articles based upon the country name. If the country is
the United States of America, then it will grab the recent articles
for the State. Pywapi is used to get the current weather from Weather.com
based upon the city's location id (which is manually imported from the
admin site).
"""
import datetime
import json
import pytz
import pywapi
import urllib2
import us
import logging
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_page
from django_countries.fields import Country
from timezonefinder import TimezoneFinder
from twython import Twython

from .forms import CityForm
from .models import *


twitterHandle = ''
TWITTER_KEY = 'kkgJHe2AJCJ7TEumZa7WZ2pdR'
TWITTER_SECRET = 'z4fl2dFDDiLrV6w66Mpu2hu9lLSW0tEVkBAUTcyhgv2zaj4H6q'
CACHE_TIME_DAY = 86400
CACHE_TIME_FIVE = 60 * 5
logger = logging.getLogger(__name__)

@cache_page(60 * 40)
def home(request):
    logger.debug('The home page was called. ')
    cityform = CityForm()
    if request.method == 'POST':
        cityform = CityForm(request.POST)
        if cityform.is_valid():
            citydata = cityform.cleaned_data
            cityInfo = City.objects.get(id=citydata['city'])
            logger.info('request successfully changed')
            return redirect('detail', country_code=cityInfo.country, city_code=citydata['city'])
    else:
        return render(request, 'home/home.html', {'cityform': cityform})


def detail(request, country_code, city_code):

    if country_code not in countries:
        logger.error('Invalid Country Code Error')
        raise Http404("Invalid Country Code")
    cityData = City.objects.get(id=city_code)

    current_weather = fetchCurrentWeather(city_code, cityData)
    current_icon = fetchCurrentIcon(city_code, current_weather)
    icons = fetchIcons(city_code, current_weather)
    local_timezone = fetchTimezone(city_code, current_weather)
    current_time = datetime.datetime.now(pytz.timezone(local_timezone))

    cityAndState = current_weather['location']['name']
    news = fetchNews(country_code, city_code, cityAndState)
    state = fetchState(country_code, city_code, cityAndState)
    text = fetchTwitter(city_code, current_weather)
    currentText = currentWeatherErrorCheck(current_weather)

    logger.info('data is stored to be passed to detail.html')
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
            'timezone': local_timezone,
            'current_time': current_time,
            'tommDate': current_weather['forecasts'][1]['date'],
            'news': news,
            'date2': current_weather['forecasts'][2]['date'], 'date3': current_weather['forecasts'][3]['date'],
            'day1forecast': current_weather['forecasts'][1]['day']['brief_text'], 'day1Icon': icons[0],
            'day1_precip': current_weather['forecasts'][1]['day']['chance_precip'],
            'day1_high': current_weather['forecasts'][1]['high'],
            'day1_low': current_weather['forecasts'][1]['low'],
            'day2forecast': current_weather['forecasts'][2]['day']['brief_text'], 'day2Icon': icons[1],
            'day2_precip': current_weather['forecasts'][2]['day']['chance_precip'],
            'day2_high': current_weather['forecasts'][2]['high'],
            'day2_low': current_weather['forecasts'][2]['low'],
            'day3forecast': current_weather['forecasts'][3]['day']['brief_text'], 'day3Icon': icons[2],
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


def currentWeatherErrorCheck(current_weather):
    if current_weather['current_conditions']['text'] == '':
        logger.debug('current weather is unavailable - trying to get weather from brief text')
        currentText = current_weather['forecasts'][0]['day']['brief_text']
        if currentText == '':
            currentText = 'information is currently unavailable'
    else:
        currentText = current_weather['current_conditions']['text']

    return currentText


def getState(countryName, cityState):
    state = ' '
    name = str(countryName)
    if name == 'United States of America':
        stateCode = cityState[-2:]
        state = us.states.lookup(stateCode)
        state = state.name + ', '
    return ' ' + state


def getNews(cityState, countryName):
    name = str(countryName)
    if name == 'United States of America':
        stateCode = cityState[-2:]
        state = us.states.lookup(stateCode)
        state = state.name
        name = state
    name = name.replace(' ', '%20')

    try:
        url = 'http://api.nytimes.com/svc/semantic/v2/concept/name/nytd_geo/'\
              + name + '.json?fields=all&api-key=694311ac0a739a6c388fcebe9605c7d9:11:75176215'
        list = []
        f = urllib2.urlopen(url)
        # f = urllib.request.urlopen(url)
        content = f.read()
        decoded_response = content.decode('utf-8')
        jsonResponse = json.loads(decoded_response)

        length = len(jsonResponse["results"][0]["article_list"]["results"])

        if length > 0:
            for x in range(length):
                list.append(jsonResponse["results"][0]["article_list"]["results"][x]["title"])
        else:
            list = ['No Current News to Report']

        return list
    except:
        list = ['No News to Report']
        return list


def findTimezone(lat, long):
    tf = TimezoneFinder()
    point = (float(long), float(lat))
    timezoneName = tf.timezone_at(*point)

    return timezoneName


def tryTwitter(lat, long):
    twitter = Twython(TWITTER_KEY, TWITTER_SECRET, oauth_version=2)
    ACCESS_TOKEN = twitter.obtain_access_token()
    twitter = Twython(TWITTER_KEY, access_token=ACCESS_TOKEN)
    geoString = lat + ',' + long + ',150mi'
    a = twitter.search(q='#news', geocode=geoString, count=10)
    list_length = len(a['statuses'])

    try:
        if list_length > 2:
            text = a['statuses'][0]['text']
            twitterHandle = a['statuses'][0]['user']['screen_name']
            text1 = a['statuses'][1]['text']
            twitterHandle1 = a['statuses'][1]['user']['screen_name']
            text2 = a['statuses'][2]['text']
            twitterHandle2 = a['statuses'][2]['user']['screen_name']
            myList = [text, twitterHandle, text1, twitterHandle1, text2, twitterHandle2]
        else:
            raise Exception
    except:
        text = 'no news to report'
        twitterHandle = ''
        myList = [text, twitterHandle, text, twitterHandle, text, twitterHandle, ]  # , text1, twitterHandle1]

    return myList


def fetchNews(country_code, city_code, cityAndState):
    cityObject = City.objects.get(id=city_code)
    news = cache.get(cityObject.cache_key('news'))
    if news is None:
        news = getNews(cityAndState, countryName=str(Country(country_code).name))
        cache.set(cityObject.cache_key('news'), news, CACHE_TIME_DAY)
    return news


def fetchState(country_code, city_code, cityAndState):
    cityObject = City.objects.get(id=city_code)
    state = cache.get(cityObject.cache_key('state'))
    if state is None:
        state = getState(str(Country(country_code).name), cityAndState)
        cache.set(cityObject.cache_key('state'), state, CACHE_TIME_DAY)
        print(str(cityObject.cache_key('state')))
    return state


def fetchTimezone(city_code, current_weather):
    cityObject = City.objects.get(id=city_code)
    local_timezone = cache.get(cityObject.cache_key('timezone'))
    if local_timezone is None:
        local_timezone = findTimezone(current_weather['location']['lat'], current_weather['location']['lon'])
        cache.set(cityObject.cache_key('timezone'), local_timezone, CACHE_TIME_DAY)
    return local_timezone


def fetchCurrentIcon(city_code, current_weather):
    cityObject = City.objects.get(id=city_code)
    current_icon = cache.get(cityObject.cache_key('current_icon'))
    if current_icon is None:
        icon_num = current_weather['current_conditions']['icon']
        # error handling -- stupid queenstown never has current conditions, so just get their forecast for today
        if icon_num == '':
            icon_num = current_weather['forecasts'][0]['day']['icon']
        current_icon = 'http://l.yimg.com/a/i/us/we/52/{}.gif'.format(icon_num)
        cache.set(cityObject.cache_key('current_icon'), current_icon, CACHE_TIME_FIVE)
    return current_icon


def fetchIcons(city_code, current_weather):
    cityObject = City.objects.get(id=city_code)
    icons = cache.get(cityObject.cache_key('icons'))
    if icons is None:
        day1_icon = 'http://l.yimg.com/a/i/us/we/52/{}.gif'.format(current_weather['forecasts'][1]['day']['icon'])
        day2_icon = 'http://l.yimg.com/a/i/us/we/52/{}.gif'.format(current_weather['forecasts'][2]['day']['icon'])
        day3_icon = 'http://l.yimg.com/a/i/us/we/52/{}.gif'.format(current_weather['forecasts'][3]['day']['icon'])
        icons = [day1_icon, day2_icon, day3_icon]
        cache.set(cityObject.cache_key('icons'), icons, CACHE_TIME_FIVE)

    return icons


def fetchCurrentWeather(city_code, cityData):
    cityObject = City.objects.get(id=city_code)
    current_weather = cache.get(cityObject.cache_key('current_weather'))
    if current_weather is None:
        current_weather = pywapi.get_weather_from_weather_com(cityData.location_id)
        cache.set(cityObject.cache_key('current_weather'), current_weather, CACHE_TIME_FIVE)
    return current_weather


def fetchTwitter(city_code, current_weather):
    cityObject = City.objects.get(id=city_code)
    text = cache.get(cityObject.cache_key('twitter'))
    if text is None:
        text = tryTwitter(current_weather['location']['lat'], current_weather['location']['lon'])
        cache.set(cityObject.cache_key('twitter'), text, CACHE_TIME_FIVE)
    return text


"""
@param country_code  the country code of the given city
@param city_code     the id of the given city. This is used to get
                        the city object.

This method is used to update the caches for the city. This will
make repeat calls to a city (with or without celery) much faster.
This is the method called by the celery task. It will constantly
update the cities in the background so that the user has no wait time.
"""
def update_city(country_code, city_code):
    cityData = City.objects.get(id=city_code)

    current_weather = fetchCurrentWeather(city_code, cityData)
    fetchCurrentIcon(city_code, current_weather)
    fetchIcons(city_code, current_weather)
    local_timezone = fetchTimezone(city_code, current_weather)
    datetime.datetime.now(pytz.timezone(local_timezone))

    cityAndState = current_weather['location']['name']
    fetchNews(country_code, city_code, cityAndState)
    fetchState(country_code, city_code, cityAndState)
    fetchTwitter(city_code, current_weather)
    currentWeatherErrorCheck(current_weather)
    print("inside update city method")
