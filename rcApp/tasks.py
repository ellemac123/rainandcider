from __future__ import absolute_import
import os
from celery import Celery
from celery.utils.log import get_task_logger
from .views import *
BROKER_URL = "redis://:{}@{}:{}".format(os.environ.get('OPENSHIFT_REDIS_PASSWORD', ''),
                                        os.environ.get('OPENSHIFT_REDIS_HOST', ''),
                                        os.environ.get('OPENSHIFT_REDIS_PORT', ''))
app = Celery('tasks')
logger = get_task_logger('raincider')

"""
@:param run_every   The task will run every 10 seconds
@:param name        The name of the task is update_cache
Update_cache will be called by the celery beat and the
cache will call update_city for each city each time
this is called. This is so the users will 'never' have
to wait for the page to load.
"""
@app.task(run_every=10, name="update_cache")
def update_cache():
    logger.debug('Called the cache')
    for city in City.objects.all():
        update_city(city.country, city.pk)
        logger.debug("updated the cache of : " + str(city.pk))
