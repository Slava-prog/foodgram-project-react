from django.contrib.auth import get_user_model
from django.db import models
from colorfield.fields import ColorField

User = get_user_model()
CHOICES = (
        ('кг', 'Килограм'),
        ('гр', 'грам'),
        ('литр', 'литр'),
        ('чл', 'чайная ложка'),
        ('стл', 'столовая ложка'),
    )


class Ingredient(models.Model):
    name = models.CharField(max_length=25)
    measurement_unit = models.CharField(max_length=50,  choices = CHOICES)

    def __str__(self):
        return f'{self.name}'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_for_recipe'
    )
    '''recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient'
        )'''
    amount = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.ingredient}'


class Tag(models.Model):
    name = models.CharField(max_length=25)
    color = ColorField(default='#FF0000')
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Recipe(models.Model):
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
        related_name='tags'
    )
    ingredients = models.ManyToManyField(
        RecipeIngredient,
        related_name='ingredients'
    ) # , through='RecipeIngredient'
    cooking_time = models.PositiveIntegerField()

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.name
    

class Follow(models.Model):
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