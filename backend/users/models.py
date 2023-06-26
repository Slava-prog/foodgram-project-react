from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class CustomUser(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор')
    ]
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Имя пользователя содержит недопустимый символ'
            )
        ],
        verbose_name='Пользователь'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Почта'
    )
    role = models.CharField(
        max_length=9,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль'
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Фамилия'
    )
    is_subscribed = models.BooleanField(default=False, verbose_name='Подписан')
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль'
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
