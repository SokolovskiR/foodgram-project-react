from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from core.permissions import AuthorAdminOrReadOnly
from foodgram.models import (
    Tag, Ingredient, FavouriteList,
    Recipe
)
from .serializers import (
    TagSerializer, IngredientSerializer,
    FavouriteListSerializer, RecipeSerializer
)


class AutoAddAuthorEditorMixin:
    """Mixin to add author/editor automatically on create/update."""

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user, last_editor=user)
    
    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(last_editor=user)


class TagViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Viewset to retrieve tags."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = [AllowAny]


class IngredientViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Viewset to retrieve ingredients."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = [AllowAny]


class FavouriteListViewSet(
    AutoAddAuthorEditorMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
    
):
    """Viewset for recipes favourite list."""

    serializer_class = FavouriteListSerializer
    permission_classes = [AuthorAdminOrReadOnly]

    def delete(self, request, recipe_id):
        favourite_entry = FavouriteList.objects.filter(
            recipe_id=recipe_id, user=request.user
        ).first()
        if favourite_entry:
            favourite_entry.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'этого рецепта нет в избранном'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('recipe_id'))
        if request.user.foodgram_favouritelist_users.filter(recipe=recipe).exists():
            return Response(
                {'errors': 'Этот рецепт уже в списке избранного!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)


class RecipeViewSet(AutoAddAuthorEditorMixin, viewsets.ModelViewSet):
    """Vieset for recipes."""

    serializer_class = RecipeSerializer
    permission_classes = [AuthorAdminOrReadOnly]
    queryset = Recipe.objects.select_related()

