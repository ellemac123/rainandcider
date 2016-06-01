from __future__ import absolute_import
import os
from celery import Celery
from celery.utils.log import get_task_logger
from .views import *
BROKER_URL = "redis://:{}@{}:{}".format(os.environ.get('OPENSHIFT_REDIS_PASSWORD', ''),
                                        os.environ.get('OPENSHIFT_REDIS_HOST', ''),
                                        os.environ.get('OPENSHIFT_REDIS_PORT', ''))

#app = Celery('tasks', broker=BROKER_URL, backend=BROKER_URL)
app = Celery('tasks')
logger = get_task_logger('raincider')

@app.task(run_every=10, name="update_cache")
def update_cache():
    """
    This will update the cache so that the user
    'never' has to wait for content to load
    """
    logger.debug('Called the cache')
    for city in City.objects.all():
        update_city(city.country, city.pk)
        logger.debug("updated the cache of : " + str(city.pk))
