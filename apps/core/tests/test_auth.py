from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

import pytest
from freezegun import freeze_time

from ..models import OneTimeCode

User = get_user_model()


def test_list_auth_actions(client):
    url = reverse("api:auth-list")
    response = client.get(url)
    assert set(response.data.keys()) == set(["user", "register", "verify"])
    assert response.data["user"] == "http://testserver/api/auth/user/"
    assert response.data["register"] == "http://testserver/api/auth/register/"
    assert response.data["verify"] == "http://testserver/api/auth/verify/"


@pytest.mark.django_db
class TestUser:
    url = reverse("api:auth-user")

    def test_user_logged_out(self, client):
        assert client.get(self.url).status_code == HTTPStatus.NO_CONTENT

    def test_user_logged_in(self, logged_client):
        user = logged_client.user
        response = logged_client.get(self.url)
        assert response.status_code == HTTPStatus.OK
        assert response.data["id"] == user.id
        assert response.data["email"] == user.email
        assert response.data["data"] == {}

    def test_user_with_data(self, client, user_factory):
        profiles = {"profiles": [{"name": "P1", "score": 0}]}
        client.force_login(user_factory(data=profiles))
        response = client.get(self.url)
        assert response.data["data"] == profiles


@pytest.mark.django_db
class TestRegister:
    url = reverse("api:auth-register")

    def test_get_not_allowed(self, client):
        assert client.get(self.url).status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_successful_register(self, client, mailoutbox):
        data = {"email": "e@e.com", "password": "change-me!"}
        response = client.post(self.url, data)
        assert response.status_code == HTTPStatus.CREATED
        assert response.data == {
            "email": data["email"],
            "next_url": "http://testserver/api/auth/verify/",
        }
        assert User.objects.filter(email="e@e.com", is_active=False).exists()
        assert len(mailoutbox) == 1
        assert "is your code for" in mailoutbox[0].subject

    def test_fail_register_existing_user(self, client, user, mailoutbox):
        data = {"email": user.email, "password": "change-me!"}
        response = client.post(self.url, data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        error = response.data["email"][0]
        assert error.code == "invalid"
        assert str(error) == "This email is already in use."
        assert not mailoutbox

    def test_fail_register_invalid_password(self, client, mailoutbox):
        data = {"email": "e@e.com", "password": "12345678"}
        response = client.post(self.url, data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        error = response.data["password"][0]
        assert error.code == "password_too_common"
        assert str(error) == "This password is too common."
        assert not mailoutbox


@pytest.mark.django_db
class TestVerify:
    url = reverse("api:auth-verify")

    def test_get_not_allowed(self, client):
        assert client.get(self.url).status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_successful_verify(self, client, user_factory):
        user = user_factory(is_active=False)
        otp = OneTimeCode.generate(user)
        response = client.post(self.url, {"email": user.email, "code": otp.code})
        assert response.status_code == HTTPStatus.OK
        assert response.data == {
            "id": user.id,
            "email": user.email,
            "data": {},
            "date_joined": user.date_joined.astimezone().isoformat(),
        }
        user.refresh_from_db(fields=["is_active"])
        assert user.is_active

    def test_fail_verify_with_active_user(self, client, user):
        otp = OneTimeCode.generate(user)
        response = client.post(self.url, {"email": user.email, "code": otp.code})
        assert response.status_code == HTTPStatus.GONE
        assert response.data["code"] == "not_valid"

    def test_fail_verify_with_wrong_code(self, client, user_factory):
        non_valid_code = "000000"
        user = user_factory(is_active=False)
        otp = OneTimeCode.generate(user)
        assert otp.code != non_valid_code, f"Flacky test! The code is {non_valid_code}"
        response = client.post(self.url, {"email": user.email, "code": non_valid_code})
        assert response.status_code == HTTPStatus.GONE
        assert response.data["code"] == "not_valid"

    def test_user_doesnt_exist(self, client):
        response = client.post(self.url, {"email": "e@e.eu", "code": "123456"})
        assert response.status_code == HTTPStatus.BAD_REQUEST
        error = response.data["email"][0]
        assert error.code == "invalid"
        assert str(error) == "This email does not exist."

    def test_one_time_code_not_well_formatted(self, client, user):
        otp = OneTimeCode.generate(user)
        response = client.post(self.url, {"email": user.email, "code": "what?"})
        assert response.status_code == HTTPStatus.BAD_REQUEST
        error = response.data["code"][0]
        assert error.code == "invalid"
        assert str(error) == "The entered value is not 6 digits."
