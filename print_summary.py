import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pbas_portal.settings')
django.setup()

from onboarding_offboarding.models import Employee
from leave_management.models import LeaveApplication
from salary_payroll.models import SalarySlip
from section1.models import Section1Submission

print("=== RNS HR SYSTEM E2E — DATABASE SUMMARY ===")
print("  Employees:        ", Employee.objects.count(), "records")
print("  Active Faculty:   ", Employee.objects.filter(status="ACTIVE").count())
print("  Onboarding:       ", Employee.objects.filter(status="ONBOARDING").count())
print("  Relieved:         ", Employee.objects.filter(status="RELIEVED").count())
print("  Leave Applications:", LeaveApplication.objects.count(), "records")
print("  Salary Slips:     ", SalarySlip.objects.count(), "records")
print("  PBAS Submissions: ", Section1Submission.objects.count(), "records")

total_net = sum(s.net_salary for s in SalarySlip.objects.all())
print("  Total Nov Payroll: Rs {:,.2f}".format(total_net))

print("\n=== PORTAL ROUTES ===")
print("  Master Dashboard:  http://127.0.0.1:8000/")
print("  Portal 1 (E2E):    http://127.0.0.1:8000/onboarding-offboarding/")
print("  Portal 2 (Leave):  http://127.0.0.1:8000/leave/")
print("  Portal 3 (Salary): http://127.0.0.1:8000/salary/")
print("  Portal 4 (PBAS):   http://127.0.0.1:8000/pbas/")
print("\n  Relieving Letter:  http://127.0.0.1:8000/onboarding-offboarding/document/relieving/RNSIT-EC-0899/")
print("  Exp Certificate:   http://127.0.0.1:8000/onboarding-offboarding/document/experience/RNSIT-EC-0899/")
print("  Pay Slip (Ramesh): http://127.0.0.1:8000/salary/payslip/employee/RNSIT-CS-1042/")
