from rest_framework import serializers
from .models import Panel, PanelField, PanelSubmission, DynamicDataSource


class PanelFieldSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    
    class Meta:
        model = PanelField
        fields = [
            'id', 'name', 'label', 'field_type', 'order', 'is_required',
            'default_value', 'help_text', 'validation_regex', 'options'
        ]
    
    def get_options(self, obj):
        return obj.get_options()


class PanelSerializer(serializers.ModelSerializer):
    fields = PanelFieldSerializer(many=True, read_only=True)
    
    class Meta:
        model = Panel
        fields = ['id', 'title', 'description', 'order', 'fields']


class PanelSubmissionSerializer(serializers.ModelSerializer):
    panel_title = serializers.CharField(source='panel.title', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PanelSubmission
        fields = ['id', 'panel', 'panel_title', 'username', 'data', 'status', 'created_at']
        read_only_fields = ['user', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class DynamicDataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicDataSource
        fields = [
            'id', 'name', 'description', 'source_type', 'endpoint_url',
            'authentication_method', 'cache_duration', 'is_active'
        ] 
