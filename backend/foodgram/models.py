from django.contrib.auth import get_user_model
from django.db import models
from colorfield.fields import ColorField
from slugify import slugify

User = get_user_model()
CHOICES = (
        ('кг', 'Килограм'),
        ('гр', 'грам'),
        ('литр', 'литр'),
        ('чл', 'чайная ложка'),
        ('стл', 'столовая ложка'),
    )


class Ingredient(models.Model):
    "Класс ингредиентов для создания рецепта."
    name = models.CharField(max_length=25)
    measurement_unit = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class RecipeIngredient(models.Model):
    "Класс, позволяющий указывать количество ингредиента для рецепта."
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_for_recipe'
    )
    amount = models.PositiveIntegerField()

    def __str__(self):
        name = self.ingredient.name
        amount = self.amount
        ingredient = self.ingredient.measurement_unit
        return f'{name} {amount} {ingredient}'


class Tag(models.Model):
    "Таги для рецептов"
    name = models.CharField(max_length=200)
    color = ColorField(default='#FF0000')
    slug = models.SlugField(max_length=200, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    "Класс рецептов."
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User, related_name='recipe',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=25)
    image = models.ImageField(
        upload_to='foodgram/images/',
        blank=True,
        null=True,
        default=None
    )
    text = models.TextField(max_length=200)
    tags = models.ManyToManyField(
        Tag,
    )
    is_favorited = models.BooleanField(
        default=False,
        verbose_name='в избранном')
    is_in_shopping_cart = models.BooleanField(
        default=False,
        verbose_name='в списке покупок')
    ingredients = models.ManyToManyField(
        RecipeIngredient,
    )
    cooking_time = models.PositiveIntegerField()

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class Follow(models.Model):
    "Класс для подписки на понравившегося пользователя."
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
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
        related_name='elector'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=(
                'user', 'recipe'), name='unique_favor'),
        ]


class Shopping_cart(models.Model):
    "Класс списка покупок."
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoper'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoping'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=(
                'user', 'recipe'), name='unique_shoping'),
        ]
