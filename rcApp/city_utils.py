import json
import logging
import logging
import urllib2

import datetime
import pytz
import pywapi
import us
import us
from django.core.cache import cache
from django_countries.fields import Country
from timezonefinder import TimezoneFinder
from twython import Twython

twitterHandle = ''
TWITTER_KEY = 'kkgJHe2AJCJ7TEumZa7WZ2pdR'
TWITTER_SECRET = 'z4fl2dFDDiLrV6w66Mpu2hu9lLSW0tEVkBAUTcyhgv2zaj4H6q'
CACHE_TIME_DAY = 86400
CACHE_TIME_FIVE = 60 * 5
logger = logging.getLogger(__name__)


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
    """
    @param cityState       the city and state string used to pass to the
                                news. The API uses it to get the news from the
                                state if there is a state, and if not it will use
                                the country name.
    @:param countryName    the name of the country. used to get the country news.

    This function with get the country or state news from the NYTimes using the
    NYTimes api. The url contains the api-key which is unique. It is given to
    developers that are registered to grab data via searches. This data is in json
    and is parsed here.
    """

    name = str(countryName)
    if name == 'United States of America':
        stateCode = cityState[-2:]
        state = us.states.lookup(stateCode)
        state = state.name
        name = state
    name = name.replace(' ', '%20')

    try:
        url = 'http://api.nytimes.com/svc/semantic/v2/concept/name/nytd_geo/' \
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
    distance = '150'
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


def fetchNews(country_code, cityObject, cityAndState):
    news = cache.get(cityObject.cache_key('news'))
    if news is None:
        news = getNews(cityAndState, countryName=str(Country(country_code).name))
        cache.set(cityObject.cache_key('news'), news, CACHE_TIME_DAY)
    return news


def fetchState(country_code, cityObject, cityAndState):
    state = cache.get(cityObject.cache_key('state'))
    if state is None:
        state = getState(str(Country(country_code).name), cityAndState)
        cache.set(cityObject.cache_key('state'), state, CACHE_TIME_DAY)
        print(str(cityObject.cache_key('state')))
    return state


def fetchTimezone(cityObject, current_weather):
    local_timezone = cache.get(cityObject.cache_key('timezone'))
    if local_timezone is None:
        local_timezone = findTimezone(current_weather['location']['lat'], current_weather['location']['lon'])
        cache.set(cityObject.cache_key('timezone'), local_timezone, CACHE_TIME_DAY)
    return local_timezone


def fetchCurrentIcon(cityObject, current_weather):
    current_icon = cache.get(cityObject.cache_key('current_icon'))
    if current_icon is None:
        icon_num = current_weather['current_conditions']['icon']
        # if no current conditions, get day forecast
        if icon_num == '':
            icon_num = current_weather['forecasts'][0]['day']['icon']
        current_icon = 'http://l.yimg.com/a/i/us/we/52/{}.gif'.format(icon_num)
        cache.set(cityObject.cache_key('current_icon'), current_icon, CACHE_TIME_FIVE)
    return current_icon


def fetchIcons(cityObject, current_weather):
    icons = cache.get(cityObject.cache_key('icons'))
    if icons is None:
        day1_icon = 'http://l.yimg.com/a/i/us/we/52/{}.gif'.format(current_weather['forecasts'][1]['day']['icon'])
        day2_icon = 'http://l.yimg.com/a/i/us/we/52/{}.gif'.format(current_weather['forecasts'][2]['day']['icon'])
        day3_icon = 'http://l.yimg.com/a/i/us/we/52/{}.gif'.format(current_weather['forecasts'][3]['day']['icon'])
        icons = [day1_icon, day2_icon, day3_icon]
        cache.set(cityObject.cache_key('icons'), icons, CACHE_TIME_FIVE)

    return icons


def fetchCurrentWeather(cityObject):
    current_weather = cache.get(cityObject.cache_key('current_weather'))
    if current_weather is None:
        current_weather = pywapi.get_weather_from_weather_com(cityObject.location_id)
        cache.set(cityObject.cache_key('current_weather'), current_weather, CACHE_TIME_FIVE)
    return current_weather


def fetchTwitter(cityObject, current_weather):
    text = cache.get(cityObject.cache_key('twitter'))
    if text is None:
        text = tryTwitter(current_weather['location']['lat'], current_weather['location']['lon'])
        cache.set(cityObject.cache_key('twitter'), text, CACHE_TIME_FIVE)
    return text
