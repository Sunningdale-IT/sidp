from django.contrib import admin
from .models import OperationTemplate, OperationExecution, OperationLog, SecretMapping


class SecretMappingInline(admin.TabularInline):
    model = SecretMapping
    extra = 1


@admin.register(OperationTemplate)
class OperationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'panel', 'operation_type', 'requires_approval', 'is_active', 'created_at')
    list_filter = ('operation_type', 'requires_approval', 'is_active', 'panel', 'created_at')
    search_fields = ('name', 'description', 'panel__title')
    ordering = ('name',)
    inlines = [SecretMappingInline]
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'panel', 'is_active')
        }),
        ('Operation Configuration', {
            'fields': ('operation_type', 'command_template', 'timeout_seconds', 'retry_count', 'requires_approval')
        }),
        ('Scripts', {
            'fields': ('pre_execution_script', 'post_execution_script'),
            'classes': ('collapse',)
        }),
        ('Environment', {
            'fields': ('environment_variables', 'required_secrets'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(OperationExecution)
class OperationExecutionAdmin(admin.ModelAdmin):
    list_display = ('template', 'user', 'status', 'started_at', 'completed_at', 'exit_code')
    list_filter = ('status', 'template__operation_type', 'started_at', 'completed_at')
    search_fields = ('template__name', 'user__username', 'executed_command')
    readonly_fields = (
        'template', 'submission', 'user', 'executed_command', 'output', 
        'error_output', 'exit_code', 'started_at', 'completed_at',
        'created_at', 'updated_at', 'created_by', 'updated_by'
    )
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Execution Details', {
            'fields': ('template', 'submission', 'user', 'status')
        }),
        ('Command & Output', {
            'fields': ('executed_command', 'output', 'error_output', 'exit_code'),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Executions are created through the API
    
    def has_change_permission(self, request, obj=None):
        # Only allow changing status and approval fields
        return request.user.is_superuser


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ('execution', 'level', 'message_preview', 'timestamp')
    list_filter = ('level', 'timestamp', 'execution__template__name')
    search_fields = ('message', 'execution__template__name')
    readonly_fields = ('execution', 'level', 'message', 'timestamp')
    ordering = ('-timestamp',)
    
    def message_preview(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = 'Message Preview'
    
    def has_add_permission(self, request):
        return False  # Logs are created automatically
    
    def has_change_permission(self, request, obj=None):
        return False  # Logs should not be modified


@admin.register(SecretMapping)
class SecretMappingAdmin(admin.ModelAdmin):
    list_display = ('operation_template', 'secret_key', 'key_vault_secret', 'created_at')
    list_filter = ('operation_template', 'created_at')
    search_fields = ('secret_key', 'operation_template__name', 'key_vault_secret__name')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change) 
