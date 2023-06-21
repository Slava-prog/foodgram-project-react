from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from .models import Ingredient, Tag, Recipe, RecipeIngredient
from users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""
    class Meta:
        model = CustomUser
        fields = (
            'username', 'email',
            'is_subscribed', 'id',
            'first_name', 'last_name'
        )


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

    def validate(self, data):
        if CustomUser.objects.filter(
            username=data.get('username'),
            email=data.get('email')
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


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели RecipeIngredient."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    # amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeGETSerializer(serializers.ModelSerializer):
    """Сериализатор для объектов класса Recipe для обработки GET-запросов"""
    tags = TagSerializer(many=True, read_only=True)
    ingridients = RecipeIngredientSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        exclude = ('pub_date', )


class RecipePOSTSerializer(serializers.ModelSerializer):
    """Сериализатор для объектов класса Recipe
    для обработки небезопасных запросов"""
    # image = Base64ImageField(max_length=None, use_url=True)
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='id',
        queryset=Tag.objects.all()
    )
    ingredients = RecipeIngredientSerializer(many=True)
    author = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Recipe
        exclude = ('pub_date', )

    def get_or_create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient = ingredient['id']
            ingredients, created = RecipeIngredient.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )

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
