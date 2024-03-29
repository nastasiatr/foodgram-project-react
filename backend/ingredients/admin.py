from django.conf import settings
from django.contrib import admin

from .models import Ingredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit', )
    list_editable = ('name', 'measurement_unit', )
    search_fields = ('name', 'measurement_unit', )
    list_filter = ('name',)
    empty_value_display = settings.ADMIN_MODEL_EMPTY_VALUE
