from django.conf.urls import patterns, include, url

from django.contrib import admin

from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^', include('rcApp.urls')),
    url(r'^admin/', admin.site.urls),
)
