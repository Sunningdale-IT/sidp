from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from panels.models import Panel


@login_required
def dashboard(request):
    """Main dashboard view with 1960s vintage modern styling."""
    panels = Panel.objects.filter(is_active=True).order_by('order')
    context = {
        'panels': panels,
        'user': request.user,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def panel_detail(request, panel_id):
    """Panel detail view with form for user interaction."""
    panel = get_object_or_404(Panel, id=panel_id, is_active=True)
    
    # Get recent submissions for this panel by the current user
    from panels.models import PanelSubmission
    recent_submissions = PanelSubmission.objects.filter(
        panel=panel, 
        user=request.user
    ).order_by('-created_at')[:5]  # Last 5 submissions
    
    if request.method == 'POST':
        # Collect form data
        form_data = {}
        errors = {}
        
        for field in panel.fields.filter(is_active=True):
            value = request.POST.get(field.name, '').strip()
            
            # Validate required fields
            if field.is_required and not value:
                errors[field.name] = 'This field is required.'
                continue
            
            # Convert field types
            if field.field_type == 'number' and value:
                try:
                    value = float(value)
                except ValueError:
                    errors[field.name] = 'Please enter a valid number.'
                    continue
            elif field.field_type == 'boolean':
                value = value.lower() in ['true', '1', 'on', 'yes']
            
            form_data[field.name] = value
        
        if not errors:
            # Submit to API directly (internal call to avoid CSRF issues)
            try:
                from panels.models import PanelSubmission
                from panels.serializers import PanelSubmissionSerializer
                
                # Create submission data
                submission_data = {
                    'panel': panel.id,
                    'data': form_data
                }
                
                # Create serializer with request context
                serializer = PanelSubmissionSerializer(
                    data=submission_data, 
                    context={'request': request}
                )
                
                if serializer.is_valid():
                    submission = serializer.save()
                    
                    # Trigger async operation processing
                    try:
                        from operations.tasks import process_panel_submission
                        process_panel_submission.delay(submission.id)
                    except ImportError:
                        # Celery not available, handle synchronously or skip
                        pass
                    
                    messages.success(request, f'Panel "{panel.title}" submitted successfully! Submission ID: {submission.id}')
                    return redirect('core:panel_detail', panel_id=panel_id)
                else:
                    error_messages = []
                    for field, field_errors in serializer.errors.items():
                        for error in field_errors:
                            error_messages.append(f'{field}: {error}')
                    messages.error(request, f'Submission failed: {", ".join(error_messages)}')
                    
            except Exception as e:
                messages.error(request, f'Error submitting panel: {str(e)}')
        else:
            for field, error in errors.items():
                messages.error(request, f'{field}: {error}')
    
    context = {
        'panel': panel,
        'fields': panel.fields.filter(is_active=True).order_by('order'),
        'recent_submissions': recent_submissions,
    }
    return render(request, 'core/panel_detail.html', context)


def login_view(request):
    """Login page view with authentication handling."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'core:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please enter both username and password.')
    
    return render(request, 'core/login.html')


def logout_view(request):
    """Custom logout view with user feedback."""
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f'You have been successfully logged out. See you later, {username}!')
    else:
        messages.info(request, 'You were not logged in.')
    
    return redirect('core:login')


def health_check(request):
    """Health check endpoint for Kubernetes."""
    return JsonResponse({
        'status': 'healthy',
        'user': request.user.username if request.user.is_authenticated else 'anonymous'
    }) 
