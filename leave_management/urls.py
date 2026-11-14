from django.urls import path
from . import views

urlpatterns = [
    path('', views.leave_portal_view, name='leave_portal'),
    path('api/apply/', views.api_apply_leave, name='api_apply_leave'),
    path('api/hod-action/<int:app_id>/', views.api_hod_action, name='api_hod_action'),
    path('api/principal-action/<int:app_id>/', views.api_principal_action, name='api_principal_action'),
]
