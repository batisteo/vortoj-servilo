from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

import pytest

from ..serializers import CategorySerializer


@pytest.mark.django_db
class TestCategory:
    url = reverse("api:category-list")

    def test_categories_logged_out(self, client):
        assert client.get(self.url).status_code == HTTPStatus.OK

    def test_game(self, client, category):
        response = client.get(self.url)
        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == category.id

    def test_no_category_listed(self, client):
        assert client.get(self.url).data == []

    def test_category_listed(self, client, category):
        assert client.get(self.url).data == [CategorySerializer(category).data]

    def test_post_category_logged_out(self, client):
        assert client.post(self.url).status_code == HTTPStatus.FORBIDDEN

    def test_post_category_logged_in(self, logged_client):
        assert logged_client.post(self.url).status_code == HTTPStatus.FORBIDDEN

    def test_post_category_as_staff(
        self, staff_client, category_factory, language, user
    ):
        category = category_factory.build(language=language, author=user)
        data = CategorySerializer(category).data
        del data["id"]
        data["path"] = SimpleUploadedFile("category.zip", b"zipfile")
        response = staff_client.post(self.url, data)
        assert response.status_code == HTTPStatus.CREATED
        assert response.data["version"] == category.version
        assert response.data["uid"] == category.uid
        assert response.data["name"] == category.name
        assert response.data["description"] == category.description
        assert response.data["language"] == category.language.code
        assert response.data["difficulty"] == category.difficulty
        assert response.data["xp_minimum"] == category.xp_minimum
        assert response.data["xp_modifier"] == category.xp_modifier
        assert response.data["author"] == category.author.email
        assert response.data["community"] == category.community
        assert response.data["approved"] == False
        assert response.data["approved_by"] == None

    def test_patch_category_logged_out(self, client):
        assert client.patch(self.url).status_code == HTTPStatus.FORBIDDEN

    def test_patch_category_logged_in(self, logged_client):
        assert logged_client.patch(self.url).status_code == HTTPStatus.FORBIDDEN

    def test_patch_category_as_staff(self, staff_client, category):
        data = {"data": {"profile": "Other"}}
        url = reverse("api:category-detail", kwargs={"pk": category.pk})
        response = staff_client.patch(url, data, format="json")
        assert response.status_code == HTTPStatus.OK
        assert response.data["data"] == data["data"]
        assert response.data["id"] == category.pk
        category.refresh_from_db()
        assert category.data == data["data"]

    def test_delete_category_logged_out(self, client):
        assert client.delete(self.url).status_code == HTTPStatus.FORBIDDEN

    def test_delete_category_logged_in(self, logged_client):
        assert logged_client.delete(self.url).status_code == HTTPStatus.FORBIDDEN

    def test_delete_category_as_staff(self, staff_client, category):
        url = reverse("api:category-detail", kwargs={"pk": category.pk})
        response = staff_client.delete(url)
        assert response.status_code == HTTPStatus.NO_CONTENT
        with pytest.raises(category.__class__.DoesNotExist):
            category.refresh_from_db()
