from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    """Base model with common fields for all models."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='%(class)s_updated'
    )

    class Meta:
        abstract = True


class SecretStore(BaseModel):
    """Model to store references to Azure Key Vault secrets."""
    name = models.CharField(max_length=255, unique=True)
    key_vault_name = models.CharField(max_length=255)
    secret_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.key_vault_name}/{self.secret_name})"

    class Meta:
        db_table = 'core_secret_store' 
