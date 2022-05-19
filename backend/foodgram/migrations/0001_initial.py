# Generated by Django 3.2.13 on 2022-05-19 18:35

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Название')),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания')),
                ('date_modified', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Дата последнего редактирования')),
                ('measurement_unit', models.CharField(max_length=200, verbose_name='Единица измерения')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foodgram_ingredient_authors', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('last_editor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foodgram_ingredient_editors', to=settings.AUTH_USER_MODEL, verbose_name='Последний редактор')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='IngredientAmount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, 'укажите количество не менее 1')], verbose_name='Количество')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient_amounts', to='foodgram.ingredient', verbose_name='Ингредиент')),
            ],
            options={
                'verbose_name': 'Количество ингредиента',
                'verbose_name_plural': 'Количество ингредиентов',
                'ordering': ['ingredient'],
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Название')),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания')),
                ('date_modified', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Дата последнего редактирования')),
                ('text', models.TextField(verbose_name='Описание')),
                ('image', models.ImageField(upload_to='recipes/', verbose_name='Картинка')),
                ('cooking_time', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, 'минимальное время приготовления 1 мин.')], verbose_name='Время приготовления в минутах')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foodgram_recipe_authors', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('ingredients', models.ManyToManyField(related_name='ingredients', through='foodgram.IngredientAmount', to='foodgram.Ingredient', verbose_name='Ингредиенты')),
                ('last_editor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foodgram_recipe_editors', to=settings.AUTH_USER_MODEL, verbose_name='Последний редактор')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ['-date_modified'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Название')),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания')),
                ('date_modified', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Дата последнего редактирования')),
                ('color', models.CharField(max_length=7, unique=True, validators=[django.core.validators.RegexValidator('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', 'пожалуйста введите валидный шестнадцатеричный цветовой код')], verbose_name='Цветовой HEX-код')),
                ('slug', models.SlugField(unique=True, verbose_name='Читаемое представление тега (слаг)')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foodgram_tag_authors', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('last_editor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foodgram_tag_editors', to=settings.AUTH_USER_MODEL, verbose_name='Последний редактор')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания')),
                ('date_modified', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Дата последнего редактирования')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foodgram_subscription_authors', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('following', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL, verbose_name='Автор рецептов')),
                ('last_editor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foodgram_subscription_editors', to=settings.AUTH_USER_MODEL, verbose_name='Последний редактор')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follower', to=settings.AUTH_USER_MODEL, verbose_name='Подписчик')),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
                'ordering': ['-date_created'],
            },
        ),
        migrations.CreateModel(
            name='ShoppingList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания')),
                ('date_modified', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Дата последнего редактирования')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foodgram_shoppinglist_authors', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('last_editor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foodgram_shoppinglist_editors', to=settings.AUTH_USER_MODEL, verbose_name='Последний редактор')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foodgram_shoppinglist_recipes', to='foodgram.recipe', verbose_name='Рецепт')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foodgram_shoppinglist_users', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Список покупок',
                'verbose_name_plural': 'Списки покупок',
            },
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(related_name='recipe_tags', to='foodgram.Tag', verbose_name='Теги'),
        ),
        migrations.AddField(
            model_name='ingredientamount',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient_amount_recipes', to='foodgram.recipe', verbose_name='Рецепт'),
        ),
        migrations.CreateModel(
            name='FavouriteList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания')),
                ('date_modified', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Дата последнего редактирования')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foodgram_favouritelist_authors', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('last_editor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foodgram_favouritelist_editors', to=settings.AUTH_USER_MODEL, verbose_name='Последний редактор')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foodgram_favouritelist_recipes', to='foodgram.recipe', verbose_name='Рецепт')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foodgram_favouritelist_users', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Избранное',
                'verbose_name_plural': 'Избранное',
            },
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(fields=('user', 'following'), name='unique_following'),
        ),
        migrations.AddConstraint(
            model_name='ingredientamount',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_recipe_ingredient'),
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='unique_tags'),
        ),
    ]
