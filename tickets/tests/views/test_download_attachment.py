from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from tickets.tests.factories import AttachmentFactory
from tickets.tests.factories import TicketFactory
from users.factories import UserFactory


class DownloadAttachmentTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(email_verified=True, mobile_verified=True)
        cls.other_user = UserFactory(email_verified=True, mobile_verified=True)
        cls.staff = UserFactory(
            is_staff=True,
            roles=["tickets.accountable"],
        )
        cls.other_staff = UserFactory(
            is_staff=True,
            roles=["tickets.accountable"],
        )
        cls.superuser = UserFactory(is_staff=True, is_superuser=True)
        cls.attachment = AttachmentFactory(user=cls.user)
        TicketFactory(
            user=cls.user, accountable=cls.staff, attachments=[cls.attachment]
        )
        cls.url = reverse("attachment-download", kwargs={"pk": cls.attachment.pk})

    def test_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_superuser_on_admin_host(self):
        self.client.force_authenticate(self.superuser)
        response = self.client.get(self.url, headers={"host": "api.admin.testserver"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_accountable_on_admin_host(self):
        self.client.force_authenticate(self.staff)
        response = self.client.get(self.url, headers={"host": "api.admin.testserver"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_other_user(self):
        self.client.force_authenticate(self.other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_staff(self):
        self.client.force_authenticate(self.other_staff)
        response = self.client.get(self.url, headers={"host": "api.admin.testserver"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
