# Generated by Django 5.0.4 on 2024-05-13 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_order_dateendfact_alter_order_datecomplete_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='processPeriod',
            field=models.IntegerField(default=1, verbose_name='Дней на выполнение (min)'),
        ),
    ]
