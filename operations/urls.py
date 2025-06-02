from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'templates', views.OperationTemplateViewSet)
router.register(r'executions', views.OperationExecutionViewSet, basename='execution')
router.register(r'logs', views.OperationLogViewSet, basename='log')

app_name = 'operations'

urlpatterns = [
    path('', include(router.urls)),
] 
