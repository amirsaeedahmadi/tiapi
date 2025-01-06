from unittest.mock import patch

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from tickets.tests.factories import TicketFactory
from users.factories import UserFactory


class CloseTicketTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(email_verified=True, mobile_verified=True)
        cls.other_user = UserFactory(email_verified=True, mobile_verified=True)
        cls.staff = UserFactory(is_staff=True, roles=["tickets.accountable"])
        cls.other_staff = UserFactory(is_staff=True, roles=["tickets.accountable"])
        cls.superuser = UserFactory(is_superuser=True)
        cls.ticket = TicketFactory(user=cls.user)
        cls.url = reverse("ticket-close", kwargs={"pk": cls.ticket.pk})

    def test_unauthenticated(self):
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_other_user(self):
        self.client.force_authenticate(self.other_user)
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("utils.kafka.KafkaEventStore.add_event")
    def test_other_staff_on_admin_host(self, add_event):
        self.client.force_authenticate(self.other_staff)
        response = self.client.patch(self.url, headers={"host": "api.admin.testserver"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        add_event.assert_called()

    @patch("utils.kafka.KafkaEventStore.add_event")
    def test_superuser_on_admin_host(self, add_event):
        self.client.force_authenticate(self.superuser)
        response = self.client.patch(self.url, headers={"host": "api.admin.testserver"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        add_event.assert_called()

    @patch("utils.kafka.KafkaEventStore.add_event")
    def test_user(self, add_event):
        self.client.force_authenticate(self.user)
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        add_event.assert_called()
