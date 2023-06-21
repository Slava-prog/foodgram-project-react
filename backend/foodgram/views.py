from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
# from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from .models import Ingredient, Tag, Recipe, RecipeIngredient
from users.models import CustomUser
#from .filters import TitleFilter
#from .mixins import CreateDestroyListViewSet, CreateMixin
from .permissions import (IsAdmin, IsAdminAuthororReadOnly, IsAdminOrReadOnly)
from .serializers import (IngredientSerializer, TagSerializer, RecipeIngredientSerializer,
                          RecipeGETSerializer, RecipePOSTSerializer,
                          UserSerializer, SignUpSerializer, ObtainTokenSerializer)
from .utils import check_password


class SignUpViewSet(APIView):
    """Вьюсет для создания обьектов класса User."""
    queryset = CustomUser.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data
        user, _ = CustomUser.objects.get_or_create(
            **serializer.validated_data
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


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
                {'token': str(AccessToken.for_user(user))},
                status=status.HTTP_200_OK
            )
        return Response(
            {'password': 'Пароль неверен'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для обьектов модели User."""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('username',)
    # lookup_field = 'username'

    @action(
        methods=['POST'],
        detail=False,
        permission_classes=(permissions.AllowAny,)
    )
    def create_user(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=['GET', 'PATCH', 'DELETE'],
        detail=False,
        #url_path=r'(?P<username>[\w.@+-]+)',
        #url_name='get_user',
    )
    def get_user(self, request, username):
        user = get_object_or_404(CustomUser, username=username)
        if request.method == "PATCH":
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == "DELETE":
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET', 'PATCH'],
            detail=False,
            permission_classes=(permissions.IsAuthenticated,),
            # url_path='me'
            )
    def change_info(self, request):
        serializer = UserSerializer(request.user)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для объектов класса Ingredient"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для объектов класса Ingredient"""
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer
    # permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для объектов класса Tag"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    #permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для объектов класса Title"""
    queryset = Recipe.objects.all()
    # permission_classes = (IsAdminOrReadOnly,)
    # filter_backends = (DjangoFilterBackend, )
    # filterset_class = TitleFilter
    pagination_class = PageNumberPagination

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
