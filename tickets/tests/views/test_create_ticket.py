from unittest.mock import patch

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from users.factories import UserFactory
from utils.files import uploaded_image_file


class CreateTicketTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse("ticket-list")

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(is_staff=False)
        cls.staff = UserFactory(
            email="admin@admin.com",
            is_staff=True,
            roles=["tickets.accountable"],
        )

    def test_unauthenticated(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("utils.kafka.KafkaEventStore.add_event")
    def test_successful(self, add_event):
        self.client.force_authenticate(self.user)
        data = {
            "priority": 1,
            "cat": 1,
            "subject": "my_subject",
            "description": "my_description",
            "file1": uploaded_image_file(),
            "file2": uploaded_image_file(),
        }
        response = self.client.post(self.url, data=data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        add_event.assert_called()
        data = response.json()
        self.assertIn("attachments", data)
        self.assertEqual(len(data["attachments"]), 2)
        self.assertIn("user", data)
        self.assertIn("email", data["user"])
        self.assertEqual(data["user"]["email"], self.user.email)
        self.assertIn("priority", data)
        self.assertEqual(data["priority"], 1)
        self.assertIn("cat", data)
        self.assertEqual(data["cat"], 1)
        self.assertIn("subject", data)
        self.assertEqual(data["subject"], "my_subject")

    @patch("utils.kafka.KafkaEventStore.add_event")
    def test_staff_on_admin_host(self, add_event):
        self.client.force_authenticate(self.staff)
        data = {
            "priority": 1,
            "cat": 1,
            "subject": "my_subject",
            "description": "my_description",
        }
        response = self.client.post(
            self.url, data=data, headers={"host": "api.admin.testserver"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        add_event.assert_called()
