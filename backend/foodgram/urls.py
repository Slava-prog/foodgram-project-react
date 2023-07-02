from django.urls import path, include
from rest_framework import routers

from .views import (
    IngredientViewSet, LogoutViewSet, ObtainTokenViewSet,
    RecipeViewSet, TagViewSet, UserGetPostViewSet
)

app_name = 'foodgram'

router_v1 = routers.DefaultRouter()

router_v1.register('recipes', RecipeViewSet, basename='recipe')
router_v1.register('tags', TagViewSet, basename='tag')
router_v1.register('ingredients', IngredientViewSet, basename='ingredient')
router_v1.register('users', UserGetPostViewSet, basename='users')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/token/login/',
         ObtainTokenViewSet.as_view({'post': 'create'}),
         name='token'),
    path('auth/token/logout/',
         LogoutViewSet.as_view({'post': 'post'}),
         name='token'),
]
