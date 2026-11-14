from datetime import date, timedelta
from django.utils import timezone
from onboarding_offboarding.models import Employee
from leave_management.models import LeaveApplication

def seed_sample_leaves():
    if LeaveApplication.objects.exists():
        return

    faculty_ramesh = Employee.objects.filter(employee_id='RNSIT-CS-1042').first()
    faculty_uma = Employee.objects.filter(employee_id='RNSIT-ECE-0101').first()
    faculty_ganga = Employee.objects.filter(employee_id='RNSIT-AI-0520').first()
    faculty_vyasa = Employee.objects.filter(employee_id='RNSIT-ECE-0615').first()

    today = date.today()

    if faculty_ramesh:
        # Case 1: Finally approved CL (3 days)
        app1 = LeaveApplication.objects.create(
            employee=faculty_ramesh,
            leave_type='CL',
            start_date=today - timedelta(days=20),
            end_date=today - timedelta(days=18),
            total_days=3.0,
            reason='Family emergency and personal commitments.',
            substitute_faculty='Dr. Shruthi U (Covering AI lab session)',
            hod_status='APPROVED',
            hod_remarks='Class handover verified with Dr. Shruthi U. Approved.',
            hod_action_at=timezone.now() - timedelta(days=21),
            principal_status='APPROVED',
            principal_remarks='Approved as recommended.',
            principal_action_at=timezone.now() - timedelta(days=20),
            overall_status='APPROVED',
            is_balance_deducted=True
        )

        # Case 2: Pending HoD review (2 days EL)
        LeaveApplication.objects.create(
            employee=faculty_ramesh,
            leave_type='EL',
            start_date=today + timedelta(days=5),
            end_date=today + timedelta(days=6),
            total_days=2.0,
            reason='Attending International Conference on Deep Learning (IEEE ICDE 2026).',
            substitute_faculty='Ms. Ganga M S',
            hod_status='PENDING',
            overall_status='PENDING_HOD',
            is_balance_deducted=False
        )

    if faculty_ganga:
        # Case 3: Recommended by HoD, Pending Principal review
        LeaveApplication.objects.create(
            employee=faculty_ganga,
            leave_type='CL',
            start_date=today + timedelta(days=2),
            end_date=today + timedelta(days=3),
            total_days=2.0,
            reason='Attending VTU Academic Workshop at Belagavi campus.',
            substitute_faculty='Dr. Swathi Darla',
            hod_status='APPROVED',
            hod_remarks='Recommended. Syllabus schedule maintained.',
            hod_action_at=timezone.now() - timedelta(hours=6),
            principal_status='PENDING',
            overall_status='PENDING_PRINCIPAL',
            is_balance_deducted=False
        )

    if faculty_vyasa:
        # Case 4: Rejected by HoD (Slide 4: HoD rejection resubmit application will enable to Employee)
        LeaveApplication.objects.create(
            employee=faculty_vyasa,
            leave_type='CL',
            start_date=today - timedelta(days=5),
            end_date=today - timedelta(days=4),
            total_days=2.0,
            reason='Personal travel during mid-term test evaluation week.',
            substitute_faculty='Not specified',
            hod_status='REJECTED',
            hod_remarks='Cannot approve leave during mid-term exam grading window. Please adjust dates or provide alternative examiner arrangement.',
            hod_action_at=timezone.now() - timedelta(days=6),
            overall_status='HOD_REJECTED',
            is_balance_deducted=False
        )

    print("Successfully seeded sample Leave Management applications.")
