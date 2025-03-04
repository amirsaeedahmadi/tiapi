from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from tickets.tests.factories import TicketFactory
from users.factories import UserFactory


class ListAssignablesTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = UserFactory(is_staff=True, roles=["tickets.accountable"])
        UserFactory(email="use12@gmail.com", is_staff=True)
        UserFactory(
            email="use123@gmail.com",
            is_staff=True,
            is_active=False,
            roles=["tickets.accountable"],
        )
        UserFactory(
            email="use1234@gmail.com",
            is_staff=True,
            roles=["tickets.accountable"],
        )
        UserFactory(
            email="use12345@gmail.com",
            is_staff=True,
            roles=["tickets.accountable"],
        )
        cls.ticket = TicketFactory(accountable=cls.staff)
        cls.url = reverse("ticket-assignables", kwargs={"pk": cls.ticket.pk})

    def test_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_admin_host(self):
        self.client.force_authenticate(self.staff)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_accountable(self):
        self.staff.roles = []
        self.staff.save()
        self.client.force_authenticate(self.staff)
        response = self.client.get(self.url, headers={"host": "api.admin.testserver"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_email_url_param_is_required(self):
        self.client.force_authenticate(self.staff)
        response = self.client.get(self.url, headers={"host": "api.admin.testserver"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search(self):
        self.client.force_authenticate(self.staff)
        response = self.client.get(
            self.url,
            {"assignable": "use"},
            headers={"host": "api.admin.testserver"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("results", data)
        results = data["results"]
        self.assertEqual(len(results), 2)
        result = results[0]
        self.assertIn("email", result)
        self.assertIn("first_name", result)
        self.assertIn("last_name", result)
