"""
@author Laura Macaluso
@version 1.3, 06/3/2016

Models.py creates a city model that will
hold each city created by the admin. Uses the
django_countries package.
"""
from django.db import models
from django_countries import countries
from django_countries.fields import CountryField



class City(models.Model):
    """
    This is the city model. It has three fields:
    country, which holds the country name, using
    django countries, city, which holds the city
    name, and location_id, which is the location
    id from weather.com. The location_id is used
    to get the weather forecast from pywapi.
    """
    country = CountryField(choices=list(countries))
    city = models.CharField(max_length=20)
    location_id = models.CharField(max_length=8)

    def cache_key(self, type):
        return "{}_{}_{}".format(type, self.country, self.id)

    def __str__(self):
        return self.city

