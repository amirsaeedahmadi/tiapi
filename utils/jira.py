import uuid
import logging

from io import BytesIO
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.http import HttpResponse
from requests.auth import HTTPBasicAuth

from tickets.events import JiraTicketCommentCreated
from tickets.models import Ticket
from tickets.serializers import JiraIssueCommentSerializer
from tickets.serializers import JiraIssueTypeSerializer


logger = logging.getLogger(__name__)

class IssueTypes:
    TASK = "Task"
    EPIC = "Epic"
    STORY = "Story"
    BUG = "Bug"
    INCIDENT = "ثبت رخداد"
    CHANGE = "اعمال تغییر"
    ITSM_TASK = "تسک جدید"
    NEW_SERVICE = "سرویس جدید"

class Categories:
    TECHNICAL = "فنی"
    SALES = "فروش"

class JiraService:
    customer_id_field = "customfield_10200"
    category_field = "customfield_10203"
    panel_customer_name_field = "customfield_10300"
    panel_customer_email_field = "customfield_10302"

    

    ISSUE_TYPE_MAPPING = {
        Ticket.TECHNICAL: IssueTypes.INCIDENT,
        Ticket.SALE: IssueTypes.NEW_SERVICE,
    }

    CATEGORY_MAPPING = {
        Ticket.TECHNICAL: Categories.TECHNICAL,
        Ticket.SALE: Categories.SALES,
    }


    def __init__(
        self, base_url=None, username=None, password=None, default_project_key=None
    ):
        self.auth = HTTPBasicAuth(username=username, password=password)
        self.bare_base_url = base_url
        self.base_url = urljoin(base_url, "/rest/api/2/")
        self.default_project_key = default_project_key


    def request(self, method, path, headers=None, **kwargs):
        headers = headers or {}

        if "files" not in kwargs:
            headers.setdefault("Content-Type", "application/json")

        url = urljoin(self.base_url, path)
        return requests.request(
            method,
            url,
            headers=headers,
            timeout=5,
            verify=False,
            auth=self.auth,
            **kwargs,
        )


    def create_issue(
        self,
        customer_id,
        summary,
        description,
        issue_type,
        project_key,
        user_full_name, 
        user_email,
        category_field,
    ):
        data = {
            "fields": {
                "project": {"key": project_key or self.default_project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": issue_type},
                self.panel_customer_name_field: user_full_name,
                self.panel_customer_email_field: user_email,
                self.customer_id_field: customer_id,
                self.category_field: category_field,
            }
        }
        response = self.request("POST", "issue", json=data)
        response.raise_for_status()
        return response.json()
    
    def add_attachment(self, ticket_id, django_uploaded_file):
        path = f"/rest/api/2/issue/{ticket_id}/attachments"
        headers = {
            "X-Atlassian-Token": "no-check"
        }

        files = {
            "file": (django_uploaded_file.name, django_uploaded_file)
        }
        
        response = self.request(
            method="POST",
            path=path,
            headers=headers,
            files=files,
        )
        response.raise_for_status()
        return response.json()
    
    def fetch_tickets(self, customer_id=None, page=None, page_size=None, ticket_id=None, ordering="created DESC", project=None):
        page = page or 1
        page_size = page_size or 10
        payload = {
            "startAt": (page - 1) * page_size,
            "maxResults": page_size,
        }

        jql_parts = []
        if customer_id:
            jql_parts.append(f"customer_id ~ {customer_id}")
        if ticket_id:
            jql_parts.append(f"id = {ticket_id}")
        
        jql_parts.append(f'project = "{"TPP"}"')

        jql_query = " AND ".join(jql_parts) if jql_parts else ""
        if ordering:
            jql_query += f" ORDER BY {ordering}"

        if jql_query:
            payload["jql"] = jql_query

        response = self.request("POST", "search", json=payload)
        response.raise_for_status()
        return response.json()


    def fetch_ticket_detail(
        self,
        ticket_id,
        fields=(),
    ):
        path = f"/rest/api/2/issue/{ticket_id}"
        if fields:
            path += f"?fields={','.join(fields)}"

        response = self.request(
            method="GET",
            path=path,
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
    
    def fetch_ticket_comments(self, ticket_id, page=None, page_size=None):
        page = int(page or 1)
        page_size = int(page_size or 10)
        start_at = (page - 1) * page_size

        path = f"/rest/api/2/issue/{ticket_id}/comment"
        params = {
            "startAt": start_at,
            "maxResults": page_size
        }

        try:
            response = self.request(
                method="GET",
                path=path,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            # logger.error(f"Failed to fetch comments for ticket {ticket_id}: {e}")
            raise

    def create_comment(self, ticket_id, comment_text):
        path = f"/rest/api/2/issue/{ticket_id}/comment"
        payload = {
            "body": comment_text
        }
        try:
            response = self.request("POST", path, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            logger.error(f"Failed to add comment to ticket {ticket_id}: {e}")
            raise



    def add_comment_created(self, **data):
        comment_serializer = JiraIssueCommentSerializer(data=data)
        comment_serializer.is_valid(raise_exception=True)
        followup_data = comment_serializer.to_panel_followup(
            ticket_id=data["ticket_id"]
        )
        followup_data["id"] = uuid.uuid4()
        event = JiraTicketCommentCreated(followup_data)
        # self.event_store.add_event(event)
        return followup_data
    
    def download_attachment(
        self,
        attachment_id,
        filename
    ):
        path = f"/secure/attachment/{attachment_id}/{filename}"
        url = urljoin(self.bare_base_url, path)
        response = requests.request(
            "GET",
            url,
            timeout=5,
            verify=False,
            auth=self.auth,
        )

        django_response = HttpResponse(
            content=response.content,
            status=response.status_code,
            headers = {
                'Content-Disposition': response.headers["Content-Disposition"]
            }
        )


        
        return django_response


jira_service = JiraService(**settings.JIRA_SETTINGS)
