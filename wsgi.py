#!/usr/bin/python
import os
from myproject.wsgi import application

virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/'
virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
try:
    execfile(virtualenv, dict(__file__=virtualenv))
except IOError:
    pass

os.environ["CELERY_LOADER"] = "django"
