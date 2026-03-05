# 🏥 Hospital Management System

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![SQLite](https://img.shields.io/badge/SQLite-3-lightblue?style=flat-square&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

A fully-featured **Hospital Management System** built with Python and SQLite. Covers database design, relational modeling, CRUD operations, stored views, and analytical SQL queries across 10 interlinked tables.

---

## 📐 Database Schema

```
departments ──< doctors ──< appointments >── patients
                    │                            │
                    └──< admissions >────────────┤
                                                 │
               patients >── medical_records      │
               patients >── bills ───────────────┘
               medical_records >── prescriptions >── medicines
               departments ──< staff
```

**10 tables:** `departments`, `doctors`, `patients`, `appointments`, `admissions`, `medical_records`, `medicines`, `prescriptions`, `bills`, `staff`

**3 views:** `v_patient_summary`, `v_doctor_workload`, `v_revenue_summary`

---

## ✨ Features

- **Database Design** — Normalized schema with FK constraints, indexes, and CHECK constraints
- **Seed Data** — 120 patients, 10 doctors, 300 appointments, 80 admissions, 150 bills, 200 records
- **CRUD Operations** — Add patients, book appointments, admit/discharge, create bills
- **Analytics Queries** — 20+ production-grade SQL queries covering all business areas
- **CLI Reports** — Formatted terminal reports using `tabulate`

### Reports Available
| Report | Description |
|--------|-------------|
| Dashboard | Live KPI summary |
| Appointments | Recent + upcoming with status |
| Active Admissions | Current inpatients with days admitted |
| Monthly Revenue | Gross, collected, outstanding per month |
| Doctor Workload | Appointments, admissions, completion rate |
| Top Diagnoses | Most common conditions |
| Outstanding Balances | Patients with unpaid bills |
| Low Stock | Medicines below reorder level |
| Patient Summary | Full journey per patient |

---

## 🚀 Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/hospital-management-system.git
cd hospital-management-system

pip install -r requirements.txt

# 1. Create & seed the database
python seed.py

# 2. Run the full demo (CRUD + all reports)
python app.py

# 3. Explore raw SQL queries
sqlite3 hospital.db < queries.sql
# or open hospital.db in DB Browser for SQLite
```

---

## 🗂️ Project Structure

```
hospital-management-system/
│
├── schema.sql       # DDL — all tables, indexes, views
├── seed.py          # Populates DB with realistic sample data
├── queries.sql      # 20+ analytical SQL queries
├── app.py           # Python CLI — CRUD + reporting
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech Stack

- **SQLite 3** — Embedded relational database
- **Python sqlite3** — Standard library DB interface
- **tabulate** — Terminal table formatting

---

## 📊 Sample Queries Covered

- Patient age group & blood group distribution
- Appointment trend analysis (monthly, by day of week)
- Doctor performance & completion rates
- Average length of stay per department
- Revenue by payment method & department
- Most prescribed medicines + pharmacy revenue
- Payroll breakdown by department

---

## 📄 License

MIT License
