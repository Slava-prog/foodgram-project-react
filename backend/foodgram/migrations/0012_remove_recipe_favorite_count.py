# Generated by Django 4.2.2 on 2023-06-25 23:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0011_recipe_favorite_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='favorite_count',
        ),
    ]
