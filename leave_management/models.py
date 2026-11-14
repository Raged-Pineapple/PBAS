from django.db import models
from django.utils import timezone
from onboarding_offboarding.models import Employee

class LeaveApplication(models.Model):
    LEAVE_TYPES = [
        ('CL', 'Casual Leave (CL)'),
        ('EL', 'Earned Leave (EL)'),
        ('ML', 'Medical Leave (ML)'),
        ('OD', 'On Duty (OD - Conferences/Syllabus)'),
        ('LOP', 'Loss of Pay (LOP)'),
    ]

    STATUS_CHOICES = [
        ('PENDING_HOD', 'Pending HoD Review'),
        ('HOD_REJECTED', 'Rejected by HoD (Resubmit Enabled)'),
        ('PENDING_PRINCIPAL', 'Recommended by HoD, Pending Principal'),
        ('PRINCIPAL_REJECTED', 'Rejected by Principal'),
        ('APPROVED', 'Finally Approved & Balance Deducted'),
        ('CANCELLED', 'Withdrawn by Employee'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_applications')
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPES, default='CL')
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.FloatField(default=1.0)
    reason = models.TextField()
    substitute_faculty = models.CharField(max_length=150, blank=True, default='', help_text="Handover faculty for scheduled classes")

    # Workflow Step 2: HoD Approval
    hod_status = models.CharField(max_length=20, default='PENDING') # PENDING, APPROVED, REJECTED
    hod_remarks = models.TextField(blank=True, default='')
    hod_action_at = models.DateTimeField(null=True, blank=True)

    # Workflow Step 3: Principal Approval
    requires_principal_approval = models.BooleanField(default=True, help_text="Configurable approval level based on category / duration > 2 days")
    principal_status = models.CharField(max_length=20, default='PENDING')
    principal_remarks = models.TextField(blank=True, default='')
    principal_action_at = models.DateTimeField(null=True, blank=True)

    # Workflow Step 4: HR Final Notification & Deduction
    overall_status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING_HOD')
    is_balance_deducted = models.BooleanField(default=False, help_text="Only finally approved leave triggers official deduction")
    is_lop = models.BooleanField(default=False, help_text="Auto-flagged if applied leave exceeds remaining quota")
    lop_days = models.FloatField(default=0.0)

    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.employee_id} - {self.leave_type} ({self.total_days} days) - {self.overall_status}"

    def trigger_final_approval(self):
        """
        Executes Slide 5 Rule:
        Only finally approved leave is deducted.
        Available Balance = Allotted - Approved.
        """
        if self.is_balance_deducted:
            return

        emp = self.employee
        if self.leave_type == 'CL':
            if emp.cl_available >= self.total_days:
                emp.cl_used += self.total_days
            else:
                # Excess converts to LOP
                covered = emp.cl_available
                self.lop_days = self.total_days - covered
                self.is_lop = True
                emp.cl_used += covered
        elif self.leave_type == 'EL':
            if emp.el_available >= self.total_days:
                emp.el_used += self.total_days
            else:
                covered = emp.el_available
                self.lop_days = self.total_days - covered
                self.is_lop = True
                emp.el_used += covered
        elif self.leave_type == 'ML':
            if emp.ml_available >= self.total_days:
                emp.ml_used += self.total_days
            else:
                covered = emp.ml_available
                self.lop_days = self.total_days - covered
                self.is_lop = True
                emp.ml_used += covered
        elif self.leave_type == 'LOP':
            self.is_lop = True
            self.lop_days = self.total_days

        emp.save()
        self.is_balance_deducted = True
        self.overall_status = 'APPROVED'
        self.save()
