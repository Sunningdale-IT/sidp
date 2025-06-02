from django.contrib import admin
from .models import SecretStore


@admin.register(SecretStore)
class SecretStoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'key_vault_name', 'secret_name', 'is_active', 'created_at')
    list_filter = ('is_active', 'key_vault_name', 'created_at')
    search_fields = ('name', 'secret_name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change) 
