import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from onboarding_offboarding.models import Employee
from .models import SalarySlip

def salary_hub_view(request):
    """
    Salary Calculator & Monthly Payroll Management Hub
    Implements Slides 6 & 7 of RNSIT Faculty Hackathon 2026 Problem Statement.
    """
    if not request.session.get('is_authenticated'):
        return redirect('/login/')
    user_role = request.session.get('user_role', 'FACULTY')
    emp_id = request.session.get('employee_id', 'RNSIT-CS-1042')

    current_employee = Employee.objects.filter(employee_id=emp_id).first()
    if not current_employee:
        current_employee = Employee.objects.first()

    slips = SalarySlip.objects.select_related('employee').order_by('-created_at')

    # Total payroll stats
    total_payroll = sum(s.net_salary for s in slips)
    total_deductions_sum = sum(s.total_deductions for s in slips)
    total_gross = sum(s.gross_earnings for s in slips)

    context = {
        'current_employee': current_employee,
        'slips': slips,
        'total_payroll': total_payroll,
        'total_gross': total_gross,
        'total_deductions_sum': total_deductions_sum,
        'user_role': user_role,
        'user_name': request.session.get('user_name', current_employee.full_name),
    }
    return render(request, 'salary_payroll/hub.html', context)


def payslip_detail_view(request, slip_id):
    """
    Official RNSIT Monthly Salary Slip printable format.
    Directly fulfills Slide 7: "The salary slip will be generated in employee login"
    """
    slip = get_object_or_404(SalarySlip, id=slip_id)

    # Convert net salary to words
    net_int = int(slip.net_salary)
    net_in_words = number_to_inr_words(net_int)

    context = {
        'slip': slip,
        'employee': slip.employee,
        'net_in_words': net_in_words,
    }
    return render(request, 'salary_payroll/payslip.html', context)


def employee_latest_payslip_view(request, employee_id):
    """
    Shortcut for employee login to view their latest monthly salary slip.
    """
    employee = get_object_or_404(Employee, employee_id=employee_id)
    slip = SalarySlip.objects.filter(employee=employee).order_by('-created_at').first()
    if not slip:
        return HttpResponse("No pay slip generated for this employee yet.", status=404)
    return redirect('payslip_detail', slip_id=slip.id)


@csrf_exempt
def api_calculate_salary(request):
    """
    REST API for real-time monthly salary calculation (Slide 6 & 7).
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        basic = float(data.get('basic_pay', 57700.0))
        da_pct = float(data.get('da_percentage', 50.0))
        hra_pct = float(data.get('hra_percentage', 20.0))
        transport = float(data.get('transport_allowance', 3600.0))
        special = float(data.get('special_allowance', 0.0))
        lop_days = float(data.get('lop_days', 0.0))
        pt = float(data.get('professional_tax', 200.0))
        tds = float(data.get('tds', 2000.0))

        result = SalarySlip.calculate_salary(
            basic=basic, da_pct=da_pct, hra_pct=hra_pct,
            transport=transport, special=special, lop_days=lop_days,
            pt=pt, tds=tds
        )
        return JsonResponse({'success': True, 'calculation': result})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def number_to_inr_words(num):
    """Simple Indian numbering word converter."""
    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
             "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

    if num == 0:
        return "Zero"

    def two_digit(n):
        if n < 20:
            return units[n]
        return tens[n // 10] + (" " + units[n % 10] if n % 10 else "")

    parts = []
    # Crores
    crores = num // 10000000
    if crores:
        parts.append(two_digit(crores) + " Crore")
        num %= 10000000
    # Lakhs
    lakhs = num // 100000
    if lakhs:
        parts.append(two_digit(lakhs) + " Lakh")
        num %= 100000
    # Thousands
    thousands = num // 1000
    if thousands:
        parts.append(two_digit(thousands) + " Thousand")
        num %= 1000
    # Hundreds
    hundreds = num // 100
    if hundreds:
        parts.append(units[hundreds] + " Hundred")
        num %= 100
    # Remainder
    if num:
        parts.append(two_digit(num))

    return "Rupees " + " ".join(parts) + " Only"
