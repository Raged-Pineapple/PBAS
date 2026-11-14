import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calculator import (
    calculate_section_1, calculate_section_2, calculate_section_3, 
    calculate_section_4, calculate_complete_pbas
)

class TestAllSectionsCalculator(unittest.TestCase):
    def test_section_1(self):
        payload = {
            'odd_feedback_courses': [{'course_name': 'CS101', 'round_1': 90.0, 'round_2': 90.0}],
            'even_feedback_courses': [{'course_name': 'CS201', 'round_1': 90.0, 'round_2': 90.0}],
            'odd_results_courses': [{'course_name': 'CS101', 'appeared': 60, 'passed': 60}],
            'even_results_courses': [{'course_name': 'CS201', 'appeared': 60, 'passed': 60}],
            'other_tlp_c': {
                'c_ii_own_syllabus': [{'title': 'Syllabus 1'}],
                'c_ix_ai_tools': [{'tool_name': 'AI Tool 1'}]
            }
        }
        res = calculate_section_1(payload)
        self.assertEqual(res['feedback_a']['marks_awarded'], 27) # 90 * 30 / 100 = 27
        self.assertEqual(res['results_b']['marks_awarded'], 20) # 100% * 20 / 100 = 20
        self.assertEqual(res['total_ab']['score_awarded'], 47)
        # C = 5 (syllabus) + 2.5 (AI) = 7.5
        # Total = 47 + 7.5 = 54.5
        self.assertEqual(res['section_score'], 54.5)

    def test_section_2_caps(self):
        payload = {
            'sec2_ii_publications': [
                {'category': 'q1', 'author_order': 1}, # 20
                {'category': 'q1', 'author_order': 1}, # 20 -> 40, capped at 30
            ],
            'sec2_vii_patents': [{'status': 'granted'}], # 10
            'sec2_x_startups': [{'name': 'Startup 1'}] # 10
        }
        # 30 (pub) + 10 (patent) + 10 (startup) = 50 -> capped at 40
        res = calculate_section_2(payload)
        self.assertEqual(res['components']['sec2_ii']['score'], 30.0)
        self.assertEqual(res['section_score'], 40.0)

    def test_section_3_caps(self):
        payload = {
            'sec3_iv_certifications': [{'title': 'AWS Solutions Architect'}], # 10
            'sec3_xi_automation': [{'title': 'PBAS Portal Automation'}], # 10
            'sec3_ii_memberships': [{'society': 'IEEE'}] # 2.5
        }
        # 10 + 10 + 2.5 = 22.5 -> capped at 20
        res = calculate_section_3(payload)
        self.assertEqual(res['section_score'], 20.0)

    def test_scaling_and_grades(self):
        payload = {
            'section1': {
                'odd_feedback_courses': [{'course_name': 'C1', 'round_1': 100, 'round_2': 100}],
                'even_feedback_courses': [{'course_name': 'C2', 'round_1': 100, 'round_2': 100}],
                'odd_results_courses': [{'course_name': 'C1', 'appeared': 50, 'passed': 50}],
                'even_results_courses': [{'course_name': 'C2', 'appeared': 50, 'passed': 50}],
                'other_tlp_c': {'c_ii_own_syllabus': [{'t': '1'}, {'t': '2'}, {'t': '3'}, {'t': '4'}]}
            }, # 50 + 10 = 60
            'section2': {
                'sec2_ii_publications': [{'category': 'q1', 'author_order': 1}, {'category': 'q2', 'author_order': 1}]
            }, # 30
            'section3': {
                'sec3_iv_certifications': [{'title': 'Cert 1'}],
                'sec3_xi_automation': [{'title': 'Auto 1'}]
            }, # 20
            'hod_review': {
                'discipline_attitude': 3,
                'academic_planning': 3,
                'dept_admin_support': 3,
                'accreditation_fdp': 3,
                'autonomous_support': 3
            }, # 15
            'principal_review': {
                'vision_goal': 1,
                'leadership_mgmt': 1,
                'involvement_admin': 1,
                'research_innovation': 1,
                'overall_discipline': 1
            } # 5
        }
        # Subtotal I+II+III = 60 + 30 + 20 = 110 / 130
        # Scaled = (110 / 130) * 80 = 67.69
        # Grand = 67.69 + 15 + 5 = 87.69 -> Grade "Very Good"
        res = calculate_complete_pbas(payload)
        summary = res['summary']
        self.assertEqual(summary['subtotal_130'], 110.0)
        self.assertEqual(round(summary['scaled_80'], 2), 67.69)
        self.assertEqual(summary['hod_evaluation']['total'], 15.0)
        self.assertEqual(summary['principal_evaluation']['total'], 5.0)
        self.assertEqual(round(summary['grand_total_100'], 2), 87.69)
        self.assertEqual(summary['grade'], 'Very Good')

if __name__ == '__main__':
    unittest.main()
