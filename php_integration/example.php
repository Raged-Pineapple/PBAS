<?php
/**
 * Example demonstrating how to use PBAS Section 1 in PHP:
 * Option 1: Native PHP Calculation Engine
 * Option 2: Connecting to Django REST API
 */

require_once __DIR__ . '/Section1Calculator.php';
require_once __DIR__ . '/PBASApiClient.php';

echo "=== PBAS Section 1 PHP Integration Demo ===\n\n";

// Sample submission data for Section 1
$sampleData = [
    'odd_feedback_courses' => [
        ['course_name' => 'BCS301 - Data Structures', 'round_1' => 88.0, 'round_2' => 92.0],
        ['course_name' => 'BCS302 - Operating Systems', 'round_1' => 82.0, 'round_2' => 86.0]
    ],
    'even_feedback_courses' => [
        ['course_name' => 'BCS401 - Algorithms', 'round_1' => 90.0, 'round_2' => 94.0]
    ],
    'odd_results_courses' => [
        ['course_name' => 'BCS301 - Data Structures', 'appeared' => 64, 'passed' => 61]
    ],
    'even_results_courses' => [
        ['course_name' => 'BCS401 - Algorithms', 'appeared' => 62, 'passed' => 59]
    ],
    'other_tlp_c' => [
        'c_ii_own_syllabus' => [
            ['title' => 'Advanced Cloud Computing']
        ],
        'c_v_online_completed' => [
            ['title' => 'Deep Learning Specialization', 'duration_hours' => 45]
        ],
        'c_vi_nptel' => [
            ['title' => 'Cloud Computing', 'duration_weeks' => 8, 'grade_type' => 'elite_gold']
        ],
        'c_ix_ai_tools' => [
            ['tool_name' => 'GitHub Copilot for Code Analysis'],
            ['tool_name' => 'ChatGPT for Prompt-Based Assessments']
        ],
        'c_x_tlp_methods' => [
            'Flipped Classroom',
            'Mini Projects',
            'Peer Learning'
        ]
    ]
];

// Option 1: Native PHP Calculation
echo "--- OPTION 1: Native PHP Calculation ---\n";
$result = Section1Calculator::calculateSection1($sampleData);
echo "Feedback Marks (Max 30): " . $result['feedback_a']['marks_awarded'] . "\n";
echo "Results Marks (Max 20): " . $result['results_b']['marks_awarded'] . "\n";
echo "Total Course Feedback & Results (Max 50): " . $result['total_ab']['score_awarded'] . "\n";
echo "Other TLP Components C Score: " . $result['other_tlp_c']['total_c_score'] . "\n";
echo "FINAL SECTION 1 SCORE (Max 70): " . $result['section1_total']['final_score'] . " / 70\n\n";

// Option 2: Django REST API (when Django server is running)
echo "--- OPTION 2: Via Django API Client ---\n";
echo "Use PBASApiClient:\n";
echo "\$client = new PBASApiClient('http://127.0.0.1:8000');\n";
echo "\$apiResult = \$client->calculateSection1(\$sampleData);\n";
