from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from core.permissions import AuthorAdminOrReadOnly
from foodgram.models import Ingredient, IngredientAmount, Recipe, Tag

from .fitlers import IngredientFilter, RecipeFilter
from .mixins import AutoAddAuthorEditorMixin, DestroyMixin, ListRetrieveMixin
from .serializers import (FavouriteListSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer, RecipeViewSerializer,
                          ShoppingListSerializer, SubscriptionSerializer,
                          TagSerializer)
from .utils import generate_shopping_list

User = get_user_model()


class TagViewSet(ListRetrieveMixin):
    """Viewset to retrieve tags."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(ListRetrieveMixin):
    """Viewset to retrieve ingredients."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = [AllowAny]
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(AutoAddAuthorEditorMixin, viewsets.ModelViewSet):
    """Vieset for recipes."""

    permission_classes = [AuthorAdminOrReadOnly]
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeViewSerializer
        return RecipeCreateUpdateSerializer


class FavouriteListViewSet(DestroyMixin, viewsets.ModelViewSet):
    """Viewset for recipes favourite list."""

    serializer_class = FavouriteListSerializer
    permission_classes = [AuthorAdminOrReadOnly]
    lookup_field = 'recipe_id'

    def get_queryset(self):
        return self.request.user.foodgram_favouritelist_users.all()

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('recipe_id'))
        if request.user.foodgram_favouritelist_users.filter(
                recipe=recipe).exists():
            return Response(
                {'errors': 'Этот рецепт уже в списке избранного!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)


class SubscriptionListViewSet(DestroyMixin, viewsets.ModelViewSet):
    """Viewset for subscription list."""

    serializer_class = SubscriptionSerializer
    permission_classes = [AuthorAdminOrReadOnly]
    lookup_field = 'author_id'

    def get_queryset(self):
        return self.request.user.follower.all()


class ShoppingListViewSet(DestroyMixin, viewsets.ModelViewSet):
    """Viewset for shopping list."""

    serializer_class = ShoppingListSerializer
    permission_classes = [AuthorAdminOrReadOnly, IsAuthenticated]
    lookup_field = 'recipe_id'

    def get_queryset(self):
        return self.request.user.foodgram_shoppinglist_users.all()

    def list(self, request, *args, **kwargs):
        """Get shopping list as plain text."""
        recipes = request.user.foodgram_shoppinglist_users.values('recipe')
        ingredients = IngredientAmount.objects.filter(
            recipe__in=recipes).values(
                'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount_sum=Sum('amount'))
        if not ingredients:
            return Response(
                {'errors': 'список покупок пуст'},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_list = generate_shopping_list(
            ingredients, request.user.username
        )
        response = HttpResponse(
            shopping_list, status=status.HTTP_200_OK,
            content_type='text/plain'
        )
        response['Content-Disposition'] = (
            'attachment; filename="my_shopping_list.txt"'
        )
        return response
