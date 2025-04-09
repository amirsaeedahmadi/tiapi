import magic
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.reverse import reverse

from users.serializers import UserSerializer

from .models import Attachment
from .models import FollowUp
from .models import Ticket

User = get_user_model()

ALLOWED_MIMETYPES = [
    "image/jpeg",
    "image/png",
    "image/gif",
    "application/pdf",
    "text/plain",
    "application/msword",
    "image/bmp",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]


class ReadOnlyTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"


class AttachmentSerializer(serializers.ModelSerializer):
    filename = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        exclude = ("user", "created_at", "updated_at")
        extra_kwargs = {"file": {"write_only": True}}

    def get_filename(self, obj):
        return obj.file.name.split("/")[-1]

    def get_download_url(self, obj):
        return reverse(
            "attachment-download",
            request=self.context.get("request"),
            kwargs={"pk": obj.pk},
        )

    def validate_file(self, value):
        if value.size > settings.MAX_ATTACHMENT_SIZE * 1024 * 1024:
            msg = _("Document file size must be less than {size} MB.")
            raise serializers.ValidationError(
                msg.format(size=settings.MAX_ATTACHMENT_SIZE)
            )
        mime_type = magic.from_buffer(value.read(2048), mime=True)
        if mime_type not in ALLOWED_MIMETYPES:
            msg = _("Documents must be either a picture or PDF.")
            raise serializers.ValidationError(msg)
        return value


class TicketSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)
    cat_display = serializers.SerializerMethodField()
    priority_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = "__all__"
        extra_kwargs = {"attachments": {"read_only": True}}

    def get_cat_display(self, obj):
        return Ticket.CAT_CHOICES[obj.cat]

    def get_priority_display(self, obj):
        return Ticket.PRIO_CHOICES[obj.priority]

    def get_status_display(self, obj):
        return Ticket.STATUS_CHOICES[obj.status]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["user"] = UserSerializer(instance.user).data
        if instance.accountable:
            ret["accountable"] = UserSerializer(instance.accountable).data
        return ret

    def create(self, validated_data):
        from .services import ticket_service

        return ticket_service.create(**validated_data)


class AccountableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("accountable",)
        extra_kwargs = {
            "accountable": {
                "required": True,
                "read_only": False,
                "queryset": User.objects.all(),
            }
        }


class ReadOnlyFollowUpSerializer(serializers.ModelSerializer):
    ticket = ReadOnlyTicketSerializer(read_only=True)

    class Meta:
        model = FollowUp
        fields = "__all__"


class FollowUpSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = FollowUp
        fields = "__all__"

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["user"] = UserSerializer(instance.user).data
        return ret

    def create(self, validated_data):
        from .services import ticket_service

        return ticket_service.add_followup(**validated_data)
    
    
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

