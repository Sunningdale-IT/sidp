from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel
import json


class Panel(BaseModel):
    """Model representing a configurable panel in the dashboard."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'title']
        db_table = 'panels_panel'

    def __str__(self):
        return self.title


class PanelField(BaseModel):
    """Model representing individual fields within a panel."""
    
    FIELD_TYPES = [
        ('radio', 'Radio Buttons'),
        ('boolean', 'Boolean/Checkbox'),
        ('dropdown', 'Dropdown Menu'),
        ('text', 'Free Text Input'),
        ('textarea', 'Text Area'),
        ('number', 'Number Input'),
        ('email', 'Email Input'),
        ('url', 'URL Input'),
    ]
    
    panel = models.ForeignKey(Panel, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=False)
    default_value = models.TextField(blank=True)
    help_text = models.TextField(blank=True)
    validation_regex = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    
    # For dynamic options (dropdown, radio)
    options_source = models.CharField(max_length=255, blank=True, help_text="API endpoint or static options")
    static_options = models.JSONField(default=list, blank=True, help_text="Static options as JSON array")
    
    class Meta:
        ordering = ['order', 'name']
        unique_together = ['panel', 'name']
        db_table = 'panels_panel_field'

    def __str__(self):
        return f"{self.panel.title} - {self.label}"

    def get_options(self):
        """Get options for dropdown/radio fields."""
        if self.static_options:
            return self.static_options
        # TODO: Implement dynamic options fetching from API
        return []


class PanelSubmission(BaseModel):
    """Model to store user submissions for panels."""
    panel = models.ForeignKey(Panel, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.JSONField(default=dict)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    
    class Meta:
        db_table = 'panels_panel_submission'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.panel.title} - {self.user.username} ({self.status})"


class DynamicDataSource(BaseModel):
    """Model to configure dynamic data sources for panel fields."""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    source_type = models.CharField(
        max_length=50,
        choices=[
            ('docker_registry', 'Docker Registry'),
            ('kubernetes_api', 'Kubernetes API'),
            ('azure_api', 'Azure API'),
            ('git_repository', 'Git Repository'),
            ('custom_api', 'Custom API'),
        ]
    )
    endpoint_url = models.URLField(blank=True)
    authentication_method = models.CharField(
        max_length=50,
        choices=[
            ('none', 'None'),
            ('bearer_token', 'Bearer Token'),
            ('basic_auth', 'Basic Authentication'),
            ('api_key', 'API Key'),
            ('azure_ad', 'Azure AD'),
        ],
        default='none'
    )
    auth_config = models.JSONField(default=dict, blank=True)
    cache_duration = models.PositiveIntegerField(default=300, help_text="Cache duration in seconds")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'panels_dynamic_data_source'

    def __str__(self):
        return self.name 
