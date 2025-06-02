from django.contrib import admin
from .models import Panel, PanelField, PanelSubmission, DynamicDataSource


class PanelFieldInline(admin.TabularInline):
    model = PanelField
    extra = 1
    fields = ('name', 'label', 'field_type', 'order', 'is_required', 'is_active')


@admin.register(Panel)
class PanelAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('order', 'title')
    inlines = [PanelFieldInline]
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PanelField)
class PanelFieldAdmin(admin.ModelAdmin):
    list_display = ('panel', 'label', 'field_type', 'order', 'is_required', 'is_active')
    list_filter = ('field_type', 'is_required', 'is_active', 'panel')
    search_fields = ('name', 'label', 'panel__title')
    ordering = ('panel', 'order', 'name')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PanelSubmission)
class PanelSubmissionAdmin(admin.ModelAdmin):
    list_display = ('panel', 'user', 'status', 'created_at')
    list_filter = ('status', 'panel', 'created_at')
    search_fields = ('user__username', 'panel__title')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'data')
    ordering = ('-created_at',)
    
    def has_add_permission(self, request):
        return False  # Submissions are created through the API
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser  # Only superusers can modify submissions


@admin.register(DynamicDataSource)
class DynamicDataSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type', 'authentication_method', 'is_active', 'created_at')
    list_filter = ('source_type', 'authentication_method', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'endpoint_url')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change) 
