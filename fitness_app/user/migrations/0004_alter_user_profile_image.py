# Generated by Django 4.2.7 on 2023-11-16 18:28

from django.db import migrations, models
import user.models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_equipmentlist_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_image',
            field=models.ImageField(blank=True, null=True, upload_to=user.models.upload_path),
        ),
    ]