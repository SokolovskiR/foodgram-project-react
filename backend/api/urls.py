from django.urls import path, include

from rest_framework import routers
from djoser.views import TokenCreateView, TokenDestroyView
from .views import (
    TagViewSet, IngredientViewSet, FavouriteListViewSet,
    RecipeViewSet, SubscriptionListViewSet
)

router = routers.DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')


# router.register(
#     r'recipes/(?P<recipe_id>\d+)/favorite',
#     FavouriteListViewSet,
#     basename='favourite_list'
# )


urlpatterns = [
    path('users/subscriptions/', SubscriptionListViewSet.as_view({'get': 'list'}), name='subscriptions'),
    path(
        'users/<int:author_id>/subscribe/',
        SubscriptionListViewSet.as_view({'get': 'create', 'delete': 'destroy'}), name='subscribe'
    ),
    path('', include('djoser.urls')),
    path('auth/token/login/', TokenCreateView.as_view(), name='token_obtain'),
    path('auth/token/logout/', TokenDestroyView.as_view(), name='token_destroy'),
    path('', include(router.urls))

]
