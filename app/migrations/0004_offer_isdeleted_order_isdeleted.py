# Generated by Django 5.0.4 on 2024-05-09 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_remove_order_dateaccepted_offer_processperiod_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='isDeleted',
            field=models.BooleanField(default=False, verbose_name='Удалён'),
        ),
        migrations.AddField(
            model_name='order',
            name='isDeleted',
            field=models.BooleanField(default=False, verbose_name='Удалён'),
        ),
    ]