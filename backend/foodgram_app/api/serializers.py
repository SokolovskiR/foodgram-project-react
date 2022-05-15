from django.shortcuts import get_object_or_404

from rest_framework import serializers

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
    
    def validate(self, data):
        recipe_id = self.context.get(
            'request'
        ).parser_context.get('kwargs').get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = self.context['request'].user
        if self.context['request'].method == 'POST':
            if user.foodgram_favouritelist_users.filter(recipe=recipe).exists():
                raise serializers.ValidationError(
                    'Этот рецепт уже в списке избранного!'
                )
            ###test###    
            data['author_id'] = user.id
            data['last_editor_id'] = user.id
        elif self.context['request'].method == 'DELETE':
            if not user.foodgram_favouritelist_users.filter(recipe=recipe).exists():
                raise serializers.ValidationError(
                    'Этого рецепта нет в списке избранного!'
                )
        data['recipe_id'] = recipe_id
        data['user_id'] = user.id
        return data
    
    def create(self, validated_data):
        return super().create(validated_data)


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscribtions."""

    pass

    