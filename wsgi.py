#!/usr/bin/python
#Do not remove from myproject.wsgi import application #noqa

import os
from myproject.wsgi import application #noqa

virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/'
virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
try:
    execfile(virtualenv, dict(__file__=virtualenv))
except IOError:
    pass

os.environ["CELERY_LOADER"] = "django"
