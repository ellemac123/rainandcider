import datetime
import json

import pytz
import pywapi
import urllib2
import us
from django.contrib import messages
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


@cache_page(60 * 40)
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
        return render(request, 'home/home.html', {'cityform': cityform})


def detail(request, country_code, city_code):
    if country_code not in countries:
        raise Http404("Invalid Country Code")
    cityData = City.objects.get(id=city_code)

    current_weather = fetchCurrentWeather(country_code, city_code, cityData)
    current_icon = fetchCurrentIcon(country_code, city_code, current_weather)
    icons = fetchIcons(country_code, city_code, current_weather)
    local_timezone = fetchTimezone(country_code, city_code, current_weather)
    current_time = datetime.datetime.now(pytz.timezone(local_timezone))

    cityAndState = current_weather['location']['name']
    news = fetchNews(country_code, city_code, cityAndState)
    state = fetchState(country_code, city_code, cityAndState)
    text = fetchTwitter(country_code, city_code, current_weather)
    currentText = currentWeatherErrorCheck(current_weather)

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
        currentText = current_weather['forecasts'][0]['day']['brief_text']
        if currentText == '':
            currentText = 'information is currently unavailable'
    else:
        currentText = current_weather['current_conditions']['text'] + ' and'

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
        url = 'http://api.nytimes.com/svc/semantic/v2/concept/name/nytd_geo/' + name + '.json?fields=all&api-key=694311ac0a739a6c388fcebe9605c7d9:11:75176215'
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

    return myList;


def fetchNews(country_code, city_code, cityAndState):
    # news = cache.get('news_{}_{}'.format(country_code, city_code))
    cityObject = City.objects.get(id=city_code)
    news = cache.get(cityObject.cache_key('news'))
    if news is None:
        news = getNews(cityAndState, countryName=str(Country(country_code).name))
        cache.set(cityObject.cache_key('news'), news, CACHE_TIME_DAY)
        # cache.set('news_{}_{}'.format(country_code, city_code), news, CACHE_TIME_DAY)
    return news


def fetchState(country_code, city_code, cityAndState):
    # state = cache.get('state_{}_{}'.format(country_code, city_code))
    cityObject = City.objects.get(id=city_code)
    state = cache.get(cityObject.cache_key('state'))
    if state is None:
        state = getState(str(Country(country_code).name), cityAndState)
        # cache.set('state_{}_{}'.format(country_code, city_code), state, CACHE_TIME_DAY)
        cache.set(cityObject.cache_key('state'), state)
        print(cityObject.cache_key('state'))
    return state


def fetchTimezone(country_code, city_code, current_weather):
    cityObject = City.objects.get(id=city_code)
    local_timezone = cache.get(cityObject.cache_key('timezone'))
    #local_timezone = cache.get('timezone_{}_{}'.format(country_code, city_code))
    if local_timezone is None:
        local_timezone = findTimezone(current_weather['location']['lat'], current_weather['location']['lon'])
        cache.set(cityObject.cache_key('timezone'), local_timezone, CACHE_TIME_DAY)

        # cache.set('timezone_{}_{}'.format(country_code, city_code), local_timezone, CACHE_TIME_DAY)
    return local_timezone


def fetchCurrentIcon(country_code, city_code, current_weather):
    current_icon = cache.get('currentIcon_{}_{}'.format(country_code, city_code))
    if current_icon is None:
        icon_num = current_weather['current_conditions']['icon']
        # error handling -- stupid queenstown never has current conditions, so just get their forecast for today
        if icon_num == '':
            icon_num = current_weather['forecasts'][0]['day']['icon']
        current_icon = 'http://l.yimg.com/a/i/us/we/52/{}.gif'.format(icon_num)
        cache.set('currentIcon_{}_{}'.format(country_code, city_code), current_icon, CACHE_TIME_FIVE)
    return current_icon


def fetchIcons(country_code, city_code, current_weather):
    icons = cache.get('icon_{}_{}'.format(country_code, city_code))
    if icons is None:
        day1_icon = 'http://l.yimg.com/a/i/us/we/52/{}.gif'.format(current_weather['forecasts'][1]['day']['icon'])
        day2_icon = 'http://l.yimg.com/a/i/us/we/52/{}.gif'.format(current_weather['forecasts'][2]['day']['icon'])
        day3_icon = 'http://l.yimg.com/a/i/us/we/52/{}.gif'.format(current_weather['forecasts'][3]['day']['icon'])
        icons = [day1_icon, day2_icon, day3_icon]
        cache.set('icon_{}_{}'.format(country_code, city_code), icons, CACHE_TIME_FIVE)
    return icons


def fetchCurrentWeather(country_code, city_code, cityData):
    current_weather = cache.get('weather_{}_{}'.format(country_code, city_code))
    if current_weather is None:
        current_weather = pywapi.get_weather_from_weather_com(cityData.location_id)
        cache.set('weather_{}_{}'.format(country_code, city_code), current_weather, CACHE_TIME_FIVE)
    return current_weather


def fetchTwitter(country_code, city_code, current_weather):
    text = cache.get('twitter_{}_{}'.format(country_code, city_code))
    if text is None:
        text = tryTwitter(current_weather['location']['lat'], current_weather['location']['lon'])
        cache.set('twitter_{}_{}'.format(country_code, city_code), text, CACHE_TIME_FIVE)
    return text


    #
    # current_time = cache.get('currentTime_{}_{}'.format(country_code, city_code))
    # if current_time is None:
    #     current_time = datetime.datetime.now(pytz.timezone(local_timezone))
    #     cache.set('currentTime_{}_{}'.format(country_code, city_code), current_time, CACHE_TIME_FIVE)
