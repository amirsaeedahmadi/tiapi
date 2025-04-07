from rest_framework import serializers
from users.models import User


class JiraIssueProjectSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    key = serializers.CharField(required=False)


class JiraIssueTypeSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    name = serializers.ChoiceField(
        required=False,
        choices=[
            "Task",
            "Epic",
            "Story",
            "Bug",
            "ثبت رخداد",
            "اعمال تغییر",
            "تسک جدید",
            "سرویس جدید",
        ],
    )


class JiraIssuePrioritySerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    name = serializers.ChoiceField(
        required=False, choices=["Highest", "High", "Medium", "Low", "Lowest"]
    )

    PANEL_PRIORITY_MAPPER = {
        "Highest": 1,
        "High": 2,
        "Medium": 3,
        "Low": 4,
        "Lowest": 5,
    }


class JiraIssueStatusSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    name = serializers.ChoiceField(
        required=False, choices=["باز", "در حال انجام", "حل شده", "بسته"]
    )
    description = serializers.CharField(required=False)

    PANEL_STATUS_MAPPER = {"باز": 0, "در حال انجام": 2, "حل شده": 1}


class JiraIssueResolutionSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)


class JiraIssueStatusCategorySerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    key = serializers.CharField(required=False)


class JiraIssueCreatorSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    key = serializers.CharField(required=False)
    emailAddress = serializers.CharField(required=False)
    displayName = serializers.CharField(required=False)


class JiraIssueAssigneeSerializer(JiraIssueCreatorSerializer):
    pass


class JiraIssueAttachmentSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    author = JiraIssueCreatorSerializer()
    size = serializers.IntegerField(required=False)
    file_name = serializers.CharField(required=False)
    content = serializers.CharField(required=False)


class JiraIssueCommentSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    body = serializers.CharField()
    author = JiraIssueCreatorSerializer()
    created = serializers.DateTimeField(required=False)
    updated = serializers.DateTimeField(required=False)

    def to_panel_followup(self, ticket_id):
        self.is_valid(raise_exception=True)
        user_email = self.validated_data["author"]["emailAddress"]
        user_id = User.objects.get(email=user_email).id
        return {
            "ticket": ticket_id,
            "user": user_id,
            "description": self.validated_data["body"],
            "attachments": [],
        }


class JiraIssueSerializer(serializers.Serializer):
    panel_id_field = "customfield_10201"
    customer_id_field = "customfield_10200"

    id = serializers.CharField(required=False)
    key = serializers.CharField(required=False)
    summary = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    project = JiraIssueProjectSerializer()
    creator = JiraIssueCreatorSerializer()
    assignee = JiraIssueAssigneeSerializer()
    status = JiraIssueStatusSerializer()
    issuetype = JiraIssueTypeSerializer()
    priority = JiraIssuePrioritySerializer()
    resolution = JiraIssueResolutionSerializer(allow_null=True, required=False)
    customfield_10200 = serializers.CharField(
        required=False, allow_null=True, source="customer_id"
    )
    customfield_10201 = serializers.CharField(
        required=False, allow_null=True, source="panel_id"
    )
    attachment = serializers.ListSerializer(
        required=False, child=JiraIssueAttachmentSerializer()
    )
    comments = serializers.ListSerializer(
        required=False, child=JiraIssueCommentSerializer()
    )

    def to_panel_ticket(self):
        self.is_valid(raise_exception=True)
        validated_data = self.validated_data
        panel_ticket_format = {
            "description": validated_data["description"],
            "user": validated_data["customer_id"],
            "id": validated_data["panel_id"],
            "subject": validated_data["summary"],
            "status": JiraIssueStatusSerializer.PANEL_STATUS_MAPPER.get(
                validated_data["status"]["name"]
            ),
            "priority": JiraIssuePrioritySerializer.PANEL_PRIORITY_MAPPER.get(
                validated_data["priority"]["name"]
            ),
        }
        return panel_ticket_format


BASE_JIRA_ISSUE_RESOLUTIONS = [
    JiraIssueResolutionSerializer(instance={"id": "10100", "name": "حل شده"}),
    JiraIssueResolutionSerializer(
        instance={"id": "10101", "name": "غیرقابل حل / نامعتبر"}
    ),
    JiraIssueResolutionSerializer(instance={"id": "10102", "name": "تکراری"}),
    JiraIssueResolutionSerializer(instance={"id": "10103", "name": "Done"}),
    JiraIssueResolutionSerializer(instance={"id": "10104", "name": "Won't Do"}),
    JiraIssueResolutionSerializer(instance={"id": "10105", "name": "Duplicate"}),
    JiraIssueResolutionSerializer(instance={"id": "10106", "name": "Cannot Reproduce"}),
]
BASE_JIRA_ISSUE_STATUSES = [
    JiraIssueStatusSerializer(instance={"id": "10100", "name": "باز"}),
    JiraIssueStatusSerializer(instance={"id": "10101", "name": "در حال انجام"}),
    JiraIssueStatusSerializer(instance={"id": "10103", "name": "حل شده"}),
]
