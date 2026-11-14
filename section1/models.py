from django.db import models
import json

class Section1Submission(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted for Review'),
        ('REVISION_REQUESTED', 'Revision Requested by HOD'),
        ('VERIFIED', 'Verified by HOD / Principal'),
        ('APPROVED', 'Approved by Principal'),
    ]

    faculty_name = models.CharField(max_length=150, default='Faculty Member')
    employee_id = models.CharField(max_length=50, blank=True, null=True)
    department = models.CharField(max_length=100, default='Computer Science & Engineering')
    academic_year = models.CharField(max_length=50, default='2026-2027')
    
    # Section Scores
    section1_final_score = models.FloatField(default=0.0, help_text="Section I Score (Max 70)")
    section2_final_score = models.FloatField(default=0.0, help_text="Section II Score (Max 40)")
    section3_final_score = models.FloatField(default=0.0, help_text="Section III Score (Max 20)")
    section4_final_score = models.FloatField(default=0.0, help_text="Section IV Score (Max 20)")
    
    # Scaling and Reviews
    subtotal_130 = models.FloatField(default=0.0, help_text="Subtotal I + II + III (Max 130)")
    scaled_80 = models.FloatField(default=0.0, help_text="Scaled Score (Max 80)")
    hod_score = models.FloatField(default=0.0, help_text="HOD Evaluation (Max 15)")
    principal_score = models.FloatField(default=0.0, help_text="Principal Evaluation (Max 5)")
    grand_total_100 = models.FloatField(default=0.0, help_text="Grand Total Performance Score (Max 100)")
    performance_grade = models.CharField(max_length=50, default='Not Evaluated')

    # Detailed breakdown JSON
    raw_payload = models.TextField(blank=True, default='{}')
    calculation_breakdown = models.TextField(blank=True, default='{}')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.faculty_name} ({self.academic_year}) - Grand: {self.grand_total_100}/100 [{self.performance_grade}]"

    def get_breakdown(self):
        try:
            return json.loads(self.calculation_breakdown)
        except Exception:
            return {}


class UploadedEvidence(models.Model):
    EVIDENCE_STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('VERIFIED', 'Verified by HOD'),
        ('REJECTED', 'Rejected by HOD'),
    ]

    submission = models.ForeignKey(
        Section1Submission, 
        on_delete=models.CASCADE, 
        related_name='evidence_documents', 
        null=True, 
        blank=True
    )
    component_code = models.CharField(max_length=50, help_text="E.g. Sec1_A1, Sec2_Pub, Sec3_Cert...")
    file = models.FileField(upload_to='evidence/%Y/%m/')
    original_filename = models.CharField(max_length=255)
    file_size_kb = models.FloatField(default=0.0)
    is_verified = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=EVIDENCE_STATUS_CHOICES, default='PENDING')
    rejection_reason = models.TextField(blank=True, null=True, help_text="Review feedback why document was rejected")
    reviewed_at = models.DateTimeField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.component_code}] {self.original_filename} ({self.status})"


class AppraisalNotification(models.Model):
    submission = models.ForeignKey(
        Section1Submission, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    evidence = models.ForeignKey(
        UploadedEvidence, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='notifications'
    )
    component_title = models.CharField(max_length=255)
    component_code = models.CharField(max_length=50, blank=True, null=True)
    notification_type = models.CharField(max_length=50, default='REJECTION') # 'REJECTION', 'REMARK', 'ACTION_REQUIRED'
    message = models.TextField(help_text="HOD Review / Rejection Reason")
    created_by = models.CharField(max_length=150, default='HOD')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.notification_type}] {self.component_title} - {self.created_by}"
