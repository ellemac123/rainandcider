from __future__ import absolute_import

from django.conf import settings
from celery import Celery

app = Celery('myproject')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda : settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))