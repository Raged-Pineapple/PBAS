<?php
/**
 * RNSIT PBAS (Performance Based Appraisal System)
 * Native PHP Comprehensive Calculation Engine for All Sections (I, II, III, IV, Reviews, 100-mark Scaling)
 */

class PBASComprehensiveCalculator {

    public static function roundUpFraction(float $val): int {
        return (int) ceil($val);
    }

    // SECTION I
    public static function calculateSection1(array $payload): array {
        // Feedback A
        $oddFb = $payload['odd_feedback_courses'] ?? [];
        $evenFb = $payload['even_feedback_courses'] ?? [];

        $calcSemFb = function($courses) {
            $sum = 0; $count = 0;
            foreach ($courses as $c) {
                $r = [];
                if (isset($c['round_1']) && trim((string)$c['round_1']) !== '') $r[] = (float)$c['round_1'];
                if (isset($c['round_2']) && trim((string)$c['round_2']) !== '') $r[] = (float)$c['round_2'];
                if (count($r) > 0) {
                    $sum += (array_sum($r) / count($r));
                    $count++;
                }
            }
            return $count > 0 ? ($sum / $count) : 0.0;
        };
        $a1 = $calcSemFb($oddFb);
        $a2 = $calcSemFb($evenFb);
        $combA = ($a1 > 0 && $a2 > 0) ? (($a1 + $a2) / 2) : max($a1, $a2);
        $marksA = min(self::roundUpFraction(($combA * 30.0) / 100.0), 30);

        // Results B
        $oddRes = $payload['odd_results_courses'] ?? [];
        $evenRes = $payload['even_results_courses'] ?? [];

        $calcSemRes = function($courses) {
            $sum = 0; $count = 0;
            foreach ($courses as $c) {
                $app = (float)($c['appeared'] ?? 0);
                $pass = (float)($c['passed'] ?? 0);
                if ($app > 0) {
                    $sum += (($pass / $app) * 100.0);
                    $count++;
                }
            }
            return $count > 0 ? ($sum / $count) : 0.0;
        };
        $b1 = $calcSemRes($oddRes);
        $b2 = $calcSemRes($evenRes);
        $combB = ($b1 > 0 && $b2 > 0) ? (($b1 + $b2) / 2) : max($b1, $b2);
        $marksB = min(self::roundUpFraction(($combB * 20.0) / 100.0), 20);

        $marksAB = min($marksA + $marksB, 50);

        // Other TLP C
        $cData = $payload['other_tlp_c'] ?? [];
        $scoreC = 0.0;

        $scoreC += min(count($cData['c_ii_own_syllabus'] ?? []) * 5.0, 10.0);

        $fundRaw = 0;
        foreach ($cData['c_iii_funded_activities'] ?? [] as $f) {
            $amt = (float)($f['funding_amount'] ?? 0);
            $role = strtoupper((string)($f['role'] ?? 'PI'));
            if ($amt >= 100000) {
                $fundRaw += ($amt / 100000.0) * (strpos($role, 'CO') === false ? 2.0 : 1.0);
            }
        }
        $scoreC += min($fundRaw, 10.0);
        $scoreC += min(count($cData['c_iv_org_fdp'] ?? []) * 10.0, 10.0);

        $vCount = 0;
        foreach ($cData['c_v_online_completed'] ?? [] as $oc) {
            if ((float)($oc['duration_hours'] ?? 0) >= 30) $vCount++;
        }
        $scoreC += min($vCount * 2.5, 10.0);

        $nptelRaw = 0;
        $gMap = ['completed' => 5.0, 'elite' => 6.0, 'elite_silver' => 8.0, 'elite_gold' => 10.0];
        foreach ($cData['c_vi_nptel'] ?? [] as $np) {
            $g = str_replace([' ', '+'], ['_', '_'], strtolower((string)($np['grade_type'] ?? 'completed')));
            $nptelRaw += $gMap[$g] ?? 5.0;
        }
        $scoreC += min($nptelRaw, 10.0);

        $devRaw = 0;
        foreach ($cData['c_vii_courses_developed'] ?? [] as $cd) {
            $pt = strtolower((string)($cd['platform_type'] ?? ''));
            $devRaw += (strpos($pt, 'youtube') !== false || strpos($pt, 'rnsit') !== false) ? 5.0 : 10.0;
        }
        $scoreC += min($devRaw, 10.0);

        $rpRaw = 0;
        foreach ($cData['c_viii_resource_person'] ?? [] as $rp) {
            $rpRaw += (strpos(strtolower((string)($rp['type'] ?? '')), 'prof') !== false) ? 10.0 : 5.0;
        }
        $scoreC += min($rpRaw, 10.0);
        $scoreC += min(count($cData['c_ix_ai_tools'] ?? []) * 2.5, 5.0);
        $scoreC += min(count($cData['c_x_tlp_methods'] ?? []) * 2.5, 10.0);

        $finalScore = min($marksAB + $scoreC, 70.0);

        return [
            'section_name' => 'Section I – Teaching Learning Process',
            'max_marks' => 70,
            'feedback_marks_a' => $marksA,
            'results_marks_b' => $marksB,
            'total_ab' => $marksAB,
            'other_tlp_c' => round($scoreC, 2),
            'section_score' => round($finalScore, 2)
        ];
    }

    // SECTION II
    public static function calculateSection2(array $payload): array {
        $totalRaw = 0.0;

        // i. Invited talks (2.5/act; cap 5)
        $totalRaw += min(count($payload['sec2_i_talks'] ?? []) * 2.5, 5.0);

        // ii. Publications (cap 30)
        $rates = [
            'q1' => [20.0, 10.0],
            'q2' => [15.0, 7.5],
            'q3' => [12.5, 6.25],
            'q4' => [10.0, 5.0],
            'conf' => [5.0, 2.5]
        ];
        $pubRaw = 0.0;
        foreach ($payload['sec2_ii_publications'] ?? [] as $p) {
            $cat = strtolower((string)($p['category'] ?? 'q4'));
            $order = (int)($p['author_order'] ?? 1);
            $r = $rates[$cat] ?? [10.0, 5.0];
            $pubRaw += ($order <= 2) ? $r[0] : $r[1];
        }
        $totalRaw += min($pubRaw, 30.0);

        // iii. Books / chapters (cap 5)
        $totalRaw += min(count($payload['sec2_iii_books'] ?? []) * 2.5, 5.0);

        // iv. Proposals (cap 5)
        $totalRaw += min(count($payload['sec2_iv_proposals'] ?? []) * 5.0, 5.0);

        // v. Funded projects (cap 20)
        $projRaw = 0.0;
        foreach ($payload['sec2_v_projects'] ?? [] as $pr) {
            $amt = (float)($pr['funding_amount'] ?? 0);
            $mult = (strpos(strtoupper((string)($pr['role'] ?? 'PI')), 'CO') !== false) ? 0.60 : 1.0;
            if ($amt > 1000000) $projRaw += 20.0 * $mult;
            elseif ($amt >= 500000) $projRaw += 15.0 * $mult;
            elseif ($amt >= 100000) $projRaw += 5.0 * $mult;
        }
        $totalRaw += min($projRaw, 20.0);

        // vi. Consultancy (cap 10)
        $conRaw = 0.0;
        foreach ($payload['sec2_vi_consultancy'] ?? [] as $c) {
            $conRaw += ((float)($c['consultancy_amount'] ?? 0) > 500000) ? 10.0 : 5.0;
        }
        $totalRaw += min($conRaw, 10.0);

        // vii. Patents (cap 10)
        $patRaw = 0.0;
        foreach ($payload['sec2_vii_patents'] ?? [] as $pt) {
            $patRaw += (strtolower((string)($pt['status'] ?? 'granted')) === 'granted') ? 10.0 : 5.0;
        }
        $totalRaw += min($patRaw, 10.0);

        // viii. PhD (cap 10)
        $phdRaw = 0.0;
        foreach ($payload['sec2_viii_phd'] ?? [] as $phd) {
            $role = strtolower((string)($phd['role'] ?? 'guide'));
            $stat = strtolower((string)($phd['status'] ?? 'awarded'));
            if (strpos($role, 'co') !== false) {
                $phdRaw += 5.0;
            } else {
                $phdRaw += (strpos($stat, 'award') !== false || strpos($stat, 'full') !== false) ? 10.0 : 5.0;
            }
        }
        $totalRaw += min($phdRaw, 10.0);

        // ix. Immersion (cap 10)
        $immRaw = 0.0;
        foreach ($payload['sec2_ix_immersion'] ?? [] as $im) {
            $immRaw += min(((float)($im['weeks'] ?? 4)) * 2.5, 10.0);
        }
        $totalRaw += min($immRaw, 10.0);

        // x. Startups (cap 10)
        $totalRaw += min(count($payload['sec2_x_startups'] ?? []) * 10.0, 10.0);

        // xi. SIG (cap 5)
        $totalRaw += min(count($payload['sec2_xi_sig'] ?? []) * 5.0, 5.0);

        return [
            'section_name' => 'Section II – Research & Development and Consultancy Work',
            'max_marks' => 40,
            'raw_total' => round($totalRaw, 2),
            'section_score' => round(min($totalRaw, 40.0), 2)
        ];
    }

    // SECTION III
    public static function calculateSection3(array $payload): array {
        $totalRaw = 0.0;

        // i. FDP Attended Outside (cap 5)
        $fdpRaw = 0.0;
        foreach ($payload['sec3_i_fdp_attended'] ?? [] as $it) {
            $days = (float)($it['days'] ?? 5);
            $lvl = strtolower((string)($it['level'] ?? 'national'));
            $fdpRaw += $days * ((strpos($lvl, 'nat') !== false || strpos($lvl, 'int') !== false) ? 1.0 : 0.5);
        }
        $totalRaw += min($fdpRaw, 5.0);

        // ii. Membership (cap 2.5)
        $totalRaw += count($payload['sec3_ii_memberships'] ?? []) > 0 ? 2.5 : 0.0;

        // iii. Coordinator COE (cap 5)
        $totalRaw += min(count($payload['sec3_iii_coe'] ?? []) * 5.0, 5.0);

        // iv. Certifications (cap 10)
        $totalRaw += min(count($payload['sec3_iv_certifications'] ?? []) * 10.0, 10.0);

        // v. Organized (cap 5)
        $orgRaw = 0.0;
        foreach ($payload['sec3_v_organized'] ?? [] as $o) {
            $orgRaw += (strtolower((string)($o['type'] ?? 'conference')) === 'conference') ? 5.0 : (((float)($o['days'] ?? 5)) * 1.0);
        }
        $totalRaw += min($orgRaw, 5.0);

        // vi. KSCST (cap 2.5)
        $totalRaw += min(count($payload['sec3_vi_kscst'] ?? []) * 2.5, 2.5);

        // vii. Seed grant (cap 7.5)
        $totalRaw += min(count($payload['sec3_vii_seed_grant'] ?? []) * 7.5, 7.5);

        // viii. URF/PRF (cap 5)
        $totalRaw += min(count($payload['sec3_viii_urf'] ?? []) * 5.0, 5.0);

        // ix. Student publication (cap 10)
        $totalRaw += min(count($payload['sec3_ix_student_pub'] ?? []) * 5.0, 10.0);

        // x. Hackathons (cap 5)
        $hRaw = 0.0;
        foreach ($payload['sec3_x_hackathons'] ?? [] as $h) {
            $lvl = strtolower((string)($h['level'] ?? 'national'));
            $hRaw += (strpos($lvl, 'nat') !== false || strpos($lvl, 'int') !== false) ? 3.0 : 2.0;
        }
        $totalRaw += min($hRaw, 5.0);

        // xi. Automation (cap 10)
        $totalRaw += min(count($payload['sec3_xi_automation'] ?? []) * 10.0, 10.0);

        return [
            'section_name' => 'Section III – Technical & Professional Activities',
            'max_marks' => 20,
            'raw_total' => round($totalRaw, 2),
            'section_score' => round(min($totalRaw, 20.0), 2)
        ];
    }

    // SECTION IV & GRAND EVALUATION
    public static function calculateCompletePBAS(array $payload): array {
        $sec1 = self::calculateSection1($payload['section1'] ?? $payload);
        $sec2 = self::calculateSection2($payload['section2'] ?? $payload);
        $sec3 = self::calculateSection3($payload['section3'] ?? $payload);

        $subtotal130 = $sec1['section_score'] + $sec2['section_score'] + $sec3['section_score'];
        $scaled80 = ($subtotal130 / 130.0) * 80.0;

        $hod = $payload['hod_review'] ?? [];
        $hodTotal = min((float)($hod['discipline_attitude'] ?? 3), 3.0)
                  + min((float)($hod['academic_planning'] ?? 3), 3.0)
                  + min((float)($hod['dept_admin_support'] ?? 3), 3.0)
                  + min((float)($hod['accreditation_fdp'] ?? 3), 3.0)
                  + min((float)($hod['autonomous_support'] ?? 3), 3.0);

        $p = $payload['principal_review'] ?? [];
        $pTotal = min((float)($p['vision_goal'] ?? 1), 1.0)
                + min((float)($p['leadership_mgmt'] ?? 1), 1.0)
                + min((float)($p['involvement_admin'] ?? 1), 1.0)
                + min((float)($p['research_innovation'] ?? 1), 1.0)
                + min((float)($p['overall_discipline'] ?? 1), 1.0);

        $grandTotal = min(round($scaled80 + $hodTotal + $pTotal, 2), 100.0);

        if ($grandTotal >= 91.0) $grade = 'Excellent';
        elseif ($grandTotal >= 81.0) $grade = 'Very Good';
        elseif ($grandTotal >= 71.0) $grade = 'Good';
        elseif ($grandTotal >= 61.0) $grade = 'Average';
        else $grade = 'Not Satisfactory';

        return [
            'section1' => $sec1,
            'section2' => $sec2,
            'section3' => $sec3,
            'summary' => [
                'subtotal_130' => round($subtotal130, 2),
                'scaled_80' => round($scaled80, 2),
                'hod_total' => round($hodTotal, 2),
                'principal_total' => round($pTotal, 2),
                'grand_total_100' => $grandTotal,
                'grade' => $grade
            ]
        ];
    }
}
