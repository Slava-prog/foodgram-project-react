from django.contrib import admin

from .models import Ingredient, Tag, Recipe


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'measurement_unit'
                    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'color'
                    )

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'pub_date',
                    'author',
                    'name',
                    'image',
                    'text',
                    'cooking_time',
                    )
