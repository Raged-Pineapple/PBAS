# RNS HR System Entry — Exit (E2E)
### Unified Digital HR Platform | RNS Educational Institutions
**RNSIT Faculty Hackathon 2026 · Problem Statement 2 (Software Category)**  
**Team TechTrinity**: Dr. Uma S V, Dr. Leena Chandrashekar, Dr. Shruthi U, Dr. Swathi Darla, Ms. Ganga M S, Mr. Vyasaraj T

---

## 📌 Overview

The **RNS HR System E2E** is a unified digital web platform integrating four interconnected human resource portals into a single cohesive experience. Designed for all RNS educational institutions (RNSIT, PU College, First Grade College, and RNS School), it covers the complete faculty and staff lifecycle from initial hiring to final relieving settlement.

---

## 🏛️ The Four Integrated Portals

### 1. Onboarding & Offboarding Portal (Entry-to-Exit Lifecycle)
* **Route**: `/onboarding-offboarding/`
* **Description**: Manages the complete employment lifecycle from first day of service to final departure.
* **Key Features**:
  * **6-Step Onboarding Wizard**: Personal dossier, document verification, biometric ID generation, departmental allocation, and orientation tracking.
  * **8-Step Offboarding Workflow**: Resignation submission, notice period monitoring, asset handover, and handover verification.
  * **6 Department Clearances**: Multi-department no-dues signoffs (Library, Accounts, Department HoD, Laboratory, Central Store, and HR).
  * **Official Document Generation**: Instant generation of printable official **Relieving Letters** and **Experience Certificates** with verification tokens.

---

### 2. Faculty & Staff Leave Management Portal
* **Route**: `/leave/`
* **Description**: End-to-end leave application, workflow routing, and official quota tracking system.
* **Key Features**:
  * **Multi-Tier Approval Workflow**: Structured four-stage process: *Employee Application → HoD Recommendation → Principal Sanction → HR Record Update*.
  * **Leave Quota & Balance Tracking**: Live accounting of Casual Leave (CL), Earned Leave (EL), and Medical Leave (ML).
  * **Official Rule Enforcement**: Only final approval by the Principal triggers deduction from the employee's official leave balance; rejections allow faculty to modify and resubmit.
  * **Class Substitution Handover**: Requires nominating alternative faculty for lecture coverage prior to submission.
  * **LOP Conversion**: Excess leaves beyond available quotas are automatically flagged as Loss of Pay (LOP) and fed directly into payroll.

---

### 3. Salary Calculator & Monthly Payroll Portal
* **Route**: `/salary/`
* **Description**: 7th Central Pay Commission (CPC) salary computation and monthly payroll management engine.
* **Key Features**:
  * **Salary Computation Engine**: Calculates Basic Pay, Dearness Allowance (DA @ 50%), House Rent Allowance (HRA @ 20%), and Transport Allowance (TA).
  * **Statutory Deductions**: Deducts Employee Provident Fund (PF @ 12%), Professional Tax (PT), and Tax Deducted at Source (TDS).
  * **Dynamic LOP Integration**: Real-time salary adjustment based on unapproved leave days calculated by the Leave Management portal: `LOP Deduction = (Gross Salary ÷ 30) × LOP Days`.
  * **Interactive Calculator Sandbox**: Sliders for basic pay adjustments and live LOP day simulation.
  * **Official Printable Pay Slips**: Generates official institutional salary slips with earnings, deductions, bank details, and net pay disbursement.

---

### 4. Performance Based Appraisal System (PBAS) Portal
* **Route**: `/pbas/` (or `/faculty/`, `/hod/`, `/principal/`)
* **Description**: Annual self-appraisal and multi-tiered evaluation portal based on the 100-mark institutional appraisal framework.
* **Key Features**:
  * **Section I — Teaching Learning Process (70 Marks)**: Student feedback, academic results, funded activities, MOOCs/NPTEL, AI tools, and 20 innovative pedagogy methods.
  * **Section II — Research & Development (40 Marks)**: Indexed journal publications (Q1–Q4), research proposals, patents, and Ph.D. guidance.
  * **Section III — Technical & Professional Activities (20 Marks)**: Professional society memberships, certifications, and industry interaction.
  * **100-Mark Scale**: Sections I–III subtotal (130) scaled to 80 marks, combined with **HoD Evaluation (15 marks)** and **Principal Evaluation (5 marks)**.
  * **Evidence Management**: Evidence attachment modal with HoD verification, rejection feedback, and revision workflows.
  * **Official PDF Export**: Generates submission reports ready for NAAC/NBA accreditation.

---

## 👥 Role-Based Workspaces & Navigation Flow

The platform features a single **Unified Sign-In Portal** (`/login/`) that directs each authenticated user into a tailored workspace:

| Role | Default Landing | Primary Responsibilities |
|---|---|---|
| **Faculty Member** | Faculty Workspace | File PBAS self-appraisals, apply for leave, view leave balances, view monthly payslips, and check service dossier. |
| **Head of Department (HoD)** | HoD Review Desk | Evaluate departmental PBAS submissions (15 marks), action faculty leave applications, monitor departmental staffing and payroll. |
| **Principal / Director** | Executive Desk | Final authorization of PBAS appraisals (5 marks + final grade), final sanction of leaves (triggers balance deductions), signing exit clearances. |

---

## 🚀 Quick Start Guide

### Prerequisites
* Python 3.10+
* Django 5+ or 6+
* `python-dotenv`

### Installation & Execution
```powershell
# 1. Navigate to the project directory
cd d:\rnsitportal\PBAS

# 2. Install dependencies (if not already installed)
python -m pip install django python-dotenv

# 3. Apply database migrations
python manage.py migrate

# 4. Start the Django development server
python manage.py runserver 127.0.0.1:8000
```

Open **`http://127.0.0.1:8000/`** in your browser.

### Default Demo Credentials (Configured in `.env`)
* **Faculty**: `faculty` / `faculty123`
* **HoD**: `hod` / `hod123`
* **Principal**: `principal` / `principal123`

*(Fast 1-click login buttons are also available directly on the `/login/` screen for seamless demonstration)*

---

## 🛠️ Technology Stack
* **Backend**: Django 6.1 (Python MVC framework)
* **Frontend**: Tailwind CSS 3, FontAwesome 6, Inter & JetBrains Mono typography
* **Database**: SQLite3 (development) / PostgreSQL compatible
* **Architecture**: Modular Django apps (`onboarding_offboarding`, `leave_management`, `salary_payroll`, `section1`, `core_portal`) communicating via internal ORM and REST JSON endpoints.

---
*© 2026 RNS Educational Institutions · Developed by Team TechTrinity for RNSIT Faculty Hackathon 2026.*
