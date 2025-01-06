from django.contrib.auth import get_user_model
from django.db import models
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from utils.models import BaseModel

User = get_user_model()


def upload_attachment(instance, filename):
    return f"attachments/{filename}"


class Attachment(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="uploaded_attachments",
        editable=False,
    )
    file = models.FileField(upload_to=upload_attachment)


class TicketManager(models.Manager):
    def create_ticket(self, **kwargs):
        attachments = kwargs.pop("attachments")
        user = kwargs.pop("user")
        with transaction.atomic():
            instance = self.create(user_id=user, **kwargs)
            instance.attachments.set(attachments)
            return instance

    def assign_ticket(self, pk, accountable=None):
        instance = self.get(pk=pk)
        if accountable:
            if not isinstance(accountable, User):
                accountable = User.objects.filter(pk=accountable).first()
        else:
            exclude_kwargs = (
                {"pk": instance.accountable.pk} if instance.accountable else {}
            )
            accountable = User.objects.get_least_assigned_accountable(exclude_kwargs)

        if accountable:
            if accountable == instance.accountable:
                return None
            if (
                not accountable.is_active
                or not accountable.has_perm("tickets.accountable")
                or not accountable.is_staff
            ):
                return None
            qs = self.filter(pk=pk, status__in=[self.model.OPEN])
            updated = qs.update(accountable=accountable)
            if updated:
                return accountable
        return None


class Ticket(BaseModel):
    id = models.UUIDField(primary_key=True, editable=False)
    ref_code = models.IntegerField(editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tickets", editable=False
    )
    SALE = 1
    TECHNICAL = 2

    CAT_CHOICES = {TECHNICAL: _("Technical Dept."), SALE: _("Sale Dept.")}
    cat = models.PositiveSmallIntegerField(choices=CAT_CHOICES)
    URGENT = 1
    HIGH = 2
    MODERATE = 3
    LOW = 4
    PRIO_CHOICES = {
        URGENT: _("Urgent"),
        HIGH: _("High"),
        MODERATE: _("Moderate"),
        LOW: _("Low"),
    }
    priority = models.PositiveSmallIntegerField(choices=PRIO_CHOICES)
    subject = models.CharField(max_length=256)
    description = models.TextField()
    attachments = models.ManyToManyField(Attachment)
    accountable = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name="assigned_tickets",
        editable=False,
    )
    OPEN = 0
    CLOSED = 1
    STATUS_CHOICES = {OPEN: _("Open"), CLOSED: _("Closed")}
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=OPEN)
    objects = TicketManager()

    class Meta:
        ordering = ["-created_at"]

    def assign(self, accountable=None):
        if not accountable:
            exclude_kwargs = {"pk": self.accountable.pk} if self.accountable else {}
            accountable = User.objects.get_least_assigned_accountable(exclude_kwargs)

        if accountable:
            if accountable == self.accountable:
                return None
            if (
                not accountable.is_active
                or not accountable.has_perm("tickets.accountable")
                or not accountable.is_staff
            ):
                return None
            qs = Ticket.objects.filter(pk=self.pk, status__in=[self.OPEN])
            updated = qs.update(accountable=accountable)
            if updated:
                return accountable
        return None


class FollowUpManager(models.Manager):
    def create_followup(self, **kwargs):
        kwargs.pop("audience")
        attachments = kwargs.pop("attachments")
        user = kwargs.pop("user")
        ticket = kwargs.pop("ticket")
        with transaction.atomic():
            instance = self.create(ticket_id=ticket, user_id=user, **kwargs)
            instance.attachments.set(attachments)
            return instance


class FollowUp(BaseModel):
    id = models.UUIDField(primary_key=True, editable=False)
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name="followups", editable=False
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followups", editable=False
    )
    description = models.TextField()
    attachments = models.ManyToManyField(Attachment)
    objects = FollowUpManager()

    class Meta:
        ordering = ["created_at"]
