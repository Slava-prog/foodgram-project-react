import webcolors

from rest_framework import serializers

from .models import Follow


class Hex2NameColor(serializers.Field):
    "Возврат удобочтимого цвета."
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


def is_subscribed(self, obj):
    try:
        author = self.context.get('request').user
        return Follow.objects.filter(
            user=obj.id, author=author).exists()
    except TypeError:
        return False


def check_password(user, password):
    "Проверка правильности пароля."
    return str(user.password) == str(password)


def writing_shopping_cart(shopping_cart):
    "Создание файла со списком покупок"
    shopping_list = {}
    with open('files/shopping_cart.txt', "w+") as file:
        file.write('Список покупок:'.encode('utf-8').decode('utf-8') + '\n')
        for name, amount, unit in shopping_cart:
            if name not in shopping_list:
                shopping_list[name] = {'amount': amount, 'unit': unit}
            else:
                shopping_list[name]['amount'] += amount
        for name, data in shopping_list.items():
            line = f'{name} - {data["amount"]} {data["unit"]}'
            file.write(line.encode('utf-8').decode('utf-8') + '\n')
        file.close()
