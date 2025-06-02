import subprocess
import logging
import os
import tempfile
from django.conf import settings
from .models import OperationExecution, OperationLog

logger = logging.getLogger(__name__)


class OperationExecutor:
    """Service to execute operations with proper security and logging."""
    
    def __init__(self):
        self.command_validator = CommandValidator()
    
    def execute_operation(self, operation_template, parameters, user):
        """Execute an operation template with given parameters."""
        try:
            # Create execution record
            execution = OperationExecution.objects.create(
                template=operation_template,
                user=user,
                parameters=parameters,
                status='running'
            )
            
            # Validate command
            command = self._build_command(operation_template, parameters)
            if not self.command_validator.is_safe_command(command):
                raise ValueError(f"Command failed security validation: {command}")
            
            # Log start
            self._log_operation(execution, 'info', f"Starting operation: {command}")
            
            # Execute command
            result = self._execute_command(command, execution)
            
            # Update execution status
            execution.status = 'completed' if result['returncode'] == 0 else 'failed'
            execution.output = result['stdout']
            execution.error_output = result['stderr']
            execution.save()
            
            return execution
            
        except Exception as e:
            logger.error(f"Operation execution failed: {str(e)}")
            if 'execution' in locals():
                execution.status = 'failed'
                execution.error_output = str(e)
                execution.save()
                self._log_operation(execution, 'error', f"Operation failed: {str(e)}")
            raise
    
    def _build_command(self, template, parameters):
        """Build the command string from template and parameters."""
        command = template.command_template
        
        # Replace parameters in command template
        for key, value in parameters.items():
            placeholder = f"{{{key}}}"
            command = command.replace(placeholder, str(value))
        
        return command
    
    def _execute_command(self, command, execution):
        """Execute the command with proper environment and logging."""
        env = os.environ.copy()
        
        # Add any environment variables from secrets
        # Note: Secret management removed for now
        
        try:
            # Execute command
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=tempfile.gettempdir()
            )
            
            stdout, stderr = process.communicate(timeout=300)  # 5 minute timeout
            
            result = {
                'returncode': process.returncode,
                'stdout': stdout,
                'stderr': stderr
            }
            
            # Log output
            if stdout:
                self._log_operation(execution, 'info', f"STDOUT: {stdout}")
            if stderr:
                self._log_operation(execution, 'warning' if process.returncode == 0 else 'error', f"STDERR: {stderr}")
            
            return result
            
        except subprocess.TimeoutExpired:
            process.kill()
            error_msg = "Command execution timed out"
            self._log_operation(execution, 'error', error_msg)
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': error_msg
            }
        except Exception as e:
            error_msg = f"Command execution error: {str(e)}"
            self._log_operation(execution, 'error', error_msg)
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': error_msg
            }
    
    def _log_operation(self, execution, level, message):
        """Log operation details."""
        OperationLog.objects.create(
            execution=execution,
            level=level,
            message=message
        )
        
        # Also log to Django logger
        getattr(logger, level)(f"Operation {execution.id}: {message}")


class CommandValidator:
    """Validates commands for security before execution."""
    
    DANGEROUS_COMMANDS = [
        'rm -rf /',
        'dd if=',
        'mkfs',
        'fdisk',
        'format',
        'del /f /s /q',
        'shutdown',
        'reboot',
        'halt',
        'poweroff',
        'init 0',
        'init 6',
        'kill -9 1',
        'killall',
        'pkill',
        'chmod 777',
        'chown root',
        'sudo su',
        'su root',
        '> /dev/',
        'curl | sh',
        'wget | sh',
        'eval',
        'exec',
        '$()',
        '`',
        '&&',
        '||',
        ';',
        '|',
        '>',
        '>>',
        '<',
        '<<',
    ]
    
    ALLOWED_COMMANDS = [
        'kubectl',
        'docker',
        'git',
        'terraform',
        'helm',
        'az',
        'aws',
        'gcloud',
        'echo',
        'cat',
        'ls',
        'pwd',
        'whoami',
        'date',
        'curl',
        'wget',
    ]
    
    def is_safe_command(self, command):
        """Check if a command is safe to execute."""
        command_lower = command.lower().strip()
        
        # Check for dangerous patterns
        for dangerous in self.DANGEROUS_COMMANDS:
            if dangerous in command_lower:
                logger.warning(f"Dangerous command detected: {command}")
                return False
        
        # Check if command starts with allowed command
        first_word = command_lower.split()[0] if command_lower.split() else ''
        if first_word not in self.ALLOWED_COMMANDS:
            logger.warning(f"Command not in allowed list: {first_word}")
            return False
        
        # Additional checks
        if len(command) > 1000:  # Prevent extremely long commands
            logger.warning(f"Command too long: {len(command)} characters")
            return False
        
        return True 
