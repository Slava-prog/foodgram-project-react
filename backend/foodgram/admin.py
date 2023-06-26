from django.contrib import admin
from .models import (Ingredient, Tag, Recipe, RecipeIngredient,
                     Follow, Favorite, Shopping_cart, )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'user',
                    'recipe'
                    )


@admin.register(Shopping_cart)
class Shopping_cartAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'user',
                    'recipe'
                    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'user',
                    'author'
                    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'measurement_unit'
                    )
    list_filter = ('name',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'ingredient',
                    'amount'
                    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'color'
                    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ('favorite_count',)
    list_display = ('id',
                    'name',
                    'author',
                    )
    list_filter = ('author', 'name', 'tags')

    def favorite_count(self, obj):
        return obj.favorite.count()
