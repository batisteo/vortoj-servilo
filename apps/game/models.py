from django.db import models

from django_extensions.db.models import TimeStampedModel


def zip_file_path(instance, filename):
    return f"categories/{instance.name}-{instance.uid}-{instance.version}.zip"


class Language(models.Model):
    code = models.CharField(max_length=6, unique=True)
    name_en = models.CharField(max_length=100)

    def __str__(self):
        return self.code


class Category(TimeStampedModel):
    uid = models.CharField("UID", max_length=36, unique=True)
    version = models.CharField("version", max_length=16)
    name = models.CharField("name", max_length=100)
    description = models.TextField("description", blank=True)
    language = models.ForeignKey(
        Language, verbose_name="language", on_delete=models.CASCADE, to_field="code"
    )
    difficulty = models.PositiveSmallIntegerField("difficulty", default=0)
    xp_minimum = models.PositiveSmallIntegerField("XP minimum", default=0)
    xp_modifier = models.PositiveSmallIntegerField("XP modifier", default=1)
    author = models.ForeignKey(
        "core.User",
        verbose_name="author",
        on_delete=models.CASCADE,
        related_name="categories",
    )
    community = models.BooleanField("community", default=False)
    date_approved = models.DateTimeField("date approved", null=True, blank=True)
    approved_by = models.ForeignKey(
        "core.User",
        verbose_name="approved by",
        on_delete=models.CASCADE,
        related_name="approved_categories",
        null=True,
        blank=True,
    )
    zip_file = models.FileField("ZIP file", upload_to=zip_file_path, blank=True)
    data = models.JSONField("data", default=list, blank=True)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    @property
    def approved(self):
        return self.date_approved is not None

    def __str__(self):
        return self.name
