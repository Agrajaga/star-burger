# Generated by Django 3.2 on 2022-07-19 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_auto_20220717_1743'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Новый'), (1, 'Собирается'), (2, 'Доставляется'), (3, 'Выполнен')], db_index=True, default=0, verbose_name='статус'),
        ),
    ]
