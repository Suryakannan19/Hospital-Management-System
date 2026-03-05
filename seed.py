"""
seed.py — Populate the hospital database with realistic sample data
"""

import sqlite3
import random
from datetime import date, timedelta
from pathlib import Path

DB_PATH = "hospital.db"

DEPARTMENTS = [
    ("Cardiology",      2, "Dr. Emily Stone",   "101"),
    ("Neurology",       3, "Dr. Alan Park",      "102"),
    ("Orthopedics",     1, "Dr. Sara Khan",      "103"),
    ("Pediatrics",      4, "Dr. James Lee",      "104"),
    ("General Surgery", 1, "Dr. Maria Gomez",    "105"),
    ("Emergency",       0, "Dr. Victor Holt",    "106"),
    ("Oncology",        5, "Dr. Nina Patel",     "107"),
    ("Radiology",       2, "Dr. Tom Wright",     "108"),
]

DOCTORS = [
    ("Emily",   "Stone",   "Cardiologist",      1, "555-1001", "e.stone@hospital.com",   "2018-03-15", 185000),
    ("Alan",    "Park",    "Neurologist",        2, "555-1002", "a.park@hospital.com",    "2016-07-01", 190000),
    ("Sara",    "Khan",    "Orthopedic Surgeon", 3, "555-1003", "s.khan@hospital.com",    "2019-01-10", 175000),
    ("James",   "Lee",     "Pediatrician",       4, "555-1004", "j.lee@hospital.com",     "2020-05-20", 160000),
    ("Maria",   "Gomez",   "General Surgeon",    5, "555-1005", "m.gomez@hospital.com",   "2015-11-30", 195000),
    ("Victor",  "Holt",    "Emergency Medicine", 6, "555-1006", "v.holt@hospital.com",    "2017-08-14", 170000),
    ("Nina",    "Patel",   "Oncologist",         7, "555-1007", "n.patel@hospital.com",   "2014-02-28", 200000),
    ("Tom",     "Wright",  "Radiologist",        8, "555-1008", "t.wright@hospital.com",  "2021-09-05", 155000),
    ("Rachel",  "Adams",   "Cardiologist",       1, "555-1009", "r.adams@hospital.com",   "2022-01-15", 178000),
    ("David",   "Chen",    "Neurologist",        2, "555-1010", "d.chen@hospital.com",    "2019-06-22", 182000),
]

PATIENT_FIRST = ["Liam","Olivia","Noah","Emma","James","Ava","Oliver","Sophia","Elijah","Isabella",
                 "William","Mia","Henry","Amelia","Lucas","Harper","Benjamin","Evelyn","Theodore","Abigail",
                 "Jack","Emily","Sebastian","Elizabeth","Aiden","Mila","Owen","Ella","Samuel","Luna"]
PATIENT_LAST  = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Wilson","Moore",
                 "Taylor","Anderson","Thomas","Jackson","White","Harris","Martin","Thompson","Martinez","Robinson"]

BLOOD_GROUPS  = ["A+","A-","B+","B-","AB+","AB-","O+","O-"]
DIAGNOSES     = [
    "Hypertension","Type 2 Diabetes","Acute MI","Asthma","COPD","Pneumonia",
    "Appendicitis","Fracture – Right Femur","Migraine","Epilepsy",
    "Breast Cancer (Stage II)","Colorectal Cancer","Hip Replacement","Knee Osteoarthritis",
    "Urinary Tract Infection","Gastroenteritis","Anemia","Depression","Anxiety Disorder","Flu"
]
MEDICINES = [
    ("Metformin",    "Antidiabetic",   0.15, 500, 100, "PharmaCo"),
    ("Lisinopril",   "Antihypertensive",0.20,400, 80,  "MediLab"),
    ("Atorvastatin", "Statin",          0.25,350, 70,  "CardioPharm"),
    ("Amoxicillin",  "Antibiotic",      0.30,600, 120, "BioMed"),
    ("Omeprazole",   "PPI",             0.18,450, 90,  "GastroLabs"),
    ("Paracetamol",  "Analgesic",       0.05,1000,200, "GeneriCo"),
    ("Ibuprofen",    "NSAID",           0.08,800, 150, "PainAway"),
    ("Salbutamol",   "Bronchodilator",  1.20,200, 40,  "RespiCare"),
    ("Warfarin",     "Anticoagulant",   0.35,250, 50,  "CardioPharm"),
    ("Morphine",     "Opioid Analgesic",2.50,100, 30,  "PainAway"),
    ("Cetirizine",   "Antihistamine",   0.10,500, 100, "AllergyX"),
    ("Insulin",      "Antidiabetic",    3.00,300, 60,  "DiabeCare"),
]
ROLES   = ["Nurse","Lab Technician","Receptionist","Pharmacist","Ward Boy","Admin","Accountant"]
ROOMS   = [f"{floor}{num:02d}" for floor in range(1,6) for num in range(1,21)]
REASONS = ["Routine checkup","Chest pain","Severe headache","Follow-up","Knee pain",
           "Abdominal pain","Fever","Shortness of breath","Back pain","Dizziness"]


def rand_date(start: str, end: str) -> str:
    s = date.fromisoformat(start)
    e = date.fromisoformat(end)
    return str(s + timedelta(days=random.randint(0, (e - s).days)))


def seed(db_path: str = DB_PATH):
    Path(db_path).unlink(missing_ok=True)
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    with open("schema.sql") as f:
        con.executescript(f.read())

    # Departments
    cur.executemany(
        "INSERT INTO departments (name,floor,head_doctor,phone_ext) VALUES (?,?,?,?)",
        DEPARTMENTS
    )

    # Doctors
    cur.executemany(
        "INSERT INTO doctors (first_name,last_name,specialization,dept_id,phone,email,hire_date,salary)"
        " VALUES (?,?,?,?,?,?,?,?)", DOCTORS
    )

    # Patients (120)
    patients = []
    for i in range(120):
        fn   = random.choice(PATIENT_FIRST)
        ln   = random.choice(PATIENT_LAST)
        dob  = rand_date("1950-01-01", "2010-12-31")
        g    = random.choice(["M","F"])
        bg   = random.choice(BLOOD_GROUPS)
        ph   = f"555-{random.randint(2000,9999)}"
        em   = f"{fn.lower()}.{ln.lower()}{i}@email.com"
        reg  = rand_date("2022-01-01", "2024-12-31")
        patients.append((fn, ln, dob, g, bg, ph, em, f"{random.randint(1,999)} Main St", reg))
    cur.executemany(
        "INSERT INTO patients (first_name,last_name,dob,gender,blood_group,phone,email,address,registered_on)"
        " VALUES (?,?,?,?,?,?,?,?,?)", patients
    )

    # Medicines
    cur.executemany(
        "INSERT INTO medicines (name,category,unit_price,stock_qty,reorder_level,manufacturer)"
        " VALUES (?,?,?,?,?,?)", MEDICINES
    )

    # Staff (30)
    staff = []
    for _ in range(30):
        fn  = random.choice(PATIENT_FIRST)
        ln  = random.choice(PATIENT_LAST)
        role = random.choice(ROLES)
        dept = random.randint(1, 8)
        ph   = f"555-{random.randint(3000,8999)}"
        sal  = round(random.uniform(35000, 85000), 2)
        hire = rand_date("2015-01-01", "2024-01-01")
        staff.append((fn, ln, role, dept, ph, sal, hire))
    cur.executemany(
        "INSERT INTO staff (first_name,last_name,role,dept_id,phone,salary,hire_date)"
        " VALUES (?,?,?,?,?,?,?)", staff
    )

    # Appointments (300)
    statuses = ["Scheduled","Completed","Cancelled","No-Show"]
    weights  = [0.20, 0.60, 0.12, 0.08]
    appts = []
    for _ in range(300):
        pid  = random.randint(1, 120)
        did  = random.randint(1, 10)
        d    = rand_date("2023-01-01", "2024-12-31")
        t    = f"{random.randint(8,17):02d}:{random.choice(['00','15','30','45'])}"
        st   = random.choices(statuses, weights)[0]
        appts.append((pid, did, d, t, st, random.choice(REASONS)))
    cur.executemany(
        "INSERT INTO appointments (patient_id,doctor_id,appt_date,appt_time,status,reason)"
        " VALUES (?,?,?,?,?,?)", appts
    )

    # Admissions (80)
    admit_list = []
    for _ in range(80):
        pid   = random.randint(1, 120)
        did   = random.randint(1, 10)
        dept  = random.randint(1, 8)
        admit = rand_date("2023-01-01", "2024-11-01")
        discharged = random.random() > 0.15
        discharge  = str(date.fromisoformat(admit) + timedelta(days=random.randint(1,14))) if discharged else None
        room  = random.choice(ROOMS)
        diag  = random.choice(DIAGNOSES)
        st    = "Discharged" if discharged else "Active"
        admit_list.append((pid, did, dept, admit, discharge, room, diag, st))
    cur.executemany(
        "INSERT INTO admissions (patient_id,doctor_id,dept_id,admit_date,discharge_date,room_number,diagnosis,status)"
        " VALUES (?,?,?,?,?,?,?,?)", admit_list
    )

    # Medical Records (200)
    records = []
    for _ in range(200):
        pid  = random.randint(1, 120)
        did  = random.randint(1, 10)
        d    = rand_date("2023-01-01", "2024-12-01")
        diag = random.choice(DIAGNOSES)
        fu   = str(date.fromisoformat(d) + timedelta(days=random.randint(7, 30)))
        records.append((pid, did, d, diag, "See prescription", "Patient stable", fu))
    cur.executemany(
        "INSERT INTO medical_records (patient_id,doctor_id,record_date,diagnosis,prescription,notes,follow_up)"
        " VALUES (?,?,?,?,?,?,?)", records
    )

    # Prescriptions (400)
    dosages   = ["1 tablet twice daily","2 tablets once daily","1 capsule thrice daily","5ml syrup twice daily"]
    prescs = []
    for _ in range(400):
        rid = random.randint(1, 200)
        mid = random.randint(1, 12)
        qty = random.randint(7, 60)
        prescs.append((rid, mid, random.choice(dosages), random.randint(5, 30), qty))
    cur.executemany(
        "INSERT INTO prescriptions (record_id,medicine_id,dosage,duration_days,qty_prescribed)"
        " VALUES (?,?,?,?,?)", prescs
    )

    # Bills (150)
    methods = ["Cash","Card","Insurance","Online"]
    bills = []
    for i in range(150):
        pid   = random.randint(1, 120)
        adm   = i + 1 if i < 80 else None
        d     = rand_date("2023-01-01", "2024-12-01")
        cons  = round(random.uniform(100, 500), 2)
        med   = round(random.uniform(50,  800), 2)
        room  = round(random.uniform(0, 3000), 2) if adm else 0
        lab   = round(random.uniform(0,  600), 2)
        total = round(cons + med + room + lab, 2)
        paid  = round(total * random.choice([0, 0.5, 1.0]), 2)
        pst   = "Paid" if paid >= total else ("Partial" if paid > 0 else "Pending")
        meth  = random.choice(methods) if paid > 0 else None
        bills.append((pid, adm, d, cons, med, room, lab, total, paid, pst, meth))
    cur.executemany(
        "INSERT INTO bills (patient_id,admission_id,bill_date,consultation_fee,medicine_cost,"
        "room_charge,lab_charge,total_amount,paid_amount,payment_status,payment_method)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?)", bills
    )

    con.commit()
    con.close()
    print(f"✅ Database seeded → {db_path}")
    print(f"   Departments : {len(DEPARTMENTS)}")
    print(f"   Doctors     : {len(DOCTORS)}")
    print(f"   Patients    : 120")
    print(f"   Appointments: 300")
    print(f"   Admissions  : 80")
    print(f"   Med Records : 200")
    print(f"   Bills       : 150")


if __name__ == "__main__":
    seed()
