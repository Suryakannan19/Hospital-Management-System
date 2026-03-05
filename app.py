"""
app.py — Hospital Management System CLI
Demonstrates Python + SQLite integration with CRUD operations and reporting.
"""

import sqlite3
import os
from datetime import date
from tabulate import tabulate

DB_PATH = "hospital.db"


def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def print_table(rows, headers="keys"):
    if not rows:
        print("  (no results)\n")
        return
    data = [dict(r) for r in rows]
    print(tabulate(data, headers="keys", tablefmt="rounded_outline", floatfmt=".2f"))
    print(f"  {len(data)} row(s)\n")


def banner(title):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


# ── CRUD Operations ─────────────────────────────────────────────

def add_patient(first_name, last_name, dob, gender, blood_group, phone, email, address):
    with connect() as con:
        cur = con.execute(
            "INSERT INTO patients (first_name,last_name,dob,gender,blood_group,phone,email,address,registered_on)"
            " VALUES (?,?,?,?,?,?,?,?,?)",
            (first_name, last_name, dob, gender, blood_group, phone, email, address, str(date.today()))
        )
        print(f"✅ Patient added — ID: {cur.lastrowid}")
        return cur.lastrowid


def get_patient(patient_id):
    with connect() as con:
        row = con.execute("SELECT * FROM patients WHERE patient_id=?", (patient_id,)).fetchone()
        if row:
            print_table([row])
        else:
            print(f"  Patient #{patient_id} not found.")


def search_patients(name_query: str):
    banner(f"Patient Search: '{name_query}'")
    with connect() as con:
        rows = con.execute(
            "SELECT patient_id, first_name||' '||last_name AS name, dob, gender, blood_group, phone"
            " FROM patients WHERE first_name LIKE ? OR last_name LIKE ?",
            (f"%{name_query}%", f"%{name_query}%")
        ).fetchall()
    print_table(rows)


def book_appointment(patient_id, doctor_id, appt_date, appt_time, reason):
    with connect() as con:
        cur = con.execute(
            "INSERT INTO appointments (patient_id,doctor_id,appt_date,appt_time,status,reason)"
            " VALUES (?,?,?,?,'Scheduled',?)",
            (patient_id, doctor_id, appt_date, appt_time, reason)
        )
        print(f"✅ Appointment booked — ID: {cur.lastrowid}")
        return cur.lastrowid


def update_appointment_status(appt_id, status):
    allowed = {"Scheduled", "Completed", "Cancelled", "No-Show"}
    if status not in allowed:
        print(f"❌ Invalid status. Choose from: {allowed}")
        return
    with connect() as con:
        con.execute("UPDATE appointments SET status=? WHERE appt_id=?", (status, appt_id))
    print(f"✅ Appointment #{appt_id} → {status}")


def admit_patient(patient_id, doctor_id, dept_id, room_number, diagnosis):
    with connect() as con:
        cur = con.execute(
            "INSERT INTO admissions (patient_id,doctor_id,dept_id,admit_date,room_number,diagnosis,status)"
            " VALUES (?,?,?,?,?,?,'Active')",
            (patient_id, doctor_id, dept_id, str(date.today()), room_number, diagnosis)
        )
        print(f"✅ Patient admitted — Admission ID: {cur.lastrowid}")
        return cur.lastrowid


def discharge_patient(admission_id):
    with connect() as con:
        con.execute(
            "UPDATE admissions SET status='Discharged', discharge_date=? WHERE admission_id=?",
            (str(date.today()), admission_id)
        )
    print(f"✅ Patient discharged — Admission #{admission_id}")


def create_bill(patient_id, admission_id, consultation_fee, medicine_cost, room_charge, lab_charge, payment_method=None):
    total = consultation_fee + medicine_cost + room_charge + lab_charge
    paid  = total if payment_method else 0
    status = "Paid" if paid >= total else "Pending"
    with connect() as con:
        cur = con.execute(
            "INSERT INTO bills (patient_id,admission_id,bill_date,consultation_fee,medicine_cost,"
            "room_charge,lab_charge,total_amount,paid_amount,payment_status,payment_method)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (patient_id, admission_id, str(date.today()),
             consultation_fee, medicine_cost, room_charge, lab_charge,
             total, paid, status, payment_method)
        )
        print(f"✅ Bill created — ID: {cur.lastrowid} | Total: ${total:,.2f} | Status: {status}")
        return cur.lastrowid


# ── Reports ─────────────────────────────────────────────────────

def report_dashboard():
    banner("HOSPITAL DASHBOARD")
    with connect() as con:
        stats = {
            "Total Patients":      con.execute("SELECT COUNT(*) FROM patients").fetchone()[0],
            "Total Doctors":       con.execute("SELECT COUNT(*) FROM doctors").fetchone()[0],
            "Active Admissions":   con.execute("SELECT COUNT(*) FROM admissions WHERE status='Active'").fetchone()[0],
            "Today's Appts":       con.execute("SELECT COUNT(*) FROM appointments WHERE appt_date=?", (str(date.today()),)).fetchone()[0],
            "Pending Bills":       con.execute("SELECT COUNT(*) FROM bills WHERE payment_status='Pending'").fetchone()[0],
            "Total Revenue":       f"${con.execute('SELECT COALESCE(SUM(paid_amount),0) FROM bills').fetchone()[0]:,.2f}",
            "Outstanding":         f"${con.execute('SELECT COALESCE(SUM(total_amount-paid_amount),0) FROM bills WHERE payment_status!=\"Paid\"').fetchone()[0]:,.2f}",
            "Low Stock Medicines": con.execute("SELECT COUNT(*) FROM medicines WHERE stock_qty<=reorder_level").fetchone()[0],
        }
    for k, v in stats.items():
        print(f"  {'•'} {k:<25} {v}")


def report_appointments(limit=15):
    banner("UPCOMING / RECENT APPOINTMENTS")
    with connect() as con:
        rows = con.execute("""
            SELECT a.appt_id,
                   p.first_name||' '||p.last_name AS patient,
                   d.first_name||' '||d.last_name AS doctor,
                   d.specialization,
                   a.appt_date, a.appt_time, a.status, a.reason
            FROM appointments a
            JOIN patients p ON a.patient_id=p.patient_id
            JOIN doctors  d ON a.doctor_id=d.doctor_id
            ORDER BY a.appt_date DESC LIMIT ?
        """, (limit,)).fetchall()
    print_table(rows)


def report_active_admissions():
    banner("ACTIVE ADMISSIONS")
    with connect() as con:
        rows = con.execute("""
            SELECT ad.admission_id,
                   p.first_name||' '||p.last_name AS patient,
                   d.first_name||' '||d.last_name AS doctor,
                   dp.name AS department,
                   ad.room_number, ad.admit_date, ad.diagnosis,
                   CAST(JULIANDAY('now')-JULIANDAY(ad.admit_date) AS INTEGER) AS days_in
            FROM admissions ad
            JOIN patients p   ON ad.patient_id=p.patient_id
            JOIN doctors  d   ON ad.doctor_id=d.doctor_id
            JOIN departments dp ON ad.dept_id=dp.dept_id
            WHERE ad.status='Active'
            ORDER BY days_in DESC
        """).fetchall()
    print_table(rows)


def report_revenue():
    banner("MONTHLY REVENUE SUMMARY")
    with connect() as con:
        rows = con.execute(
            "SELECT * FROM v_revenue_summary ORDER BY month"
        ).fetchall()
    print_table(rows)


def report_doctor_workload():
    banner("DOCTOR WORKLOAD")
    with connect() as con:
        rows = con.execute(
            "SELECT * FROM v_doctor_workload ORDER BY total_appointments DESC"
        ).fetchall()
    print_table(rows)


def report_top_diagnoses():
    banner("TOP DIAGNOSES")
    with connect() as con:
        rows = con.execute("""
            SELECT diagnosis, COUNT(*) AS cases,
                   ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM admissions),1) AS pct
            FROM admissions GROUP BY diagnosis
            ORDER BY cases DESC LIMIT 10
        """).fetchall()
    print_table(rows)


def report_billing_outstanding():
    banner("OUTSTANDING BALANCES")
    with connect() as con:
        rows = con.execute("""
            SELECT p.first_name||' '||p.last_name AS patient,
                   COUNT(b.bill_id) AS bills,
                   ROUND(SUM(b.total_amount),2) AS total_billed,
                   ROUND(SUM(b.paid_amount),2)  AS paid,
                   ROUND(SUM(b.total_amount-b.paid_amount),2) AS outstanding
            FROM bills b
            JOIN patients p ON b.patient_id=p.patient_id
            WHERE b.payment_status != 'Paid'
            GROUP BY b.patient_id HAVING outstanding > 0
            ORDER BY outstanding DESC LIMIT 15
        """).fetchall()
    print_table(rows)


def report_low_stock():
    banner("LOW STOCK MEDICINES ⚠️")
    with connect() as con:
        rows = con.execute("""
            SELECT name, category, stock_qty, reorder_level,
                   (reorder_level-stock_qty) AS units_needed, manufacturer
            FROM medicines WHERE stock_qty <= reorder_level
            ORDER BY units_needed DESC
        """).fetchall()
    print_table(rows)


def report_patient_summary():
    banner("PATIENT SUMMARY (Top 20 by billing)")
    with connect() as con:
        rows = con.execute(
            "SELECT * FROM v_patient_summary ORDER BY total_billed DESC LIMIT 20"
        ).fetchall()
    print_table(rows)


# ── Demo Runner ─────────────────────────────────────────────────

def run_demo():
    print("\n" + "="*60)
    print("  🏥  HOSPITAL MANAGEMENT SYSTEM — DEMO RUN")
    print("="*60)

    # Check DB exists
    if not os.path.exists(DB_PATH):
        print("⚠️  Database not found. Run seed.py first:\n    python seed.py")
        return

    # Dashboard
    report_dashboard()

    # CRUD demos
    banner("ADD NEW PATIENT")
    pid = add_patient("Alice", "Walker", "1990-06-15", "F", "A+",
                      "555-9999", "alice.walker@email.com", "42 Oak Lane")

    banner("BOOK APPOINTMENT")
    book_appointment(pid, 1, str(date.today()), "10:00", "Initial consultation")

    banner("ADMIT PATIENT")
    adm_id = admit_patient(pid, 1, 1, "201", "Hypertension – monitoring")

    banner("CREATE BILL")
    create_bill(pid, adm_id, 300, 150, 500, 200, payment_method="Card")

    banner("DISCHARGE PATIENT")
    discharge_patient(adm_id)

    # Reports
    report_appointments(10)
    report_active_admissions()
    report_revenue()
    report_doctor_workload()
    report_top_diagnoses()
    report_billing_outstanding()
    report_low_stock()
    report_patient_summary()

    print("\n✅ Demo complete.\n")


if __name__ == "__main__":
    run_demo()
