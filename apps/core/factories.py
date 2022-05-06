from django.contrib.auth import get_user_model
from django.utils.timezone import utc

from factory.django import DjangoModelFactory

from apps.core.tests.utils import fake_attr


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    email = fake_attr("email")
    date_joined = fake_attr("date_time_this_year", tzinfo=utc)
