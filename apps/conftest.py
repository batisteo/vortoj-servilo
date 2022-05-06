from rest_framework.test import APIClient

import pytest
from pytest_factoryboy import register

from apps.core.factories import UserFactory

register(UserFactory)  # fixtures: user & user_factory


@pytest.fixture()
def staff():
    return UserFactory(is_staff=True)


@pytest.fixture()
def client():
    return APIClient()


@pytest.fixture()
def logged_client(client, user):
    client.force_login(user)
    client.user = user
    return client


@pytest.fixture()
def staff_client(client, staff):
    client.force_login(staff)
    client.user = staff
    return client
