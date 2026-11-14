# RNSIT PBAS Digital Portal — Complete System (Sections I, II, III, IV, Reviews & 100-Mark Scale)

A complete, production-ready, modular web portal and calculation engine for the **RNSIT PBAS (Performance Based Appraisal System) Tracker - Assistant Professor**.

Built specifically for easy, seamless integration with projects using **Django** and **PHP**.

---

## 1. Overall Score Architecture

| Part / Section | Maximum Marks | Description / Key Components |
|---|---|---|
| **I. Teaching Learning Process** | **70** | Course feedback (max 30), results (max 20), own syllabus, funded activities, FDP, MOOCs, NPTEL, AI tools, 20 innovative TLP methods. |
| **II. Research & Development and Consultancy** | **40** | Q1/Q2/Q3/Q4 publications (cap 30), books, research proposals, funded projects (cap 20), consultancy, IPR/patents, Ph.D. guidance, immersion, startups, SIG. |
| **III. Technical & Professional Activities** | **20** | FDP attended outside, society memberships, COE/lab coordinator, global industry certs, organized events, KSCST guidance, seed grants, student papers, hackathons, automation software. |
| **Subtotal (I + II + III)** | **130** | Subtotal of verified marks from Sections I, II, and III. |
| **Scaled Score (out of 80)** | **80** | **Formula**: `(Subtotal ÷ 130) × 80` |
| **IV. Academic Administration** | **20** | 10 departmental responsibilities with specific measurable contributions and evidence. Evaluated by HOD / Principal. |
| **HOD Evaluation** | **15** | 5 criteria evaluated by HOD (3 marks each): Discipline, Academic Planning, Dept Admin, Accreditation/FDP, Autonomous Support. |
| **Principal Evaluation** | **05** | 5 criteria evaluated by Principal (1 mark each): Vision, Leadership, Academic Admin, Research & Innovation, Overall Discipline. |
| **Final Appraisal Score** | **100** | **Formula**: `Scaled Score (80) + HOD Evaluation (15) + Principal Evaluation (5)` |

### Official Grade Scale (out of 100)
- **Excellent**: 91 – 100
- **Very Good**: 81 – 90
- **Good**: 71 – 80
- **Average**: 61 – 70
- **Not Satisfactory**: 60 and below

---

## 2. Navigation Flow & Features

- **Top Section Navigation Bar**: Quick, 1-click navigation between:
  1. `Section I: Teaching Learning (70)`
  2. `Section II: R&D & Consultancy (40)`
  3. `Section III: Tech & Professional (20)`
  4. `Section IV: Administration (20)`
  5. `HOD & Principal Reviews (20)`
  6. `100-Mark Scale & Summary`
- **Previous / Next Section Buttons**: Smooth sequential navigation at the bottom of every section.
- **Sticky Live Header Banner**: Displays live scores for Sec I, Sec II, Sec III, the Grand Total out of 100, and current Performance Grade badge.
- **Evidence Upload Modal**: Click any "Upload / Proof / Cert / Paper PDF" button to attach files (PDF, DOCX, PNG, JPG).
- **Backend Calculation**: The "Calculate" button sends data to `/api/section1/calculate/` to evaluate every mathematical formula, ceiling, and cap.
- **Save Draft / Final**: Saves the entire submission with linked evidence into the SQLite database.
- **JSON Export**: Provides instant REST JSON export for external consumption by PHP or Django microservices.

---

## 3. How to Run the Portal

```powershell
cd d:\PBAS
python manage.py runserver 127.0.0.1:8000
```
Open **`http://127.0.0.1:8000/`** in your browser.

---

## 4. Dual Integration with Django & PHP

### A. Django Integration
- The entire application lives inside the modular Django app `section1/` and calculation engine `pbas_engine/`.
- Add `'section1.apps.Section1Config'` to `INSTALLED_APPS` and include `path('pbas/', include('section1.urls'))` in your project's `urls.py`.

### B. PHP Integration
- **Option 1 (Native PHP Engine)**: Use `php_integration/PBASComprehensiveCalculator.php` to calculate all sections natively in PHP without running Python:
  ```php
  require_once 'php_integration/PBASComprehensiveCalculator.php';
  $result = PBASComprehensiveCalculator::calculateCompletePBAS($formData);
  echo "Grand Score: " . $result['summary']['grand_total_100'] . " / 100";
  ```
- **Option 2 (REST API Client)**: Call the Django API endpoint `/api/section1/calculate/` using `php_integration/PBASApiClient.php`.
