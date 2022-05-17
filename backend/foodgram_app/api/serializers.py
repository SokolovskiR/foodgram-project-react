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



    

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

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
            ).values(
                'id', 'amount', name=F('ingredient__name'),
                measurement_unit=F('ingredient__measurement_unit')
            )

    def get_is_favorited(self, obj):
        if FavouriteList.objects.filter(
            user=self.context['request'].user,
            recipe_id=obj.id
            ).exists():
            return True
        return False
    
    def get_is_in_shopping_cart(self, obj):
        if ShoppingList.objects.filter(
            user=self.context['request'].user,
            recipe_id=obj.id
            ).exists():
            return True
        return False
    
    # def validate(self, attrs):

    #     ingredients = self.initial_data.get('ingredients')
    #     tags = self.initial_data.get('tags')

    #     self.data['tags'] = tags
    #     self.data['ingredients'] = ingredients

    def validate_tags(self):
        pass

    def validate_ingredients(self):
        pass

    

    def create(self, validated_data):
        #print(validated_data)
        # print(self.initial_data)

        self.val

        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')

        validated_data['tags'] = tags

        print(validated_data)


        return super().create(validated_data)
    





class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscribtions."""

    pass

    