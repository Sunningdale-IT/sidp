from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Panel, PanelField, PanelSubmission, DynamicDataSource
from .serializers import (
    PanelSerializer, PanelSubmissionSerializer, DynamicDataSourceSerializer
)
from .services import DynamicDataService


class PanelViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for panels - read-only for end users."""
    queryset = Panel.objects.filter(is_active=True)
    serializer_class = PanelSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit panel data."""
        panel = self.get_object()
        
        # Validate submission data against panel fields
        errors = self._validate_submission(panel, request.data)
        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create submission
        submission_data = {
            'panel': panel.id,
            'data': request.data
        }
        serializer = PanelSubmissionSerializer(
            data=submission_data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            submission = serializer.save()
            
            # Trigger async operation processing
            from operations.tasks import process_panel_submission
            process_panel_submission.delay(submission.id)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _validate_submission(self, panel, data):
        """Validate submission data against panel field requirements."""
        errors = {}
        
        for field in panel.fields.filter(is_active=True):
            value = data.get(field.name)
            
            # Check required fields
            if field.is_required and not value:
                errors[field.name] = 'This field is required.'
                continue
            
            # Validate field type specific rules
            if value and field.validation_regex:
                import re
                if not re.match(field.validation_regex, str(value)):
                    errors[field.name] = 'Invalid format.'
        
        return errors


class PanelSubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for panel submissions - users can view their own submissions."""
    serializer_class = PanelSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PanelSubmission.objects.filter(user=self.request.user)


class DynamicDataSourceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for dynamic data sources - admin only."""
    queryset = DynamicDataSource.objects.filter(is_active=True)
    serializer_class = DynamicDataSourceSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def fetch_data(self, request, pk=None):
        """Fetch data from the dynamic source."""
        source = self.get_object()
        service = DynamicDataService()
        
        try:
            data = service.fetch_data(source)
            return Response({'data': data})
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 
