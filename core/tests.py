"""
Tests for the core application.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import SecretStore


class CoreModelTests(TestCase):
    """Test core models."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testuser123'
        )
    
    def test_secret_store_creation(self):
        """Test SecretStore model creation."""
        secret = SecretStore.objects.create(
            name='test-secret',
            key_vault_name='test-vault',
            secret_name='test-secret-name',
            created_by=self.user
        )
        
        self.assertEqual(secret.name, 'test-secret')
        self.assertEqual(secret.key_vault_name, 'test-vault')
        self.assertEqual(secret.secret_name, 'test-secret-name')
        self.assertEqual(secret.created_by, self.user)
        self.assertIsNotNone(secret.created_at)
        self.assertIsNotNone(secret.updated_at)
    
    def test_secret_store_str_representation(self):
        """Test SecretStore string representation."""
        secret = SecretStore.objects.create(
            name='test-secret',
            key_vault_name='test-vault',
            secret_name='test-secret-name',
            created_by=self.user
        )
        
        # The string representation includes vault and secret name
        self.assertEqual(str(secret), 'test-secret (test-vault/test-secret-name)')


class CoreViewTests(TestCase):
    """Test core views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testuser123'
        )
    
    def test_dashboard_view_anonymous(self):
        """Test dashboard view for anonymous users."""
        response = self.client.get(reverse('core:dashboard'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_dashboard_view_authenticated(self):
        """Test dashboard view for authenticated users."""
        self.client.login(username='testuser', password='testuser123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Internal Developer Platform')
    
    def test_health_check_view(self):
        """Test health check endpoint."""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        # This is the django-health-check endpoint, so check for HTML content
        self.assertContains(response, 'System status')

    def test_login_view_get(self):
        """Test login view GET request."""
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome Back')
        self.assertContains(response, 'Sign in to your IDP account')

    def test_login_view_post_valid_credentials(self):
        """Test login view POST request with valid credentials."""
        response = self.client.post(reverse('core:login'), {
            'username': 'testuser',
            'password': 'testuser123'
        })
        # Should redirect to dashboard after successful login
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('core:dashboard'))

    def test_login_view_post_invalid_credentials(self):
        """Test login view POST request with invalid credentials."""
        response = self.client.post(reverse('core:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        # Should stay on login page with error message
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')

    def test_login_redirect_when_already_authenticated(self):
        """Test that authenticated users are redirected from login page."""
        self.client.login(username='testuser', password='testuser123')
        response = self.client.get(reverse('core:login'))
        # Should redirect to dashboard
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('core:dashboard'))

    def test_logout_functionality(self):
        """Test logout functionality and user feedback."""
        # First login
        self.client.login(username='testuser', password='testuser123')
        
        # Verify user is logged in by accessing dashboard
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Test logout
        response = self.client.get(reverse('core:logout'))
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('core:login'))
        
        # Verify user is logged out by trying to access dashboard
        response = self.client.get(reverse('core:dashboard'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
        
        # Check that logout message is displayed on login page
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response.status_code, 200)
        # The message should be in the response content
        self.assertContains(response, 'successfully logged out')

    def test_logout_when_not_authenticated(self):
        """Test logout when user is not authenticated."""
        # Try to logout without being logged in
        response = self.client.get(reverse('core:logout'))
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('core:login'))
        
        # Check that appropriate message is displayed
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You were not logged in')

    def test_panel_detail_view_authenticated(self):
        """Test panel detail view for authenticated users."""
        from panels.models import Panel, PanelField
        
        # Create a test panel
        panel = Panel.objects.create(
            title='Test Panel',
            description='Test panel description'
        )
        
        # Create a test field
        PanelField.objects.create(
            panel=panel,
            name='test_field',
            label='Test Field',
            field_type='text',
            is_required=True
        )
        
        self.client.login(username='testuser', password='testuser123')
        response = self.client.get(reverse('core:panel_detail', kwargs={'panel_id': panel.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Panel')
        self.assertContains(response, 'Test Field')

    def test_panel_submission_functionality(self):
        """Test panel submission without CSRF errors."""
        from panels.models import Panel, PanelField, PanelSubmission
        
        # Create a test panel
        panel = Panel.objects.create(
            title='Test Submission Panel',
            description='Test panel for submission'
        )
        
        # Create test fields
        PanelField.objects.create(
            panel=panel,
            name='test_text',
            label='Test Text Field',
            field_type='text',
            is_required=True
        )
        
        PanelField.objects.create(
            panel=panel,
            name='test_number',
            label='Test Number Field',
            field_type='number',
            is_required=False
        )
        
        # Login and submit panel
        self.client.login(username='testuser', password='testuser123')
        
        # Submit the panel with valid data
        response = self.client.post(reverse('core:panel_detail', kwargs={'panel_id': panel.id}), {
            'test_text': 'Sample text value',
            'test_number': '42'
        })
        
        # Should redirect after successful submission
        self.assertEqual(response.status_code, 302)
        
        # Check that submission was created
        submissions = PanelSubmission.objects.filter(panel=panel, user=self.user)
        self.assertEqual(submissions.count(), 1)
        
        submission = submissions.first()
        self.assertEqual(submission.data['test_text'], 'Sample text value')
        self.assertEqual(submission.data['test_number'], 42.0)  # Should be converted to float
        self.assertEqual(submission.status, 'pending')

    def test_panel_detail_view_anonymous(self):
        """Test panel detail view for anonymous users."""
        from panels.models import Panel
        
        # Create a test panel
        panel = Panel.objects.create(
            title='Test Panel',
            description='Test panel description'
        )
        
        response = self.client.get(reverse('core:panel_detail', kwargs={'panel_id': panel.id}))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)


class CoreIntegrationTests(TestCase):
    """Integration tests for core functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testuser123'
        )
    
    def test_database_connection(self):
        """Test that database connection works."""
        # This test verifies that we can create and query objects
        secret = SecretStore.objects.create(
            name='integration-test',
            key_vault_name='test-vault',
            secret_name='test-secret',
            created_by=self.user
        )
        
        # Query the object back
        retrieved_secret = SecretStore.objects.get(name='integration-test')
        self.assertEqual(retrieved_secret.id, secret.id)
        self.assertEqual(retrieved_secret.name, 'integration-test')
    
    def test_user_creation_and_basic_auth(self):
        """Test user creation and basic authentication."""
        # Create a new user
        new_user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='newpass123'
        )
        
        # Test authentication
        client = Client()
        login_successful = client.login(username='newuser', password='newpass123')
        self.assertTrue(login_successful)
        
        # Test that user exists
        self.assertTrue(User.objects.filter(username='newuser').exists()) 
