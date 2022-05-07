from http import HTTPStatus

from django.urls import reverse

import pytest


@pytest.mark.django_db
class TestLanguage:
    url = reverse("api:language-list")

    def test_languages_logged_out(self, client):
        assert client.get(self.url).status_code == HTTPStatus.OK

    def test_no_language_listed(self, client):
        assert client.get(self.url).data == []

    def test_language_listed(self, client, language):
        assert client.get(self.url).data == [
            {"code": language.code, "name_en": language.name_en},
        ]

    def test_post_languages_logged_out(self, client):
        assert client.post(self.url).status_code == HTTPStatus.FORBIDDEN

    def test_post_languages_logged_in(self, logged_client):
        assert logged_client.post(self.url).status_code == HTTPStatus.FORBIDDEN

    def test_post_languages_as_staff(self, staff_client):
        data = {"code": "eo", "name_en": "Esperanto"}
        response = staff_client.post(self.url, data)
        assert response.status_code == HTTPStatus.CREATED
        assert response.data == data

    def test_patch_languages_logged_out(self, client):
        assert client.patch(self.url).status_code == HTTPStatus.FORBIDDEN

    def test_patch_languages_logged_in(self, logged_client):
        assert logged_client.patch(self.url).status_code == HTTPStatus.FORBIDDEN

    def test_patch_languages_as_staff(self, staff_client, language):
        data = {"name_en": "Other"}
        url = reverse("api:language-detail", kwargs={"code": language.code})
        response = staff_client.patch(url, data)
        assert response.status_code == HTTPStatus.OK
        assert response.data == {"code": language.code, **data}
        language.refresh_from_db(fields=["name_en"])
        assert language.name_en == "Other"

    def test_delete_languages_logged_out(self, client):
        assert client.delete(self.url).status_code == HTTPStatus.FORBIDDEN

    def test_delete_languages_logged_in(self, logged_client):
        assert logged_client.delete(self.url).status_code == HTTPStatus.FORBIDDEN

    def test_delete_languages_as_staff(self, staff_client, language):
        url = reverse("api:language-detail", kwargs={"code": language.code})
        response = staff_client.delete(url)
        assert response.status_code == HTTPStatus.NO_CONTENT
        with pytest.raises(language.__class__.DoesNotExist):
            language.refresh_from_db()
