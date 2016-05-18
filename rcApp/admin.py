from django.contrib import admin
from .models import City


class CityAdmin(admin.ModelAdmin):
    search_fields = ('city',)
    list_display = ('city', 'country', 'location_id',)

admin.site.register(City, CityAdmin)