from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Category, Language

User = get_user_model()


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ["code", "name_en"]


class CategorySerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField("email", queryset=User.objects.all())
    approved_by = serializers.StringRelatedField()
    date_created = serializers.DateTimeField(source="created")
    date_modified = serializers.DateTimeField(source="modified")
    path = serializers.FileField(
        source="zip_file", required=False, use_url=False, allow_empty_file=False
    )

    class Meta:
        model = Category
        fields = [
            "id",
            "version",
            "uid",
            "name",
            "description",
            "language",
            "difficulty",
            "xp_minimum",
            "xp_modifier",
            "author",
            "community",
            "approved",
            "approved_by",
            "date_created",
            "date_modified",
            "path",
            "data",
        ]
