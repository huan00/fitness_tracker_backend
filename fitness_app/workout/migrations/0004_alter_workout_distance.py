# Generated by Django 4.1.1 on 2023-05-15 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workout', '0003_alter_workout_calories_alter_workout_distance_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workout',
            name='distance',
            field=models.FloatField(blank=True),
        ),
    ]
