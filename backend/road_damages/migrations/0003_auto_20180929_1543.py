# Generated by Django 2.1.1 on 2018-09-29 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('road_damages', '0002_auto_20180929_1418'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registereddamage',
            name='photo',
            field=models.CharField(max_length=200),
        ),
    ]
