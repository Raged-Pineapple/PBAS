from django.db import models
from django.utils import timezone
from onboarding_offboarding.models import Employee

class SalarySlip(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_slips')
    pay_month = models.CharField(max_length=50, default='November 2026')
    pay_period_days = models.IntegerField(default=30)
    paid_days = models.FloatField(default=30.0)

    # Earnings (Slide 6 & 7)
    basic_pay = models.FloatField(default=57700.0)
    da_percentage = models.FloatField(default=50.0)
    da_amount = models.FloatField(default=28850.0)
    hra_percentage = models.FloatField(default=20.0)
    hra_amount = models.FloatField(default=11540.0)
    transport_allowance = models.FloatField(default=3600.0)
    special_allowance = models.FloatField(default=0.0)

    # LOP Linkage (Slide 6: Gross earnings = Basic + DA + HRA + other - LOP)
    lop_days = models.FloatField(default=0.0)
    lop_deduction = models.FloatField(default=0.0)
    gross_earnings = models.FloatField(default=101690.0)

    # Deductions (Slide 7)
    employee_pf = models.FloatField(default=6924.0, help_text="Provident Fund (12% of basic)")
    professional_tax = models.FloatField(default=200.0)
    tds = models.FloatField(default=2000.0, help_text="Tax Deducted at Source")
    other_deductions = models.FloatField(default=0.0)
    total_deductions = models.FloatField(default=9124.0)

    # Net Salary (Slide 7: ₹92,566)
    net_salary = models.FloatField(default=92566.0)

    # Banking & Statutory details
    bank_name = models.CharField(max_length=100, default='Canara Bank (RNSIT Campus Branch)')
    account_number = models.CharField(max_length=50, default='0845101089234')
    pan_number = models.CharField(max_length=20, default='ABCDE1234F')
    pf_uan = models.CharField(max_length=50, default='100982347891')

    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.employee_id} - {self.pay_month} (Net: ₹{self.net_salary:,.2f})"

    @staticmethod
    def calculate_salary(basic, da_pct=50.0, hra_pct=20.0, transport=3600.0, special=0.0, lop_days=0.0, pt=200.0, tds=2000.0):
        """
        Pure calculation method implementing Slides 6 & 7.
        """
        basic = float(basic)
        da_amount = round(basic * (da_pct / 100.0), 2)
        hra_amount = round(basic * (hra_pct / 100.0), 2)
        transport = float(transport)
        special = float(special)

        # LOP Deduction: Daily rate = basic / 30
        daily_rate = basic / 30.0
        lop_deduction = round(daily_rate * float(lop_days), 2)

        gross_earnings = round((basic + da_amount + hra_amount + transport + special) - lop_deduction, 2)

        # PF (12% of basic up to standard cap, or min 6924)
        pf = round(basic * 0.12, 2)
        total_deductions = round(pf + pt + tds, 2)
        net_salary = round(gross_earnings - total_deductions, 2)

        return {
            'basic_pay': basic,
            'da_amount': da_amount,
            'hra_amount': hra_amount,
            'transport_allowance': transport,
            'special_allowance': special,
            'lop_days': float(lop_days),
            'lop_deduction': lop_deduction,
            'gross_earnings': gross_earnings,
            'employee_pf': pf,
            'professional_tax': pt,
            'tds': tds,
            'total_deductions': total_deductions,
            'net_salary': net_salary
        }
