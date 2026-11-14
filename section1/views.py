import json
import os
import mimetypes
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.conf import settings

from pbas_engine.calculator import (
    calculate_section_1, calculate_section_2, calculate_section_3, 
    calculate_section_4, calculate_complete_pbas
)
from django.utils import timezone
from .models import Section1Submission, UploadedEvidence, AppraisalNotification
from .auth_utils import authenticate_user, get_env_credentials
from .pdf_generator import generate_pbas_pdf

# 20 Innovative TLP Methods
INNOVATIVE_TLP_METHODS = [
    "Blended Learning",
    "Collaborative Learning",
    "Flipped Classroom",
    "Mini Projects",
    "Group Discussion",
    "Role Play Based Teaching",
    "Experiments Beyond Syllabus / Case Studies",
    "Joy of Coding / Coding Competitions",
    "Use of HackerEarth / LeetCode / coding platforms / management games",
    "Poster Presentation / Seminars",
    "Industrial Visits / Field Trips",
    "Hands-on Activity",
    "MOOC Certification",
    "Simulation Based Learning",
    "Expert Talk / Podcast / Augmented Talks",
    "Open Book Exams",
    "Peer Learning",
    "Library Assignment / Quiz",
    "Integrating Advanced Topics for Fast Learners",
    "Tutorial Classes for Weak Learners"
]

PROFESSIONAL_SOCIETIES = [
    "IEEE", "ACM", "ISTE", "IETE", "IEI", "ACCE", "ISHRAE", 
    "NSCA", "BSS", "INSA", "NIPM", "NHRD", "AIMA", "BMA"
]


# ==========================================
# AUTHENTICATION VIEWS
# ==========================================
@csrf_exempt
def login_view(request):
    """
    Role-Based Login Portal (Faculty, HOD, Principal)
    Validates credentials dynamically against .env
    """
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        role = request.POST.get('role', '')

        success, authenticated_role, user_info = authenticate_user(username, password, role)
        if success:
            request.session['is_authenticated'] = True
            request.session['user_role'] = authenticated_role
            request.session['username'] = username
            request.session['user_name'] = user_info.get('name', username)
            request.session['department'] = user_info.get('department', 'Computer Science & Engineering')
            request.session['employee_id'] = user_info.get('employee_id', '')

            if authenticated_role == 'HOD':
                return redirect('master_dashboard')
            elif authenticated_role == 'PRINCIPAL':
                return redirect('master_dashboard')
            else:
                return redirect('master_dashboard')
        else:
            error = "Invalid username or password for selected role. (Check .env credentials)"

    creds = get_env_credentials()
    return render(request, 'section1/login.html', {
        'error': error,
        'creds': creds
    })


def logout_view(request):
    request.session.flush()
    return redirect('login_view')


# ==========================================
# ROLE-BASED PORTAL VIEWS
# ==========================================
def faculty_portal_view(request):
    """
    Faculty view for appraisal self-evaluation, document upload, and submission.
    Binds directly to the logged-in faculty member's credentials and records.
    """
    user_name = request.session.get('user_name', 'Dr. Ramesh Kumar')
    employee_id = request.session.get('employee_id', 'RNSIT-CS-1042')
    department = request.session.get('department', 'Computer Science & Engineering')

    # Find submission for this faculty or create (fetch latest)
    submission = Section1Submission.objects.filter(employee_id=employee_id).order_by('-updated_at', '-id').first()
    if not submission:
        submission = Section1Submission.objects.filter(faculty_name=user_name).order_by('-updated_at', '-id').first()
    if not submission:
        submission = Section1Submission.objects.create(
            faculty_name=user_name,
            employee_id=employee_id,
            department=department,
            academic_year='2026-2027',
            status='DRAFT'
        )
    else:
        # Keep name and department in sync with current session / .env
        submission.faculty_name = user_name
        submission.department = department
        if employee_id:
            submission.employee_id = employee_id
        submission.save()

    user_role = request.session.get('user_role', 'FACULTY')

    # Fetch HOD review notifications and rejections for this faculty submission
    notifications = AppraisalNotification.objects.filter(submission=submission).order_by('-created_at')
    rejections = [n for n in notifications if n.notification_type == 'REJECTION']
    rejection_count = len(rejections)

    submission_dict = {
        'id': submission.id,
        'faculty_name': submission.faculty_name,
        'employee_id': submission.employee_id,
        'department': submission.department,
        'academic_year': submission.academic_year,
        'status': submission.status,
        'rejection_count': rejection_count,
        'raw_payload': json.loads(submission.raw_payload or '{}'),
        'calculation_breakdown': json.loads(submission.calculation_breakdown or '{}')
    }

    context = {
        'submission': submission,
        'submission_json': json.dumps(submission_dict),
        'user_role': user_role,
        'user_name': user_name,
        'employee_id': employee_id,
        'department': department,
        'notifications': notifications,
        'rejections': rejections,
        'rejection_count': rejection_count,
        'innovative_methods': INNOVATIVE_TLP_METHODS,
        'professional_societies': PROFESSIONAL_SOCIETIES
    }
    return render(request, 'section1/index.html', context)


def hod_portal_view(request):
    """
    HOD Portal: Lists all faculty submissions within department.
    HOD can view and evaluate each faculty member.
    """
    submissions = Section1Submission.objects.order_by('-updated_at')
    user_name = request.session.get('user_name', 'Dr. Kiran B. R. (HOD - CSE)')
    department = request.session.get('department', 'Computer Science & Engineering')

    return render(request, 'section1/hod_portal.html', {
        'submissions': submissions,
        'user_name': user_name,
        'department': department
    })


def hod_evaluate_view(request, submission_id):
    """
    HOD Detailed Evaluation view for a specific faculty member.
    Passes all submitted data, section breakdowns, and uploaded evidence documents.
    """
    submission = get_object_or_404(Section1Submission, id=submission_id)
    payload = json.loads(submission.raw_payload or '{}')
    breakdown = submission.get_breakdown()
    if 'section1' in breakdown and isinstance(breakdown['section1'], dict):
        for k, v in breakdown['section1'].items():
            if k not in breakdown:
                breakdown[k] = v
    evidence_docs = UploadedEvidence.objects.filter(submission=submission).order_by('-uploaded_at')
    if not evidence_docs.exists():
        # Fallback to any recent documents uploaded
        evidence_docs = UploadedEvidence.objects.order_by('-uploaded_at')[:15]

    return render(request, 'section1/hod_evaluate.html', {
        'submission': submission,
        'payload': payload,
        'breakdown': breakdown,
        'evidence_docs': evidence_docs,
        'user_name': request.session.get('user_name', 'Dr. Kiran B. R. (HOD - CSE)')
    })


def principal_portal_view(request):
    """
    Principal Portal: Lists all institutional faculty submissions.
    Principal reviews HOD evaluations and assigns final institutional scores.
    """
    submissions = Section1Submission.objects.order_by('-updated_at')
    user_name = request.session.get('user_name', 'Dr. M. K. Venkatesha (Principal)')

    return render(request, 'section1/principal_portal.html', {
        'submissions': submissions,
        'user_name': user_name
    })


def principal_evaluate_view(request, submission_id):
    """
    Principal Final Approval & Grading view for a specific faculty member.
    Passes all submitted data, HOD review remarks, and documentary evidence.
    """
    submission = get_object_or_404(Section1Submission, id=submission_id)
    payload = json.loads(submission.raw_payload or '{}')
    breakdown = submission.get_breakdown()
    if 'section1' in breakdown and isinstance(breakdown['section1'], dict):
        for k, v in breakdown['section1'].items():
            if k not in breakdown:
                breakdown[k] = v
    evidence_docs = UploadedEvidence.objects.filter(submission=submission).order_by('-uploaded_at')
    if not evidence_docs.exists():
        evidence_docs = UploadedEvidence.objects.order_by('-uploaded_at')[:15]

    return render(request, 'section1/principal_evaluate.html', {
        'submission': submission,
        'payload': payload,
        'breakdown': breakdown,
        'evidence_docs': evidence_docs,
        'user_name': request.session.get('user_name', 'Dr. M. K. Venkatesha (Principal)')
    })


# ==========================================
# CALCULATION & SAVING APIs
# ==========================================
@csrf_exempt
def api_calculate(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=405)

    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body.decode('utf-8'))
        else:
            raw_data = request.POST.get('data')
            payload = json.loads(raw_data) if raw_data else {}

        target_section = payload.get('target_section', 'all')
        
        if target_section == 'section1':
            result = calculate_section_1(payload.get('section1', payload))
        elif target_section == 'section2':
            result = calculate_section_2(payload.get('section2', payload))
        elif target_section == 'section3':
            result = calculate_section_3(payload.get('section3', payload))
        elif target_section == 'section4':
            result = calculate_section_4(payload.get('section4', payload))
        else:
            result = calculate_complete_pbas(payload)
            
        return JsonResponse({'success': True, 'data': result})
    except json.JSONDecodeError as e:
        return JsonResponse({'success': False, 'error': f'Invalid JSON: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_upload_evidence(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=405)

    uploaded_file = request.FILES.get('file')
    component_code = request.POST.get('component_code', 'GEN')
    sub_id = request.POST.get('submission_id')
    
    if not uploaded_file:
        return JsonResponse({'success': False, 'error': 'No file uploaded'}, status=400)

    try:
        submission = Section1Submission.objects.filter(id=sub_id).first() if sub_id else None
        evidence = UploadedEvidence.objects.create(
            submission=submission,
            component_code=component_code,
            file=uploaded_file,
            original_filename=uploaded_file.name,
            file_size_kb=round(uploaded_file.size / 1024.0, 2)
        )
        return JsonResponse({
            'success': True,
            'file_id': evidence.id,
            'file_url': evidence.file.url,
            'preview_url': f'/evidence/preview/{evidence.id}/',
            'download_url': f'/evidence/download/{evidence.id}/',
            'file_name': evidence.original_filename,
            'size_kb': evidence.file_size_kb,
            'is_verified': evidence.is_verified
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def _render_docx_as_html(file_path, original_filename, download_url):
    """Converts a .docx file to a beautiful, clean HTML page using mammoth."""
    import mammoth
    with open(file_path, 'rb') as f:
        res = mammoth.convert_to_html(f)
        docx_html = res.value

    wrapped_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>{original_filename}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.6;
      color: #1e293b;
      background: #f8fafc;
      margin: 0;
      padding: 24px 16px;
    }}
    .document-container {{
      max-width: 880px;
      margin: 0 auto;
      background: #ffffff;
      padding: 40px 48px;
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.06);
      border: 1px solid #e2e8f0;
    }}
    .header-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 16px;
      margin-bottom: 24px;
      border-bottom: 2px solid #2563eb;
    }}
    .doc-badge {{
      background: #dbeafe;
      color: #1d4ed8;
      font-weight: 700;
      font-size: 11px;
      padding: 4px 10px;
      border-radius: 6px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .doc-title {{
      margin: 6px 0 0 0;
      font-size: 16px;
      font-weight: 700;
      color: #0f172a;
    }}
    .download-btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      color: #1d4ed8;
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      padding: 8px 14px;
      border-radius: 8px;
      text-decoration: none;
      font-size: 12px;
      font-weight: 600;
      transition: all 0.15s;
    }}
    .download-btn:hover {{
      background: #dbeafe;
    }}
    .doc-body {{
      font-size: 14px;
      color: #334155;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
      font-size: 13px;
    }}
    th, td {{
      border: 1px solid #cbd5e1;
      padding: 8px 12px;
      text-align: left;
    }}
    th {{ background: #f1f5f9; font-weight: 600; color: #1e293b; }}
    h1, h2, h3, h4 {{ color: #0f172a; margin-top: 24px; margin-bottom: 12px; }}
    h1 {{ font-size: 22px; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; }}
    h2 {{ font-size: 18px; }}
    h3 {{ font-size: 15px; }}
    p {{ margin-bottom: 12px; }}
    ul, ol {{ margin-bottom: 14px; padding-left: 24px; }}
    li {{ margin-bottom: 4px; }}
  </style>
</head>
<body>
  <div class="document-container">
    <div class="header-bar">
      <div>
        <span class="doc-badge">Word Document Preview (.docx)</span>
        <h3 class="doc-title">{original_filename}</h3>
      </div>
      <a class="download-btn" href="{download_url}" download>⬇ Download File</a>
    </div>
    <div class="doc-body">
      {docx_html}
    </div>
  </div>
</body>
</html>"""
    response = HttpResponse(wrapped_html, content_type='text/html')
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response


@xframe_options_exempt
def preview_evidence_view(request, evidence_id):
    """
    Renders evidence files inside the portal preview modal (iframe).
    - .docx → Converted to HTML with mammoth and rendered directly.
    - PDFs / images → served inline so the browser renders them directly.
    - Other types → returns a friendly HTML page with a prominent Download button.
    """
    evidence = get_object_or_404(UploadedEvidence, id=evidence_id)

    if not evidence.file:
        return _preview_unavailable(evidence, "No file is attached to this record.")
    try:
        file_path = evidence.file.path
    except Exception:
        return _preview_unavailable(evidence, "Could not resolve file path.")
    if not os.path.exists(file_path):
        return _preview_unavailable(evidence, "File was not found on the server.")

    fname_lower = evidence.original_filename.lower()

    # 1. DOCX conversion
    if fname_lower.endswith('.docx'):
        try:
            return _render_docx_as_html(
                file_path, 
                evidence.original_filename, 
                f"/evidence/download/{evidence.id}/"
            )
        except Exception as e:
            return _preview_unavailable(evidence, f"Could not convert Word document: {e}")

    # 2. Determine MIME type
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        if fname_lower.endswith('.pdf'):
            content_type = 'application/pdf'
        elif fname_lower.endswith(('.jpg', '.jpeg')):
            content_type = 'image/jpeg'
        elif fname_lower.endswith('.png'):
            content_type = 'image/png'
        elif fname_lower.endswith('.gif'):
            content_type = 'image/gif'
        elif fname_lower.endswith('.webp'):
            content_type = 'image/webp'
        else:
            content_type = 'application/octet-stream'

    # 3. Previewable types: serve inline
    PREVIEWABLE = ('application/pdf', 'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml')
    if content_type in PREVIEWABLE:
        try:
            response = FileResponse(open(file_path, 'rb'), content_type=content_type)
            response['Content-Disposition'] = f'inline; filename="{evidence.original_filename}"'
            response['X-Frame-Options'] = 'SAMEORIGIN'
            return response
        except Exception as e:
            return _preview_unavailable(evidence, f"Error reading file: {e}")

    # 4. Fallback: friendly "download only" page
    return _preview_unavailable(
        evidence,
        f"This file type ({fname_lower.split('.')[-1].upper()}) is best viewed in its native application."
    )


@xframe_options_exempt
def preview_raw_file_view(request):
    """
    Renders any evidence file directly by its relative /media/... URL or path.
    Converts .docx to styled HTML with mammoth; serves PDFs and images inline.
    """
    file_url = request.GET.get('url', '').strip()
    if not file_url:
        return HttpResponse("No file URL specified", status=400)

    clean_url = file_url.split('#')[0].split('?')[0]
    if clean_url.startswith(settings.MEDIA_URL):
        rel_path = clean_url[len(settings.MEDIA_URL):]
    elif clean_url.startswith('/media/'):
        rel_path = clean_url[7:]
    else:
        rel_path = clean_url.lstrip('/')

    full_path = os.path.join(settings.MEDIA_ROOT, rel_path)

    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return HttpResponse(f"File not found on server: {clean_url}", status=404)

    original_filename = os.path.basename(full_path)
    fname_lower = original_filename.lower()

    # 1. DOCX conversion
    if fname_lower.endswith('.docx'):
        try:
            return _render_docx_as_html(full_path, original_filename, file_url)
        except Exception as e:
            return HttpResponse(f"Error converting Word file: {e}", status=500)

    # 2. PDF / Images
    content_type, _ = mimetypes.guess_type(full_path)
    if not content_type:
        content_type = 'application/pdf' if fname_lower.endswith('.pdf') else 'application/octet-stream'

    response = FileResponse(open(full_path, 'rb'), content_type=content_type)
    response['Content-Disposition'] = f'inline; filename="{original_filename}"'
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response


def _preview_unavailable(evidence, reason="Preview not available."):
    """Returns a minimal HTML page shown inside the preview iframe when a file can't be rendered."""
    ext = evidence.original_filename.split('.')[-1].upper() if '.' in evidence.original_filename else 'FILE'
    icon_map = {
        'DOCX': '📝', 'DOC': '📝', 'XLSX': '📊', 'XLS': '📊',
        'PPTX': '📋', 'PPT': '📋', 'ZIP': '🗜️', 'RAR': '🗜️',
    }
    icon = icon_map.get(ext, '📄')
    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
      background: #f8fafc;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      padding: 24px;
    }}
    .card {{
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      padding: 40px 48px;
      text-align: center;
      max-width: 420px;
      box-shadow: 0 4px 24px rgba(0,0,0,.07);
    }}
    .icon {{ font-size: 56px; margin-bottom: 16px; }}
    .filename {{ font-size: 15px; font-weight: 700; color: #1e293b; margin-bottom: 6px; word-break: break-word; }}
    .reason {{ font-size: 13px; color: #64748b; margin-bottom: 24px; }}
    .btn {{
      display: inline-flex; align-items: center; gap: 8px;
      padding: 10px 22px; border-radius: 10px; text-decoration: none;
      font-size: 13px; font-weight: 700;
      background: #2563eb; color: white;
      transition: background .15s;
    }}
    .btn:hover {{ background: #1d4ed8; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">{icon}</div>
    <div class="filename">{evidence.original_filename}</div>
    <div class="reason">{reason}</div>
    <a class="btn" href="/evidence/download/{evidence.id}/">
      ⬇ Download to View
    </a>
  </div>
</body>
</html>"""
    return HttpResponse(html, content_type='text/html')


def download_evidence_view(request, evidence_id):
    """
    Forces file download attachment with original filename when user clicks Download.
    """
    evidence = get_object_or_404(UploadedEvidence, id=evidence_id)
    if not evidence.file or not os.path.exists(evidence.file.path):
        return HttpResponse("Document file not found on server", status=404)

    content_type, _ = mimetypes.guess_type(evidence.file.path)
    if not content_type:
        content_type = 'application/octet-stream'

    response = FileResponse(open(evidence.file.path, 'rb'), content_type=content_type, as_attachment=True, filename=evidence.original_filename)
    return response


@csrf_exempt
def api_toggle_verify_evidence(request, evidence_id):
    """
    Allows HOD / Principal to mark an evidence file as Verified / Validated in real-time.
    """
    evidence = get_object_or_404(UploadedEvidence, id=evidence_id)
    if request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8')) if request.body else {}
            if 'verified' in body:
                evidence.is_verified = bool(body['verified'])
            else:
                evidence.is_verified = not evidence.is_verified
            
            if evidence.is_verified:
                evidence.status = 'VERIFIED'
                evidence.rejection_reason = ''
                evidence.reviewed_at = timezone.now()
            else:
                evidence.status = 'PENDING'
            evidence.save()
            return JsonResponse({
                'success': True,
                'evidence_id': evidence.id,
                'is_verified': evidence.is_verified,
                'status': evidence.status,
                'message': 'Verification status updated'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': True, 'evidence_id': evidence.id, 'is_verified': evidence.is_verified, 'status': evidence.status})


@csrf_exempt
def api_reject_evidence(request, evidence_id):
    """
    HOD rejects an uploaded evidence file with a review comment explaining why it was rejected.
    Updates evidence status, creates an AppraisalNotification, and alerts the faculty portal.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    evidence = get_object_or_404(UploadedEvidence, id=evidence_id)
    try:
        body = json.loads(request.body.decode('utf-8')) if request.body else {}
        reason = body.get('reason', '').strip()
        if not reason:
            return JsonResponse({'success': False, 'error': 'A rejection reason is required.'}, status=400)

        evidence.status = 'REJECTED'
        evidence.is_verified = False
        evidence.rejection_reason = reason
        evidence.reviewed_at = timezone.now()
        evidence.save()

        # Update submission status to REVISION_REQUESTED
        submission = evidence.submission
        if not submission and body.get('submission_id'):
            submission = Section1Submission.objects.filter(id=body['submission_id']).first()
            if submission:
                evidence.submission = submission
                evidence.save()
        notif_id = None
        if submission:
            submission.status = 'REVISION_REQUESTED'
            submission.save()

            notif = AppraisalNotification.objects.create(
                submission=submission,
                evidence=evidence,
                component_title=evidence.original_filename,
                component_code=evidence.component_code,
                notification_type='REJECTION',
                message=reason,
                created_by=request.session.get('user_name', 'HOD')
            )
            notif_id = notif.id

        return JsonResponse({
            'success': True,
            'message': 'Document rejected. Notification and review comment sent to Faculty Portal.',
            'evidence_id': evidence.id,
            'status': 'REJECTED',
            'rejection_reason': reason,
            'notification_id': notif_id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_reject_inline_item(request):
    """
    HOD rejects a specific course row or claimed component with a review comment.
    Persists rejection feedback in submission raw_payload, creates an AppraisalNotification,
    and sets submission status to REVISION_REQUESTED so faculty is notified.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        body = json.loads(request.body.decode('utf-8')) if request.body else {}
        sub_id = body.get('submission_id')
        component_title = body.get('component_title', 'Course / Component Evidence')
        component_code = body.get('component_code', 'SEC1_A')
        item_key = body.get('item_key', '')
        file_url = body.get('file_url', '')
        reason = body.get('reason', '').strip()

        if not reason:
            return JsonResponse({'success': False, 'error': 'A review comment explaining the rejection is required.'}, status=400)

        submission = get_object_or_404(Section1Submission, id=sub_id)
        submission.status = 'REVISION_REQUESTED'

        # Persist rejection inside submission raw_payload
        payload = json.loads(submission.raw_payload or '{}')
        if 'rejected_items' not in payload:
            payload['rejected_items'] = {}
        payload['rejected_items'][item_key] = {
            'title': component_title,
            'reason': reason,
            'file_url': file_url,
            'rejected_at': timezone.now().strftime('%d %b %Y, %I:%M %p'),
            'rejected_by': request.session.get('user_name', 'HOD')
        }
        submission.raw_payload = json.dumps(payload)
        submission.save()

        # Check if matching UploadedEvidence exists on this submission
        matching_ev = None
        if file_url:
            clean_filename = os.path.basename(file_url.split('?')[0])
            matching_ev = UploadedEvidence.objects.filter(
                submission=submission, 
                file__icontains=clean_filename
            ).first()
            if matching_ev:
                matching_ev.status = 'REJECTED'
                matching_ev.is_verified = False
                matching_ev.rejection_reason = reason
                matching_ev.reviewed_at = timezone.now()
                matching_ev.save()

        # Create AppraisalNotification for Faculty Portal
        notif = AppraisalNotification.objects.create(
            submission=submission,
            evidence=matching_ev,
            component_title=component_title,
            component_code=component_code,
            notification_type='REJECTION',
            message=reason,
            created_by=request.session.get('user_name', 'HOD')
        )

        return JsonResponse({
            'success': True,
            'message': 'Document rejected. Review feedback will appear as a notification in Faculty Portal.',
            'item_key': item_key,
            'reason': reason,
            'notification_id': notif.id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_dismiss_notification(request, notification_id):
    """
    Faculty marks a review notification as read / acknowledged.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    notif = get_object_or_404(AppraisalNotification, id=notification_id)
    notif.is_read = True
    notif.save()
    return JsonResponse({'success': True, 'notification_id': notif.id})


@csrf_exempt
def api_save_submission(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=405)

    try:
        body = json.loads(request.body.decode('utf-8'))
        payload = body.get('payload', {})
        faculty_name = body.get('faculty_name', 'Faculty Member')
        employee_id = body.get('employee_id', '')
        department = body.get('department', 'Computer Science & Engineering')
        academic_year = body.get('academic_year', '2026-2027')
        status = 'SUBMITTED' if body.get('submit_final') else body.get('status', 'DRAFT')

        result = calculate_complete_pbas(payload)

        sub_id = body.get('submission_id')
        if sub_id:
            submission = Section1Submission.objects.get(id=sub_id)
        else:
            existing = None
            if employee_id:
                existing = Section1Submission.objects.filter(employee_id=employee_id).order_by('-updated_at', '-id').first()
            if not existing and faculty_name:
                existing = Section1Submission.objects.filter(faculty_name=faculty_name).order_by('-updated_at', '-id').first()
            submission = existing if existing else Section1Submission()

        submission.faculty_name = faculty_name
        submission.employee_id = employee_id
        submission.department = department
        submission.academic_year = academic_year
        submission.status = status

        submission.section1_final_score = result['section1']['section_score']
        submission.section2_final_score = result['section2']['section_score']
        submission.section3_final_score = result['section3']['section_score']
        submission.section4_final_score = result['section4']['marks_awarded']
        
        sum_data = result['summary']
        submission.subtotal_130 = sum_data['subtotal_130']
        submission.scaled_80 = sum_data['scaled_80']
        submission.hod_score = sum_data['hod_evaluation']['total']
        submission.principal_score = sum_data['principal_evaluation']['total']
        submission.grand_total_100 = sum_data['grand_total_100']
        submission.performance_grade = sum_data['grade']

        submission.raw_payload = json.dumps(payload)
        submission.calculation_breakdown = json.dumps(result)
        submission.save()

        file_ids = body.get('file_ids') or payload.get('uploaded_file_ids') or []
        if file_ids:
            UploadedEvidence.objects.filter(id__in=file_ids).update(submission=submission)

        return JsonResponse({
            'success': True,
            'message': 'PBAS Submission saved successfully',
            'submission_id': submission.id,
            'status': submission.status,
            'grand_total_100': submission.grand_total_100,
            'grade': submission.performance_grade,
            'result': result
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_hod_submit_review(request):
    """
    HOD completes departmental evaluation and forwards to Principal.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        sub_id = data.get('submission_id')
        submission = get_object_or_404(Section1Submission, id=sub_id)

        # Parse HOD criteria
        hod_data = {
            'discipline_attitude': float(data.get('hod_c1', 3)),
            'academic_planning': float(data.get('hod_c2', 3)),
            'dept_admin_support': float(data.get('hod_c3', 3)),
            'accreditation_fdp': float(data.get('hod_c4', 3)),
            'autonomous_support': float(data.get('hod_c5', 3)),
            'remarks': data.get('hod_remarks', ''),
            'increment_recommended': bool(data.get('increment_recommended', True))
        }

        sec4_score = min(float(data.get('sec4_score', 16)), 20.0)
        submission.section4_final_score = sec4_score

        # Recalculate complete with new HOD data
        raw_payload = json.loads(submission.raw_payload or '{}')
        raw_payload['hod_review'] = hod_data
        result = calculate_complete_pbas(raw_payload)

        submission.hod_score = result['summary']['hod_evaluation']['total']
        submission.scaled_80 = result['summary']['scaled_80']
        submission.grand_total_100 = result['summary']['grand_total_100']
        submission.performance_grade = result['summary']['grade']
        submission.status = 'VERIFIED'
        submission.raw_payload = json.dumps(raw_payload)
        submission.calculation_breakdown = json.dumps(result)
        submission.save()

        return JsonResponse({
            'success': True,
            'message': 'Evaluation saved and forwarded to Principal!',
            'submission_id': submission.id,
            'status': submission.status,
            'hod_score': submission.hod_score,
            'grand_total_100': submission.grand_total_100,
            'grade': submission.performance_grade
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_principal_submit_decision(request):
    """
    Principal completes institutional evaluation and final approval.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        sub_id = data.get('submission_id')
        submission = get_object_or_404(Section1Submission, id=sub_id)

        principal_data = {
            'vision_goal': float(data.get('p_c1', 1)),
            'leadership_mgmt': float(data.get('p_c2', 1)),
            'involvement_admin': float(data.get('p_c3', 1)),
            'research_innovation': float(data.get('p_c4', 1)),
            'overall_discipline': float(data.get('p_c5', 1)),
            'remarks': data.get('principal_remarks', ''),
            'increment_approved': bool(data.get('increment_approved', True))
        }

        raw_payload = json.loads(submission.raw_payload or '{}')
        raw_payload['principal_review'] = principal_data
        result = calculate_complete_pbas(raw_payload)

        submission.principal_score = result['summary']['principal_evaluation']['total']
        submission.grand_total_100 = result['summary']['grand_total_100']
        submission.performance_grade = result['summary']['grade']
        submission.status = 'APPROVED'
        submission.raw_payload = json.dumps(raw_payload)
        submission.calculation_breakdown = json.dumps(result)
        submission.save()

        return JsonResponse({
            'success': True,
            'message': 'Appraisal decision finalized successfully!',
            'submission_id': submission.id,
            'status': submission.status,
            'principal_score': submission.principal_score,
            'grand_total_100': submission.grand_total_100,
            'grade': submission.performance_grade
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==========================================
# PDF & EXPORT VIEWS
# ==========================================
def download_pdf_view(request, submission_id=None):
    """
    Generates and returns the official PDF appraisal report.
    """
    if submission_id:
        sub = get_object_or_404(Section1Submission, id=submission_id)
    else:
        sub = Section1Submission.objects.order_by('-updated_at').first()
        if not sub:
            return HttpResponse("No appraisal submission found to generate PDF.", status=404)

    pdf_content = generate_pbas_pdf(sub)
    safe_name = sub.faculty_name.replace(' ', '_').replace('.', '')
    filename = f"RNSIT_PBAS_{safe_name}_{sub.academic_year}.pdf"

    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def export_json(request, submission_id=None):
    if submission_id:
        sub = get_object_or_404(Section1Submission, id=submission_id)
    else:
        sub = Section1Submission.objects.order_by('-updated_at').first()
        if not sub:
            return JsonResponse({'message': 'No submission found'}, status=404)

    return JsonResponse({
        'submission_id': sub.id,
        'faculty_name': sub.faculty_name,
        'employee_id': sub.employee_id,
        'department': sub.department,
        'academic_year': sub.academic_year,
        'status': sub.status,
        'scores': {
            'section1_score': sub.section1_final_score,
            'section2_score': sub.section2_final_score,
            'section3_score': sub.section3_final_score,
            'section4_score': sub.section4_final_score,
            'subtotal_130': sub.subtotal_130,
            'scaled_80': sub.scaled_80,
            'hod_score': sub.hod_score,
            'principal_score': sub.principal_score,
            'grand_total_100': sub.grand_total_100,
            'performance_grade': sub.performance_grade
        },
        'payload': json.loads(sub.raw_payload or '{}'),
        'calculation_breakdown': json.loads(sub.calculation_breakdown or '{}')
    })
