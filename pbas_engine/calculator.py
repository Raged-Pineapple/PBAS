"""
RNSIT PBAS (Performance Based Appraisal System) - Assistant Professor
Comprehensive Calculation Engine for All Sections (I, II, III, IV, Reviews, and 100-Mark Scaling)
"""

import math
from typing import Dict, Any, List


def round_up_fraction(val: float) -> int:
    """Rounds up fraction to next higher integer as per PBAS workbook."""
    return math.ceil(val)


# ==========================================
# SECTION I: TEACHING LEARNING PROCESS (70)
# ==========================================
def calculate_feedback_a(odd_courses: List[Dict[str, Any]], even_courses: List[Dict[str, Any]]) -> Dict[str, Any]:
    def process_courses(courses):
        details = []
        total_avg = 0.0
        valid_count = 0
        for c in courses:
            rounds = [float(r) for r in [c.get('round_1'), c.get('round_2')] if r is not None and str(r).strip() != '']
            course_avg = (sum(rounds) / len(rounds)) if rounds else 0.0
            if rounds:
                total_avg += course_avg
                valid_count += 1
            details.append({
                'course_name': c.get('course_name', '').strip(),
                'round_1': c.get('round_1'),
                'round_2': c.get('round_2'),
                'average': round(course_avg, 2),
                'evidence_file': c.get('evidence_file', '')
            })
        sem_avg = (total_avg / valid_count) if valid_count > 0 else 0.0
        return round(sem_avg, 2), details

    a1_avg, a1_details = process_courses(odd_courses)
    a2_avg, a2_details = process_courses(even_courses)

    if a1_avg > 0 and a2_avg > 0:
        combined_avg = (a1_avg + a2_avg) / 2.0
    elif a1_avg > 0:
        combined_avg = a1_avg
    elif a2_avg > 0:
        combined_avg = a2_avg
    else:
        combined_avg = 0.0

    raw_marks = (combined_avg * 30.0) / 100.0
    marks_a = min(round_up_fraction(raw_marks), 30)

    return {
        'a1_odd_sem_average': round(a1_avg, 2),
        'a1_details': a1_details,
        'a2_even_sem_average': round(a2_avg, 2),
        'a2_details': a2_details,
        'combined_feedback_average': round(combined_avg, 2),
        'raw_marks': round(raw_marks, 2),
        'marks_awarded': marks_a,
        'max_marks': 30
    }


def calculate_results_b(odd_courses: List[Dict[str, Any]], even_courses: List[Dict[str, Any]]) -> Dict[str, Any]:
    def process_courses(courses):
        details = []
        total_pct = 0.0
        valid_count = 0
        for c in courses:
            appeared = float(c.get('appeared', 0) or 0)
            passed = float(c.get('passed', 0) or 0)
            pass_pct = (passed / appeared * 100.0) if appeared > 0 else 0.0
            if appeared > 0:
                total_pct += pass_pct
                valid_count += 1
            details.append({
                'course_name': c.get('course_name', '').strip(),
                'appeared': int(appeared),
                'passed': int(passed),
                'pass_percentage': round(pass_pct, 2),
                'evidence_file': c.get('evidence_file', '')
            })
        sem_avg = (total_pct / valid_count) if valid_count > 0 else 0.0
        return round(sem_avg, 2), details

    b1_avg, b1_details = process_courses(odd_courses)
    b2_avg, b2_details = process_courses(even_courses)

    if b1_avg > 0 and b2_avg > 0:
        combined_avg = (b1_avg + b2_avg) / 2.0
    elif b1_avg > 0:
        combined_avg = b1_avg
    elif b2_avg > 0:
        combined_avg = b2_avg
    else:
        combined_avg = 0.0

    raw_marks = (combined_avg * 20.0) / 100.0
    marks_b = min(round_up_fraction(raw_marks), 20)

    return {
        'b1_odd_sem_average': round(b1_avg, 2),
        'b1_details': b1_details,
        'b2_even_sem_average': round(b2_avg, 2),
        'b2_details': b2_details,
        'combined_results_average': round(combined_avg, 2),
        'raw_marks': round(raw_marks, 2),
        'marks_awarded': marks_b,
        'max_marks': 20
    }


def calculate_other_tlp_c(c_data: Dict[str, Any]) -> Dict[str, Any]:
    breakdown = {}
    total_c = 0.0

    # ii. Own syllabus (5/course; cap 10)
    own_syllabus_list = c_data.get('c_ii_own_syllabus', [])
    score_ii = min(len(own_syllabus_list) * 5.0, 10.0)
    breakdown['c_ii'] = {'name': 'Own syllabus for core subjects', 'items': own_syllabus_list, 'score': score_ii, 'max': 10}
    total_c += score_ii

    # iii. External funded academic activity (PI: 2/₹1L, Co-PI: 1/₹1L; min ₹1L; cap 10)
    funded_list = c_data.get('c_iii_funded_activities', [])
    raw_iii = 0.0
    for act in funded_list:
        amount = float(act.get('funding_amount', 0) or 0)
        role = str(act.get('role', 'PI')).upper().strip()
        if amount >= 100000:
            rate = 2.0 if 'CO' not in role else 1.0
            raw_iii += (amount / 100000.0) * rate
    score_iii = min(raw_iii, 10.0)
    breakdown['c_iii'] = {'name': 'External funded academic activity', 'items': funded_list, 'score': round(score_iii, 2), 'max': 10}
    total_c += score_iii

    # iv. Organizing FDP NIRF (10/activity; min ₹1L; cap 10)
    org_fdp_list = c_data.get('c_iv_org_fdp', [])
    score_iv = min(len(org_fdp_list) * 10.0, 10.0)
    breakdown['c_iv'] = {'name': 'Organizing FDP with NIRF institution', 'items': org_fdp_list, 'score': score_iv, 'max': 10}
    total_c += score_iv

    # v. Online courses completed >=30 hrs (2.5/course; cap 10)
    online_completed = c_data.get('c_v_online_completed', [])
    valid_v = sum(1 for oc in online_completed if float(oc.get('duration_hours', 0) or 0) >= 30)
    score_v = min(valid_v * 2.5, 10.0)
    breakdown['c_v'] = {'name': 'Online courses completed (>=30 hrs)', 'items': online_completed, 'score': score_v, 'max': 10}
    total_c += score_v

    # vi. NPTEL online courses >= 4 wks (Completed: 5, Elite: 6, Elite+Silver: 8, Elite+Gold: 10; cap 10)
    nptel_list = c_data.get('c_vi_nptel', [])
    grade_map = {'completed': 5.0, 'elite': 6.0, 'elite_silver': 8.0, 'elite_gold': 10.0}
    raw_vi = sum(grade_map.get(str(i.get('grade_type', 'completed')).lower().replace(' ', '_').replace('+', '_'), 5.0) for i in nptel_list)
    score_vi = min(raw_vi, 10.0)
    breakdown['c_vi'] = {'name': 'NPTEL online courses completed', 'items': nptel_list, 'score': score_vi, 'max': 10}
    total_c += score_vi

    # vii. Online courses developed (External: 10, RNSIT YouTube: 5; cap 10)
    courses_dev = c_data.get('c_vii_courses_developed', [])
    raw_vii = sum(5.0 if any(k in str(cd.get('platform_type', '')).lower() for k in ['youtube', 'rnsit']) else 10.0 for cd in courses_dev)
    score_vii = min(raw_vii, 10.0)
    breakdown['c_vii'] = {'name': 'Online courses developed', 'items': courses_dev, 'score': score_vii, 'max': 10}
    total_c += score_vii

    # viii. Resource person >=18 hrs (Internship: 5, Prof Courses: 10; cap 10)
    resource_list = c_data.get('c_viii_resource_person', [])
    raw_viii = sum(10.0 if 'prof' in str(rp.get('type', '')).lower() else 5.0 for rp in resource_list)
    score_viii = min(raw_viii, 10.0)
    breakdown['c_viii'] = {'name': 'Resource person for internship / prof courses', 'items': resource_list, 'score': score_viii, 'max': 10}
    total_c += score_viii

    # ix. AI tools in TLP (2.5/tool; cap 5)
    ai_tools_list = c_data.get('c_ix_ai_tools', [])
    score_ix = min(len(ai_tools_list) * 2.5, 5.0)
    breakdown['c_ix'] = {'name': 'Use of AI tools in TLP', 'items': ai_tools_list, 'score': score_ix, 'max': 5}
    total_c += score_ix

    # x. Innovative TLP methods (2.5/method; cap 10)
    tlp_methods = c_data.get('c_x_tlp_methods', [])
    score_x = min(len(tlp_methods) * 2.5, 10.0)
    breakdown['c_x'] = {'name': 'Innovative TLP methods', 'methods': tlp_methods, 'score': score_x, 'max': 10}
    total_c += score_x

    return {'components': breakdown, 'total_c_score': round(total_c, 2)}


def calculate_section_1(payload: Dict[str, Any]) -> Dict[str, Any]:
    feedback_result = calculate_feedback_a(payload.get('odd_feedback_courses', []), payload.get('even_feedback_courses', []))
    results_result = calculate_results_b(payload.get('odd_results_courses', []), payload.get('even_results_courses', []))
    raw_ab = feedback_result['marks_awarded'] + results_result['marks_awarded']
    score_ab = min(raw_ab, 50)
    c_result = calculate_other_tlp_c(payload.get('other_tlp_c', {}))
    raw_total = score_ab + c_result['total_c_score']
    final_score = min(raw_total, 70)

    return {
        'section_name': 'Section I – Teaching Learning Process',
        'max_marks': 70,
        'feedback_a': feedback_result,
        'results_b': results_result,
        'total_ab': {'raw_marks': raw_ab, 'score_awarded': score_ab, 'max_marks': 50},
        'other_tlp_c': c_result,
        'section_score': round(final_score, 2),
        'raw_total': round(raw_total, 2)
    }


# =========================================================================
# SECTION II: RESEARCH & DEVELOPMENT AND CONSULTANCY WORK (MAX: 40 MARKS)
# =========================================================================
def calculate_section_2(payload: Dict[str, Any]) -> Dict[str, Any]:
    breakdown = {}
    total_raw = 0.0

    # i. Invited talk
    talks = payload.get('sec2_i_talks', [])
    score_i = min(len(talks) * 2.5, 5.0)
    breakdown['sec2_i'] = {'name': 'Invited talk / Keynote', 'items': talks, 'score': score_i, 'max': 5}
    total_raw += score_i

    # ii. Publications (combined cap 30)
    pub_rates = {
        'q1': (20.0, 10.0),
        'q2': (15.0, 7.5),
        'q3': (12.5, 6.25),
        'q4': (10.0, 5.0),
        'conf': (5.0, 2.5)
    }
    pubs = payload.get('sec2_ii_publications', [])
    raw_pub = 0.0
    for p in pubs:
        cat = str(p.get('category', 'q4')).lower()
        author_order = int(p.get('author_order', 1) or 1)
        r12, r3 = pub_rates.get(cat, (10.0, 5.0))
        raw_pub += r12 if author_order <= 2 else r3
    score_pub = min(raw_pub, 30.0)
    breakdown['sec2_ii'] = {'name': 'Publications with RNSIT Affiliation', 'items': pubs, 'raw_score': round(raw_pub, 2), 'score': score_pub, 'max': 30}
    total_raw += score_pub

    # iii. Books / chapters (2.5/chapter; cap 5)
    books = payload.get('sec2_iii_books', [])
    score_iii = min(len(books) * 2.5, 5.0)
    breakdown['sec2_iii'] = {'name': 'Books / Book Chapters', 'items': books, 'score': score_iii, 'max': 5}
    total_raw += score_iii

    # iv. Research proposals (5/proposal; cap 5)
    proposals = payload.get('sec2_iv_proposals', [])
    score_iv = min(len(proposals) * 5.0, 5.0)
    breakdown['sec2_iv'] = {'name': 'Research Proposals Submitted', 'items': proposals, 'score': score_iv, 'max': 5}
    total_raw += score_iv

    # v. Research funded projects (cap 20)
    projects = payload.get('sec2_v_projects', [])
    raw_v = 0.0
    for pr in projects:
        amt = float(pr.get('funding_amount', 0) or 0)
        role = str(pr.get('role', 'PI')).upper()
        mult = 1.0 if 'CO' not in role else 0.60
        if amt > 1000000:
            raw_v += 20.0 * mult
        elif amt >= 500000:
            raw_v += 15.0 * mult
        elif amt >= 100000:
            raw_v += 5.0 * mult
    score_v = min(raw_v, 20.0)
    breakdown['sec2_v'] = {'name': 'Research Funded Projects', 'items': projects, 'raw_score': round(raw_v, 2), 'score': score_v, 'max': 20}
    total_raw += score_v

    # vi. Consultancy projects (cap 10)
    consultancies = payload.get('sec2_vi_consultancy', [])
    raw_vi = 0.0
    for c in consultancies:
        amt = float(c.get('consultancy_amount', 0) or 0)
        raw_vi += 10.0 if amt > 500000 else 5.0
    score_vi = min(raw_vi, 10.0)
    breakdown['sec2_vi'] = {'name': 'Consultancy Projects', 'items': consultancies, 'score': score_vi, 'max': 10}
    total_raw += score_vi

    # vii. IPR & Patents (Granted: 10, Published: 5; cap 10)
    patents = payload.get('sec2_vii_patents', [])
    raw_vii = sum(10.0 if str(pt.get('status', 'granted')).lower() == 'granted' else 5.0 for pt in patents)
    score_vii = min(raw_vii, 10.0)
    breakdown['sec2_vii'] = {'name': 'IPR & Patents', 'items': patents, 'score': score_vii, 'max': 10}
    total_raw += score_vii

    # viii. Ph.D. Guidance (cap 10)
    phd_list = payload.get('sec2_viii_phd', [])
    raw_viii = 0.0
    for phd in phd_list:
        role = str(phd.get('role', 'guide')).lower()
        stat = str(phd.get('status', 'awarded')).lower()
        if 'co' in role:
            raw_viii += 5.0
        else:
            raw_viii += 10.0 if ('award' in stat or 'full' in stat) else 5.0
    score_viii = min(raw_viii, 10.0)
    breakdown['sec2_viii'] = {'name': 'Ph.D. Guidance / Awarded', 'items': phd_list, 'score': score_viii, 'max': 10}
    total_raw += score_viii

    # ix. Industry immersion (2.5/week, min 4 wks; cap 10)
    immersion = payload.get('sec2_ix_immersion', [])
    raw_ix = sum(min(float(im.get('weeks', 4) or 4) * 2.5, 10.0) for im in immersion)
    score_ix = min(raw_ix, 10.0)
    breakdown['sec2_ix'] = {'name': 'Faculty Industry Immersion (min 4 wks)', 'items': immersion, 'score': score_ix, 'max': 10}
    total_raw += score_ix

    # x. Mentoring student startups (10/startup; cap 10)
    startups = payload.get('sec2_x_startups', [])
    score_x = min(len(startups) * 10.0, 10.0)
    breakdown['sec2_x'] = {'name': 'Mentoring Student Startups', 'items': startups, 'score': score_x, 'max': 10}
    total_raw += score_x

    # xi. Special Interest Group SIG (5/activity; cap 5)
    sig = payload.get('sec2_xi_sig', [])
    score_xi = min(len(sig) * 5.0, 5.0)
    breakdown['sec2_xi'] = {'name': 'Active Member of RNSIT SIG', 'items': sig, 'score': score_xi, 'max': 5}
    total_raw += score_xi

    final_score = min(total_raw, 40.0)
    return {
        'section_name': 'Section II – Research & Development and Consultancy Work',
        'max_marks': 40,
        'components': breakdown,
        'raw_total': round(total_raw, 2),
        'section_score': round(final_score, 2)
    }


# =========================================================================
# SECTION III: TECHNICAL & PROFESSIONAL ACTIVITIES (MAX: 20 MARKS)
# =========================================================================
def calculate_section_3(payload: Dict[str, Any]) -> Dict[str, Any]:
    breakdown = {}
    total_raw = 0.0

    # i. FDP attended outside (cap 5)
    fdp_att = payload.get('sec3_i_fdp_attended', [])
    raw_i = 0.0
    for it in fdp_att:
        days = float(it.get('days', 5) or 5)
        lvl = str(it.get('level', 'national')).lower()
        raw_i += days * (1.0 if 'nat' in lvl or 'int' in lvl else 0.5)
    score_i = min(raw_i, 5.0)
    breakdown['sec3_i'] = {'name': 'ATAL/Workshops/FDP Attended Outside', 'items': fdp_att, 'score': score_i, 'max': 5}
    total_raw += score_i

    # ii. Professional membership (cap 2.5)
    memberships = payload.get('sec3_ii_memberships', [])
    score_ii = 2.5 if len(memberships) > 0 else 0.0
    breakdown['sec3_ii'] = {'name': 'Professional Society Membership', 'items': memberships, 'score': score_ii, 'max': 2.5}
    total_raw += score_ii

    # iii. Coordinator COE / Lab (cap 5)
    coe = payload.get('sec3_iii_coe', [])
    score_iii = min(len(coe) * 5.0, 5.0)
    breakdown['sec3_iii'] = {'name': 'Coordinator COE / Lab / Startup', 'items': coe, 'score': score_iii, 'max': 5}
    total_raw += score_iii

    # iv. Industry certification (cap 10)
    certs = payload.get('sec3_iv_certifications', [])
    score_iv = min(len(certs) * 10.0, 10.0)
    breakdown['sec3_iv'] = {'name': 'Global / Industry Certification', 'items': certs, 'score': score_iv, 'max': 10}
    total_raw += score_iv

    # v. Conference / FDP organized (cap 5)
    org = payload.get('sec3_v_organized', [])
    raw_v = 0.0
    for o in org:
        if str(o.get('type', 'conference')).lower() == 'conference':
            raw_v += 5.0
        else:
            raw_v += float(o.get('days', 5) or 5) * 1.0
    score_v = min(raw_v, 5.0)
    breakdown['sec3_v'] = {'name': 'Conference / FDP Organized', 'items': org, 'score': score_v, 'max': 5}
    total_raw += score_v

    # vi. KSCST/IEI student project guidance (cap 2.5)
    kscst = payload.get('sec3_vi_kscst', [])
    score_vi = min(len(kscst) * 2.5, 2.5)
    breakdown['sec3_vi'] = {'name': 'KSCST/IEI Funded Student Project Guidance', 'items': kscst, 'score': score_vi, 'max': 2.5}
    total_raw += score_vi

    # vii. Seed grant / RA (cap 7.5)
    seed = payload.get('sec3_vii_seed_grant', [])
    score_vii = min(len(seed) * 7.5, 7.5)
    breakdown['sec3_vii'] = {'name': 'RNSIT Seed Grant / Research Assistant', 'items': seed, 'score': score_vii, 'max': 7.5}
    total_raw += score_vii

    # viii. URF/PRF funded projects (cap 5)
    urf = payload.get('sec3_viii_urf', [])
    score_viii = min(len(urf) * 5.0, 5.0)
    breakdown['sec3_viii'] = {'name': 'RNSIT URF/PRF Funded Projects', 'items': urf, 'score': score_viii, 'max': 5}
    total_raw += score_viii

    # ix. Student conference paper (5/paper; cap 10)
    student_pub = payload.get('sec3_ix_student_pub', [])
    score_ix = min(len(student_pub) * 5.0, 10.0)
    breakdown['sec3_ix'] = {'name': 'International Conference Paper by Students', 'items': student_pub, 'score': score_ix, 'max': 10}
    total_raw += score_ix

    # x. Mentoring hackathons (State: 2; Nat/Int: 3; cap 5)
    hackathons = payload.get('sec3_x_hackathons', [])
    raw_x = sum(3.0 if 'nat' in str(h.get('level', 'national')).lower() or 'int' in str(h.get('level', '')).lower() else 2.0 for h in hackathons)
    score_x = min(raw_x, 5.0)
    breakdown['sec3_x'] = {'name': 'Mentoring / Winning Hackathons', 'items': hackathons, 'score': score_x, 'max': 5}
    total_raw += score_x

    # xi. Automation software development & deployment (cap 10)
    automation = payload.get('sec3_xi_automation', [])
    score_xi = min(len(automation) * 10.0, 10.0)
    breakdown['sec3_xi'] = {'name': 'Automation Software Deployed by Interns', 'items': automation, 'score': score_xi, 'max': 10}
    total_raw += score_xi

    final_score = min(total_raw, 20.0)
    return {
        'section_name': 'Section III – Technical & Professional Activities',
        'max_marks': 20,
        'components': breakdown,
        'raw_total': round(total_raw, 2),
        'section_score': round(final_score, 2)
    }


# =========================================================================
# SECTION IV: ACADEMIC ADMINISTRATION (10 LINES)
# =========================================================================
def calculate_section_4(payload: Dict[str, Any]) -> Dict[str, Any]:
    responsibilities = payload.get('sec4_responsibilities', [])
    valid_count = len([r for r in responsibilities if r.get('role') or r.get('contribution')])
    return {
        'section_name': 'Section IV – Academic Administration Activities',
        'responsibilities': responsibilities,
        'count': valid_count,
        'max_marks': 20,
        'marks_awarded': min(float(payload.get('sec4_marks_awarded', 0) or 0), 20.0)
    }


# =========================================================================
# HOD & PRINCIPAL REVIEWS AND 100-MARK SCALING
# =========================================================================
def calculate_reviews_and_final_grade(
    sec1_score: float,
    sec2_score: float,
    sec3_score: float,
    hod_data: Dict[str, Any],
    principal_data: Dict[str, Any]
) -> Dict[str, Any]:
    subtotal_130 = min(sec1_score, 70.0) + min(sec2_score, 40.0) + min(sec3_score, 20.0)
    scaled_80 = (subtotal_130 / 130.0) * 80.0

    # HOD Evaluation (5 criteria, up to 3 each, max 15)
    hod_c1 = min(float(hod_data.get('discipline_attitude', 3) or 0), 3.0)
    hod_c2 = min(float(hod_data.get('academic_planning', 3) or 0), 3.0)
    hod_c3 = min(float(hod_data.get('dept_admin_support', 3) or 0), 3.0)
    hod_c4 = min(float(hod_data.get('accreditation_fdp', 3) or 0), 3.0)
    hod_c5 = min(float(hod_data.get('autonomous_support', 3) or 0), 3.0)
    hod_total = hod_c1 + hod_c2 + hod_c3 + hod_c4 + hod_c5

    # Principal Evaluation (5 criteria, up to 1 each, max 5)
    p_c1 = min(float(principal_data.get('vision_goal', 1) or 0), 1.0)
    p_c2 = min(float(principal_data.get('leadership_mgmt', 1) or 0), 1.0)
    p_c3 = min(float(principal_data.get('involvement_admin', 1) or 0), 1.0)
    p_c4 = min(float(principal_data.get('research_innovation', 1) or 0), 1.0)
    p_c5 = min(float(principal_data.get('overall_discipline', 1) or 0), 1.0)
    principal_total = p_c1 + p_c2 + p_c3 + p_c4 + p_c5

    grand_total = min(round(scaled_80 + hod_total + principal_total, 2), 100.0)

    if grand_total >= 91.0:
        grade = 'Excellent'
        badge_color = 'emerald'
    elif grand_total >= 81.0:
        grade = 'Very Good'
        badge_color = 'blue'
    elif grand_total >= 71.0:
        grade = 'Good'
        badge_color = 'indigo'
    elif grand_total >= 61.0:
        grade = 'Average'
        badge_color = 'amber'
    else:
        grade = 'Not Satisfactory'
        badge_color = 'rose'

    return {
        'subtotal_130': round(subtotal_130, 2),
        'scaled_80': round(scaled_80, 2),
        'hod_evaluation': {
            'total': round(hod_total, 2),
            'max': 15,
            'criteria': {
                'discipline_attitude': hod_c1,
                'academic_planning': hod_c2,
                'dept_admin_support': hod_c3,
                'accreditation_fdp': hod_c4,
                'autonomous_support': hod_c5
            },
            'remarks': hod_data.get('remarks', ''),
            'increment_recommended': hod_data.get('increment_recommended', True)
        },
        'principal_evaluation': {
            'total': round(principal_total, 2),
            'max': 5,
            'criteria': {
                'vision_goal': p_c1,
                'leadership_mgmt': p_c2,
                'involvement_admin': p_c3,
                'research_innovation': p_c4,
                'overall_discipline': p_c5
            },
            'remarks': principal_data.get('remarks', ''),
            'increment_approved': principal_data.get('increment_approved', True)
        },
        'grand_total_100': grand_total,
        'grade': grade,
        'badge_color': badge_color
    }


def calculate_complete_pbas(payload: Dict[str, Any]) -> Dict[str, Any]:
    sec1 = calculate_section_1(payload.get('section1', payload))
    sec2 = calculate_section_2(payload.get('section2', payload))
    sec3 = calculate_section_3(payload.get('section3', payload))
    sec4 = calculate_section_4(payload.get('section4', payload))
    
    summary = calculate_reviews_and_final_grade(
        sec1['section_score'],
        sec2['section_score'],
        sec3['section_score'],
        payload.get('hod_review', {}),
        payload.get('principal_review', {})
    )

    return {
        'section1': sec1,
        'section2': sec2,
        'section3': sec3,
        'section4': sec4,
        'summary': summary
    }
