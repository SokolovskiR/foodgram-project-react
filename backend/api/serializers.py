from django.shortcuts import get_object_or_404
from django.db.models import F
import base64, uuid
from django.core.files.base import ContentFile

from rest_framework import serializers

from foodgram.models import IngredientAmount
from users.models import User
from foodgram.models import (
    Subscription, Tag, Ingredient,
    FavouriteList, ShoppingList, Recipe
)


class CommonActionsMixin:
    """Common serializer actions mixin."""

    def get_absolute_url(self, url):
        """Generate absolute url path for image file."""
        request = self.context.get('request')
        return request.build_absolute_uri(url)


class Base64ImageField(CommonActionsMixin, serializers.ImageField):
    """Custom field to to convert Base64 image string to file."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            id = uuid.uuid4()
            data = ContentFile(
                base64.b64decode(imgstr),
                name = id.urn[9:] + '.' + ext
            )
        return super(Base64ImageField, self).to_internal_value(data)
    
    def to_representation(self, value):
        return self.get_absolute_url(value.url)


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
        if user.is_anonymous:
            return False
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


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Serializer for ingredient amounts."""
    name = serializers.ReadOnlyField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    # ingredients = serializers.SerializerMethodField()
    ingredients = IngredientAmountSerializer(
        many=True,
        read_only=True,
    )
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


    # def get_ingredients(self, obj):
    #     qs = obj.ingredients.all()
    #     return IngredientAmountSerializer(qs, many=True).data

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return FavouriteList.objects.filter(
            user=user, recipe_id=obj.id
            ).exists()
    
    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=user, recipe_id=obj.id
            ).exists()

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        new_recipe = super().create(validated_data)
        # new_recipe = Recipe.objects.create(**validated_data)
        new_recipe.tags.add(*tags)
        ingredient_amounts_to_create = []
        for ing in ingredients:
            ingredient_amounts_to_create.append(
                IngredientAmount(recipe=new_recipe, **dict(ing))
            )
        ing_amount_create = IngredientAmount.objects.bulk_create(
            ingredient_amounts_to_create
        )
        return new_recipe



class FavouriteListSerializer(CommonActionsMixin, serializers.ModelSerializer):
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
        data['image'] = self.get_absolute_url(recipe.image.url)
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


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscribtions."""

    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()


    class Meta:
        model = Subscription
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes',
            'recipes_count'
        )

    def get_recipes_count(self, obj):
        user =  self.context['request'].user
        return user.foodgram_recipe_authors.count()
    
    def get_recipes(self, obj):
        user =  self.context['request'].user
        return user.foodgram_recipe_authors.all()
    
    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    