from import_export import resources

from foodgram.models import (
    Ingredient, FavouriteList, Subscription,
    IngredientAmount, Recipe, Tag, ShoppingList,
    User
)


class SaveAuthorEditorResourceMixin:
    """Mixin to save author/editor."""

    def before_import_row(self, row, **kwargs):
        row['author'] = kwargs['user'].id
        row['last_editor'] = kwargs['user'].id


class TagResource(resources.ModelResource):
    """Resource to import/export tags via admin panel."""

    class Meta:
        model = Tag


class IngredientResource(
    SaveAuthorEditorResourceMixin,
    resources.ModelResource
    ):
    """Resource to import/export ingredients via admin panel."""

    class Meta:
        model = Ingredient


class FavouriteResource(resources.ModelResource):
    """Resource to import/export favourite list via admin panel"""

    class Meta:
        model = FavouriteList


class SubscriptionResource(resources.ModelResource):
    """Resource to import/export subscription list via admin panel"""

    class Meta:
        model = Subscription


class IngredientAmountResource(resources.ModelResource):
    """Resource to import/export ingredient amount matches via admin panel"""

    class Meta:
        model = IngredientAmount

class ShoppingResource(resources.ModelResource):
    """Resource to import/export list via admin panel"""

    class Meta:
        model = ShoppingList


class RecipeResource(resources.ModelResource):
    """Resource to import/export ingredient amount matches via admin panel"""

    class Meta:
        model = Recipe
