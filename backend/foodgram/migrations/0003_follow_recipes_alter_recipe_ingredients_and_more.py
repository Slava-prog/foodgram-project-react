# Generated by Django 4.2.2 on 2023-06-21 19:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0002_alter_recipeingredient_ingredient'),
    ]

    operations = [
        migrations.AddField(
            model_name='follow',
            name='recipes',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='following_recipes', to='foodgram.recipe'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(to='foodgram.recipeingredient'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(to='foodgram.tag'),
        ),
    ]