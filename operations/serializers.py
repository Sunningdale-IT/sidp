from rest_framework import serializers
from .models import OperationTemplate, OperationExecution, OperationLog, SecretMapping


class SecretMappingSerializer(serializers.ModelSerializer):
    key_vault_secret_name = serializers.CharField(source='key_vault_secret.name', read_only=True)
    
    class Meta:
        model = SecretMapping
        fields = ['id', 'secret_key', 'key_vault_secret_name']


class OperationTemplateSerializer(serializers.ModelSerializer):
    secret_mappings = SecretMappingSerializer(many=True, read_only=True)
    panel_title = serializers.CharField(source='panel.title', read_only=True)
    
    class Meta:
        model = OperationTemplate
        fields = [
            'id', 'name', 'description', 'panel', 'panel_title', 'operation_type',
            'command_template', 'timeout_seconds', 'retry_count', 'requires_approval',
            'environment_variables', 'required_secrets', 'secret_mappings', 'is_active'
        ]


class OperationExecutionSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    panel_title = serializers.CharField(source='submission.panel.title', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = OperationExecution
        fields = [
            'id', 'template', 'template_name', 'submission', 'panel_title',
            'user', 'username', 'status', 'executed_command', 'output',
            'error_output', 'exit_code', 'started_at', 'completed_at',
            'approved_by', 'approved_by_username', 'approved_at', 'duration',
            'created_at'
        ]
        read_only_fields = [
            'user', 'executed_command', 'output', 'error_output', 'exit_code',
            'started_at', 'completed_at', 'approved_by', 'approved_at', 'created_at'
        ]
    
    def get_duration(self, obj):
        if obj.duration:
            return str(obj.duration)
        return None


class OperationLogSerializer(serializers.ModelSerializer):
    execution_name = serializers.CharField(source='execution.template.name', read_only=True)
    
    class Meta:
        model = OperationLog
        fields = ['id', 'execution', 'execution_name', 'level', 'message', 'timestamp'] 
