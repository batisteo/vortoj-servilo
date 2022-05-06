from http import HTTPStatus

from django.urls import reverse

import pytest


@pytest.mark.django_db
class TestUser:
    def test_user_logged_out(self, client):
        url = reverse("user-list")
        assert client.get(url).status_code == HTTPStatus.NO_CONTENT

    def test_user_logged_in(self, logged_client):
        user = logged_client.user
        url = reverse("user-list")
        response = logged_client.get(url)
        assert response.status_code == HTTPStatus.OK
        assert response.data["data"] == {}
        assert response.data["id"] == user.id
        assert response.data["email"] == user.email

    def test_user_with_data(self, client, user_factory):
        profiles = {"profiles": [{"name": "P1", "score": 0}]}
        client.force_login(user_factory(data=profiles))
        response = client.get(reverse("user-list"))
        assert response.data["data"] == profiles
