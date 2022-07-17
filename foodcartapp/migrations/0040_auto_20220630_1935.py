# Generated by Django 3.2 on 2022-06-30 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_auto_20220630_1931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='address',
            field=models.CharField(db_index=True, max_length=150, verbose_name='адрес'),
        ),
        migrations.AlterField(
            model_name='order',
            name='firstname',
            field=models.CharField(db_index=True, max_length=50, verbose_name='имя'),
        ),
        migrations.AlterField(
            model_name='order',
            name='lastname',
            field=models.CharField(db_index=True, max_length=50, verbose_name='фамилия'),
        ),
    ]