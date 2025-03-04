import json
import logging
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings

logger = logging.getLogger(__name__)

class JiraClient:
    
    def __init__(self, base_url=None, username=None, password=None):
        """
        Initialize the Jira client.
        
        Args:
            base_url: The base URL for Jira API (defaults to settings.JIRA_URL)
            username: Jira username (defaults to settings.JIRA_USERNAME)
            password: Jira password (defaults to settings.JIRA_PASSWORD)
        """
        self.base_url = base_url or settings.JIRA_URL
        self.username = username or settings.JIRA_USERNAME
        self.password = password or settings.JIRA_PASSWORD
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def create_issue(self, project_key, summary, description, issue_type_id):
        """
        Create a new issue in Jira.
        
        Args:
            project_key: The project key (e.g., 'DRVG')
            summary: Issue summary/title
            description: Detailed description of the issue
            issue_type_id: ID of the issue type (e.g., '10100')
            
        Returns:
            dict: Response data from Jira or None if request failed
        """
        data = {
            "fields": {
                "project": {
                    "key": project_key
                },
                "summary": summary,
                "description": description,
                "issuetype": {
                    "id": issue_type_id
                }
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/issue/",
                auth=HTTPBasicAuth(self.username, self.password),
                headers=self.headers,
                data=json.dumps(data),
                verify=settings.JIRA_VERIFY_SSL
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating Jira issue: {str(e)}")
            return None


def create_jira_issue(project_key, summary, description, issue_type_id):
    """
    Utility function to create a Jira issue.
    
    Args:
        project_key: The project key (e.g., 'DRVG')
        summary: Issue summary/title
        description: Detailed description of the issue
        issue_type_id: ID of the issue type (e.g., '10100')
        
    Returns:
        dict: Response data from Jira or None if request failed
    """
    client = JiraClient()
    return client.create_issue(project_key, summary, description, issue_type_id)