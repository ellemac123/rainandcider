from django.conf.urls import patterns, include, url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='index'),
    #url(r'detail/(?P<country_code>[A-Z]{2})/$', views.detail, name = 'detail'),
    #url(r'detail/(?P<country_code>[A-Z]{2})/(?P<city_code>([0-9]{1}|[0-9]{2}))/$', views.detail, name = 'detail'),

    # url(r'detail/(?P<country_code>[A-Z]{2})/(?P<city_code>[0-9]{1})/$', views.detail, name = 'detail'),
    ]
