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
