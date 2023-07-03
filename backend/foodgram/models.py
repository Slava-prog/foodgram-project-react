from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.db import models
from slugify import slugify

User = get_user_model()


class Ingredient(models.Model):
    "Класс ингредиентов для создания рецепта."
    name = models.CharField(
        max_length=25,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class RecipeIngredient(models.Model):
    "Класс, позволяющий указывать количество ингредиента для рецепта."
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_for_recipe',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        ordering = ['-id']
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        name = self.ingredient.name
        amount = self.amount
        unit = self.ingredient.measurement_unit
        return f'{name} {amount} {unit}'


class Tag(models.Model):
    "Таги для рецептов"
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    color = ColorField(
        default='#FF0000',
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Слаг'
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    "Класс рецептов."
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User, related_name='recipe',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=25,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='foodgram/images/',
        verbose_name='Картинка'
    )
    text = models.TextField(
        max_length=200,
        verbose_name='Описание'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег'
    )
    ingredients = models.ManyToManyField(
        RecipeIngredient,
        verbose_name='Ингредиенты'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}'


class Follow(models.Model):
    "Класс для подписки на понравившегося пользователя."
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Избранный'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=(
                'user', 'author'), name='unique_follow'),
            models.CheckConstraint(check=~models.Q(user=models.F(
                'author')), name='dont_follow_your_self'),
        ]


class Favorite(models.Model):
    "Добавление рецепта в избранное."
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='elector',
        verbose_name='Подписчик'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(fields=(
                'user', 'recipe'), name='unique_favor'),
        ]


class ShoppingCart(models.Model):
    "Класс списка покупок."
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoper',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoping',
        verbose_name='Рецепт для покупок'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(fields=(
                'user', 'recipe'), name='unique_shoping'),
        ]
