from django.urls import path, include

from rest_framework import routers
from djoser.views import TokenCreateView, TokenDestroyView
from .views import (
    TagViewSet, IngredientViewSet, FavouriteListViewSet,
    RecipeViewSet, SubscriptionListShowViewSet
)

router = routers.DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')

# router.register(
#     r'recipes/(?P<recipe_id>\d+)/favorite',
#     FavouriteListViewSet,
#     basename='favourite_list'
# )
# router.register(
#     'recipes/subscriptions',
#     SubscriptionListShowViewSet,
#     basename='subscriptions_show'
# )


router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/token/login/', TokenCreateView.as_view(), name='token_obtain'),
    path('auth/token/logout/', TokenDestroyView.as_view(), name='token_destroy'),
    path('', include(router.urls))
]
