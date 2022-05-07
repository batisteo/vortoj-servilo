from django.contrib import admin

from .models import Category, Language


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ["name_en", "code"]
    list_display_link = ["name_en", "code"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["__str__", "uid", "language", "author", "version"]
