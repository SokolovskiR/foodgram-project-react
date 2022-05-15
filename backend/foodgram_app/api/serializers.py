from django.shortcuts import get_object_or_404

from rest_framework import serializers

from foodgram.models import IngredientAmount
from users.models import User
from foodgram.models import (
    Subscription, Tag, Ingredient,
    FavouriteList, ShoppingList, Recipe
)


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for users."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if Subscription.objects.filter(
            following=obj, user=user
            ).first():
            return True
        return False


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class FavouriteListSerializer(serializers.ModelSerializer):
    """Serializer for list of favourite recipes."""

    class Meta:
        model = FavouriteList
        fields = ('id',)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        recipe_id = self.context.get(
            'request'
        ).parser_context.get('kwargs').get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        data['name'] = recipe.name
        data['image'] = self.context.get(
            'request'
            ).build_absolute_uri(recipe.image.url)
        data['cooking_time'] = recipe.cooking_time
        return data
    
    def create(self, validated_data):
        recipe_id = self.context.get(
            'request'
        ).parser_context.get('kwargs').get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = self.context['request'].user
        validated_data['recipe'] = recipe
        validated_data['user'] = user
        return super().create(validated_data)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    tags = TagSerializer(many=True)

    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name',
            'image', 'text', 'cooking_time'
        )
    

    def get_ingredients(self, obj):
        return IngredientAmount.objects.filter(
            recipe=obj
            ).select_related('recipe').values(
                'id', 'recipe__name', 'recipe__measurement_unit', 'amount'
            )

    def get_is_favorited(self, obj):
        return 'PLACEHOLDER'
    
    def get_is_in_shopping_cart(self, obj):
        return 'PLACEHOLDER'



    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['tags']


    #     return data
    

    





class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscribtions."""

    pass

    