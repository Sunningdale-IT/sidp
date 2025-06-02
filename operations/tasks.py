from celery import shared_task
from django.utils import timezone
from django.contrib.auth.models import User
from .models import OperationExecution, OperationTemplate, OperationLog
from .services import OperationExecutor
from panels.models import PanelSubmission
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_panel_submission(self, submission_id):
    """Process a panel submission by executing associated operations."""
    try:
        submission = PanelSubmission.objects.get(id=submission_id)
        submission.status = 'processing'
        submission.save()
        
        # Get operation templates for this panel
        templates = OperationTemplate.objects.filter(
            panel=submission.panel,
            is_active=True
        )
        
        if not templates.exists():
            submission.status = 'completed'
            submission.save()
            return f"No operations configured for panel {submission.panel.title}"
        
        # Create operation executions
        executions = []
        for template in templates:
            execution = OperationExecution.objects.create(
                template=template,
                submission=submission,
                user=submission.user,
                executed_command="",  # Will be populated during execution
                status='pending'
            )
            executions.append(execution)
        
        # Execute operations
        executor = OperationExecutor()
        all_successful = True
        
        for execution in executions:
            try:
                if execution.template.requires_approval:
                    # Skip execution if approval is required
                    continue
                
                success = executor.execute_operation(execution)
                if not success:
                    all_successful = False
                    
            except Exception as e:
                logger.error(f"Error executing operation {execution.id}: {str(e)}")
                execution.status = 'failed'
                execution.error_output = str(e)
                execution.save()
                all_successful = False
        
        # Update submission status
        if all_successful:
            submission.status = 'completed'
        else:
            submission.status = 'failed'
        submission.save()
        
        return f"Processed submission {submission_id} with {len(executions)} operations"
        
    except PanelSubmission.DoesNotExist:
        logger.error(f"Panel submission {submission_id} not found")
        return f"Submission {submission_id} not found"
    except Exception as e:
        logger.error(f"Error processing submission {submission_id}: {str(e)}")
        return f"Error processing submission {submission_id}: {str(e)}"


@shared_task(bind=True)
def execute_operation(self, execution_id):
    """Execute a single operation."""
    try:
        execution = OperationExecution.objects.get(id=execution_id)
        
        if execution.status != 'approved' and execution.template.requires_approval:
            return f"Operation {execution_id} requires approval"
        
        executor = OperationExecutor()
        success = executor.execute_operation(execution)
        
        if success:
            return f"Operation {execution_id} completed successfully"
        else:
            return f"Operation {execution_id} failed"
            
    except OperationExecution.DoesNotExist:
        logger.error(f"Operation execution {execution_id} not found")
        return f"Operation execution {execution_id} not found"
    except Exception as e:
        logger.error(f"Error executing operation {execution_id}: {str(e)}")
        return f"Error executing operation {execution_id}: {str(e)}"


@shared_task
def cleanup_old_executions():
    """Clean up old operation executions and logs."""
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=30)
    
    # Delete old executions
    old_executions = OperationExecution.objects.filter(
        created_at__lt=cutoff_date,
        status__in=['completed', 'failed', 'cancelled']
    )
    
    count = old_executions.count()
    old_executions.delete()
    
    logger.info(f"Cleaned up {count} old operation executions")
    return f"Cleaned up {count} old operation executions" 
