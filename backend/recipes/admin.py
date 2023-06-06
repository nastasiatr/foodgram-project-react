from django.conf import settings
from django.contrib import admin

from .models import (
    Recipe,
    IngredientInRecipe,
    FavoriteRecipe,
    TagRecipe,
    ShoppingCartRecipe,
)


class IngredientInRecipeInline(admin.TabularInline):
    template = 'admin/edit_inline/custom_tabular.html'
    model = IngredientInRecipe
    extra = 0
    min_num = 1


class FavoriteRecipeInline(admin.TabularInline):
    model = FavoriteRecipe
    extra = 0


class TagRecipeInline(admin.TabularInline):
    template = 'admin/edit_inline/custom_tabular.html'
    model = TagRecipe
    extra = 0
    min_num = 1


class ShoppingCartRecipeInline(admin.TabularInline):
    model = ShoppingCartRecipe
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    @admin.display(description='Количество добавленных рецептов в избранное')
    def favorite_amount(self):
        """Вывод в админке количества избранных рецептов."""
        return FavoriteRecipe.objects.filter(recipe=self.id).count()

    @admin.display(description='Игредиенты')
    def ingredients_in_recipe(self):
        """Вывод в админке ингредиентов рецепта."""
        return self.ingredientinrecipe_set.values_list()

    list_display = ('pk', 'name', 'author', ingredients_in_recipe, favorite_amount, )
    search_fields = ('author', 'name', )
    list_filter = ('name', 'author', 'tags', )
    inlines = (IngredientInRecipeInline, FavoriteRecipeInline, TagRecipeInline, ShoppingCartRecipeInline, )
    readonly_fields = (favorite_amount,)
    empty_value_display = settings.ADMIN_MODEL_EMPTY_VALUE


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount', )
    list_editable = ('amount',)
    list_filter = ('recipe', 'ingredient', )
    empty_value_display = settings.ADMIN_MODEL_EMPTY_VALUE


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'user', )
    list_filter = ('recipe', 'user', )
    empty_value_display = settings.ADMIN_MODEL_EMPTY_VALUE


@admin.register(ShoppingCartRecipe)
class ShoppingCartRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'user', )
    list_filter = ('recipe', 'user', )
    empty_value_display = settings.ADMIN_MODEL_EMPTY_VALUE


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'tag', )
    list_filter = ('recipe', 'tag', )
    empty_value_display = settings.ADMIN_MODEL_EMPTY_VALUE
