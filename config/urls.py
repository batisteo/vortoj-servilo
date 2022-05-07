from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.core.views import UserViewSet
from apps.game.views import CategoryViewSet, LanguageViewSet

router = DefaultRouter()
router.register("auth/user", UserViewSet)
router.register("languages", LanguageViewSet)
router.register("categories", CategoryViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
