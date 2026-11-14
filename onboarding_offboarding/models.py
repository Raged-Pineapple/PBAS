from django.db import models
from django.utils import timezone

class Employee(models.Model):
    INSTITUTION_CHOICES = [
        ('RNS Institute of Technology', 'RNS Institute of Technology (RNSIT)'),
        ('RNS PU College', 'RNS PU College'),
        ('RNS First Grade College', 'RNS First Grade College'),
        ('RNS School', 'RNS International School'),
    ]

    STATUS_CHOICES = [
        ('ONBOARDING', 'In Onboarding Process'),
        ('ACTIVE', 'Active Faculty Member'),
        ('RESIGNED', 'Resignation Submitted'),
        ('NOTICE_PERIOD', 'Serving Notice Period'),
        ('RELIEVED', 'Relieved / Exited'),
    ]

    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    ]

    # Unique Employee ID (e.g., RNSIT-CS-1042)
    employee_id = models.CharField(max_length=50, unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='FEMALE')
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, default='')

    # Academic & Organizational Info
    institution = models.CharField(max_length=100, choices=INSTITUTION_CHOICES, default='RNS Institute of Technology')
    department = models.CharField(max_length=100, default='Computer Science & Engineering')
    designation = models.CharField(max_length=100, default='Assistant Professor')
    reporting_authority = models.CharField(max_length=150, default='Dr. Kiran B. R. (HOD - CSE)')
    date_of_joining = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')

    # Qualifications & Experience
    highest_qualification = models.CharField(max_length=100, default='Ph.D.')
    specialization = models.CharField(max_length=150, default='Artificial Intelligence & Machine Learning')
    university = models.CharField(max_length=150, default='Visvesvaraya Technological University (VTU)')
    year_of_passing = models.IntegerField(default=2021)
    teaching_experience_years = models.FloatField(default=6.5)
    industry_experience_years = models.FloatField(default=2.0)
    research_experience_years = models.FloatField(default=4.0)

    # Baseline Salary Parameters (Linked to Salary Portal)
    basic_pay = models.FloatField(default=57700.0)
    da_percentage = models.FloatField(default=50.0)
    hra_percentage = models.FloatField(default=20.0)
    transport_allowance = models.FloatField(default=3600.0)

    # Baseline Leave Quotas (Linked to Leave Portal)
    cl_allotted = models.FloatField(default=12.0)
    cl_used = models.FloatField(default=3.0)
    el_allotted = models.FloatField(default=15.0)
    el_used = models.FloatField(default=5.0)
    ml_allotted = models.FloatField(default=10.0)
    ml_used = models.FloatField(default=2.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee_id} - {self.first_name} {self.last_name} ({self.designation}, {self.department})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def cl_available(self):
        return max(0.0, self.cl_allotted - self.cl_used)

    @property
    def el_available(self):
        return max(0.0, self.el_allotted - self.el_used)

    @property
    def ml_available(self):
        return max(0.0, self.ml_allotted - self.ml_used)


class OnboardingChecklist(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='onboarding_checklist')
    appointment_order_no = models.CharField(max_length=100, default='RNSIT/APPT/2026/042')
    appointment_order_date = models.DateField(default=timezone.now)

    # 6-Step Verification Flags
    step1_appointment_order_verified = models.BooleanField(default=False)
    step1_joining_report_received = models.BooleanField(default=False)
    step2_personal_details_captured = models.BooleanField(default=False)
    step2_academic_credentials_captured = models.BooleanField(default=False)
    step3_experience_verified = models.BooleanField(default=False)
    step3_eligibility_checked = models.BooleanField(default=False)
    step4_documents_uploaded = models.BooleanField(default=False)
    step4_hr_doc_check_completed = models.BooleanField(default=False)
    step5_employee_id_generated = models.BooleanField(default=False)
    step5_hr_record_activated = models.BooleanField(default=False)
    step6_dept_role_allocated = models.BooleanField(default=False)
    step6_reporting_assigned = models.BooleanField(default=False)

    verification_notes = models.TextField(blank=True, default='')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Onboarding Checklist: {self.employee.employee_id} - {'Completed' if self.is_completed else 'In Progress'}"

    @property
    def progress_percentage(self):
        steps = [
            self.step1_appointment_order_verified and self.step1_joining_report_received,
            self.step2_personal_details_captured and self.step2_academic_credentials_captured,
            self.step3_experience_verified and self.step3_eligibility_checked,
            self.step4_documents_uploaded and self.step4_hr_doc_check_completed,
            self.step5_employee_id_generated and self.step5_hr_record_activated,
            self.step6_dept_role_allocated and self.step6_reporting_assigned,
        ]
        return int((sum(1 for s in steps if s) / len(steps)) * 100)


class OnboardingDocument(models.Model):
    DOC_TYPES = [
        ('APPOINTMENT_ORDER', 'Appointment Order Copy'),
        ('JOINING_REPORT', 'Signed Joining Report'),
        ('PHD_DEGREE', 'Ph.D. / PG Convocation Degree Certificate'),
        ('UG_DEGREE', 'UG Degree Certificate & Marks Transcripts'),
        ('PREV_EXPERIENCE', 'Previous Employment Relieving & Experience Letter'),
        ('GOVT_ID', 'Government ID (Aadhaar & PAN Card)'),
        ('BANK_DETAILS', 'Bank Passbook / Cancelled Cheque for Salary Credit'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending Verification'),
        ('VERIFIED', 'Verified by HR'),
        ('REJECTED', 'Rejected / Re-upload Required'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=50, choices=DOC_TYPES)
    title = models.CharField(max_length=200)
    file_path = models.CharField(max_length=500, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='VERIFIED')
    verifier_name = models.CharField(max_length=100, default='HR Admin Office')
    verification_comments = models.TextField(blank=True, default='Verified against original documents.')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.employee_id} - {self.get_doc_type_display()} ({self.status})"


class OffboardingRequest(models.Model):
    STATUS_CHOICES = [
        ('SUBMITTED', 'Resignation Submitted'),
        ('HOD_REVIEWED', 'HoD Review Completed'),
        ('PRINCIPAL_APPROVED', 'Approved by Principal / Management'),
        ('CLEARANCES_PENDING', 'Clearances In Progress'),
        ('HR_VERIFIED', 'HR Final Settlement Verified'),
        ('COMPLETED', 'Exit Completed & Relieved'),
    ]

    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='offboarding_request')
    resignation_date = models.DateField(default=timezone.now)
    proposed_last_day = models.DateField()
    actual_last_day = models.DateField(null=True, blank=True)
    reason = models.CharField(max_length=200, default='Pursuing higher academic opportunities abroad / industry transition')
    handover_plan = models.TextField(blank=True, default='Syllabus completed. Lab in-charge responsibilities and project mentoring handover documents submitted to HoD.')

    # 02 HoD Review
    hod_status = models.CharField(max_length=20, default='RECOMMENDED')
    hod_comments = models.TextField(blank=True, default='Academic handover verified. Substitute course coordinator assigned. Recommended for acceptance.')
    hod_reviewed_at = models.DateTimeField(null=True, blank=True)

    # 03 Principal / Management Approval
    principal_status = models.CharField(max_length=20, default='APPROVED')
    principal_comments = models.TextField(blank=True, default='Approved subject to completion of standard institutional no-dues clearance.')
    principal_approved_at = models.DateTimeField(null=True, blank=True)

    # 04 Notice Period Monitoring
    notice_period_required_days = models.IntegerField(default=30)
    notice_period_served_days = models.IntegerField(default=30)
    notice_waiver_granted = models.BooleanField(default=False)
    notice_shortfall_days = models.IntegerField(default=0)

    # 05 Department-Wise Clearances (6 Clearances)
    library_cleared = models.BooleanField(default=True)
    library_remarks = models.CharField(max_length=200, default='All 4 borrowed library books returned. No outstanding dues.')
    library_cleared_by = models.CharField(max_length=100, default='Chief Librarian')

    lab_cleared = models.BooleanField(default=True)
    lab_remarks = models.CharField(max_length=200, default='IoT Lab kit inventory verified. Keys and logbooks handed over.')
    lab_cleared_by = models.CharField(max_length=100, default='Lab Superintendent')

    it_cleared = models.BooleanField(default=True)
    it_remarks = models.CharField(max_length=200, default='College faculty email scheduled for archive. Assigned Dell laptop returned.')
    it_cleared_by = models.CharField(max_length=100, default='IT Systems Admin')

    stores_cleared = models.BooleanField(default=True)
    stores_remarks = models.CharField(max_length=200, default='Departmental furniture and stationeries accounted for.')
    stores_cleared_by = models.CharField(max_length=100, default='Stores Officer')

    assets_cleared = models.BooleanField(default=True)
    assets_remarks = models.CharField(max_length=200, default='Smart faculty RFID card and vehicle parking badge surrendered.')
    assets_cleared_by = models.CharField(max_length=100, default='Estate & Security Officer')

    accounts_cleared = models.BooleanField(default=True)
    accounts_remarks = models.CharField(max_length=200, default='Salary settled through last working day. No pending travel advances or loans.')
    accounts_cleared_by = models.CharField(max_length=100, default='Chief Accounts Officer')

    # 06 HR Verification & Settlement
    hr_verified = models.BooleanField(default=True)
    hr_settlement_notes = models.TextField(blank=True, default='All 6 department clearances verified without objection. Gratuity and final settlement processed.')
    
    # 07 Exit Completion
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='COMPLETED')
    is_exit_completed = models.BooleanField(default=True)
    
    # 08 Exit Documents
    relieving_order_number = models.CharField(max_length=100, default='RNSIT/EST/REL/2026/019')
    experience_cert_number = models.CharField(max_length=100, default='RNSIT/EST/EXP/2026/019')
    conduct_assessment = models.CharField(max_length=50, default='Exemplary')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Offboarding: {self.employee.employee_id} - {self.status}"

    @property
    def clearances_count(self):
        items = [
            self.library_cleared, self.lab_cleared, self.it_cleared,
            self.stores_cleared, self.assets_cleared, self.accounts_cleared
        ]
        return sum(1 for c in items if c)
