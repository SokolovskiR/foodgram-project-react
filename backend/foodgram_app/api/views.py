from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from core.permissions import AuthorAdminOrReadOnly
from foodgram.models import (
    Tag, Ingredient, FavouriteList
)
from .serializers import (
    TagSerializer, IngredientSerializer,
    FavouriteListSerializer
)


class TagViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Viewset to retrieve tags."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Viewset to retrieve ingredients."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()



class FavouriteListViewSet(
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
