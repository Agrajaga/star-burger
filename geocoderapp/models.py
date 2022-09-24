from datetime import datetime

from django.conf import settings
from django.db import models
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
    calculated = models.BooleanField(
        'адрес обработан',
        default=False,
    )

    def fill_coordinates(self):
        try:
            geocoder = Yandex(api_key=settings.YANDEX_API_KEY)
            normalized_address, coords = geocoder.geocode(self.address)
            self.normalized_address = normalized_address
            self.latitude, self.longitude = coords
            self.calculated = True
        except (GeopyError, TypeError):
            self.normalized_address = ''
            self.latitude, self.longitude = None, None
            self.calculated = False

        self.timestamp = datetime.now()
        self.save()
