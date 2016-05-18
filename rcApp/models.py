from django.db import models
from django_countries import countries
from django_countries.fields import CountryField


def en_zed():
    return 'NZ'


''' changed country field from choices=list(countries) '''


class City(models.Model):
    country = CountryField(choices=list(countries));  # hold the country co
    city = models.CharField(max_length=20);
    location_id = models.CharField(max_length=8);

    def __str__(self):
        return self.city


class AllowNull(models.Model):
    country = CountryField(null=True, blank_label='(select country)')
