from random import choice
from string import ascii_uppercase

from django.utils.timezone import utc

import factory
from factory.django import DjangoModelFactory, FileField

from apps.core.factories import UserFactory
from apps.core.tests.utils import fake_attr


class LanguageFactory(DjangoModelFactory):
    class Meta:
        model = "game.Language"

    name_en = fake_attr("language_name")

    @factory.lazy_attribute
    def code(self):
        char = choice(ascii_uppercase)
        return f"{self.name_en[:2].lower()}_{self.name_en[-2:].upper()}{char}"


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = "game.Category"

    version = fake_attr("numerify", text="%!")
    uid = fake_attr("numerify", text="%#######")
    name = fake_attr("word")
    description = fake_attr("paragraph", nb_sentences=5)
    language = factory.SubFactory(LanguageFactory)
    author = factory.SubFactory(UserFactory)
    community = fake_attr("boolean", chance_of_getting_true=10)
    date_approved = fake_attr("date_time_this_year", tzinfo=utc)
    difficulty = fake_attr("pyint", max_value=9)
    xp_minimum = fake_attr("pyint", max_value=9)
    xp_modifier = fake_attr("pyint", max_value=9)
    approved_by = factory.SubFactory(UserFactory)
    created = fake_attr("date_time_this_year", tzinfo=utc)
    modified = fake_attr("date_time_this_year", tzinfo=utc)
    zip_file = FileField(filename="category.zip")
    data = fake_attr(
        "json",
        data_columns={
            "sentence": "sentence",
            "correct_answer": "words",
            "wrong_answer": "words",
            "incorrect_spelling": "words",
            "image": "file_name",
            "audio": "file_name",
        },
    )
