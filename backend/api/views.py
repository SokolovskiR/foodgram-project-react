from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.permissions import AuthorAdminOrReadOnly
from foodgram.models import (Ingredient, IngredientAmount, Recipe,
                             Subscription, Tag)

from .fitlers import IngredientFilter, RecipeFilter
from .serializers import (FavouriteListSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer, RecipeViewSerializer,
                          ShoppingListSerializer, SubscriptionSerializer,
                          TagSerializer)

User = get_user_model()


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
    filterset_class = IngredientFilter


class RecipeViewSet(AutoAddAuthorEditorMixin, viewsets.ModelViewSet):
    """Vieset for recipes."""

    permission_classes = [AuthorAdminOrReadOnly]
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeViewSerializer
        return RecipeCreateUpdateSerializer


class FavouriteListViewSet(viewsets.ModelViewSet):
    """Viewset for recipes favourite list."""

    serializer_class = FavouriteListSerializer
    permission_classes = [AuthorAdminOrReadOnly]
    lookup_field = 'recipe_id'

    def get_queryset(self):
        return self.request.user.foodgram_favouritelist_users.all()

    def destroy(self, request, recipe_id):
        favourite_entry = request.user.foodgram_favouritelist_users.filter(
            recipe_id=recipe_id
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
        if request.user.foodgram_favouritelist_users.filter(
            recipe=recipe).exists():
            return Response(
                {'errors': 'Этот рецепт уже в списке избранного!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)


class SubscriptionListViewSet(viewsets.ModelViewSet):
    """Viewset for subscription list."""

    serializer_class = SubscriptionSerializer
    permission_classes = [AuthorAdminOrReadOnly]

    def get_queryset(self):
        return self.request.user.follower.all()
    
    def destroy(self, request, author_id):
        author = get_object_or_404(User, pk=author_id)
        subscription = Subscription.objects.filter(
            following=author, user=request.user
        ).first()
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Этого пользователя нет в подписках!'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ShoppingListViewSet(viewsets.ModelViewSet):
    """Viewset for shopping list."""

    serializer_class = ShoppingListSerializer
    permission_classes = [AuthorAdminOrReadOnly, IsAuthenticated]

    def get_queryset(self):
        return self.request.user.foodgram_shoppinglist_users.all()
    
    def destroy(self, request, recipe_id):
        shopping_entry = request.user.foodgram_shoppinglist_users.filter(
            recipe_id=recipe_id
        ).first()
        if shopping_entry:
            shopping_entry.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'этого рецепта нет в списке покупок'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def list(self, request, *args, **kwargs):
        recipes = request.user.foodgram_shoppinglist_users.values('recipe')
        ingredients = IngredientAmount.objects.filter(
            recipe__in=recipes).values(
                'ingredient__name', 'ingredient__measurement_unit'
                ).annotate(amount_sum=Sum('amount'))
        if ingredients:
            shopping_list = [
                (
                    f'FOODGRAM список покупок '
                    f'для пользователя {request.user.username}\n\n'
                )
            ]
            for i, item in enumerate(ingredients, start=1):
                shopping_list.append(
                    (
                        f'{i}. '
                        f'{item["ingredient__name"]} '
                        f'({item["ingredient__measurement_unit"]}) - '
                        f'{item["amount_sum"]}\n'
                    )
                )
            response = HttpResponse(
                shopping_list, status=status.HTTP_200_OK,
                content_type='text/plain'
            )
            response['Content-Disposition'] = (
                'attachment; filename=my_shopping_list.txt'
            )
            return response
        return Response(
            {'errors': 'список покупок пуст'},
            status=status.HTTP_400_BAD_REQUEST
        )
