"""
Django management command to create default users for the IDP system.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction


class Command(BaseCommand):
    help = 'Create default users for the IDP system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing users with new passwords',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        with transaction.atomic():
            # Create or update testuser
            testuser, created = User.objects.get_or_create(
                username='testuser',
                defaults={
                    'email': 'testuser@example.com',
                    'first_name': 'Test',
                    'last_name': 'User',
                    'is_active': True,
                    'is_staff': False,
                    'is_superuser': False,
                }
            )
            
            if created or force:
                testuser.set_password('testuser123')
                testuser.save()
                status = 'created' if created else 'updated'
                self.stdout.write(
                    self.style.SUCCESS(f'Test user {status}: testuser/testuser123')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Test user already exists (use --force to update password)')
                )

            # Create or update superuser
            superuser, created = User.objects.get_or_create(
                username='superuser',
                defaults={
                    'email': 'superuser@example.com',
                    'first_name': 'Super',
                    'last_name': 'User',
                    'is_active': True,
                    'is_staff': True,
                    'is_superuser': True,
                }
            )
            
            if created or force:
                superuser.set_password('superuser123')
                superuser.save()
                status = 'created' if created else 'updated'
                self.stdout.write(
                    self.style.SUCCESS(f'Super user {status}: superuser/superuser123')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Super user already exists (use --force to update password)')
                )

            # Also ensure the admin user exists (for backward compatibility)
            admin_user, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@example.com',
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'is_active': True,
                    'is_staff': True,
                    'is_superuser': True,
                }
            )
            
            if created or force:
                admin_user.set_password('admin')
                admin_user.save()
                status = 'created' if created else 'updated'
                self.stdout.write(
                    self.style.SUCCESS(f'Admin user {status}: admin/admin')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Admin user already exists (use --force to update password)')
                )

        self.stdout.write(
            self.style.SUCCESS('\nDefault users are ready:')
        )
        self.stdout.write('  • testuser/testuser123 (regular user)')
        self.stdout.write('  • superuser/superuser123 (superuser)')
        self.stdout.write('  • admin/admin (superuser - legacy)') 
