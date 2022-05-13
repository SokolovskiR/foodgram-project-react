from django.contrib import admin

from .models import (
    Tag, Ingredient, IngredientAmount,
    Recipe, FavouriteList, ShoppingList, Subscription
)


class SaveAuthorEditorMixin:
    """
    Mixin to auto save author and editor to each model.
    """

    empty_value_display = '-пусто-'
    search_fields = ('name',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
            obj.last_editor = request.user
        super().save_model(request, obj, form, change)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return tuple()
        return ('author', 'last_editor')


@admin.register(Tag)
class TagAdmin(SaveAuthorEditorMixin, admin.ModelAdmin):
    """Tags administration."""
    list_display = (
        'pk',
        'name',
        'color_hexcode',
        'slug',
        'last_editor',
        'date_modified'
    )
    search_fields = ('name','slug')


@admin.register(Ingredient)
class IngredientAdmin(SaveAuthorEditorMixin, admin.ModelAdmin):
    """Ingredients administration."""
    list_display = (
        'pk',
        'name',
        'measurement_unit',
        'last_editor',
        'date_modified'
    )


@admin.register(IngredientAmount)
class IngredientAmountAdmin(SaveAuthorEditorMixin, admin.ModelAdmin):
    """IngredientAmounts administration."""
    list_display = (
        'pk',
        'ingredient',
        'amount',
        'last_editor',
        'date_modified'
    )
    search_fields = ('ingredient__name',)


@admin.register(Recipe)
class RecipeAdmin(SaveAuthorEditorMixin, admin.ModelAdmin):
    """Recipes administration."""
    list_display = (
        'pk',
        'name',
        'author',
        'get_ingredients',
        'get_tags',
        'last_editor',
        'date_created',
        'date_modified'
    )
    search_fields = ('name', 'author', 'get_tags', 'get_ingredients')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('ingredients', 'tags')

    def get_ingredients(self, obj):
        return ','.join([i.name for i in obj.ingredients.all()])
    
    def get_tags(self, obj):
        return ','.join([t.name for t in obj.tags.all()])



@admin.register(FavouriteList)
class FavouriteListAdmin(SaveAuthorEditorMixin, admin.ModelAdmin):
    """Favourite recipes list administration."""
    list_display = (
        'pk',
        'author',
        'recipe',
        'date_modified'
    )
    search_fields = ('author', 'recipe')


@admin.register(ShoppingList)
class ShoppingListAdmin(FavouriteListAdmin):
    """Shopping list administration."""
    pass


@admin.register(Subscription)
class SubscriptionAdmin(SaveAuthorEditorMixin, admin.ModelAdmin):
    """Subscriptions administration."""
    list_display = (
        'pk',
        'user',
        'following',
        'date_modified'
    )
    search_fields = ('user', 'following')