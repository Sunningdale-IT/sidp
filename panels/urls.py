from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'panels', views.PanelViewSet)
router.register(r'submissions', views.PanelSubmissionViewSet, basename='submission')
router.register(r'data-sources', views.DynamicDataSourceViewSet)

app_name = 'panels'

urlpatterns = [
    path('', include(router.urls)),
] 
