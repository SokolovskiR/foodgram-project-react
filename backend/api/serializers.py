from django.shortcuts import get_object_or_404
import base64, uuid
from django.core.files.base import ContentFile

from rest_framework import serializers

from foodgram.models import IngredientAmount
from users.models import User
from foodgram.models import (
    Subscription, Tag, Ingredient,
    FavouriteList, ShoppingList, Recipe
)


class Base64ImageField(serializers.ImageField):
    """
    Custom field to convert Base64 image string to file,
    when saving to database.
    """

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
        return self.context.get('request').build_absolute_uri(value.url)


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
        read_only_fields = ('id', 'name', 'measurement_unit')


class IngredientAmountShowSerializer(serializers.ModelSerializer):
    """Serializer for displaying ingredients with amounts."""
    
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    """Read only recipe serializer."""
    
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')
    


class RecipeViewSerializer(serializers.ModelSerializer):
    """Serializer for displaying recipes."""

    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
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
        qs = IngredientAmount.objects.filter(recipe=obj)
        return IngredientAmountShowSerializer(qs, many=True).data

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


class IngredientAddToRecipeSerializer(serializers.ModelSerializer):
    """Serializer to add ingredients to a recipe."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer to create or update recipes."""
    
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientAddToRecipeSerializer(many=True)
    cooking_time = serializers.IntegerField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients: 
            raise serializers.ValidationError('Нужен хотя бы один ингредиент')
        for ingredient in ingredients:
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    'Количество должно быть больше нуля'
                )
        return data

    def validate_tags(self, data):
        tags = self.initial_data.get('tags')
        if not tags: 
            raise serializers.ValidationError('Нужен хотя бы один тег')
        return data


    def validate_cooking_time(self, data):
        if not isinstance(data, int):
            raise serializers.ValidationError(
                'Неверный формат, ожидается целое позитивное число'
            )
        if data <= 0:
            raise serializers.ValidationError(
                'Минимальное время готовки должно быть больше нуля'
            )
        return data

    def add_ingredients(self, ingredients, recipe):
          for ing in ingredients:
            ing_id=ing.get('id')
            IngredientAmount.objects.create(
                recipe=recipe,
                ingredient=ing_id,
                amount=ing.get('amount')
            )      

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        image = validated_data.pop('image')
        new_recipe = Recipe.objects.create(image=image, **validated_data)
        self.add_ingredients(ingredients, new_recipe)
        new_recipe.tags.set(tags)
        return new_recipe


    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        instance.last_editor = validated_data.get(
            'last_editor', self.context['request'].user
        )
        if 'tags' in self.initial_data:
            tags_data = validated_data.pop('tags')
            instance.tags.set(tags_data)
        if 'ingredients' in self.initial_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.add_ingredients(ingredients, instance)
        instance.save()
        return instance
    
    def to_representation(self, instance):
        return RecipeViewSerializer(
            instance, context={
                'request': self.context.get('request')
            }).data


class FavouriteListSerializer(serializers.ModelSerializer):
    """Serializer for list of favourite recipes."""

    class Meta:
        model = FavouriteList
        fields = ('id',)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        recipe_id = request.parser_context.get('kwargs').get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        data['name'] = recipe.name
        data['image'] = request.build_absolute_uri(recipe.image.url)
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

    id = serializers.ReadOnlyField(source='following.id')
    email = serializers.ReadOnlyField(source='following.email')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
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
        return self.context['request'].user.foodgram_recipe_authors.count()
    
    def get_recipes(self, obj):
        request = self.context.get('request')
        user = request.user
        recipes_limit = request.query_params.get('recipes_limit')
        try:
            recipes_limit = int(recipes_limit)
        except (TypeError, ValueError):
            recipes_limit = None
        qs = user.foodgram_recipe_authors.all()
        if recipes_limit:
            qs = qs[:recipes_limit]
        return RecipeReadOnlySerializer(
            qs, many=True, context=self.context
            ).data
    
    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(
            user=obj.user,
            following=obj.following
            ).exists()

    def create(self, validated_data):
        kwargs = self.context.get('request').parser_context.get('kwargs')
        author = get_object_or_404(User, pk=kwargs.get('author_id'))
        user = self.context.get('request').user
        if user == author:
            raise serializers.ValidationError(
                {'errors': 'Нельзя подписаться на себя!'}
            )     
        elif user.follower.filter(
            following=author).exists():
            raise serializers.ValidationError(
                {'errors': 'Вы уже подписаны на этого пользователя!'},
            )
        clean_data = {'user': user, 'following': author}
        return super().create(clean_data)