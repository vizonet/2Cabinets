# Generated by Django 5.0.4 on 2024-05-11 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_rename_datecompleted_order_datecomplete'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='isAccepted',
            field=models.BooleanField(blank=True, default=False, verbose_name='Принято заказчиком?'),
        ),
    ]