# Generated by Django 5.0.4 on 2024-05-07 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='number',
            field=models.PositiveBigIntegerField(null=True, verbose_name='Номер'),
        ),
        migrations.AddField(
            model_name='order',
            name='number',
            field=models.PositiveBigIntegerField(null=True, verbose_name='Номер'),
        ),
    ]
