from pathlib import Path

import magic
from django.contrib.auth import get_user_model
from django.http.response import HttpResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

# from jira.services import jira_service
from users.permissions import IsAdminHost
from users.serializers import SearchAdminUserSerializer
from utils.tokens import generate_integer_code

from .models import Attachment
from .models import Ticket
from .permissions import HasAccountableRole
from .permissions import HasAccountableRoleOrEmailAndMobileVerified
from .serializers import AccountableSerializer
from .serializers import AttachmentSerializer
from .serializers import FollowUpSerializer
from .serializers import TicketSerializer
from .services import ticket_service
from .services import jira_service

User = get_user_model()


class TicketViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    filterset_fields = ("status", "accountable", "user", "cat", "priority")
    search_fields = ("ref_code", "user__email", "user__first_name", "user__last_name")

    def get_permission_classes(self):
        if self.action in ["assignables", "assign"]:
            return [IsAdminHost, HasAccountableRole]

        return [HasAccountableRoleOrEmailAndMobileVerified]

    def get_permissions(self):
        return [permission() for permission in self.get_permission_classes()]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.is_admin_host:
            return qs.filter(user=self.request.user)
        return qs

    def list(self, request, *args, **kwargs):
        cat = request.query_params.get("cat")
        if not cat:
            raise ValidationError({"detail": _("Cat is required")})
        if cat == Ticket.TECHNICAL:
            # TODO: check this 
            queryset = jira_service.list_tickets(user_id=request.user.pk)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        cat = request.query_params.get("cat")
        if not cat:
            raise ValidationError({"detail": _("Cat is required")})
        if cat == Ticket.TECHNICAL:
            pass
            # TODO: fetch single ticket from jira
        else:
            super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serialized_attachments = []
        attachment_ids = []
        for value in request.FILES.values():
            data = {"file": value}
            serializer = AttachmentSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save(user=request.user)
            attachment_ids.append(instance.pk)
            serializer = AttachmentSerializer(instance, context={"request": request})
            serialized_attachments.append(serializer.data)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=request.user,
            attachment_ids=attachment_ids,
            ref_code=generate_integer_code(length=8),
        )
        data = serializer.data.copy()
        data["attachments"] = serialized_attachments
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


    @action(methods=["GET"], detail=True, serializer_class=SearchAdminUserSerializer)
    def assignables(self, request, pk=None):
        instance = self.get_object()
        exclude_kwargs = {"pk": instance.accountable.pk} if instance.accountable else {}
        search = request.GET.get("assignable")
        if not search:
            raise ValidationError({"assignable": _("This url param is required.")})
        queryset = User.objects.get_assignable_admins(
            filter_kwargs={"email__contains": search}, exclude_kwargs=exclude_kwargs
        ).order_by("email")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        methods=["PATCH"],
        detail=True,
        serializer_class=AccountableSerializer,
    )
    def assign(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = ticket_service.assign(
            instance, serializer.validated_data["accountable"]
        )
        serializer = TicketSerializer(instance)
        return Response(serializer.data)

    @action(methods=["GET"], detail=True, serializer_class=FollowUpSerializer)
    def followups(self, request, pk=None):
        cat = request.query_params.get("cat")
        if not cat:
            raise ValidationError({"detail": _("Cat is required")})
        if cat == Ticket.TECHNICAL:
            pass
            # TODO: fetch comments from jira
        else:
            instance = self.get_object()
            queryset = instance.followups.all()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

    @followups.mapping.post
    def followup(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status == Ticket.CLOSED:
            raise exceptions.ValidationError({"detail": _("Ticket closed.")})

        serialized_attachments = []
        attachment_ids = []
        for value in request.FILES.values():
            data = {"file": value}
            serializer = AttachmentSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save(user=request.user)
            attachment_ids.append(instance.pk)
            serializer = AttachmentSerializer(instance, context={"request": request})
            serialized_attachments.append(serializer.data)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ticket=ticket, user=request.user, attachment_ids=attachment_ids)
        data = serializer.data.copy()
        data["attachments"] = serialized_attachments
        return Response(data, status=status.HTTP_201_CREATED)

    @action(methods=["PATCH"], detail=True)
    def close(self, request, pk=None):
        instance = self.get_object()
        if instance.status == Ticket.CLOSED:
            raise exceptions.ValidationError({"detail": _("Ticket closed.")})
        instance = ticket_service.close(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class DownloadAttachmentView(APIView):
    permission_classes = (HasAccountableRoleOrEmailAndMobileVerified,)

    def get(self, request, pk=None):
        obj = Attachment.objects.filter(pk=pk).first()
        if obj:
            if request.is_admin_host:
                if not request.user.has_perm("tickets.accountable"):
                    msg = _("No file was found for this admin")
                    raise exceptions.NotFound(msg)
            else:
                instance = obj.ticket_set.first()
                if not instance:
                    instance = obj.followup_set.first()
                    if not instance:
                        msg = _("No ticket or followup was found for this file")
                        raise exceptions.NotFound(msg)

                if isinstance(instance, Ticket):
                    if not (
                        request.user.is_superuser
                        or request.user == instance.user
                        or request.user.has_perm("tickets.accountable")
                    ):
                        msg = _("No file was found for this user")
                        raise exceptions.NotFound(msg)
                elif not (
                    request.user.is_superuser
                    or request.user == instance.user
                    or request.user.has_perm("tickets.accountable")
                    or request.user == instance.ticket.user
                ):
                    msg = _("No file was found for this user")
                    raise exceptions.NotFound(msg)
            try:
                with Path(obj.file.path).open("rb") as file:
                    content_type = magic.from_buffer(file.read(2048), mime=True)
                    response = HttpResponse(file, content_type=content_type)
                    response["Content-Disposition"] = (
                        f'attachment; filename="{obj.file.name.split("/")[-1]}"'
                    )
                    return response
            except FileNotFoundError as e:
                msg = _("File not found. It may have been deleted")
                raise exceptions.NotFound(msg) from e

        msg = _("Attachment not found.")
        raise exceptions.NotFound(msg)
