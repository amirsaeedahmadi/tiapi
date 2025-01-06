from typing import Optional

from django.db import models
from rest_framework_simplejwt.models import TokenUser as _TokenUser


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class TokenUser(_TokenUser):
    def has_perm(self, perm: str, obj: Optional[object] = None) -> bool:
        return perm in self.permissions

