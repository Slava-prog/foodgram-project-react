from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers

from .views import (
    IngredientViewSet, TagViewSet,
    RecipeViewSet, UserGetPostViewSet, ObtainTokenViewSet
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
    path('auth/token/logout/', include('djoser.urls')),
    path('auth/token/logout/', include('djoser.urls.jwt')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
