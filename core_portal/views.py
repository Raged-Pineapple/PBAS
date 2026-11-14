import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from onboarding_offboarding.models import Employee, OnboardingChecklist, OffboardingRequest
from leave_management.models import LeaveApplication
from salary_payroll.models import SalarySlip
from section1.models import Section1Submission

def master_dashboard_view(request):
    """
    Unified Master Web Portal Hub for RNS HR System Entry - Exit (E2E).
    TechTrinity — RNSIT Faculty Hackathon 2026.
    """
    # Auth guard — redirect to unified login if not authenticated
    if not request.session.get('is_authenticated'):
        return redirect('/login/')
    active_role = request.session.get('user_role', 'FACULTY')
    active_inst = request.session.get('institution', 'RNS Institute of Technology')

    # Team members from presentation (Slide 1)
    team_members = [
        {'name': 'Dr. Uma S V', 'role': 'Professor & Dean First Year', 'dept': 'ECE'},
        {'name': 'Dr. Leena Chandrashekar', 'role': 'Associate Professor', 'dept': 'ECE'},
        {'name': 'Dr. Shruthi U', 'role': 'Associate Professor', 'dept': 'CSE (AI&ML)'},
        {'name': 'Dr. Swathi Darla', 'role': 'Associate Professor', 'dept': 'CSE (Cyber Security)'},
        {'name': 'Ms. Ganga M S', 'role': 'Assistant Professor', 'dept': 'CSE (AI&ML)'},
        {'name': 'Mr. Vyasaraj T', 'role': 'Assistant Professor', 'dept': 'ECE'},
    ]

    # Metrics across all 4 portals
    total_faculty = Employee.objects.count()
    active_faculty = Employee.objects.filter(status='ACTIVE').count()
    onboarding_faculty = Employee.objects.filter(status='ONBOARDING').count()
    exit_faculty = Employee.objects.filter(status__in=['RESIGNED', 'NOTICE_PERIOD', 'RELIEVED']).count()

    pending_leaves = LeaveApplication.objects.filter(overall_status__in=['PENDING_HOD', 'PENDING_PRINCIPAL']).count()
    total_approved_leaves = LeaveApplication.objects.filter(overall_status='APPROVED').count()

    total_payroll_val = sum(s.net_salary for s in SalarySlip.objects.all())
    pbas_submissions_count = Section1Submission.objects.count()

    # Active employee for current session demo
    current_emp_id = request.session.get('employee_id', 'RNSIT-CS-1042')
    current_employee = Employee.objects.filter(employee_id=current_emp_id).first() or Employee.objects.first()

    institutions = [
        'RNS Institute of Technology',
        'RNS PU College',
        'RNS First Grade College',
        'RNS School',
    ]

    roles = [
        {'code': 'FACULTY', 'name': 'Faculty Member', 'icon': 'fa-chalkboard-user'},
        {'code': 'HOD', 'name': 'Head of Department (HoD)', 'icon': 'fa-user-tie'},
        {'code': 'PRINCIPAL', 'name': 'Principal / Director', 'icon': 'fa-building-columns'},
        {'code': 'HR_ADMIN', 'name': 'HR & Admin Staff', 'icon': 'fa-id-card-clip'},
        {'code': 'ACCOUNTS', 'name': 'Finance & Accounts', 'icon': 'fa-calculator'},
        {'code': 'MANAGEMENT', 'name': 'Governing Body / Trust', 'icon': 'fa-crown'},
        {'code': 'IQAC', 'name': 'IQAC Quality Cell', 'icon': 'fa-award'},
    ]

    # All employees for the master snapshot table
    all_employees = Employee.objects.filter(status__in=['ACTIVE', 'ONBOARDING']).order_by('department', 'first_name')

    # Build enriched employee list with latest salary
    employee_rows = []
    for emp in all_employees:
        latest_slip = SalarySlip.objects.filter(employee=emp).order_by('-pay_month').first()
        employee_rows.append({
            'emp': emp,
            'net_salary': latest_slip.net_salary if latest_slip else emp.basic_pay,
            'has_slip': latest_slip is not None,
        })

    user_name = request.session.get('user_name', current_employee.full_name if current_employee else 'Faculty Member')

    context = {
        'team_members': team_members,
        'active_role': active_role,
        'active_inst': active_inst,
        'institutions': institutions,
        'roles': roles,
        'current_employee': current_employee,
        'user_name': user_name,
        'total_faculty': total_faculty,
        'active_faculty': active_faculty,
        'onboarding_faculty': onboarding_faculty,
        'exit_faculty': exit_faculty,
        'pending_leaves': pending_leaves,
        'total_approved_leaves': total_approved_leaves,
        'total_payroll_val': total_payroll_val,
        'pbas_submissions_count': pbas_submissions_count,
        'employee_rows': employee_rows,
    }
    return render(request, 'core_portal/dashboard.html', context)


@csrf_exempt
def api_quick_switch(request):
    """
    AJAX endpoint for instant role or institution switching during live demonstrations.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        if 'role' in data:
            request.session['user_role'] = data['role']
        if 'institution' in data:
            request.session['institution'] = data['institution']
        if 'employee_id' in data:
            request.session['employee_id'] = data['employee_id']
            emp = Employee.objects.filter(employee_id=data['employee_id']).first()
            if emp:
                request.session['user_name'] = emp.full_name
                request.session['department'] = emp.department

        return JsonResponse({'success': True, 'role': request.session.get('user_role')})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
