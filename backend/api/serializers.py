from django.db import transaction
from djoser import serializers as djoser_serializers
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers as serializers

from ingredients.models import Ingredient
from recipes.models import IngredientInRecipe, Recipe
from tags.models import Tag
from users.models import Subscription, User


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time',)
        read_only_fields = fields


class UserSerializer(djoser_serializers.UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, author):
        request = self.context['request']
        return (
                request.user.is_authenticated
                and author.subscriptions.filter(user=request.user).exists()
        )

    class Meta(djoser_serializers.UserSerializer.Meta):
        model = User
        fields = djoser_serializers.UserSerializer.Meta.fields + ('is_subscribed',)


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count',)
        read_only_fields = fields

    def get_recipes(self, user_object):
        queryset = user_object.recipes.all()
        recipes_limit = self.context['request'].query_params.get('recipes_limit')
        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
                queryset = queryset[:recipes_limit]
            except (TypeError, ValueError):
                raise serializers.ValidationError(
                    'Ошибка запроса получения рецептов'
                )
        return RecipeMinifiedSerializer(queryset, many=True).data

    def get_recipes_count(self, user_object):
        return user_object.recipes.count()


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Subscription
        fields = ('user', 'author',)

    def validate(self, attrs):
        user = self.context.get('request').user
        author = self.initial_data.get('author')
        if user == author:
            raise serializers.ValidationError('Подписка "Нас себя" не возможна!')
        if author.subscriptions.filter(user=user).exists():
            raise serializers.ValidationError(
                'Подписаться на автора можно только 1 раз!'
            )
        return super().validate(attrs)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        source='ingredient', slug_field='id', queryset=Ingredient.objects.all()
    )
    name = serializers.SlugRelatedField(
        source='ingredient', slug_field='name', read_only=True
    )
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient', slug_field='measurement_unit', read_only=True
    )

    class Meta:
        model = IngredientInRecipe
        exclude = ('recipe', 'ingredient',)


class RecipeListSerializer(serializers.ModelSerializer):
    author = UserSerializer(default=serializers.CurrentUserDefault(), read_only=True)
    image = Base64ImageField(max_length=None, use_url=True)
    ingredients = IngredientInRecipeSerializer(
        source="ingredientinrecipe_set", many=True
    )
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('created',)

    def get_is_favorited(self, recipe):
        request = self.context['request']
        return (
                request.user.is_authenticated
                and recipe.favoriterecipe_set.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        request = self.context['request']
        return (
                request.user.is_authenticated
                and recipe.shoppingcartrecipe_set.filter(user=request.user).exists()
        )


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(
        source='ingredientinrecipe_set', many=True
    )
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        depth = 2
        fields = ('ingredients',
                  'tags',
                  'image',
                  'name',
                  'text',
                  'cooking_time',)

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data

    @staticmethod
    def create_ingredientsinrecipe(recipe, ingredientinrecipe_set):
        IngredientInRecipe.objects.bulk_create(
            [
                IngredientInRecipe(
                    recipe=recipe, ingredient=item['ingredient'], amount=item['amount']
                )
                for item in ingredientinrecipe_set
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        request = self.context['request']
        ingredientinrecipe_set = validated_data.pop('ingredientinrecipe_set')
        tags = validated_data.pop('tags')
        instance = Recipe.objects.create(author=request.user, **validated_data)
        RecipeSerializer.create_ingredientsinrecipe(instance, ingredientinrecipe_set)
        instance.tags.set(tags)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        if 'ingredientinrecipe_set' in validated_data:
            ingredientinrecipe_set = validated_data.pop('ingredientinrecipe_set')
            if ingredientinrecipe_set:
                instance.ingredients.clear()
            RecipeSerializer.create_ingredientsinrecipe(
                instance, ingredientinrecipe_set
            )
        return super().update(instance, validated_data)

    def validate(self, attrs):
        if len(attrs['tags']) == 0:
            raise serializers.ValidationError('Выберите хотя бы 1 тег.')

        if len(attrs['tags']) != len(set(attrs['tags'])):
            raise serializers.ValidationError('Теги должны быть уникальны.')

        if len(attrs['ingredientinrecipe_set']) == 0:
            raise serializers.ValidationError(
                'Выберите хотя бы 1 ингредиент.'
            )

        ingredients = attrs['ingredientinrecipe_set']
        if len(ingredients) != len(set(obj['ingredient'] for obj in ingredients)):
            raise serializers.ValidationError('Ингредиенты должны быть уникальны.')

        if any(obj['amount'] <= 0 for obj in ingredients):
            raise serializers.ValidationError(
                'Количество игредиента должно быть больше 0.'
            )

        if attrs['cooking_time'] <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0.'
            )
        return super().validate(attrs)
