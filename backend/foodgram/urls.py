from django.urls import path, include
from rest_framework import routers

from .views import (
    IngredientViewSet,
    RecipeViewSet, TagViewSet, UserGetPostViewSet
)

app_name = 'foodgram'

router_v1 = routers.DefaultRouter()

router_v1.register('recipes', RecipeViewSet, basename='recipe')
router_v1.register('tags', TagViewSet, basename='tag')
router_v1.register('ingredients', IngredientViewSet, basename='ingredient')
router_v1.register('users', UserGetPostViewSet, basename='users')

urlpatterns = [
    path('users/subscriptions/',
         UserGetPostViewSet.as_view({'get': 'subscriptions'}),
         name='subscriptions'),
    path('', include('djoser.urls')),
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
