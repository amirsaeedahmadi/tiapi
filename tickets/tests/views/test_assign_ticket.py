from unittest.mock import patch

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from tickets.tests.factories import TicketFactory
from users.factories import UserFactory


class AssignTicketTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = UserFactory(is_staff=True, roles=["tickets.accountable"])
        cls.other_staff = UserFactory(is_staff=True, roles=["tickets.accountable"])
        cls.ticket = TicketFactory(accountable=cls.staff)
        cls.url = reverse("ticket-assign", kwargs={"pk": cls.ticket.pk})

    def test_unauthenticated(self):
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_admin_host(self):
        self.client.force_authenticate(self.staff)
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_accountable(self):
        self.staff.roles = []
        self.staff.save()
        self.client.force_authenticate(self.staff)
        response = self.client.patch(self.url, headers={"host": "api.admin.testserver"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_accountable_is_required(self):
        self.client.force_authenticate(self.staff)
        response = self.client.patch(self.url, headers={"host": "api.admin.testserver"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("utils.kafka.KafkaEventStore.add_event")
    def test_assign_to_other_staff(self, add_event):
        self.client.force_authenticate(self.staff)
        data = {
            "accountable": self.other_staff.pk,
        }
        response = self.client.patch(
            self.url, data, headers={"host": "api.admin.testserver"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        add_event.assert_called()

    def test_assign_to_existing_accountable(self):
        self.client.force_authenticate(self.staff)
        data = {
            "accountable": self.staff.pk,
        }
        response = self.client.patch(
            self.url, data, headers={"host": "api.admin.testserver"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_to_non_accountable_user(self):
        self.other_staff.roles = []
        self.other_staff.save()
        self.client.force_authenticate(self.staff)
        data = {
            "accountable": self.other_staff.pk,
        }
        response = self.client.patch(
            self.url, data, headers={"host": "api.admin.testserver"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_to_inactive_user(self):
        self.other_staff.is_active = False
        self.other_staff.save()
        self.client.force_authenticate(self.staff)
        data = {
            "accountable": self.other_staff.pk,
        }
        response = self.client.patch(
            self.url, data, headers={"host": "api.admin.testserver"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_to_non_staff_user(self):
        self.other_staff.is_staff = False
        self.other_staff.save()
        self.client.force_authenticate(self.staff)
        data = {
            "accountable": self.other_staff.pk,
        }
        response = self.client.patch(
            self.url, data, headers={"host": "api.admin.testserver"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
