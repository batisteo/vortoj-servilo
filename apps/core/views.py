from django.contrib.auth import get_user_model
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .serializers import UserSerializer


class UserViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()

    def list(self, request):
        if request.user.is_anonymous:
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        return Response(self.get_serializer_class()(request.user).data)
