from django.contrib import admin

from .models import City


class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', 'country', 'location_id')
    search_fields = ('id', 'city', 'country', 'location_id')

admin.site.register(City, CityAdmin)
