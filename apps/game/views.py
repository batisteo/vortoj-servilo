from rest_framework.viewsets import ModelViewSet

from apps.core.permissions import IsAdminUserOrReadOnly

from .models import Category, Language
from .serializers import CategorySerializer, LanguageSerializer


class LanguageViewSet(ModelViewSet):
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    lookup_field = "code"


class CategoryViewSet(ModelViewSet):
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = Category.objects.select_related("author", "approved_by")
    serializer_class = CategorySerializer
    filterset_fields = ["language"]
    search_fields = ["name", "description", "^author__email"]
    ordering_field = ["created", "modified"]
    ordering = ["-created"]
