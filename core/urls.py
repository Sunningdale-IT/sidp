from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('panel/<int:panel_id>/', views.panel_detail, name='panel_detail'),
    path('health/', views.health_check, name='health_check'),
] 
