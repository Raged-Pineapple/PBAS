from onboarding_offboarding.models import Employee
from salary_payroll.models import SalarySlip

def seed_sample_salaries():
    if SalarySlip.objects.exists():
        return

    faculty_list = Employee.objects.filter(status='ACTIVE')
    for emp in faculty_list:
        basic = emp.basic_pay
        calc = SalarySlip.calculate_salary(basic=basic, da_pct=50.0, hra_pct=20.0, transport=3600.0, lop_days=0.0)

        # For Ramesh Kumar, match the exact numbers from Slide 7
        if emp.employee_id == 'RNSIT-CS-1042':
            calc['employee_pf'] = 6924.0
            calc['professional_tax'] = 200.0
            calc['tds'] = 2000.0
            calc['total_deductions'] = 9124.0
            calc['net_salary'] = 92566.0

        SalarySlip.objects.create(
            employee=emp,
            pay_month='November 2026',
            pay_period_days=30,
            paid_days=30.0,
            basic_pay=calc['basic_pay'],
            da_percentage=50.0,
            da_amount=calc['da_amount'],
            hra_percentage=20.0,
            hra_amount=calc['hra_amount'],
            transport_allowance=calc['transport_allowance'],
            special_allowance=calc['special_allowance'],
            lop_days=calc['lop_days'],
            lop_deduction=calc['lop_deduction'],
            gross_earnings=calc['gross_earnings'],
            employee_pf=calc['employee_pf'],
            professional_tax=calc['professional_tax'],
            tds=calc['tds'],
            total_deductions=calc['total_deductions'],
            net_salary=calc['net_salary'],
            bank_name='Canara Bank (RNSIT Campus Branch)',
            account_number=f"08451010{emp.id:05d}",
            pan_number=f"ABCDE{emp.id:04d}F",
            pf_uan=f"1009823{emp.id:05d}"
        )

    print("Successfully seeded monthly Salary Slips for faculty members.")
