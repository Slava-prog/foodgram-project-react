from django_filters import rest_framework as filters

from .models import Recipe


class RecipeFilter(filters.FilterSet):
    "Фильтр для модели Recipe"
    author = filters.NumberFilter()
    tags = filters.CharFilter(
        field_name="tags",
        method='filter_tags'
        )
    is_favorited = filters.NumberFilter(
        field_name="is_favorited",
        method='filter_is_favorited'
        )
    is_in_shopping_cart = filters.NumberFilter(
        field_name="is_in_shopping_cart",
        method='filter_is_in_shopping_cart'
        )

    class Meta:
        model = Recipe
        fields = ('tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_tags(self, queryset, tags, slug):
        return queryset.filter(tags__slug=slug)

    def filter_is_favorited(self, queryset, is_favorited, mean):
        user = self.request.user
        if mean == 1:
            return queryset.filter(favorite__user=user)
        else:
            return queryset.exclude(favorite__user=user)

    def filter_is_in_shopping_cart(self, queryset, is_in_shopping_cart, mean):
        user = self.request.user
        if mean == 1:
            return queryset.filter(shoping__user=user)
        else:
            return queryset.exclude(shoping__user=user)
