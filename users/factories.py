import uuid

import factory
from django.contrib.auth import get_user_model
from faker import Faker

User = get_user_model()
faker = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    id = factory.LazyAttribute(lambda _: uuid.uuid4())
    first_name = factory.LazyAttribute(lambda _: faker.first_name())
    last_name = factory.LazyAttribute(lambda _: faker.last_name())
    email = factory.LazyAttribute(lambda _: faker.unique.email())
    email_verified = factory.LazyAttribute(lambda _: faker.boolean())
