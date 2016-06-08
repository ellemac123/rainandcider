import json
import logging
import urllib2

import pywapi
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


def weather_error_check(current_weather):
    if current_weather['current_conditions']['text'] == '':
        logger.debug('current weather is unavailable - trying to get weather from brief text')
        current_text = current_weather['forecasts'][0]['day']['brief_text']
        if current_text == '':
            current_text = 'information is currently unavailable'
    else:
        current_text = current_weather['current_conditions']['text']

    return current_text


def get_state(countryName, cityState):
    state = ' '
    name = str(countryName)
    if name == 'United States of America':
        state_code = cityState[-2:]
        state = us.states.lookup(state_code)
        state = state.name + ', '
    return ' ' + state


def get_news(city_state, country_name):
    """
    @param city_state       the city and state string used to pass to the
                                news. The API uses it to get the news from the
                                state if there is a state, and if not it will use
                                the country name.
    @:param country_name    the name of the country. used to get the country news.

    This function with get the country or state news from the NYTimes using the
    NYTimes api. The url contains the api-key which is unique. It is given to
    developers that are registered to grab data via searches. This data is in json
    and is parsed here.
    """
    name = str(country_name)
    if name == 'United States of America':
        state_code = city_state[-2:]
        state = us.states.lookup(state_code)
        state = state.name
        name = state
    name = name.replace(' ', '%20')

    try:
        url = 'http://api.nytimes.com/svc/semantic/v2/concept/name/nytd_geo/' \
              + name + '.json?fields=all&api-key=694311ac0a739a6c388fcebe9605c7d9:11:75176215'
        news_list = []
        f = urllib2.urlopen(url)
        # f = urllib.request.urlopen(url)
        content = f.read()
        decoded_response = content.decode('utf-8')
        json_response = json.loads(decoded_response)

        length = len(json_response["results"][0]["article_list"]["results"])

        if length > 0:
            for x in range(length):
                news_list.append(json_response["results"][0]["article_list"]["results"][x]["title"])
        else:
            news_list = ['No Current News to Report']

        return news_list
    except:
        news_list = ['No News to Report']
        return news_list


def find_timezone(latitude, longitude):
    tf = TimezoneFinder()
    geo_point = (float(longitude), float(latitude))
    timezone_name = tf.timezone_at(*geo_point)

    return timezone_name


def get_twitter_data(latitude, longitude):
    distance = '150'
    twitter = Twython(TWITTER_KEY, TWITTER_SECRET, oauth_version=2)
    access_token = twitter.obtain_access_token()
    twitter = Twython(TWITTER_KEY, access_token=access_token)
    geo_string = latitude + ',' + longitude + ',150mi'
    a = twitter.search(q='#news', geocode=geo_string, count=10)
    list_length = len(a['statuses'])
    try:
        if list_length > 2:
            text = a['statuses'][0]['text']
            twitter_handle = a['statuses'][0]['user']['screen_name']
            text1 = a['statuses'][1]['text']
            twitter_handle1 = a['statuses'][1]['user']['screen_name']
            text2 = a['statuses'][2]['text']
            twitter_handle2 = a['statuses'][2]['user']['screen_name']
            my_list = [text, twitter_handle, text1, twitter_handle1, text2, twitter_handle2]
        else:
            raise Exception
    except:
        text = 'no news to report'
        twitter_handle = ''
        my_list = [text, twitter_handle, text, twitter_handle, text, twitter_handle, ]  # , text1, twitterHandle1]

    return my_list


def cache_news(country_code, city_object, city_state):
    news = cache.get(city_object.cache_key('news'))
    if news is None:
        news = get_news(city_state, country_name=str(Country(country_code).name))
        cache.set(city_object.cache_key('news'), news, CACHE_TIME_DAY)
    return news


def cache_state(country_code, city_object, city_state):
    state = cache.get(city_object.cache_key('state'))
    if state is None:
        state = get_state(str(Country(country_code).name), city_state)
        cache.set(city_object.cache_key('state'), state, CACHE_TIME_DAY)
        print(str(city_object.cache_key('state')))
    return state


def cache_timezone(city_object, current_weather):
    local_timezone = cache.get(city_object.cache_key('timezone'))
    if local_timezone is None:
        local_timezone = find_timezone(current_weather['location']['lat'], current_weather['location']['lon'])
        cache.set(city_object.cache_key('timezone'), local_timezone, CACHE_TIME_DAY)
    return local_timezone


def cache_current_icon(city_object, current_weather):
    current_icon = cache.get(city_object.cache_key('current_icon'))
    if current_icon is None:
        icon_num = current_weather['current_conditions']['icon']
        # if no current conditions, get day forecast
        if icon_num == '':
            icon_num = current_weather['forecasts'][0]['day']['icon']
        current_icon = 'http://l.yimg.com/a/i/us/we/52/{}.gif'.format(icon_num)
        cache.set(city_object.cache_key('current_icon'), current_icon, CACHE_TIME_FIVE)
    return current_icon


def cache_forecast_icons(city_object, current_weather):
    icons = cache.get(city_object.cache_key('icons'))
    if icons is None:
        day1_icon = 'http://l.yimg.com/a/i/us/we/52/{}.gif'.format(current_weather['forecasts'][1]['day']['icon'])
        day2_icon = 'http://l.yimg.com/a/i/us/we/52/{}.gif'.format(current_weather['forecasts'][2]['day']['icon'])
        day3_icon = 'http://l.yimg.com/a/i/us/we/52/{}.gif'.format(current_weather['forecasts'][3]['day']['icon'])
        icons = [day1_icon, day2_icon, day3_icon]
        cache.set(city_object.cache_key('icons'), icons, CACHE_TIME_FIVE)

    return icons


def cache_current_weather_data(city_object):
    current_weather = cache.get(city_object.cache_key('current_weather'))
    if current_weather is None:
        current_weather = pywapi.get_weather_from_weather_com(city_object.location_id)
        cache.set(city_object.cache_key('current_weather'), current_weather, CACHE_TIME_FIVE)
    return current_weather


def cache_twitter(city_object, current_weather):
    text = cache.get(city_object.cache_key('twitter'))
    if text is None:
        text = get_twitter_data(current_weather['location']['lat'], current_weather['location']['lon'])
        cache.set(city_object.cache_key('twitter'), text, CACHE_TIME_FIVE)
    return text
