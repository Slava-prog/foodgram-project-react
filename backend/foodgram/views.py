from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .filters import RecipeFilter
from .models import (Ingredient, Favorite, Follow, Recipe,
                     RecipeIngredient, ShoppingCart, Tag)
from .permissions import IsAdminOrReadOnly
from .serializers import (IngredientSerializer,
                          TagSerializer,
                          RecipeIngredientSerializer,
                          RecipeGETSerializer,
                          RecipePOSTSerializer,
                          UserSerializer,
                          UserGETSerializer,
                          UserSetPasswordSerializer,
                          SignUpSerializer,
                          ObtainTokenSerializer,
                          FollowSerializer,
                          FavoriteSerializer,
                          ShoppingCartSerializer)
from .utils import check_password, writing_shopping_cart
from users.models import CustomUser


class ObtainTokenViewSet(viewsets.ModelViewSet):
    """Вьюсет для получения пользователем JWT токена."""
    queryset = CustomUser.objects.all()
    serializer_class = ObtainTokenSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = ObtainTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        user = get_object_or_404(CustomUser, email=email)

        if check_password(user, password):
            return Response(
                {'auth_token': str(AccessToken.for_user(user))},
                status=status.HTTP_200_OK
            )
        return Response(
            {'password': 'Пароль неверен'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserGetPostViewSet(UserViewSet):
    """Вьюсет для обьектов модели User."""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (permissions.AllowAny,)

    @action(
        methods=['POST'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def set_password(self, request, *args, **kwargs):
        serializer = UserSetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data.get('new_password')
        password = serializer.validated_data.get('current_password')
        user = self.request.user

        if check_password(user, password):
            user.password = new_password
            user.save()
            return Response(
                'Пароль успешно изменен',
                status=status.HTTP_200_OK
            )
        return Response(
            {'password': 'Пароль неверен'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        user = self.request.user
        serializer = UserGETSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['POST'],
        detail=False,
        permission_classes=(permissions.AllowAny,)
    )
    def create_user(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request, *args, **kwargs):
        queryset = Follow.objects.filter(user=self.request.user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, *args, **kwargs):
        author = get_object_or_404(CustomUser, id=kwargs.get('pk'))
        user = self.request.user
        if request.method == "POST":
            if author == user:
                return Response(
                    {'errors': 'Нет смысла подписываться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST)
            if Follow.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на данного пользователя'},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = FollowSerializer(
                data=request.data,
                context={'request': request, 'author': author},
            )
            if serializer.is_valid(raise_exception=True):
                Follow.objects.create(author=author, user=user)
                serializer = self.get_serializer(author)
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK)
        elif request.method == "DELETE":
            if Follow.objects.filter(user=user, author=author).exists():
                Follow.objects.get(user=user, author=author).delete()
                return Response(
                    'Вы успешно отписались',
                    status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'А подписки то и не было...'},
                status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserGETSerializer
        return UserSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для объектов класса Ingredient."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для объектов класса RecipeIngredient."""
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для объектов класса Tag."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для объектов класса Recipe."""
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    pagination_class = LimitOffsetPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGETSerializer
        return RecipePOSTSerializer

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(
                author=self.request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        user = self.request.user
        if ShoppingCart.objects.filter(user=user).exists():
            shopping_cart = Recipe.objects.filter(
                shoping__user=user).values_list(
                    'ingredients__ingredient__name',
                    'ingredients__amount',
                    'ingredients__ingredient__measurement_unit')
            writing_shopping_cart(shopping_cart)
            return FileResponse(
                open('files/shopping_cart.txt', 'rb'),
                as_attachment=True)
        return Response(
            {'errors': 'Список покупок пуст'},
            status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('pk'))
        user = self.request.user
        if request.method == "POST":
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Данный рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = FavoriteSerializer(
                data=request.data,
                context={'request': request, 'recipe': recipe},
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save(recipe=recipe, user=user)
                return Response(
                    {'Вы подписаны на рецепт': serializer.data},
                    status=status.HTTP_200_OK)
        else:
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                Favorite.objects.get(user=user, recipe=recipe).delete()
                return Response(
                    'Рецепт удален из избранного',
                    status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'А рецепта в избранном и не было...'},
                status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('pk'))
        user = self.request.user
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Данный рецепт уже в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = ShoppingCartSerializer(
                data=request.data,
                context={'request': request, 'recipe': recipe},
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save(recipe=recipe, user=user)
                return Response(
                    {'Рецепт добавлен в список покупок': serializer.data},
                    status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                ShoppingCart.objects.get(user=user, recipe=recipe).delete()
                return Response(
                    'Рецепт удален из списка покупок',
                    status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'А рецепта в списке и не было...'},
                status=status.HTTP_400_BAD_REQUEST)
