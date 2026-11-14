from django.urls import path
from . import views

urlpatterns = [
    path('', views.onboarding_hub_view, name='onboarding_hub'),
    path('employee/<str:employee_id>/', views.employee_detail_view, name='employee_detail'),
    path('offboarding/<str:employee_id>/', views.offboarding_detail_view, name='offboarding_detail'),
    path('document/relieving/<str:employee_id>/', views.relieving_letter_view, name='relieving_letter'),
    path('document/experience/<str:employee_id>/', views.experience_cert_view, name='experience_cert'),

    # APIs
    path('api/create/', views.api_create_onboarding_employee, name='api_create_onboarding_employee'),
    path('api/clearance/<str:employee_id>/', views.api_toggle_clearance, name='api_toggle_clearance'),
    path('api/finalize-exit/<str:employee_id>/', views.api_finalize_exit, name='api_finalize_exit'),
]
