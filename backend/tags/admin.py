
from django.conf import settings
from django.contrib import admin

from .models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug', )
    list_editable = ('name', 'color', 'slug', )
    search_fields = ('name', 'slug', )
    list_filter = ('name',)
    empty_value_display = settings.ADMIN_MODEL_EMPTY_VALUE
