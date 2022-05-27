from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import (FavouriteList, Ingredient, IngredientAmount, Recipe,
                     ShoppingList, Subscription, Tag)
from .resources import (FavouriteResource, IngredientAmountResource,
                        IngredientResource, RecipeResource, ShoppingResource,
                        SubscriptionResource, TagResource)


class IngredientInLine(admin.StackedInline):
    """Inlines to add multiple ingredients to a recipe."""

    model = IngredientAmount
    extra = 0
    min_num = 1


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
        """
        Automatically save author and editor when creating instance,
        but allow to edit these fields when updating.
        """
        if obj:
            return tuple()
        return ('author', 'last_editor')


@admin.register(Tag)
class TagAdmin(SaveAuthorEditorMixin, ImportExportModelAdmin):
    """Tags administration."""

    resource_class = TagResource
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
        'last_editor',
        'date_modified'
    )
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(SaveAuthorEditorMixin, ImportExportModelAdmin):
    """Ingredients administration."""

    resource_class = IngredientResource
    list_display = (
        'pk',
        'name',
        'measurement_unit',
        'last_editor',
        'date_modified'
    )


@admin.register(IngredientAmount)
class IngredientAmountAdmin(ImportExportModelAdmin):
    """IngredientAmounts administration."""

    resource_class = IngredientAmountResource
    list_display = (
        'pk',
        'recipe',
        'ingredient',
        'amount'
    )
    search_fields = ('ingredient__name', 'recipe__name')


@admin.register(Recipe)
class RecipeAdmin(SaveAuthorEditorMixin, ImportExportModelAdmin):
    """Recipes administration."""

    resource_class = RecipeResource
    list_display = (
        'pk',
        'name',
        'author',
        'get_tags',
        'get_favourite_add_count',
        'date_created'
    )
    search_fields = (
        'name', 'author__username', 'author__last_name',
        'tags__name'
    )
    inlines = [IngredientInLine]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('tags', 'ingredients')

    def get_tags(self, obj):
        return ', '.join(obj.tags.values_list('name', flat=True))

    def get_favourite_add_count(self, obj):
        return FavouriteList.objects.filter(
            recipe_id=obj.id
        ).count()

    get_tags.short_description = 'Теги'
    get_favourite_add_count.short_description = (
        'Добавлений в избранное'
    )


@admin.register(FavouriteList)
class FavouriteListAdmin(ImportExportModelAdmin):
    """Favourite recipes list administration."""

    resource_class = FavouriteResource
    list_display = (
        'pk',
        'user',
        'recipe',
        'date_created'
    )
    search_fields = ('user__username', 'recipe__name')


@admin.register(ShoppingList)
class ShoppingListAdmin(FavouriteListAdmin):
    """Shopping list administration."""

    resource_class = ShoppingResource


@admin.register(Subscription)
class SubscriptionAdmin(ImportExportModelAdmin):
    """Subscriptions administration."""

    resource_class = SubscriptionResource
    list_display = (
        'pk',
        'user',
        'author',
        'date_created'
    )
    search_fields = (
        'user__username', 'user__last_name',
        'author__username', 'author__last_name'
    )
