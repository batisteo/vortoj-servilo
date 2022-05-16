from django.contrib.auth import get_user_model
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .serializers import RegisterSerializer, UserSerializer, ValidateCodeSerializer
from .utils import get_url

User = get_user_model()


class AuthViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "user":
            return UserSerializer
        if self.action == "verify":
            return ValidateCodeSerializer
        return RegisterSerializer

    def list(self, request):
        return Response(
            {
                action.url_name: f"{get_url(request._request)}{action.url_path}/"
                for action in self.get_extra_actions()
            }
        )

    @action(detail=False)
    def user(self, request):
        if request.user.is_anonymous:
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        return Response(self.get_serializer_class()(request.user).data)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def register(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def verify(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            user = serializer.is_valid(raise_exception=True)
        except Http404:
            detail = (
                "This code was already used "
                "or issued more than 10 minutes ago "
                "or user is already verified"
            )
            return Response(
                {
                    "message": "Code is no longer valid",
                    "code": "not_valid",
                    "detail": detail,
                },
                status=status.HTTP_410_GONE,
            )
        return Response(UserSerializer(user).data)
