from django.contrib import admin

from .models import City


class CityAdmin(admin.ModelAdmin):
    fields = ('id', 'city')


admin.site.register(City, CityAdmin)
