# Generated by Django 3.2 on 2022-08-06 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geocoderapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='geopoint',
            name='calculated',
            field=models.BooleanField(default=False, verbose_name='адрес обработан'),
        ),
        migrations.AlterField(
            model_name='geopoint',
            name='latitude',
            field=models.DecimalField(db_index=True, decimal_places=6, max_digits=8, null=True, verbose_name='широта'),
        ),
        migrations.AlterField(
            model_name='geopoint',
            name='longitude',
            field=models.DecimalField(db_index=True, decimal_places=6, max_digits=8, null=True, verbose_name='долгота'),
        ),
    ]
