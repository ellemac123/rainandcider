import logging
import us

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
