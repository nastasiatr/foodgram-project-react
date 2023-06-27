from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from ingredients.models import Ingredient
from tags.models import Tag
from users.models import User, UserRelated


class Recipe(models.Model):
    created = models.DateTimeField(
        'Дата создания рецепта',
        auto_now_add=True,
        help_text='Автоматически устанавливается текущая дата и время',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        verbose_name='Автор рецепта',
        help_text='Выберите, пожалуйста, автора рецепта из списка',
    )
    name = models.CharField(
        'Название рецепта',
        max_length=settings.NAME_MAX_LENGTH,
        help_text='Введите, пожалуйста, название рецепта'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
        help_text='Добавьте, пожалуйста, картинку',
    )
    text = models.TextField(
        'Описание рецепта',
        help_text='Введите, пожалуйста, описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        help_text='Введите время приготовления в минутах',
        validators=[
            MinValueValidator(1, message='Укажите время (>= 1)'), ], )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты',
        help_text='Выберите, пожалуйста, ингредиенты из списка',
    )
    tags = models.ManyToManyField(
        Tag, through='TagRecipe',
        verbose_name='Теги', help_text='Выберите теги'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = '%(class)ss'
        ordering = ("-created",)

    def __str__(self) -> str:
        return f'id: {self.id} Автор: {str(self.author)} Название: {self.name}'


class RecipeRelated(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Выберите, пожалуйста, рецепт',
    )

    class Meta:
        abstract = True


class TagRecipe(RecipeRelated):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.RESTRICT,
        verbose_name='Тег',
        help_text='Выберите, пожалуйста, тег из списка',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_recipe_tag',
                fields=['recipe', 'tag'],
            ),
        ]
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'


class FavoriteRecipe(RecipeRelated, UserRelated):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_favorite',
                fields=["recipe", "user"],
            ),
        ]
        verbose_name = 'Ваш любимый рецепт'
        verbose_name_plural = 'Ваши любимые рецепты'


class ShoppingCartRecipe(RecipeRelated, UserRelated):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_shopping_cart',
                fields=["recipe", "user"],
            ),
        ]
        verbose_name = 'Рецепт в корзине пользователя'
        verbose_name_plural = 'Рецепты в корзинах пользователей'


class IngredientInRecipe(RecipeRelated):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.RESTRICT,
        verbose_name='Ингредиент рецепта',
        help_text='Выберите, пожалуйста, ингредиент рецепта',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество ингредиентов',
        help_text='Введите количество ингредиентов',
        validators=[
            MinValueValidator(
                1,
                message='Укажите кол-во ингредиентов (больше, или равное 1)'),
        ],
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self) -> str:
        return (
            f'{self.ingredient.name} — {self.amount} '
            f'{self.ingredient.measurement_unit}'
        )
