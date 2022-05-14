from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinValueValidator


MIN_ING_AMOUNT = 1
MIN_COOK_TIME = 1
MAX_NAME_LENGTH = 200
MAX_UNIT_LENGTH = 200


User = get_user_model()


class CustomBaseModel(models.Model):
    """Base model class with common fields."""

    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_NAME_LENGTH,
        unique=True
    )
    date_created = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        db_index=True
    )
    date_modified = models.DateTimeField(
        verbose_name='Дата последнего редактирования',
        auto_now=True,
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='%(app_label)s_%(class)s_authors'
    )
    last_editor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Последний редактор',
        related_name='%(app_label)s_%(class)s_editors'
    )

    class Meta:
        abstract = True
        ordering = ['-date_modified']

    def __str__(self):
        return f'{self.name} - {self.author}'


class Tag(CustomBaseModel):
    """Model for tags."""

    color = models.CharField(
        verbose_name='Цветовой HEX-код',
        validators=[
            RegexValidator(
                r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                'пожалуйста введите валидный шестнадцатеричный цветовой код'
            )
        ],
        unique=True,
        max_length=10
    )
    slug = models.SlugField(
        verbose_name='Читаемое представление тега (слаг)',
        unique=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name} - {self.slug} - {self.color}'


class Ingredient(CustomBaseModel):
    """Model for recipe ingredients."""

    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_UNIT_LENGTH
    )

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_tags'
            )
        ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} [{self.measurement_unit}]'


class Recipe(CustomBaseModel):
    """Model for recipes."""

    text = models.TextField(
        verbose_name='Описание'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[
            MinValueValidator(MIN_COOK_TIME, 
            f'время приготовления должно быть не менее {MIN_COOK_TIME} мин.'
            )
        ]
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipe_tags'
    )

    class Meta:
        ordering = ['-date_modified']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} - {self.author}'


class IngredientAmount(models.Model):
    """Model to match ingredient to amounts for a recipe."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_amount_recipes',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amounts',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(MIN_ING_AMOUNT, 
            f'укажите количество не менее {MIN_ING_AMOUNT}'
            )
        ]
    )

    class Meta:
        ordering = ['ingredient']
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.recipe.name} - {self.ingredient} {self.amount}'


class GeneralListBaseModel(CustomBaseModel):
    """General model for shopping and favourite lists."""

    name = None
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_recipes',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_users',
        verbose_name='Пользователь'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['content_type', 'object_id', 'user', 'recipe'], 
                name='%(app_label)s_%(class)s_user_recipe_unique'
            ),
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe} - {self.date_created}'


class FavouriteList(GeneralListBaseModel):
    """Recipes for favourite list."""

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingList(GeneralListBaseModel):
    """Recipes for shopping list."""

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class Subscription(CustomBaseModel):
    """Subscriptions to authors of recipes."""

    name = None
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор рецептов'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_following'
            )
        ]
        ordering = ['-date_created']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (
            f'{self.date_created} '
            f'- {self.user.username} '
            f'подписался на {self.following.username}'
        )