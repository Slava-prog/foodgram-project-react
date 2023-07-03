import io

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from .models import Follow, Recipe


def is_subscribed(self, obj):
    "Проверка подписки для пользователя."
    try:
        author = self.context.get('request').user
        return Follow.objects.filter(
            author=obj.id, user=author).exists()
    except TypeError:
        return False


def check_password(user, password):
    "Проверка правильности пароля."
    return str(user.password) == str(password)


def writing_shopping_cart(shopping_cart):
    "Создание файла со списком покупок."
    shopping_list = {}
    file = io.StringIO()
    file.write('Список покупок:'.encode('utf-8').decode('utf-8') + '\n')
    for ingredient in shopping_cart:
        name = ingredient['ingredients__ingredient__name']
        measurement_unit = ingredient[
            'ingredients__ingredient__measurement_unit']
        amount = ingredient['amount']
        ingredient_str = f'{name}, {measurement_unit}'
        shopping_list[ingredient_str] = amount
    for name, data in shopping_list.items():
        line = f'{name} - {data}'
        file.write(line.encode('utf-8').decode('utf-8') + '\n')
    response = HttpResponse(
        file.getvalue(), content_type="text/plain", charset="utf-8")
    response['Content-Disposition'] = 'attachment'
    return response


def add_delete_shopping_cart_favorite(self, request, Model,
                                      Serializer, *args, **kwargs):
    "Добавление и отбавление списка покупок и избранного."
    recipe = get_object_or_404(Recipe, id=kwargs.get('pk'))
    user = self.request.user
    if request.method == 'POST':
        if Model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': 'Данный рецепт уже тут...'},
                status=status.HTTP_400_BAD_REQUEST)
        serializer = Serializer(
            data=request.data,
            context={'request': request, 'recipe': recipe},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(recipe=recipe, user=user)
        return Response(
            {'Рецепт успешно добавлен': serializer.data},
            status=status.HTTP_200_OK)
    if Model.objects.filter(user=user, recipe=recipe).exists():
        Model.objects.get(user=user, recipe=recipe).delete()
        return Response(
            'Рецепт успешно удален',
            status=status.HTTP_204_NO_CONTENT)
    return Response(
        {'errors': 'А рецепта то и не было...'},
        status=status.HTTP_400_BAD_REQUEST)
