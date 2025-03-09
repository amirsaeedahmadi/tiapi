from django.conf import settings
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin
from tickets.models import Ticket
from io import BytesIO
import requests
import json


class JiraIssueProject:
    def __init__(self, id:str=None, key:str=None):
        self.id = id
        self.key = key

    @property
    def data(self):
        keys = ["id", "key", ]
        data = {key: getattr(self, key) for key in keys if hasattr(self, key)}
        data = dict(filter(lambda item: item[1] is not None, data.items()))
        return data


class JiraIssueType:
    def __init__(self, id:str=None, name:str=None):
        self.id = id
        self.name = name

    @property
    def data(self):
        keys = ["id", "name", ]
        data = {key: getattr(self, key) for key in keys if hasattr(self, key)}
        data = dict(filter(lambda item: item[1] is not None, data.items()))
        return data

class JiraIssuePriority:
    def __init__(self, id:str=None, name:str=None):
        self.id = id
        self.name = name

    @property
    def data(self):
        keys = ["id", "name", ]
        data = {key: getattr(self, key) for key in keys if hasattr(self, key)}
        data = dict(filter(lambda item: item[1] is not None, data.items()))
        return data


class JiraIssueStatus:
    def __init__(self, id:str=None, name:str=None, description:str=None):
        self.id = id
        self.name = name
        self.description = description

    @property
    def data(self):
        keys = ["id", "name", "description"]
        data = {key: getattr(self, key) for key in keys if hasattr(self, key)}
        data = dict(filter(lambda item: item[1] is not None, data.items()))
        return data


class JiraIssueResolution:
    def __init__(self, id:str=None, name:str=None, description:str=None):
        self.id = id
        self.name = name
        self.description = description

    @property
    def data(self):
        keys = ["id", "name", "description"]
        data = {key: getattr(self, key) for key in keys if hasattr(self, key)}
        data = dict(filter(lambda item: item[1] is not None, data.items()))
        return data


class JiraIssueStatusCategory:
    def __init__(self, id:str=None, name:str=None, key:str=None):
        self.id = id
        self.name = name
        self.key = key

    @property
    def data(self):
        keys = ["id", "name", "key"]
        data = {key: getattr(self, key) for key in keys if hasattr(self, key)}
        data = dict(filter(lambda item: item[1] is not None, data.items()))
        return data



BASE_JIRA_ISSUE_RESOLUTIONS = [
    JiraIssueResolution(id="10100", name="حل شده"),
    JiraIssueResolution(id="10101", name="غیرقابل حل / نامعتبر"),
    JiraIssueResolution(id="10102", name="تکراری"),
    JiraIssueResolution(id="10103", name="Done"),
    JiraIssueResolution(id="10104", name="Won't Do"),
    JiraIssueResolution(id="10105", name="Duplicate"),
    JiraIssueResolution(id="10106", name="Cannot Reproduce"),
]
BASE_JIRA_ISSUE_STATUSES = [
    JiraIssueStatus(id="10100", name="باز"),
    JiraIssueStatus(id="10101", name="در حال انجام"),
    JiraIssueStatus(id="10103", name="حل شده"),
]



class JiraIssue:
    def __init__(
        self, id:str=None,
        key:str=None,
        summary:str=None,
        assignee:str=None,
        issue_type:str=None,
        description:str=None,
        priority:str=None):

        self.id = id
        self.key = key
        self.summary = summary
        self.assignee = assignee
        self.issue_type = issue_type
        self.description = description
        self.priority = priority

    @property
    def data(self):
        keys = ["id", "key", "summary", "assignee", "issue_type", "description"]
        data = {key: getattr(self, key) for key in keys if hasattr(self, key)}
        data = dict(filter(lambda item: item[1] is not None, data.items()))
        return data


class JiraService:

    def __init__(self, event_store, auth=None, project_key="TPP"):
        self.event_store = event_store
        self.auth = auth or HTTPBasicAuth(
                                username=settings.JIRA_ADMIN_USERNAME,
                                password=settings.JIRA_ADMIN_PASSWORD
                            )
        self.base_project = JiraIssueProject(key=project_key) if project_key else None
        self.priority_choices = {
            Ticket.URGENT: JiraIssuePriority(name="Highest"),
            Ticket.HIGH: JiraIssuePriority(name="High"),
            Ticket.MODERATE: JiraIssuePriority(name="Medium"),
            Ticket.LOW: JiraIssuePriority(name="Low"),
            Ticket.LOWEST: JiraIssuePriority(name="Lowest"),
        }
        self.base_issue_type = "Task"
        self.issue_type_name_choices = [
            "Task",
            "Epic",
            "Story",
            "Bug",
            "ثبت رخداد",
            "اعمال تغییر",
            "تسک جدید",
            "سرویس جدید"
        ]

    def create_jira_issue(
        self,
        project: JiraIssueProject,
        description: str,
        issue_type: JiraIssueType,
        summary:str = None,
        customer_id:str=None,
        panel_id:str=None,
        priority:JiraIssuePriority=JiraIssuePriority(name="Lowest")):

        jira_create_issue_url = f"{settings.JIRA_BASE_URL}/rest/api/2/issue"
        headers = {"Content-Type": "application/json"}
        data = {
            "fields": {
                "project": project.data,
                "summary": summary,
                "description": description,
                "issuetype": issue_type.data,
                "priority": priority.data,
                "customfield_10200": customer_id,
                "customfield_10201": panel_id,
            }
        }
        issue_creation_response =requests.post(
            url=jira_create_issue_url,
            data=json.dumps(data),
            auth=self.auth,
            headers=headers,
            timeout=30,
            verify=False
        )
        issue_creation_response.raise_for_status()
        return issue_creation_response.json()

    def add_attachment(self, issue_key, file: BytesIO, file_name: str):
        jira_add_attachment_url = f"{settings.JIRA_BASE_URL}/rest/api/2/issue/{issue_key}/attachments"
        headers = {
            "X-Atlassian-Token": "nocheck"
        }
        files = {"file": (file_name, file)}
        add_attachment_response = requests.post(
            url=jira_add_attachment_url,
            files=files,
            headers=headers,
            auth=self.auth,
            timeout=50,
            verify=False
        )
        add_attachment_response.raise_for_status()
        return add_attachment_response.json()

    def on_crm_ticket_created(self, **data):
        user = data["user"]
        data.pop("crm_id", None)
        request_type = data.pop("request_type", None)
        issue_type_name = request_type if request_type in self.issue_type_name_choices else self.base_issue_type
        issue_type = JiraIssueType(name=issue_type_name)
        priority = self.priority_choices.get(data.get('priority'))
        jira_issue_data = {
            "project": self.base_project,
            "description": data['description'],
            "summary": data.get("subject"),
            "priority": priority,
            "issue_type": issue_type,
            "panel_id": data['id'],
            "customer_id": user,
        }
        jira_issue_data = dict(filter(lambda item: item[1] is not None, jira_issue_data.items()))
        created_ticket_data = self.create_jira_issue(**jira_issue_data)
        if attachment_download_link := data.pop("attachment_download_link", None):
            attachment_download_link = urljoin(
                settings.CRM_API_BASE_URL,
                attachment_download_link
            )
            response = requests.get(url=attachment_download_link)
            response.raise_for_status()
            file_name = response.headers['filename']
            self.add_attachment(
                issue_key=created_ticket_data['key'],
                file=BytesIO(response.content),
                file_name=file_name,
            )
            return created_ticket_data
        return created_ticket_data
