from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from rest_framework import serializers

from .fields import Base64ImageField, Hex2NameColor
from .models import (Favorite, Follow, Ingredient, Recipe,
                     RecipeIngredient, ShoppingCart, Tag)
from users.models import CustomUser
from .utils import is_subscribed


class UserGETSerializer(serializers.ModelSerializer):
    """Сериализатор для GET запросов модели User."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'first_name', 'last_name',
            'email', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        return is_subscribed(self, obj)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для POST запросов модели User."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'first_name', 'last_name',
            'email', 'is_subscribed', 'password'
        )

    def get_is_subscribed(self, obj):
        return is_subscribed(self, obj)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели RecipeIngredient."""
    id = serializers.SlugRelatedField(
        many=False,
        slug_field='id',
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeFollowSerializer(serializers.ModelSerializer):
    """Сериализатор для объектов класса Recipe для выдачи в Подписках."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeGETSerializer(serializers.ModelSerializer):
    """Сериализатор для объектов класса Recipe для обработки GET-запросов."""
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    author = UserGETSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'author', 'image', 'tags', 'cooking_time',
                  'ingredients', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        try:
            user = self.context.get('request').user
            return Favorite.objects.filter(recipe=obj.id, user=user).exists()
        except TypeError:
            return False

    def get_is_in_shopping_cart(self, obj):
        try:
            user = self.context.get('request').user
            return ShoppingCart.objects.filter(
                recipe=obj.id, user=user).exists()
        except TypeError:
            return False


class RecipePOSTSerializer(serializers.ModelSerializer):
    """Сериализатор для объектов класса Recipe
    для обработки небезопасных запросов."""
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='id',
        queryset=Tag.objects.all()
    )
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField(max_length=None, use_url=True)
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Recipe
        exclude = ('pub_date', )

    def get_or_create_ingredients(self, ingredients_list, recipe):
        ingredient_list = []
        for recipe_ingredient in ingredients_list:
            amount = recipe_ingredient.get('amount')
            ingredient = recipe_ingredient.get('ingredient')
            RecipeIngredient.objects.get_or_create(
                ingredient=ingredient,
                amount=amount,
            )
            ingredient_list.append(RecipeIngredient.objects.get(
                ingredient=ingredient,
                amount=amount))
        recipe.ingredients.set(ingredient_list)

    def create(self, validated_data):
        if 'ingredients' not in self.initial_data:
            recipe = Recipe.objects.create(**validated_data)
            return recipe
        ingredients_list = validated_data.pop('ingredients')
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        self.get_or_create_ingredients(ingredients_list, recipe)
        recipe.tags.set(tags)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        ingredients_list = validated_data.pop('ingredients')
        tags = validated_data.pop("tags")
        Recipe.objects.filter(name=instance).update(**validated_data)
        instance.tags.clear()
        instance.ingredients.clear()
        self.get_or_create_ingredients(ingredients_list, instance)
        instance.tags.set(tags)
        return instance

    def to_representation(self, instance):
        serializer = RecipeGETSerializer(instance, context=self.context)
        return serializer.data

    def validate(self, data):
        ingredient_list = []
        list_of_ingredients = data.get('ingredients')
        for ingredient_to_recipe in list_of_ingredients:
            valid_ingredient = ingredient_to_recipe.get('ingredient')
            if valid_ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Вы указали один и тот же ингредиент несколько раз'
                )
            ingredient_list.append(valid_ingredient)
        return data


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Follow."""
    email = serializers.CharField(
        source='author.email',
        read_only=True
    )
    id = serializers.CharField(
        source='author.id',
        read_only=True
    )
    username = serializers.CharField(
        source='author.username',
        read_only=True
    )
    first_name = serializers.CharField(
        source='author.first_name',
        read_only=True
    )
    last_name = serializers.CharField(
        source='author.last_name',
        read_only=True
    )
    is_subscribed = serializers.CharField(
        source='author.is_subscribed',
        read_only=True
    )
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        recipes_limit = self.context.get(
            'request').query_params.get('recipes_limit')
        if recipes_limit:
            recipes = Recipe.objects.filter(author=obj.author)[:int(recipes_limit)]
        else:
            recipes = Recipe.objects.filter(author=obj.author)
        return RecipeFollowSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Favorite."""
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    recipe = RecipeGETSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ShoppingCart."""
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    recipe = RecipeGETSerializer(read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
