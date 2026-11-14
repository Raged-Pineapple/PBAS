<?php
/**
 * RNSIT PBAS (Performance Based Appraisal System)
 * Section I: Teaching Learning Process (Maximum 70 marks)
 * Native PHP Calculation Engine
 */

class Section1Calculator {

    public static function roundUpFraction(float $val): int {
        return (int) ceil($val);
    }

    public static function calculateFeedbackA(array $oddCourses, array $evenCourses): array {
        $processCourses = function($courses) {
            $details = [];
            $totalAvg = 0.0;
            $validCount = 0;

            foreach ($courses as $c) {
                $cName = trim($c['course_name'] ?? '');
                $r1 = $c['round_1'] ?? null;
                $r2 = $c['round_2'] ?? null;

                $rounds = [];
                if ($r1 !== null && trim((string)$r1) !== '') {
                    $rounds[] = (float)$r1;
                }
                if ($r2 !== null && trim((string)$r2) !== '') {
                    $rounds[] = (float)$r2;
                }

                $courseAvg = count($rounds) > 0 ? (array_sum($rounds) / count($rounds)) : 0.0;
                if (count($rounds) > 0) {
                    $totalAvg += $courseAvg;
                    $validCount++;
                }

                $details[] = [
                    'course_name' => $cName,
                    'round_1' => $r1,
                    'round_2' => $r2,
                    'rounds_count' => count($rounds),
                    'average' => round($courseAvg, 2),
                    'evidence_file' => $c['evidence_file'] ?? ''
                ];
            }

            $semAvg = $validCount > 0 ? ($totalAvg / $validCount) : 0.0;
            return [round($semAvg, 2), $details];
        };

        list($a1Avg, $a1Details) = $processCourses($oddCourses);
        list($a2Avg, $a2Details) = $processCourses($evenCourses);

        if ($a1Avg > 0 && $a2Avg > 0) {
            $combinedAvg = ($a1Avg + $a2Avg) / 2.0;
        } elseif ($a1Avg > 0) {
            $combinedAvg = $a1Avg;
        } elseif ($a2Avg > 0) {
            $combinedAvg = $a2Avg;
        } else {
            $combinedAvg = 0.0;
        }

        $rawMarks = ($combinedAvg * 30.0) / 100.0;
        $marksA = min(self::roundUpFraction($rawMarks), 30);

        return [
            'a1_odd_sem_average' => round($a1Avg, 2),
            'a1_details' => $a1Details,
            'a2_even_sem_average' => round($a2Avg, 2),
            'a2_details' => $a2Details,
            'combined_feedback_average' => round($combinedAvg, 2),
            'raw_marks' => round($rawMarks, 2),
            'marks_awarded' => $marksA,
            'max_marks' => 30
        ];
    }

    public static function calculateResultsB(array $oddCourses, array $evenCourses): array {
        $processCourses = function($courses) {
            $details = [];
            $totalPct = 0.0;
            $validCount = 0;

            foreach ($courses as $c) {
                $cName = trim($c['course_name'] ?? '');
                $appeared = (float)($c['appeared'] ?? 0);
                $passed = (float)($c['passed'] ?? 0);

                $passPct = $appeared > 0 ? (($passed / $appeared) * 100.0) : 0.0;
                if ($appeared > 0) {
                    $totalPct += $passPct;
                    $validCount++;
                }

                $details[] = [
                    'course_name' => $cName,
                    'appeared' => (int)$appeared,
                    'passed' => (int)$passed,
                    'pass_percentage' => round($passPct, 2),
                    'evidence_file' => $c['evidence_file'] ?? ''
                ];
            }

            $semAvg = $validCount > 0 ? ($totalPct / $validCount) : 0.0;
            return [round($semAvg, 2), $details];
        };

        list($b1Avg, $b1Details) = $processCourses($oddCourses);
        list($b2Avg, $b2Details) = $processCourses($evenCourses);

        if ($b1Avg > 0 && $b2Avg > 0) {
            $combinedAvg = ($b1Avg + $b2Avg) / 2.0;
        } elseif ($b1Avg > 0) {
            $combinedAvg = $b1Avg;
        } elseif ($b2Avg > 0) {
            $combinedAvg = $b2Avg;
        } else {
            $combinedAvg = 0.0;
        }

        $rawMarks = ($combinedAvg * 20.0) / 100.0;
        $marksB = min(self::roundUpFraction($rawMarks), 20);

        return [
            'b1_odd_sem_average' => round($b1Avg, 2),
            'b1_details' => $b1Details,
            'b2_even_sem_average' => round($b2Avg, 2),
            'b2_details' => $b2Details,
            'combined_results_average' => round($combinedAvg, 2),
            'raw_marks' => round($rawMarks, 2),
            'marks_awarded' => $marksB,
            'max_marks' => 20
        ];
    }

    public static function calculateOtherTLPC(array $cData): array {
        $breakdown = [];
        $totalC = 0.0;

        // ii. Own syllabus (Max 10, 5/course)
        $syllabus = $cData['c_ii_own_syllabus'] ?? [];
        $countIi = count($syllabus);
        $rawIi = $countIi * 5.0;
        $scoreIi = min($rawIi, 10.0);
        $breakdown['c_ii'] = [
            'name' => 'Own syllabus for core subjects',
            'rate' => '5 marks per course (Max 10)',
            'items' => $syllabus,
            'count' => $countIi,
            'raw_score' => $rawIi,
            'score' => $scoreIi,
            'max' => 10
        ];
        $totalC += $scoreIi;

        // iii. External funded (PI: 2/₹1L, Co-PI: 1/₹1L; min ₹1L; Cap 10)
        $funded = $cData['c_iii_funded_activities'] ?? [];
        $rawIii = 0.0;
        foreach ($funded as $act) {
            $amt = (float)($act['funding_amount'] ?? 0);
            $role = strtoupper(trim((string)($act['role'] ?? 'PI')));
            if ($amt >= 100000) {
                $lakhs = $amt / 100000.0;
                $rate = (strpos($role, 'CO') === false) ? 2.0 : 1.0;
                $rawIii += $lakhs * $rate;
            }
        }
        $scoreIii = min($rawIii, 10.0);
        $breakdown['c_iii'] = [
            'name' => 'External funded academic activity',
            'rate' => 'PI: 2 marks/₹1L; Co-PI: 1 mark/₹1L (Min ₹1L, Max 10)',
            'items' => $funded,
            'raw_score' => round($rawIii, 2),
            'score' => round($scoreIii, 2),
            'max' => 10
        ];
        $totalC += $scoreIii;

        // iv. Organizing FDP NIRF (10 marks/activity; min ₹1L; Cap 10)
        $fdps = $cData['c_iv_org_fdp'] ?? [];
        $rawIv = 0.0;
        foreach ($fdps as $fdp) {
            $amt = (float)($fdp['funding_amount'] ?? 0);
            if ($amt >= 100000 || !empty($fdp['is_eligible'])) {
                $rawIv += 10.0;
            }
        }
        $scoreIv = min($rawIv, 10.0);
        $breakdown['c_iv'] = [
            'name' => 'Organizing FDP with national-importance/NIRF institution',
            'rate' => '10 marks per activity (Min ₹1L, Max 10)',
            'items' => $fdps,
            'raw_score' => $rawIv,
            'score' => $scoreIv,
            'max' => 10
        ];
        $totalC += $scoreIv;

        // v. Online courses completed >=30 hrs (2.5/course; Cap 10)
        $onlineComp = $cData['c_v_online_completed'] ?? [];
        $validV = 0;
        foreach ($onlineComp as $oc) {
            if ((float)($oc['duration_hours'] ?? 0) >= 30) {
                $validV++;
            }
        }
        $rawV = $validV * 2.5;
        $scoreV = min($rawV, 10.0);
        $breakdown['c_v'] = [
            'name' => 'Online courses completed (>= 30 hours)',
            'rate' => '2.5 marks per course (Max 10)',
            'items' => $onlineComp,
            'valid_count' => $validV,
            'raw_score' => $rawV,
            'score' => $scoreV,
            'max' => 10
        ];
        $totalC += $scoreV;

        // vi. NPTEL completed (Completed: 5, Elite: 6, Elite+Silver: 8, Elite+Gold: 10; Cap 10)
        $nptel = $cData['c_vi_nptel'] ?? [];
        $rawVi = 0.0;
        $gradeMap = ['completed' => 5.0, 'elite' => 6.0, 'elite_silver' => 8.0, 'elite_gold' => 10.0];
        foreach ($nptel as $it) {
            $weeks = (float)($it['duration_weeks'] ?? 0);
            $grade = str_replace([' ', '+'], ['_', '_'], strtolower((string)($it['grade_type'] ?? 'completed')));
            if ($weeks >= 4 || !empty($it['is_eligible'])) {
                $rawVi += $gradeMap[$grade] ?? 5.0;
            }
        }
        $scoreVi = min($rawVi, 10.0);
        $breakdown['c_vi'] = [
            'name' => 'NPTEL online courses completed (>= 4 weeks)',
            'rate' => 'Completed: 5; Elite: 6; Elite+Silver: 8; Elite+Gold: 10 (Max 10)',
            'items' => $nptel,
            'raw_score' => $rawVi,
            'score' => $scoreVi,
            'max' => 10
        ];
        $totalC += $scoreVi;

        // vii. Online courses developed (External: 10, RNSIT YouTube: 5; Cap 10)
        $coursesDev = $cData['c_vii_courses_developed'] ?? [];
        $rawVii = 0.0;
        foreach ($coursesDev as $cd) {
            $ptype = strtolower((string)($cd['platform_type'] ?? 'external'));
            if (strpos($ptype, 'youtube') !== false || strpos($ptype, 'rnsit') !== false) {
                $rawVii += 5.0;
            } else {
                $rawVii += 10.0;
            }
        }
        $scoreVii = min($rawVii, 10.0);
        $breakdown['c_vii'] = [
            'name' => 'Online courses developed',
            'rate' => 'External platforms: 10 marks; RNSIT YouTube: 5 marks (Max 10)',
            'items' => $coursesDev,
            'raw_score' => $rawVii,
            'score' => $scoreVii,
            'max' => 10
        ];
        $totalC += $scoreVii;

        // viii. Resource person (Summer internship: 5, Prof Courses: 10; min 18 hrs; Cap 10)
        $resources = $cData['c_viii_resource_person'] ?? [];
        $rawViii = 0.0;
        foreach ($resources as $rp) {
            $hours = (float)($rp['hours'] ?? 0);
            $rtype = strtolower((string)($rp['type'] ?? 'internship'));
            if ($hours >= 18 || !empty($rp['is_eligible'])) {
                $rawViii += (strpos($rtype, 'prof') !== false) ? 10.0 : 5.0;
            }
        }
        $scoreViii = min($rawViii, 10.0);
        $breakdown['c_viii'] = [
            'name' => 'Resource person for summer internship / professional courses',
            'rate' => 'Summer internship: 5 marks; Professional courses: 10 marks (Min 18 hrs, Max 10)',
            'items' => $resources,
            'raw_score' => $rawViii,
            'score' => $scoreViii,
            'max' => 10
        ];
        $totalC += $scoreViii;

        // ix. AI tools (2.5/tool; Cap 5)
        $aiTools = $cData['c_ix_ai_tools'] ?? [];
        $rawIx = count($aiTools) * 2.5;
        $scoreIx = min($rawIx, 5.0);
        $breakdown['c_ix'] = [
            'name' => 'Use of AI tools in teaching-learning process',
            'rate' => '2.5 marks per AI tool (Max 5)',
            'items' => $aiTools,
            'count' => count($aiTools),
            'raw_score' => $rawIx,
            'score' => $scoreIx,
            'max' => 5
        ];
        $totalC += $scoreIx;

        // x. Innovative TLP methods (2.5/method; Cap 10)
        $tlpMethods = $cData['c_x_tlp_methods'] ?? [];
        $rawX = count($tlpMethods) * 2.5;
        $scoreX = min($rawX, 10.0);
        $breakdown['c_x'] = [
            'name' => 'Innovative teaching-learning methods in classroom/laboratory',
            'rate' => '2.5 marks per method (Max 10)',
            'methods_selected' => $tlpMethods,
            'count' => count($tlpMethods),
            'raw_score' => $rawX,
            'score' => $scoreX,
            'max' => 10
        ];
        $totalC += $scoreX;

        return [
            'components' => $breakdown,
            'total_c_raw' => round($totalC, 2),
            'total_c_score' => round($totalC, 2)
        ];
    }

    public static function calculateSection1(array $payload): array {
        $feedbackResult = self::calculateFeedbackA(
            $payload['odd_feedback_courses'] ?? [],
            $payload['even_feedback_courses'] ?? []
        );

        $resultsResult = self::calculateResultsB(
            $payload['odd_results_courses'] ?? [],
            $payload['even_results_courses'] ?? []
        );

        $rawAb = $feedbackResult['marks_awarded'] + $resultsResult['marks_awarded'];
        $scoreAb = min($rawAb, 50);

        $cResult = self::calculateOtherTLPC($payload['other_tlp_c'] ?? []);
        $scoreC = $cResult['total_c_score'];

        $rawSection1Total = $scoreAb + $scoreC;
        $finalSection1Score = min($rawSection1Total, 70);

        return [
            'section_name' => 'Section I – Teaching Learning Process',
            'max_marks' => 70,
            'feedback_a' => $feedbackResult,
            'results_b' => $resultsResult,
            'total_ab' => [
                'formula' => 'min(Marks A (max 30) + Marks B (max 20), 50)',
                'raw_marks' => $rawAb,
                'score_awarded' => $scoreAb,
                'max_marks' => 50
            ],
            'other_tlp_c' => $cResult,
            'section1_total' => [
                'formula' => 'min(Score (A + B) + Score C, 70)',
                'raw_total' => round($rawSection1Total, 2),
                'final_score' => round($finalSection1Score, 2),
                'max_marks' => 70
            ]
        ];
    }
}
