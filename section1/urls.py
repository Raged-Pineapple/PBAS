from django.urls import path
from . import views

urlpatterns = [
    # Role-based Entry & Auth
    path('', views.login_view, name='login_view'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    
    # Portals
    path('faculty/', views.faculty_portal_view, name='faculty_portal'),
    path('hod/', views.hod_portal_view, name='hod_portal'),
    path('hod/evaluate/<int:submission_id>/', views.hod_evaluate_view, name='hod_evaluate'),
    path('principal/', views.principal_portal_view, name='principal_portal'),
    path('principal/evaluate/<int:submission_id>/', views.principal_evaluate_view, name='principal_evaluate'),
    
    # PDF Download
    path('export/pdf/', views.download_pdf_view, name='download_pdf_latest'),
    path('export/pdf/<int:submission_id>/', views.download_pdf_view, name='download_pdf'),

    # Evidence Preview, Download, Verify & Reject
    path('evidence/preview/raw/', views.preview_raw_file_view, name='preview_raw_file'),
    path('evidence/preview/<int:evidence_id>/', views.preview_evidence_view, name='evidence_preview'),
    path('evidence/download/<int:evidence_id>/', views.download_evidence_view, name='evidence_download'),
    path('api/evidence/<int:evidence_id>/verify/', views.api_toggle_verify_evidence, name='api_verify_evidence'),
    path('api/evidence/<int:evidence_id>/reject/', views.api_reject_evidence, name='api_reject_evidence'),
    path('api/evidence/reject-inline/', views.api_reject_inline_item, name='api_reject_inline'),
    path('api/notifications/<int:notification_id>/dismiss/', views.api_dismiss_notification, name='api_dismiss_notification'),

    # APIs
    path('api/section1/calculate/', views.api_calculate, name='api_calculate'),
    path('api/upload/', views.api_upload_evidence, name='api_upload'),
    path('api/section1/save/', views.api_save_submission, name='api_save'),
    path('api/hod/review/', views.api_hod_submit_review, name='api_hod_review'),
    path('api/principal/decision/', views.api_principal_submit_decision, name='api_principal_decision'),
    path('api/section1/export/', views.export_json, name='export_json'),
    path('api/section1/export/<int:submission_id>/', views.export_json, name='export_json_id'),
]
