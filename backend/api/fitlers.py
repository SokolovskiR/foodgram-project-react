from django_filters import FilterSet, filters
from foodgram.models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    """Filter for ingredients."""

    name = filters.CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):
    """Filters for recipe view."""

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.NumberFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def get_is_favorited(self, queryset, name, value):
        if not value or value is None:
            return queryset
        if bool(value) and not self.request.user.is_anonymous:
            return queryset.filter(
                foodgram_favouritelist_recipes__user=self.request.user
            )

    def get_is_in_shopping_cart(self, queryset, name, value):
        if not value or value is None:
            return queryset
        if bool(value) and not self.request.user.is_anonymous:
            return queryset.filter(
                foodgram_shoppinglist_recipes__user=self.request.user
            )
