import webcolors
from rest_framework import serializers


class Hex2NameColor(serializers.Field):

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


def check_password(user, password):
    return str(user.password) == str(password)


def writing_shopping_cart(shopping_cart):
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
