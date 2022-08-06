from django.contrib import admin
from .models import GeoPoint


@admin.register(GeoPoint)
class GeoPointAdmin(admin.ModelAdmin):
    list_display = [
        'calculated',
        'address',
        'normalized_address',
        'latitude',
        'longitude',
        'timestamp',
    ]
