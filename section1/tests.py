import json
import os
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from section1.models import Section1Submission, UploadedEvidence, AppraisalNotification
from section1.auth_utils import authenticate_user, get_env_credentials

class PBASIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_01_env_credentials(self):
        """Test reading credentials from .env"""
        creds = get_env_credentials()
        self.assertIn('FACULTY', creds)
        self.assertIn('HOD', creds)
        self.assertIn('PRINCIPAL', creds)

        # Authenticate Faculty
        f_user = creds['FACULTY']['username']
        f_pass = creds['FACULTY']['password']
        success, role, info = authenticate_user(f_user, f_pass, 'FACULTY')
        self.assertTrue(success)
        self.assertEqual(role, 'FACULTY')

        # Authenticate HOD
        h_user = creds['HOD']['username']
        h_pass = creds['HOD']['password']
        success, role, info = authenticate_user(h_user, h_pass, 'HOD')
        self.assertTrue(success)
        self.assertEqual(role, 'HOD')

        # Authenticate Principal
        p_user = creds['PRINCIPAL']['username']
        p_pass = creds['PRINCIPAL']['password']
        success, role, info = authenticate_user(p_user, p_pass, 'PRINCIPAL')
        self.assertTrue(success)
        self.assertEqual(role, 'PRINCIPAL')

    def test_02_full_workflow(self):
        """Test complete workflow: Login -> Upload -> Submit -> HOD Review -> Principal Decision -> PDF Export"""
        creds = get_env_credentials()
        
        # 1. Faculty Login
        res = self.client.post(reverse('login_view'), {
            'username': creds['FACULTY']['username'],
            'password': creds['FACULTY']['password'],
            'role': 'FACULTY'
        }, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.client.session.get('user_role'), 'FACULTY')

        # 2. Upload Evidence File
        sample_file = SimpleUploadedFile(
            "student_feedback_sem1.pdf",
            b"%PDF-1.4 Sample PDF content for testing evidence upload",
            content_type="application/pdf"
        )
        upload_res = self.client.post(reverse('api_upload'), {
            'file': sample_file,
            'component_code': 'SEC1_A1'
        })
        self.assertEqual(upload_res.status_code, 200)
        upload_data = json.loads(upload_res.content)
        self.assertTrue(upload_data['success'])
        evidence_id = upload_data['file_id']
        evidence_url = upload_data['file_url']

        # 3. Save Faculty Submission
        payload = {
            'odd_feedback_courses': [{'course_name': 'CS501 Computer Networks', 'round_1': 92.0, 'round_2': 88.0, 'proof_file': evidence_url}],
            'even_feedback_courses': [{'course_name': 'CS601 Compiler Design', 'round_1': 90.0, 'round_2': 90.0, 'proof_file': ''}],
            'odd_results_courses': [{'course_name': 'CS501 Computer Networks', 'appeared': 60, 'passed': 57}],
            'even_results_courses': [{'course_name': 'CS601 Compiler Design', 'appeared': 55, 'passed': 55}],
            'other_tlp_c': {
                'c_ii_own_syllabus': [{'title': 'Advanced Distributed Systems curriculum'}],
                'c_ix_ai_tools': [{'tool_name': 'GitHub Copilot in Lab Sessions'}]
            },
            'sec2_ii_publications': [
                {'category': 'q1', 'author_order': 1, 'title': 'Deep Learning for Edge Devices', 'proof_file': evidence_url}
            ],
            'sec2_iii_patents': [
                {'category': 'granted_nat_int', 'title': 'Automated Code Review System'}
            ],
            'sec3_ii_memberships': [
                {'society': 'IEEE', 'membership_id': '98765432'}
            ],
            'sec3_iv_certifications': [
                {'title': 'AWS Certified Solutions Architect', 'cert_body': 'Amazon Web Services'}
            ],
            'sec4_department_roles': [
                {'role_code': 'dept_coordinator', 'description': 'NBA Department Coordinator'}
            ],
            'uploaded_file_ids': [evidence_id]
        }

        save_res = self.client.post(
            reverse('api_save'),
            data=json.dumps({
                'faculty_name': creds['FACULTY']['name'],
                'employee_id': creds['FACULTY']['employee_id'],
                'department': creds['FACULTY']['department'],
                'academic_year': '2026-2027',
                'submit_final': True,
                'payload': payload
            }),
            content_type='application/json'
        )
        self.assertEqual(save_res.status_code, 200)
        save_data = json.loads(save_res.content)
        self.assertTrue(save_data['success'])
        submission_id = save_data['submission_id']
        self.assertEqual(save_data['status'], 'SUBMITTED')

        # Check DB submission
        sub = Section1Submission.objects.get(id=submission_id)
        self.assertEqual(sub.faculty_name, creds['FACULTY']['name'])
        self.assertEqual(sub.status, 'SUBMITTED')
        self.assertGreater(sub.section1_final_score, 0)
        self.assertGreater(sub.section2_final_score, 0)
        self.assertGreater(sub.section3_final_score, 0)

        # 4. HOD Login and Portal Inspection
        self.client.get(reverse('logout_view'))
        self.client.post(reverse('login_view'), {
            'username': creds['HOD']['username'],
            'password': creds['HOD']['password'],
            'role': 'HOD'
        }, follow=True)
        self.assertEqual(self.client.session.get('user_role'), 'HOD')

        # HOD views portal list
        hod_portal_res = self.client.get(reverse('hod_portal'))
        self.assertEqual(hod_portal_res.status_code, 200)
        self.assertContains(hod_portal_res, creds['FACULTY']['name'])

        # HOD opens detailed evaluate view
        hod_eval_res = self.client.get(reverse('hod_evaluate', args=[submission_id]))
        self.assertEqual(hod_eval_res.status_code, 200)
        self.assertContains(hod_eval_res, 'CS501 Computer Networks')
        self.assertContains(hod_eval_res, 'student_feedback_sem1.pdf')

        # HOD submits review
        hod_review_res = self.client.post(
            reverse('api_hod_review'),
            data=json.dumps({
                'submission_id': submission_id,
                'sec4_marks': 18.0,
                'sec4_remarks': 'Excellent student mentoring and branch fest coordination.',
                'hod_c1': 3.0,
                'hod_c2': 3.0,
                'hod_c3': 3.0,
                'hod_c4': 2.5,
                'hod_c5': 3.0,
                'hod_remarks': 'Outstanding academic and research dedication this year.',
                'forward_to_principal': True
            }),
            content_type='application/json'
        )
        self.assertEqual(hod_review_res.status_code, 200)
        hod_data = json.loads(hod_review_res.content)
        self.assertTrue(hod_data['success'])
        self.assertEqual(hod_data['status'], 'VERIFIED')
        self.assertEqual(hod_data['hod_score'], 14.5)

        # 5. Principal Login and Evaluation
        self.client.get(reverse('logout_view'))
        self.client.post(reverse('login_view'), {
            'username': creds['PRINCIPAL']['username'],
            'password': creds['PRINCIPAL']['password'],
            'role': 'PRINCIPAL'
        }, follow=True)
        self.assertEqual(self.client.session.get('user_role'), 'PRINCIPAL')

        # Principal views portal list
        principal_portal_res = self.client.get(reverse('principal_portal'))
        self.assertEqual(principal_portal_res.status_code, 200)
        self.assertContains(principal_portal_res, creds['FACULTY']['name'])

        # Principal opens evaluate view
        p_eval_res = self.client.get(reverse('principal_evaluate', args=[submission_id]))
        self.assertEqual(p_eval_res.status_code, 200)
        self.assertContains(p_eval_res, creds['FACULTY']['name'])
        self.assertContains(p_eval_res, 'HOD Verified')

        # Principal submits final decision
        principal_decision_res = self.client.post(
            reverse('api_principal_decision'),
            data=json.dumps({
                'submission_id': submission_id,
                'p_c1': 1.0,
                'p_c2': 1.0,
                'p_c3': 1.0,
                'p_c4': 1.0,
                'p_c5': 1.0,
                'principal_remarks': 'Approved for annual appraisal and promotion progression.',
                'final_approval': True
            }),
            content_type='application/json'
        )
        self.assertEqual(principal_decision_res.status_code, 200)
        p_data = json.loads(principal_decision_res.content)
        self.assertTrue(p_data['success'])
        self.assertEqual(p_data['status'], 'APPROVED')
        self.assertEqual(p_data['principal_score'], 5.0)
        self.assertGreater(p_data['grand_total_100'], 70)
        self.assertIn(p_data['grade'], ['Excellent', 'Very Good', 'Good'])

        # 6. Test PDF Export
        pdf_res = self.client.get(reverse('download_pdf', args=[submission_id]))
        self.assertEqual(pdf_res.status_code, 200)
        self.assertEqual(pdf_res['Content-Type'], 'application/pdf')
        self.assertTrue(pdf_res.content.startswith(b'%PDF'))

    def test_03_hod_rejection_and_faculty_notification(self):
        """Test HOD rejecting a document with review feedback and verifying notification in Faculty Portal"""
        creds = get_env_credentials()

        # 1. Faculty uploads a file and submits
        self.client.post(reverse('login_view'), {
            'username': creds['FACULTY']['username'],
            'password': creds['FACULTY']['password'],
            'role': 'FACULTY'
        }, follow=True)

        sample_file = SimpleUploadedFile("unsigned_certificate.pdf", b"%PDF-1.4 sample", content_type="application/pdf")
        upload_res = self.client.post(reverse('api_upload'), {'file': sample_file, 'component_code': 'SEC1_A1'})
        evidence_id = json.loads(upload_res.content)['file_id']

        save_res = self.client.post(
            reverse('api_save'),
            data=json.dumps({
                'faculty_name': creds['FACULTY']['name'],
                'employee_id': creds['FACULTY']['employee_id'],
                'department': creds['FACULTY']['department'],
                'academic_year': '2026-2027',
                'submit_final': True,
                'payload': {'uploaded_file_ids': [evidence_id]}
            }),
            content_type='application/json'
        )
        sub_id = json.loads(save_res.content)['submission_id']

        # 2. HOD logs in and rejects the document with a review reason
        self.client.get(reverse('logout_view'))
        self.client.post(reverse('login_view'), {
            'username': creds['HOD']['username'],
            'password': creds['HOD']['password'],
            'role': 'HOD'
        }, follow=True)

        reject_res = self.client.post(
            reverse('api_reject_evidence', args=[evidence_id]),
            data=json.dumps({'reason': 'Certificate is missing authorized HOD signature. Please re-upload signed copy.'}),
            content_type='application/json'
        )
        self.assertEqual(reject_res.status_code, 200)
        reject_data = json.loads(reject_res.content)
        self.assertTrue(reject_data['success'])
        self.assertEqual(reject_data['status'], 'REJECTED')
        notif_id = reject_data['notification_id']

        # Check DB states
        ev = UploadedEvidence.objects.get(id=evidence_id)
        self.assertEqual(ev.status, 'REJECTED')
        self.assertFalse(ev.is_verified)
        self.assertIn('missing authorized HOD signature', ev.rejection_reason)

        sub = Section1Submission.objects.get(id=sub_id)
        self.assertEqual(sub.status, 'REVISION_REQUESTED')

        # 3. Faculty logs back in and checks their portal for the notification
        self.client.get(reverse('logout_view'))
        self.client.post(reverse('login_view'), {
            'username': creds['FACULTY']['username'],
            'password': creds['FACULTY']['password'],
            'role': 'FACULTY'
        }, follow=True)

        faculty_portal_res = self.client.get(reverse('faculty_portal'))
        self.assertEqual(faculty_portal_res.status_code, 200)
        self.assertContains(faculty_portal_res, 'Action Required: Document Revision Requested by HOD')
        self.assertContains(faculty_portal_res, 'Certificate is missing authorized HOD signature')

        # 4. Faculty dismisses / acknowledges notification
        dismiss_res = self.client.post(reverse('api_dismiss_notification', args=[notif_id]))
        self.assertEqual(dismiss_res.status_code, 200)
        self.assertTrue(json.loads(dismiss_res.content)['success'])
