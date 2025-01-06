from unittest.mock import patch

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from tickets.tests.factories import TicketFactory
from users.factories import UserFactory
from utils.files import uploaded_image_file


class CreateFollowUpTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(email_verified=True, mobile_verified=True)
        cls.other_user = UserFactory(email_verified=True, mobile_verified=True)
        cls.staff = UserFactory(is_staff=True, roles=["tickets.accountable"])
        cls.other_staff = UserFactory(is_staff=True, roles=["tickets.accountable"])
        cls.superuser = UserFactory(is_superuser=True)
        cls.ticket = TicketFactory(user=cls.user)
        cls.url = reverse("ticket-followups", kwargs={"pk": cls.ticket.pk})

    def test_unauthenticated(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_email_unverified(self):
        self.user.email_verified = False
        self.user.save()
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_user(self):
        self.client.force_authenticate(self.other_user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("utils.kafka.KafkaEventStore.add_event")
    def test_other_staff_on_admin_host(self, add_event):
        self.client.force_authenticate(self.other_staff)
        data = {
            "description": "my descr",
        }
        response = self.client.post(
            self.url, data, headers={"host": "api.admin.testserver"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        add_event.assert_called()

    @patch("utils.kafka.KafkaEventStore.add_event")
    def test_superuser_on_admin_host(self, add_event):
        self.client.force_authenticate(self.superuser)
        data = {
            "description": "my descr",
        }
        response = self.client.post(
            self.url, data, headers={"host": "api.admin.testserver"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        add_event.assert_called()

    def test_description_is_required(self):
        self.client.force_authenticate(self.user)
        data = {
            "file1": uploaded_image_file(),
            "file2": uploaded_image_file(),
        }
        response = self.client.post(self.url, data=data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("utils.kafka.KafkaEventStore.add_event")
    def test_attachment_is_not_required(self, add_event):
        self.client.force_authenticate(self.user)
        data = {
            "description": "my descr",
        }
        response = self.client.post(self.url, data=data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        add_event.assert_called()
        data = response.json()
        self.assertEqual(len(data["attachments"]), 0)

    @patch("utils.kafka.KafkaEventStore.add_event")
    def test_successful(self, add_event):
        self.client.force_authenticate(self.user)
        data = {
            "description": "my descr",
            "file1": uploaded_image_file(),
            "file2": uploaded_image_file(),
        }
        response = self.client.post(self.url, data=data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        add_event.assert_called()
        data = response.json()
        self.assertEqual(len(data["attachments"]), 2)
