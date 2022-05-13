from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator


User = get_user_model()


class CustomBaseModel(models.Model):
    """Base model class with common fields."""

    name = models.CharField(
        verbose_name='Название',
        max_length=100,
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

    color_hexcode = models.CharField(
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
        return f'{self.name} - {self.slug} - {self.color_hexcode}'


class Ingredient(CustomBaseModel):
    """Model for recipe ingredients."""

    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=20
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


class IngredientAmount(CustomBaseModel):
    """Model to match ingredient to amounts for a recipe."""

    name = None
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amounts'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество'
    )

    class Meta:
        ordering = ['ingredient']
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'


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
        verbose_name='Время приготовления в минутах'
    )
    ingredients = models.ManyToManyField(
        IngredientAmount,
        related_name='recipe_ingredients'
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


class FavouriteList(CustomBaseModel):
    """Recipes for favourite list."""

    name = None
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourite_recipes',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourite_users',
        verbose_name='Пользователь'
    )

    class Meta:
        ordering = ['-date_created']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user} - {self.recipe} - {self.date_created}'


class ShoppingList(FavouriteList):
    """Recipes for shopping list."""

    class Meta:
        ordering = ['-date_created']
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
        verbose_name='Автор публикаций'
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