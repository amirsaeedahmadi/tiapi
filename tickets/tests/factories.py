import uuid

import factory
from faker import Faker

from tickets.models import Attachment
from tickets.models import FollowUp
from tickets.models import Ticket
from users.factories import UserFactory
from utils.files import uploaded_image_file
from utils.tokens import generate_integer_code

faker = Faker()


class AttachmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Attachment

    file = uploaded_image_file()
    user = factory.SubFactory(UserFactory)


class TicketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ticket

    id = factory.LazyAttribute(lambda _: uuid.uuid4())
    ref_code = factory.LazyAttribute(lambda _: generate_integer_code(length=8))
    user = factory.SubFactory(UserFactory)
    accountable = factory.SubFactory(UserFactory)
    cat = factory.Iterator([1, 2])
    priority = factory.Iterator([1, 2, 3, 4])

    @factory.post_generation
    def attachments(self, create, extracted, **kwargs):
        if not create or not extracted:
            # Simple build, or nothing to add, do nothing.
            return

        # Add the iterable of groups using bulk addition
        self.attachments.add(*extracted)


class FollowUpFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FollowUp

    id = factory.LazyAttribute(lambda _: uuid.uuid4())
    ticket = factory.SubFactory(TicketFactory)
    user = factory.SubFactory(UserFactory)
