from django.urls import path, include
from rest_framework import routers

from .views import (
    IngredientViewSet, TagViewSet,
    RecipeViewSet, UserViewSet, ObtainTokenViewSet
    )

app_name = 'foodgram'

router_v1 = routers.DefaultRouter()

router_v1.register('recipes', RecipeViewSet, basename='recipe')
router_v1.register('tags', TagViewSet, basename='tag')
router_v1.register('ingredients', IngredientViewSet, basename='ingredient')
router_v1.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/token/login/',
         ObtainTokenViewSet.as_view({'post': 'create'}),
         name='token'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
