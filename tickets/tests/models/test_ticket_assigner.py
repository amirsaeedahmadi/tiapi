from django.contrib.auth import get_user_model
from django.test import TestCase

from tickets.models import Ticket
from tickets.tests.factories import TicketFactory
from users.factories import UserFactory

User = get_user_model()


class AssignTicketTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        UserFactory.create_batch(2, is_staff=True, roles=["tickets.accountable"])
        cls.staff1 = User.objects.first()
        cls.staff2 = User.objects.last()
        TicketFactory.create_batch(3)

    def test_load_balancing(self):
        ticket = Ticket.objects.first()
        ticket.accountable = self.staff1
        ticket.save()
        ticket = Ticket.objects.last()
        self.assertEqual(ticket.assign(), self.staff2)
