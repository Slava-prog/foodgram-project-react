# Generated by Django 4.2.2 on 2023-06-22 10:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0004_alter_follow_recipes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='follow',
            name='recipes',
        ),
    ]
