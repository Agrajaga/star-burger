from datetime import datetime

from django.conf import settings
from django.db import models
from django.dispatch import receiver
from geopy.exc import GeopyError
from geopy.geocoders import Yandex


class GeoPoint(models.Model):
    address = models.CharField(
        'адрес',
        max_length=150,
        db_index=True,
        unique=True,
    )
    normalized_address = models.CharField(
        'нормализованый адрес',
        max_length=150,
        db_index=True,
    )
    latitude = models.DecimalField(
        'широта',
        db_index=True,
        decimal_places=6,
        max_digits=8,
        null=True,
    )
    longitude = models.DecimalField(
        'долгота',
        db_index=True,
        decimal_places=6,
        max_digits=8,
        null=True,
    )
    timestamp = models.DateTimeField(
        'дата обновления',
        editable=False,
    )


@receiver(models.signals.pre_save, sender=GeoPoint)
def fill_coordinates(sender, instance, **kwargs):
    if not instance.timestamp:
        try:
            geocoder = Yandex(api_key=settings.YANDEX_API_KEY)
            normalized_address, coords = geocoder.geocode(instance.address)
            instance.normalized_address = normalized_address
            instance.latitude, instance.longitude = coords
        except (GeopyError, TypeError):
            instance.normalized_address = 'нет данных'

        instance.timestamp = datetime.now()
