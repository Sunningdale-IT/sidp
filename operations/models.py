from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel
from panels.models import Panel
import json


class OperationTemplate(BaseModel):
    """Model representing a configurable operation template."""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    panel = models.ForeignKey(Panel, on_delete=models.CASCADE, related_name='operations')
    
    # Operation configuration
    operation_type = models.CharField(
        max_length=50,
        choices=[
            ('kubectl', 'Kubernetes CLI'),
            ('azure_cli', 'Azure CLI'),
            ('git', 'Git Commands'),
            ('docker', 'Docker Commands'),
            ('custom_script', 'Custom Script'),
            ('api_call', 'API Call'),
        ]
    )
    
    # Command template with placeholders
    command_template = models.TextField(
        help_text="Command template with {{variable}} placeholders"
    )
    
    # Pre and post execution scripts
    pre_execution_script = models.TextField(blank=True)
    post_execution_script = models.TextField(blank=True)
    
    # Execution settings
    timeout_seconds = models.PositiveIntegerField(default=300)
    retry_count = models.PositiveIntegerField(default=0)
    requires_approval = models.BooleanField(default=False)
    
    # Environment and security
    environment_variables = models.JSONField(default=dict, blank=True)
    required_secrets = models.JSONField(default=list, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'operations_operation_template'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.operation_type})"


class OperationExecution(BaseModel):
    """Model to track operation executions."""
    template = models.ForeignKey(OperationTemplate, on_delete=models.CASCADE, related_name='executions')
    submission = models.ForeignKey(
        'panels.PanelSubmission', 
        on_delete=models.CASCADE, 
        related_name='operations'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Execution details
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('running', 'Running'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    
    # Command and output
    executed_command = models.TextField()
    output = models.TextField(blank=True)
    error_output = models.TextField(blank=True)
    exit_code = models.IntegerField(null=True, blank=True)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Approval workflow
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_operations'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'operations_operation_execution'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.template.name} - {self.user.username} ({self.status})"

    @property
    def duration(self):
        """Calculate execution duration."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None


class OperationLog(BaseModel):
    """Model to store detailed operation logs."""
    execution = models.ForeignKey(OperationExecution, on_delete=models.CASCADE, related_name='logs')
    level = models.CharField(
        max_length=10,
        choices=[
            ('DEBUG', 'Debug'),
            ('INFO', 'Info'),
            ('WARNING', 'Warning'),
            ('ERROR', 'Error'),
            ('CRITICAL', 'Critical'),
        ]
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'operations_operation_log'
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.execution} - {self.level}: {self.message[:50]}"


class SecretMapping(BaseModel):
    """Model to map operation secrets to Azure Key Vault secrets."""
    operation_template = models.ForeignKey(OperationTemplate, on_delete=models.CASCADE, related_name='secret_mappings')
    secret_key = models.CharField(max_length=255, help_text="Key used in operation template")
    key_vault_secret = models.ForeignKey('core.SecretStore', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'operations_secret_mapping'
        unique_together = ['operation_template', 'secret_key']

    def __str__(self):
        return f"{self.operation_template.name} - {self.secret_key}" 
