from django.contrib import admin

from .models import (
    Tag, Ingredient, IngredientAmount,
    Recipe, FavouriteList, ShoppingList, Subscription
)


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
        if obj:
            return tuple()
        return ('author', 'last_editor')


@admin.register(Tag)
class TagAdmin(SaveAuthorEditorMixin, admin.ModelAdmin):
    """Tags administration."""
    list_display = (
        'pk',
        'name',
        'color',
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
class IngredientAmountAdmin(admin.ModelAdmin):
    """IngredientAmounts administration."""
    list_display = (
        'pk',
        'recipe',
        'ingredient',
        'amount'
    )
    search_fields = ('ingredient__name', 'recipe__name')


@admin.register(Recipe)
class RecipeAdmin(SaveAuthorEditorMixin, admin.ModelAdmin):
    """Recipes administration."""
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
        return qs.prefetch_related('tags')
    
    def get_tags(self, obj):
        return ', '.join([str(t.name) for t in obj.tags.all()])
    
    def get_favourite_add_count(self, obj):
        return FavouriteList.objects.filter(
            recipe_id=obj.id
            ).count()

    get_tags.short_description = 'Теги'
    get_favourite_add_count.short_description = (
        'Добавлений в избранное'
    )


@admin.register(FavouriteList)
class FavouriteListAdmin(SaveAuthorEditorMixin, admin.ModelAdmin):
    """Favourite recipes list administration."""
    list_display = (
        'pk',
        'user',
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
    search_fields = (
        'user__username', 'user__last_name',
        'following__username', 'following__last_name'
    )