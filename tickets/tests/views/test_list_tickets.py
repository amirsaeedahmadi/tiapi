from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from tickets.models import Ticket
from tickets.tests.factories import TicketFactory
from users.factories import UserFactory


class ListTicketsTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse("ticket-list")

    @classmethod
    def setUpTestData(cls):
        cls.staff = UserFactory(
            email_verified=True,
            mobile_verified=True,
            is_staff=True,
            roles=["tickets.accountable"],
        )
        cls.superuser = UserFactory(is_superuser=True)
        TicketFactory.create_batch(2, accountable=cls.staff)
        TicketFactory.create_batch(2, user=cls.staff, status=Ticket.OPEN)
        TicketFactory.create_batch(3, user=cls.staff, status=Ticket.CLOSED)
        TicketFactory.create_batch(6, cat=Ticket.SALE)
        TicketFactory.create_batch(7, cat=Ticket.TECHNICAL)
        TicketFactory.create_batch(7, priority=Ticket.LOW)
        TicketFactory.create_batch(14)

    def test_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_superuser_on_admin_host(self):
        self.client.force_authenticate(self.superuser)
        response = self.client.get(self.url, headers={"host": "api.admin.testserver"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("results", data)
        results = data["results"]
        self.assertEqual(data["count"], 41)
        result = results[0]
        self.assertIn("accountable", result)
        self.assertIn("attachments", result)

    def test_filter_by_accountable(self):
        self.client.force_authenticate(self.superuser)
        response = self.client.get(
            self.url,
            {"accountable": self.staff.pk},
            headers={"host": "api.admin.testserver"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("results", data)
        results = data["results"]
        self.assertEqual(len(results), 2)
        result = results[0]
        self.assertIn("accountable", result)
        self.assertIn("attachments", result)

    def test_accountable_queryset_on_admin_host(self):
        self.client.force_authenticate(self.staff)
        response = self.client.get(self.url, headers={"host": "api.admin.testserver"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("results", data)
        results = data["results"]
        self.assertEqual(data["count"], 41)
        result = results[0]
        self.assertIn("accountable", result)
        self.assertIn("attachments", result)

    def test_user_queryset(self):
        self.client.force_authenticate(self.staff)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("results", data)
        results = data["results"]
        self.assertEqual(len(results), 5)
        result = results[0]
        self.assertIn("accountable", result)
        self.assertIn("attachments", result)

    def test_filter_by_status(self):
        self.client.force_authenticate(self.staff)
        response = self.client.get(self.url, {"status": "1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("results", data)
        results = data["results"]
        self.assertEqual(len(results), 3)

    def test_email_unverified(self):
        self.staff.email_verified = False
        self.staff.save()
        self.client.force_authenticate(self.staff)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
