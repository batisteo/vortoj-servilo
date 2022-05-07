from .base import *  # noqa

SHELL_PLUS_IMPORTS = [
    "from apps.core.factories import UserFactory",
    "from apps.core.serializers import UserSerializer",
    "from apps.game.factories import CategoryFactory, LanguageFactory",
    "from apps.game.serializers import CategorySerializer, LanguageSerializer",
]
