import pdfkit
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (IngredientSerializer, RecipeListSerializer,
                             RecipeMinifiedSerializer, RecipeSerializer,
                             SubscriptionSerializer, TagSerializer,
                             UserWithRecipesSerializer)
from django.db.models import Sum
from django.db.models.query_utils import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.utils import timezone
from djoser import views
from ingredients.models import Ingredient
from recipes.models import (FavoriteRecipe, IngredientInRecipe, Recipe,
                            ShoppingCartRecipe, TagRecipe)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from tags.models import Tag
from users.models import Subscription, User


class TokenCreateView(views.TokenCreateView):
    def _action(self, serializer):
        response = super()._action(serializer)
        if response.status_code == status.HTTP_200_OK:
            response.status_code = status.HTTP_201_CREATED
        return response


class UserWithRecipesViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserWithRecipesSerializer
    permission_classes = (IsAuthenticated,)

    def get_author(self) -> User:
        return get_object_or_404(User, id=self.kwargs.get("author_id"))

    def get_object(self):
        return get_object_or_404(
            Subscription, user=self.request.user, author=self.get_author()
        )

    def destroy(self, request, *args, **kwargs):
        self.get_author()
        try:
            self.get_object()
        except Http404:
            data = {'errors': 'Ошибка! Невозможно отписаться. Вы не подсисаны на автора'}
            return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in (
            "create",
            "destroy",
        ):
            return SubscriptionSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return User.objects.filter(subscriptions__user=self.request.user)
        return None

    def create(self, request, *args, **kwargs):
        request.data.update(author=self.get_author())
        super().create(request, *args, **kwargs)
        serializer = self.serializer_class(
            instance=self.get_author(), context=self.get_serializer_context()
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save(author=self.get_author())


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    pagination_class = None

    def get_queryset(self):
        return Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get("name")
        if name is not None:
            qs_starts = queryset.filter(name__istartswith=name)
            qs_contains = queryset.filter(
                ~Q(name__istartswith=name) & Q(name__icontains=name)
            )
            queryset = list(qs_starts) + list(qs_contains)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeListSerializer
    edit_serializer_class = RecipeSerializer
    edit_permission_classes = (IsAuthorOrReadOnly,)

    @staticmethod
    def generate_shopping_cart_pdf(queryset, user):
        data = {
            "page_objects": queryset,
            "user": user,
            "created": timezone.now(),
        }

        template = get_template("shopping_cart.html")
        html = template.render(data)
        pdf = pdfkit.from_string(html, False, options={"encoding": "UTF-8"})

        filename = "shopping_cart.pdf"
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    def get_permissions(self):
        if self.action in (
            "destroy",
            "partial_update",
        ):
            return [permission() for permission in self.edit_permission_classes]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in (
            "create",
            "partial_update",
        ):
            return self.edit_serializer_class
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = Recipe.objects.all()
        user = self.request.user
        is_favorited = self.request.query_params.get("is_favorited")
        if is_favorited:
            recipes_id = (
                FavoriteRecipe.objects.filter(user=user).values("recipe__id")
                if user.is_authenticated
                else []
            )
            condition = Q(id__in=recipes_id)
            queryset = queryset.filter(
                condition if is_favorited == "1" else ~condition
            ).all()
        is_in_shopping_cart = self.request.query_params.get("is_in_shopping_cart")
        if is_in_shopping_cart:
            recipes_id = (
                ShoppingCartRecipe.objects.filter(user=user).values("recipe__id")
                if user.is_authenticated
                else []
            )
            condition = Q(id__in=recipes_id)
            queryset = queryset.filter(
                condition if is_in_shopping_cart == "1" else ~condition
            ).all()
        author_id = self.request.query_params.get("author")
        if author_id:
            queryset = queryset.filter(author__id=author_id).all()
        tags = self.request.query_params.getlist("tags")
        if tags:
            tags = Tag.objects.filter(slug__in=tags).all()
            recipes_id = (
                TagRecipe.objects.filter(tag__in=tags).values("recipe__id").distinct()
            )
            queryset = queryset.filter(id__in=recipes_id)
        return queryset

    @action(permission_classes=((IsAuthenticated,)), detail=False)
    def download_shopping_cart(self, request):
        queryset = (
            IngredientInRecipe.objects.filter(
                recipe__shoppingcartrecipe__user=request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(Sum("amount"))
            .order_by("ingredient__name")
        )
        return RecipeViewSet.generate_shopping_cart_pdf(queryset, request.user)

    @staticmethod
    def create_related_object(request, pk, model, serializer, error):
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(recipe=recipe, user=request.user).exists():
            return Response({"errors": error}, status.HTTP_400_BAD_REQUEST)
        instance = model(recipe=recipe, user=request.user)
        instance.save()
        serializer = serializer(
            get_object_or_404(Recipe, id=pk), context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_related_object(request, pk, model):
        get_object_or_404(model, recipe_id=pk, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["post"], detail=True)
    def favorite(self, request, pk):
        return RecipeViewSet.create_related_object(
            request,
            pk,
            FavoriteRecipe,
            RecipeMinifiedSerializer,
            "Рецепт уже добавлен в избранное.",
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return RecipeViewSet.delete_related_object(request, pk, FavoriteRecipe)

    @action(methods=["post"], detail=True)
    def shopping_cart(self, request, pk):
        return RecipeViewSet.create_related_object(
            request,
            pk,
            ShoppingCartRecipe,
            RecipeMinifiedSerializer,
            "Рецепт уже добавлен в корзину.",
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return RecipeViewSet.delete_related_object(request, pk, ShoppingCartRecipe)
