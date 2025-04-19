import logging

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from requests import HTTPError
from rest_framework import exceptions
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdminHost
from utils.jira import jira_service

from .permissions import HasAccountableRole
from .serializers import TicketSerializer
from .serializers import CommentSerializer
from .serializers import AttachmentSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


class TicketViewSet(viewsets.GenericViewSet):
    serializer_class = TicketSerializer

    def get_permission_classes(self):
        if self.action in ["assignables", "assign"]:
            return [IsAdminHost, HasAccountableRole]

        return [IsAuthenticated]

    def get_permissions(self):
        return [permission() for permission in self.get_permission_classes()]

    def list(self, request, *args, **kwargs):
        page = int(request.query_params.get("page") or 1)
        page_size = int(request.query_params.get("page_size") or 10)
        search = request.query_params.get("search") or None
        ordering = request.query_params.get("ordering") or "created DESC"

        user_id = str(request.user.pk)
        if request.is_admin_host:
            user_id = None

        try:
            data = jira_service.fetch_tickets(
                customer_id=user_id,
                page=page,
                page_size=page_size,
                ticket_id=search,
                ordering=ordering
            )
        except HTTPError as e:
            raise ValidationError({"detail": e.response.json()})

        return Response(data)
    

    def retrieve(self, request, ticket_id=None, *args, **kwargs):
        user_key = request.user.pk
        try:
            data = jira_service.fetch_ticket_detail(ticket_id=ticket_id)
        except HTTPError as e:
            raise ValidationError({"detail": str(e)})
        
        is_user_validated = ((data["fields"]["customfield_10200"] == str(user_key) or request.is_admin_host))


        if data and is_user_validated:
            return Response(data)
        else:
            raise exceptions.NotFound({"detail": _("Ticket not found")})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer_id = str(request.user.pk)
        user = User.objects.get(pk=customer_id)

        user_full_name = user.full_name  
        user_email = user.email

        summary = serializer.validated_data["subject"]
        description = serializer.validated_data["description"]
        cat = serializer.validated_data["cat"]
        issue_type = jira_service.ISSUE_TYPE_MAPPING.get(cat)
        category_field = jira_service.CATEGORY_MAPPING.get(cat)

        try:
            data = jira_service.create_issue(customer_id, summary, description, issue_type, "TPP",user_full_name, user_email, category_field)
        except HTTPError as e:
            raise ValidationError({"detail": e.response.content})

        print(data)
        
        ticket_id = data.get("id")

        print(request.FILES.values())
        
        for file in request.FILES.values():

            try:
                data = jira_service.add_attachment(ticket_id, file)
            except HTTPError as e:
                raise ValidationError({"attachment_error": e.response.content})

        
        return Response(data, status=status.HTTP_201_CREATED)

    
    def fetch_comments(self, request, ticket_id=None, *args, **kwargs):
        page = request.query_params.get("page") or 1
        page_size = request.query_params.get("page_size") or 10

        # check ticket owned by user called that
        try:
            self.retrieve(request, ticket_id=ticket_id, *args, **kwargs)
        except exceptions.APIException as e:
            return Response({"detail": str(e.detail)}, status=e.status_code)

        try:
            data = jira_service.fetch_ticket_comments(
                ticket_id=ticket_id,
                page=page,
                page_size=page_size
            )
            return Response(data)
        except HTTPError as e:
            logger.error(f"Error fetching comments for ticket {ticket_id}: {e}")
            raise ValidationError({"detail": str(e)})
    
    def create_comments(self, request, ticket_id=None, *args, **kwargs):
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment_text = serializer.validated_data["body"]

        data = jira_service.create_comment(ticket_id, comment_text)

        for file in request.FILES.values():
            try:
                data = jira_service.add_attachment(ticket_id, file)
            except HTTPError as e:
                raise ValidationError({"attachment_error": e.response.content})

        return Response(data, status=status.HTTP_201_CREATED)
    
    def download_attachment(self, request, attachment_id=None, filename=None, *args, **kwargs):
        response = jira_service.download_attachment(attachment_id, filename)

        return response