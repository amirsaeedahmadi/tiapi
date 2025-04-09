from django.conf import settings

from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin
from io import BytesIO
import requests
import json
import uuid
from tickets.models import Ticket

from jira.serializers.ticket_serializer import (
    JiraIssueSerializer,
    JiraIssueTypeSerializer,
    JiraIssueCommentSerializer,
    JiraIssueProjectSerializer,
    JiraIssuePrioritySerializer,
)
from jira.events import JiraTicketCommentCreated


class JiraService:
    def __init__(self, event_store, auth=None, project_key="TPP"):
        self.event_store = event_store
        self.auth = auth or HTTPBasicAuth(
            username=settings.JIRA_ADMIN_USERNAME, password=settings.JIRA_ADMIN_PASSWORD
        )
        self.base_project = (
            JiraIssueProjectSerializer(instance={"key": project_key})
            if project_key
            else None
        )
        self.priority_choices = {
            1: JiraIssuePrioritySerializer(instance={"name": "Highest"}),
            2: JiraIssuePrioritySerializer(instance={"name": "High"}),
            3: JiraIssuePrioritySerializer(instance={"name": "Medium"}),
            4: JiraIssuePrioritySerializer(instance={"name": "Low"}),
            5: JiraIssuePrioritySerializer(instance={"name": "Lowest"}),
        }
        self.base_issue_type = JiraIssueTypeSerializer(instance={"name": "Task"})
        self.issue_type_name_choices = [
            "Task",
            "Epic",
            "Story",
            "Bug",
            "ثبت رخداد",
            "اعمال تغییر",
            "تسک جدید",
            "سرویس جدید",
        ]

    def create_jira_issue(
        self,
        project: JiraIssueProjectSerializer,
        description: str,
        issue_type: JiraIssueTypeSerializer,
        summary: str = None,
        customer_id: str = None,
        panel_id: str = None,
        priority=JiraIssuePrioritySerializer(data={"name": "Lowest"}),
    ):
        jira_create_issue_url = f"{settings.JIRA_BASE_URL}/rest/api/2/issue"
        headers = {"Content-Type": "application/json"}
        data = {
            "fields": {
                "project": project.data,
                "summary": summary,
                "description": description,
                "issuetype": issue_type.data,
                "priority": priority.data,
                JiraIssueSerializer.panel_id_field: panel_id,
                JiraIssueSerializer.customer_id_field: customer_id,
            }
        }
        issue_creation_response = requests.post(
            url=jira_create_issue_url,
            data=json.dumps(data),
            auth=self.auth,
            headers=headers,
            timeout=30,
            verify=False,
        )
        issue_creation_response.raise_for_status()
        return issue_creation_response.json()

    def add_attachment(self, issue_key, file: BytesIO, file_name: str):
        jira_add_attachment_url = (
            f"{settings.JIRA_BASE_URL}/rest/api/2/issue/{issue_key}/attachments"
        )
        headers = {"X-Atlassian-Token": "nocheck"}
        files = {"file": (file_name, file)}
        add_attachment_response = requests.post(
            url=jira_add_attachment_url,
            files=files,
            headers=headers,
            auth=self.auth,
            timeout=50,
            verify=False,
        )
        add_attachment_response.raise_for_status()
        return add_attachment_response.json()

    def list_tickets(self, user_id):
        jira_search_url = (f"{settings.JIRA_BASE_URL}/rest/api/2/search/?customer_id="
                           f"{user_id}")
        response = requests.get(
            jira_search_url, auth=self.auth, timeout=15, verify=False
        )
        response.raise_for_status()
        data = response.json()
        tickets = []
        for item in data:
            ticket = Ticket(id=item["id"])
            tickets.append(ticket)
        return tickets


    def fetch_tickets(self, jql_filters=""):
        jira_search_url = f"{settings.JIRA_BASE_URL}/rest/api/2/search/?{jql_filters}"
        response = requests.get(
            jira_search_url, auth=self.auth, timeout=15, verify=False
        )
        response.raise_for_status()
        return response.json()

    def fetch_ticket_detail(
        self,
        issue_id_or_key,
        fields=(),
    ):
        jira_detail_search_url = (
            f"{settings.JIRA_BASE_URL}/rest/api/2/issue/{issue_id_or_key}"
        )
        if fields:
            jira_detail_search_url += f"?fields={','.join(fields)}"
        response = requests.get(
            jira_detail_search_url, auth=self.auth, timeout=15, verify=False
        )
        response.raise_for_status()
        return response.json()

    def fetch_user_tickets(self, user_id):
        return self.fetch_tickets(jql_filters=f'jql=customer_id ~ "{user_id}"')

    def on_crm_ticket_created(self, **data):
        user = data["user"]
        data.pop("crm_id", None)
        request_type = data.pop("request_type", None)
        issue_type = JiraIssueTypeSerializer(data={"name": request_type})
        if not issue_type.is_valid():
            issue_type = self.base_issue_type
        priority = self.priority_choices.get(data.get("priority"))
        jira_issue_data = {
            "project": self.base_project,
            "description": data["description"],
            "summary": data.get("subject"),
            "priority": priority,
            "issue_type": issue_type,
            "panel_id": data["id"],
            "customer_id": user,
        }
        jira_issue_data = dict(
            filter(lambda item: item[1] is not None, jira_issue_data.items())
        )
        created_ticket_data = self.create_jira_issue(**jira_issue_data)
        if attachment_download_link := data.pop("attachment_download_link", None):
            attachment_download_link = urljoin(
                settings.CRM_API_BASE_URL, attachment_download_link
            )
            response = requests.get(url=attachment_download_link)
            response.raise_for_status()
            file_name = response.headers["filename"]
            self.add_attachment(
                issue_key=created_ticket_data["key"],
                file=BytesIO(response.content),
                file_name=file_name,
            )
            return created_ticket_data
        return created_ticket_data

    def add_comment_created(self, **data):
        comment_serializer = JiraIssueCommentSerializer(data=data)
        comment_serializer.is_valid(raise_exception=True)
        followup_data = comment_serializer.to_panel_followup(
            ticket_id=data["ticket_id"]
        )
        followup_data["id"] = uuid.uuid4()
        event = JiraTicketCommentCreated(followup_data)
        self.event_store.add_event(event)
        return followup_data
