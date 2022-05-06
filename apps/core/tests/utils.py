import factory
from faker import Faker

fake = Faker()

# https://faker.readthedocs.io/en/master/providers.html
def fake_attr(attr=None, func=None, **kwargs):
    callable = lambda o: (func if func else getattr(fake, attr))(**kwargs)
    return factory.LazyAttribute(callable)
