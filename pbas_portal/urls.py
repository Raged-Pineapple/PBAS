from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core_portal import views as core_views
from section1 import views as section1_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── Unified Login / Logout (root level, shared by all portals) ──
    path('login/', section1_views.login_view, name='login_view'),
    path('logout/', section1_views.logout_view, name='logout_view'),

    # ── Module portals ──
    path('onboarding-offboarding/', include('onboarding_offboarding.urls')),
    path('leave/', include('leave_management.urls')),
    path('salary/', include('salary_payroll.urls')),
    path('pbas/', include('section1.urls')),

    # ── Quick-switch API ──
    path('api/quick-switch/', core_views.api_quick_switch, name='api_quick_switch'),

    # ── PBAS direct routes (handles internal AJAX & navigation from /pbas templates/JS) ──
    path('faculty/', section1_views.faculty_portal_view, name='root_faculty_portal'),
    path('hod/', section1_views.hod_portal_view, name='root_hod_portal'),
    path('hod/evaluate/<int:submission_id>/', section1_views.hod_evaluate_view, name='root_hod_evaluate'),
    path('principal/', section1_views.principal_portal_view, name='root_principal_portal'),
    path('principal/evaluate/<int:submission_id>/', section1_views.principal_evaluate_view, name='root_principal_evaluate'),
    path('export/pdf/', section1_views.download_pdf_view, name='root_download_pdf_latest'),
    path('export/pdf/<int:submission_id>/', section1_views.download_pdf_view, name='root_download_pdf'),
    path('evidence/preview/raw/', section1_views.preview_raw_file_view, name='root_preview_raw_file'),
    path('evidence/preview/<int:evidence_id>/', section1_views.preview_evidence_view, name='root_evidence_preview'),
    path('evidence/download/<int:evidence_id>/', section1_views.download_evidence_view, name='root_evidence_download'),
    path('api/evidence/<int:evidence_id>/verify/', section1_views.api_toggle_verify_evidence, name='root_api_verify_evidence'),
    path('api/evidence/<int:evidence_id>/reject/', section1_views.api_reject_evidence, name='root_api_reject_evidence'),
    path('api/evidence/reject-inline/', section1_views.api_reject_inline_item, name='root_api_reject_inline'),
    path('api/notifications/<int:notification_id>/dismiss/', section1_views.api_dismiss_notification, name='root_api_dismiss_notification'),
    path('api/section1/calculate/', section1_views.api_calculate, name='root_api_calculate'),
    path('api/upload/', section1_views.api_upload_evidence, name='root_api_upload'),
    path('api/section1/save/', section1_views.api_save_submission, name='root_api_save'),
    path('api/hod/review/', section1_views.api_hod_submit_review, name='root_api_hod_review'),
    path('api/principal/decision/', section1_views.api_principal_submit_decision, name='root_api_principal_decision'),
    path('api/section1/export/', section1_views.export_json, name='root_export_json'),
    path('api/section1/export/<int:submission_id>/', section1_views.export_json, name='root_export_json_id'),

    # ── Master dashboard (root) ──
    path('', core_views.master_dashboard_view, name='master_dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
