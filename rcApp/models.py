"""
@author Laura Macaluso
@version 1.3, 06/3/2016

Models.py creates 
"""
from django.db import models
from django_countries import countries
from django_countries.fields import CountryField


def en_zed():
    return 'NZ'


class City(models.Model):
    country = CountryField(choices=list(countries))
    city = models.CharField(max_length=20)
    location_id = models.CharField(max_length=8)

    def cache_key(self, type):
        return "{}_{}_{}".format(type, self.country, self.id)

    def __str__(self):
        return self.city


class AllowNull(models.Model):
    country = CountryField(null=True, blank_label='(select country)')
