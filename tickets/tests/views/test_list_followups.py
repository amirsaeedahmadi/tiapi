from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from tickets.tests.factories import FollowUpFactory
from tickets.tests.factories import TicketFactory
from users.factories import UserFactory


class ListFollowUpsTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(email_verified=True, mobile_verified=True)
        cls.other_user = UserFactory(email_verified=True, mobile_verified=True)
        cls.staff = UserFactory(is_staff=True, roles=["tickets.accountable"])
        cls.other_staff = UserFactory(is_staff=True, roles=["tickets.accountable"])
        cls.superuser = UserFactory(is_superuser=True)
        cls.ticket = TicketFactory(user=cls.user, accountable=cls.staff)
        cls.url = reverse("ticket-followups", kwargs={"pk": cls.ticket.pk})
        FollowUpFactory.create_batch(6, ticket=cls.ticket)

    def test_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_other_user(self):
        self.client.force_authenticate(self.other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_staff_on_admin_host(self):
        self.client.force_authenticate(self.other_staff)
        response = self.client.get(self.url, headers={"host": "api.admin.testserver"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_accountable_on_admin_host(self):
        self.client.force_authenticate(self.staff)
        response = self.client.get(self.url, headers={"host": "api.admin.testserver"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("results", data)
        results = data["results"]
        self.assertEqual(len(results), 6)

    def test_superuser_on_admin_host(self):
        self.client.force_authenticate(self.superuser)
        response = self.client.get(self.url, headers={"host": "api.admin.testserver"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("results", data)
        results = data["results"]
        self.assertEqual(len(results), 6)

    def test_user(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("results", data)
        results = data["results"]
        self.assertEqual(len(results), 6)
