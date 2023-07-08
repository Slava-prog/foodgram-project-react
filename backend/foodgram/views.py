from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import RecipeFilter, IngredientFilter
from .models import (Ingredient, Favorite, Follow, Recipe,
                     RecipeIngredient, ShoppingCart, Tag)
from .pagination import PageLimitPagination
from .permissions import IsAdminOrReadOnly
from .serializers import (FavoriteSerializer,
                          FollowSerializer,
                          IngredientSerializer,
                          RecipeIngredientSerializer,
                          RecipeGETSerializer,
                          RecipePOSTSerializer,
                          ShoppingCartSerializer,
                          TagSerializer,
                          UserSerializer,
                          UserGETSerializer,
                          )
from .utils import (writing_shopping_cart,
                    add_delete_shopping_cart_favorite)
from users.models import CustomUser


class UserGetPostViewSet(viewsets.ModelViewSet):
    """Вьюсет для обьектов модели User."""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageLimitPagination
    permission_classes = (permissions.AllowAny,)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
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
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(author=author, user=user)
            serializer = self.get_serializer(author)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK)
        if Follow.objects.filter(user=user, author=author).exists():
            Follow.objects.get(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
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
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    pagination_class = None
    filterset_class = IngredientFilter


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
    pagination_class = PageLimitPagination
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGETSerializer
        return RecipePOSTSerializer

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(permissions.AllowAny,)
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        user = self.request.user
        if ShoppingCart.objects.filter(user=user).exists():
            shopping_cart = Recipe.objects.filter(
                shoping__user=user).values(
                    'ingredients__ingredient__name',
                    'ingredients__ingredient__measurement_unit').annotate(
                        amount=Sum('ingredients__amount'),)
            return writing_shopping_cart(shopping_cart)
        return Response(
            {'errors': 'Список покупок пуст'},
            status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, *args, **kwargs):
        response = add_delete_shopping_cart_favorite(
            self, request, Favorite, FavoriteSerializer, *args, **kwargs)
        return response

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, *args, **kwargs):
        response = add_delete_shopping_cart_favorite(
            self, request, ShoppingCart,
            ShoppingCartSerializer, *args, **kwargs)
        return response
