import base64
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from rest_framework import serializers

from .models import (Ingredient,
                     Tag,
                     Recipe,
                     RecipeIngredient,
                     Follow,
                     Favorite,
                     Shopping_cart)
from users.models import CustomUser
from .utils import Hex2NameColor


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


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
        author = self.context.get('request').user
        return Follow.objects.filter(
            user=obj.id, author=author).exists()


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
        author = self.context.get('request').user
        return Follow.objects.filter(
            user=obj.id, author=author).exists()


class SignUpSerializer(serializers.Serializer):
    """Сериализатор для создания объектов класса User."""
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Имя пользователя содержит недопустимый символ'
            )
        ])
    email = serializers.EmailField(required=True, max_length=254)
    password = serializers.CharField(
        required=True,
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Пароль пользователя содержит недопустимый символ'
            )
        ])

    def validate(self, data):
        if CustomUser.objects.filter(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password')
        ):
            return data

        if data['username'].lower() == 'me':
            raise ValidationError(
                message='Использовать имя "me" в качестве username запрещено!'
            )
        if CustomUser.objects.filter(username=data.get('username')):
            raise serializers.ValidationError(
                'Пользователь с таким "username" уже существует'
            )
        if CustomUser.objects.filter(email=data.get('email')):
            raise serializers.ValidationError(
                'Пользователь с таким "email" уже существует'
            )
        return data


class ObtainTokenSerializer(serializers.ModelSerializer):
    """Сериализатор для объектов класса User при получении токена."""
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'password')


class UserSetPasswordSerializer(serializers.ModelSerializer):
    """Сериализатор для объектов класса User при получении токена."""
    new_password = serializers.CharField(max_length=150, required=True)
    current_password = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = CustomUser
        fields = ('new_password', 'current_password')


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
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeGETSerializer(serializers.ModelSerializer):
    """Сериализатор для объектов класса Recipe для обработки GET-запросов."""
    tags = TagSerializer(many=True, read_only=True)
    ingridients = RecipeIngredientSerializer(many=True, read_only=True)
    author = UserGETSerializer(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        depth = 1
        exclude = ('pub_date',)

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return Favorite.objects.filter(recipe=obj.id, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return Shopping_cart.objects.filter(recipe=obj.id, user=user).exists()


class RecipePOSTSerializer(serializers.ModelSerializer):
    """Сериализатор для объектов класса Recipe
    для обработки небезопасных запросов."""
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='id',
        queryset=Tag.objects.all()
    )
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Recipe
        exclude = ('pub_date', )

    def get_or_create_ingredients(self, ingredients, recipe):
        ingredient_list = []
        for ingredient in ingredients:
            amount = ingredient.pop('amount')
            ingredient = ingredient.pop('ingredient')
            RecipeIngredient.objects.get_or_create(
                ingredient=ingredient,
                amount=amount,
            )
            ingredient = RecipeIngredient.objects.get(
                ingredient=ingredient,
                amount=amount)
            ingredient_list.append(ingredient)
        recipe.ingredients.set(ingredient_list)

    def create(self, validated_data):
        if 'ingredients' not in self.initial_data:
            recipe = Recipe.objects.create(**validated_data)
            return recipe
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        self.get_or_create_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        recipe.save()
        return recipe


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Follow."""
    author = UserSerializer(read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('author', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)
        return RecipeGETSerializer(recipes, many=True).data

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


class Shopping_cartSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Shopping_cart."""
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    recipe = RecipeGETSerializer(read_only=True)

    class Meta:
        model = Shopping_cart
        fields = ('user', 'recipe')
