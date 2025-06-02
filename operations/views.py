from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import OperationTemplate, OperationExecution, OperationLog
from .serializers import (
    OperationTemplateSerializer, OperationExecutionSerializer, OperationLogSerializer
)
from .tasks import execute_operation


class OperationTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for operation templates - admin only."""
    queryset = OperationTemplate.objects.filter(is_active=True)
    serializer_class = OperationTemplateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class OperationExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for operation executions - users can view their own executions."""
    serializer_class = OperationExecutionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return OperationExecution.objects.all()
        return OperationExecution.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve an operation execution."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff members can approve operations'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        execution = self.get_object()
        
        if execution.status != 'pending':
            return Response(
                {'error': 'Operation is not in pending status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        execution.status = 'approved'
        execution.approved_by = request.user
        execution.approved_at = timezone.now()
        execution.save()
        
        # Trigger async execution
        execute_operation.delay(execution.id)
        
        return Response({'message': 'Operation approved and queued for execution'})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an operation execution."""
        execution = self.get_object()
        
        # Users can cancel their own operations, staff can cancel any
        if execution.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only cancel your own operations'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if execution.status not in ['pending', 'approved']:
            return Response(
                {'error': 'Operation cannot be cancelled in current status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        execution.status = 'cancelled'
        execution.save()
        
        return Response({'message': 'Operation cancelled'})


class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for operation logs."""
    serializer_class = OperationLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        execution_id = self.request.query_params.get('execution_id')
        if execution_id:
            # Check if user has access to this execution
            execution = get_object_or_404(OperationExecution, id=execution_id)
            if execution.user != self.request.user and not self.request.user.is_staff:
                return OperationLog.objects.none()
            return OperationLog.objects.filter(execution_id=execution_id)
        
        # Return logs for user's executions only
        if self.request.user.is_staff:
            return OperationLog.objects.all()
        
        user_executions = OperationExecution.objects.filter(user=self.request.user)
        return OperationLog.objects.filter(execution__in=user_executions) 
