import json
from datetime import date, datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from onboarding_offboarding.models import Employee
from .models import LeaveApplication

def leave_portal_view(request):
    """
    Unified Faculty & Staff Leave Management Portal
    Implements Slide 4 & 5 of RNSIT Faculty Hackathon 2026 Problem Statement.
    """
    if not request.session.get('is_authenticated'):
        return redirect('/login/')
    user_role = request.session.get('user_role', 'FACULTY')
    username = request.session.get('username', 'faculty')
    emp_id = request.session.get('employee_id', 'RNSIT-CS-1042')

    # Fetch active faculty
    current_employee = Employee.objects.filter(employee_id=emp_id).first()
    if not current_employee:
        current_employee = Employee.objects.first()

    all_employees = Employee.objects.filter(status='ACTIVE').order_by('department', 'first_name')

    # Filtered applications based on role
    if user_role == 'FACULTY':
        applications = LeaveApplication.objects.filter(employee=current_employee).order_by('-applied_at')
        pending_approvals = []
    elif user_role == 'HOD':
        applications = LeaveApplication.objects.all().order_by('-applied_at')
        pending_approvals = LeaveApplication.objects.filter(overall_status='PENDING_HOD').order_by('-applied_at')
    elif user_role == 'PRINCIPAL':
        applications = LeaveApplication.objects.all().order_by('-applied_at')
        pending_approvals = LeaveApplication.objects.filter(overall_status='PENDING_PRINCIPAL').order_by('-applied_at')
    else: # HR_ADMIN / ACCOUNTS / MANAGEMENT
        applications = LeaveApplication.objects.all().order_by('-applied_at')
        pending_approvals = LeaveApplication.objects.filter(overall_status__in=['PENDING_HOD', 'PENDING_PRINCIPAL']).order_by('-applied_at')

    # Leave balance summary
    cl_allotted = current_employee.cl_allotted
    cl_available = current_employee.cl_available
    el_allotted = current_employee.el_allotted
    el_available = current_employee.el_available
    ml_allotted = current_employee.ml_allotted
    ml_available = current_employee.ml_available

    context = {
        'current_employee': current_employee,
        'all_employees': all_employees,
        'applications': applications,
        'pending_approvals': pending_approvals,
        'cl_allotted': cl_allotted,
        'cl_available': cl_available,
        'el_allotted': el_allotted,
        'el_available': el_available,
        'ml_allotted': ml_allotted,
        'ml_available': ml_available,
        'user_role': user_role,
        'user_name': request.session.get('user_name', current_employee.full_name),
    }
    return render(request, 'leave_management/portal.html', context)


@csrf_exempt
def api_apply_leave(request):
    """
    Employee submits leave application.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        emp_id = data.get('employee_id')
        employee = get_object_or_404(Employee, employee_id=emp_id)

        leave_type = data.get('leave_type', 'CL')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        reason = data.get('reason', '').strip()
        substitute = data.get('substitute_faculty', '').strip()

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        total_days = max(1.0, float((end_date - start_date).days + 1))

        # Check balance limit warning
        available = getattr(employee, f"{leave_type.lower()}_available", 0.0)
        is_excess = total_days > available

        app = LeaveApplication.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            reason=reason,
            substitute_faculty=substitute,
            overall_status='PENDING_HOD',
            is_balance_deducted=False,
            requires_principal_approval=True
        )

        msg = f"Leave application submitted for {total_days} days ({leave_type}). Forwarded to HoD for Step 2 Review."
        if is_excess:
            msg += f" (Note: Requested days exceed current available balance of {available}. Excess will be treated as LOP on final approval)."

        return JsonResponse({
            'success': True,
            'application_id': app.id,
            'message': msg
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_hod_action(request, app_id):
    """
    Step 2: HoD Approve/Reject.
    Rejection allows employee to resubmit. Approval forwards to Principal.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        app = get_object_or_404(LeaveApplication, id=app_id)
        data = json.loads(request.body.decode('utf-8'))
        action = data.get('action') # 'APPROVE' or 'REJECT'
        remarks = data.get('remarks', '').strip()

        app.hod_remarks = remarks
        app.hod_action_at = timezone.now()

        if action == 'APPROVE':
            app.hod_status = 'APPROVED'
            app.overall_status = 'PENDING_PRINCIPAL'
            app.save()
            return JsonResponse({
                'success': True,
                'message': f"HoD approved leave for {app.employee.full_name}. Forwarded to Principal for Step 3 Final Decision."
            })
        else:
            app.hod_status = 'REJECTED'
            app.overall_status = 'HOD_REJECTED'
            app.save()
            return JsonResponse({
                'success': True,
                'message': f"HoD rejected leave request. Faculty has been notified and can modify/resubmit."
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_principal_action(request, app_id):
    """
    Step 3 & 4: Principal Final Decision.
    Final approval triggers official balance deduction and HR notification!
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        app = get_object_or_404(LeaveApplication, id=app_id)
        data = json.loads(request.body.decode('utf-8'))
        action = data.get('action') # 'APPROVE' or 'REJECT'
        remarks = data.get('remarks', '').strip()

        app.principal_remarks = remarks
        app.principal_action_at = timezone.now()

        if action == 'APPROVE':
            app.principal_status = 'APPROVED'
            app.trigger_final_approval() # Deducts from official balance!
            return JsonResponse({
                'success': True,
                'message': f"Principal approved leave application. Official leave balance updated and HR notified!"
            })
        else:
            app.principal_status = 'REJECTED'
            app.overall_status = 'PRINCIPAL_REJECTED'
            app.save()
            return JsonResponse({
                'success': True,
                'message': f"Principal rejected leave application. Balance remains intact."
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
