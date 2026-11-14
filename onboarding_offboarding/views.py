import json
from datetime import date, datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Employee, OnboardingChecklist, OnboardingDocument, OffboardingRequest

def onboarding_hub_view(request):
    """
    Main Hub for Onboarding & Offboarding (Entry to Exit Lifecycle)
    Consistent UI with RNSIT PBAS.
    """
    if not request.session.get('is_authenticated'):
        return redirect('/login/')
    selected_institution = request.GET.get('institution', 'All')
    selected_dept = request.GET.get('department', 'All')
    selected_status = request.GET.get('status', 'All')

    employees = Employee.objects.all().order_by('-created_at')

    if selected_institution != 'All':
        employees = employees.filter(institution=selected_institution)
    if selected_dept != 'All':
        employees = employees.filter(department=selected_dept)
    if selected_status != 'All':
        employees = employees.filter(status=selected_status)

    # Statistics
    total_count = Employee.objects.count()
    active_count = Employee.objects.filter(status='ACTIVE').count()
    onboarding_count = Employee.objects.filter(status='ONBOARDING').count()
    exit_count = Employee.objects.filter(status__in=['RESIGNED', 'NOTICE_PERIOD', 'RELIEVED']).count()
    offboarding_requests = OffboardingRequest.objects.select_related('employee').order_by('-created_at')

    departments = [
        'Computer Science & Engineering',
        'Electronics & Communication Engineering',
        'CSE (AI&ML)',
        'CSE (Cyber Security)',
        'Information Science & Engineering',
        'Mechanical Engineering',
    ]

    institutions = [
        'RNS Institute of Technology',
        'RNS PU College',
        'RNS First Grade College',
        'RNS School',
    ]

    context = {
        'employees': employees,
        'total_count': total_count,
        'active_count': active_count,
        'onboarding_count': onboarding_count,
        'exit_count': exit_count,
        'offboarding_requests': offboarding_requests,
        'departments': departments,
        'institutions': institutions,
        'selected_institution': selected_institution,
        'selected_dept': selected_dept,
        'selected_status': selected_status,
        'user_role': request.session.get('user_role', 'HR_ADMIN'),
        'user_name': request.session.get('user_name', 'HR Admin Office'),
    }
    return render(request, 'onboarding_offboarding/hub.html', context)


def employee_detail_view(request, employee_id):
    """
    Full view of an individual faculty member's profile and 6-step onboarding checklist.
    """
    employee = get_object_or_404(Employee, employee_id=employee_id)
    checklist, _ = OnboardingChecklist.objects.get_or_create(employee=employee)
    documents = employee.documents.all().order_by('id')
    offboarding = getattr(employee, 'offboarding_request', None)

    context = {
        'employee': employee,
        'checklist': checklist,
        'documents': documents,
        'offboarding': offboarding,
        'user_role': request.session.get('user_role', 'HR_ADMIN'),
        'user_name': request.session.get('user_name', 'HR Admin Office'),
    }
    return render(request, 'onboarding_offboarding/employee_detail.html', context)


def offboarding_detail_view(request, employee_id):
    """
    Interactive 8-Step Offboarding & 6 Department Clearances Tracker.
    """
    employee = get_object_or_404(Employee, employee_id=employee_id)
    offboarding, created = OffboardingRequest.objects.get_or_create(
        employee=employee,
        defaults={
            'resignation_date': timezone.now().date(),
            'proposed_last_day': timezone.now().date() + timedelta(days=30),
            'actual_last_day': timezone.now().date() + timedelta(days=30),
            'reason': 'Career transition / Academic advancement',
            'handover_plan': 'Courses and laboratory records handed over to department lead.',
        }
    )

    context = {
        'employee': employee,
        'offboarding': offboarding,
        'user_role': request.session.get('user_role', 'HR_ADMIN'),
        'user_name': request.session.get('user_name', 'HR Admin Office'),
    }
    return render(request, 'onboarding_offboarding/offboarding_detail.html', context)


def relieving_letter_view(request, employee_id):
    """
    Official RNSIT Relieving Letter printable format.
    """
    employee = get_object_or_404(Employee, employee_id=employee_id)
    offboarding = getattr(employee, 'offboarding_request', None)
    if not offboarding:
        return HttpResponse("No offboarding record found for this employee.", status=404)

    context = {
        'employee': employee,
        'offboarding': offboarding,
        'today': timezone.now().date(),
    }
    return render(request, 'onboarding_offboarding/relieving_letter.html', context)


def experience_cert_view(request, employee_id):
    """
    Official RNSIT Experience Certificate printable format.
    """
    employee = get_object_or_404(Employee, employee_id=employee_id)
    offboarding = getattr(employee, 'offboarding_request', None)
    if not offboarding:
        return HttpResponse("No offboarding record found for this employee.", status=404)

    # Compute tenure
    end_date = offboarding.actual_last_day if offboarding.actual_last_day else timezone.now().date()
    tenure_years = round((end_date - employee.date_of_joining).days / 365.25, 1)

    context = {
        'employee': employee,
        'offboarding': offboarding,
        'tenure_years': tenure_years,
        'today': timezone.now().date(),
    }
    return render(request, 'onboarding_offboarding/experience_certificate.html', context)


@csrf_exempt
def api_create_onboarding_employee(request):
    """
    API endpoint to register new faculty through the 6-Step Onboarding process.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        dept = data.get('department', 'Computer Science & Engineering')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip()

        if not first_name or not email:
            return JsonResponse({'success': False, 'error': 'First name and email are mandatory.'})

        # Generate unique employee ID with department code
        dept_prefix_map = {
            'Computer Science & Engineering': 'CS',
            'Electronics & Communication Engineering': 'EC',
            'CSE (AI&ML)': 'AI',
            'CSE (Cyber Security)': 'CYS',
            'Information Science & Engineering': 'IS',
            'Mechanical Engineering': 'ME',
        }
        code = dept_prefix_map.get(dept, 'GEN')
        count = Employee.objects.filter(department=dept).count() + 1
        emp_id = f"RNSIT-{code}-{count:04d}"

        # Ensure unique
        while Employee.objects.filter(employee_id=emp_id).exists():
            count += 1
            emp_id = f"RNSIT-{code}-{count:04d}"

        employee = Employee.objects.create(
            employee_id=emp_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=data.get('phone', '+91 99000 00000'),
            gender=data.get('gender', 'FEMALE'),
            institution=data.get('institution', 'RNS Institute of Technology'),
            department=dept,
            designation=data.get('designation', 'Assistant Professor'),
            reporting_authority=data.get('reporting_authority', 'Dr. Kiran B. R. (HOD - CSE)'),
            date_of_joining=data.get('date_of_joining', timezone.now().date()),
            highest_qualification=data.get('highest_qualification', 'Ph.D.'),
            specialization=data.get('specialization', 'Artificial Intelligence'),
            university=data.get('university', 'VTU Belagavi'),
            teaching_experience_years=float(data.get('teaching_exp', 3.0)),
            industry_experience_years=float(data.get('industry_exp', 1.0)),
            basic_pay=float(data.get('basic_pay', 57700.0)),
            status='ONBOARDING'
        )

        # Create Onboarding Checklist
        checklist = OnboardingChecklist.objects.create(
            employee=employee,
            appointment_order_no=f"RNSIT/APPT/2026/{employee.id:03d}",
            step1_appointment_order_verified=True,
            step1_joining_report_received=True,
            step2_personal_details_captured=True,
            step2_academic_credentials_captured=True,
            step3_experience_verified=True,
            step3_eligibility_checked=True,
            step4_documents_uploaded=True,
            step4_hr_doc_check_completed=False,
            step5_employee_id_generated=True,
            step5_hr_record_activated=False,
            step6_dept_role_allocated=True,
            step6_reporting_assigned=True,
            verification_notes='Initial 6-step entry submission received. Pending final HR document audit.'
        )

        return JsonResponse({
            'success': True,
            'employee_id': employee.employee_id,
            'name': employee.full_name,
            'message': f"Faculty {employee.full_name} enrolled successfully with Employee Code {employee.employee_id}!"
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_toggle_clearance(request, employee_id):
    """
    AJAX endpoint to update individual department clearances (Library, Lab, IT, Stores, Assets, Accounts).
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        employee = get_object_or_404(Employee, employee_id=employee_id)
        offboarding = get_object_or_404(OffboardingRequest, employee=employee)
        data = json.loads(request.body.decode('utf-8'))
        field = data.get('field') # e.g. 'library_cleared'
        val = data.get('value', True)

        if hasattr(offboarding, field):
            setattr(offboarding, field, val)
            offboarding.save()
            return JsonResponse({
                'success': True,
                'field': field,
                'value': val,
                'clearances_count': offboarding.clearances_count
            })
        return JsonResponse({'success': False, 'error': 'Invalid clearance field'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_finalize_exit(request, employee_id):
    """
    Complete exit, update status to RELIEVED, and seal documents.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        employee = get_object_or_404(Employee, employee_id=employee_id)
        offboarding = get_object_or_404(OffboardingRequest, employee=employee)

        offboarding.status = 'COMPLETED'
        offboarding.is_exit_completed = True
        offboarding.hr_verified = True
        offboarding.actual_last_day = timezone.now().date()
        offboarding.save()

        employee.status = 'RELIEVED'
        employee.save()

        return JsonResponse({
            'success': True,
            'message': f"Faculty {employee.full_name} ({employee.employee_id}) exit workflow finalized. Exit documents generated!"
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
