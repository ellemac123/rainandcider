import os
from django.conf import settings
#from celery import Celery
import celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")

app = celery.Celery('myproject')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda : settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))