-- ============================================================
--  HOSPITAL MANAGEMENT SYSTEM — DATABASE SCHEMA
--  SQLite-compatible DDL
-- ============================================================

PRAGMA foreign_keys = ON;

-- ── Departments ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS departments (
    dept_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL UNIQUE,
    floor         INTEGER NOT NULL,
    head_doctor   TEXT,
    phone_ext     TEXT
);

-- ── Doctors ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name    TEXT    NOT NULL,
    last_name     TEXT    NOT NULL,
    specialization TEXT   NOT NULL,
    dept_id       INTEGER NOT NULL REFERENCES departments(dept_id),
    phone         TEXT,
    email         TEXT    UNIQUE,
    hire_date     DATE    NOT NULL,
    salary        REAL    NOT NULL
);

-- ── Patients ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS patients (
    patient_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name    TEXT    NOT NULL,
    last_name     TEXT    NOT NULL,
    dob           DATE    NOT NULL,
    gender        TEXT    CHECK(gender IN ('M','F','Other')),
    blood_group   TEXT,
    phone         TEXT,
    email         TEXT,
    address       TEXT,
    registered_on DATE    NOT NULL DEFAULT (DATE('now'))
);

-- ── Appointments ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS appointments (
    appt_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id    INTEGER NOT NULL REFERENCES patients(patient_id),
    doctor_id     INTEGER NOT NULL REFERENCES doctors(doctor_id),
    appt_date     DATE    NOT NULL,
    appt_time     TEXT    NOT NULL,
    status        TEXT    NOT NULL DEFAULT 'Scheduled'
                          CHECK(status IN ('Scheduled','Completed','Cancelled','No-Show')),
    reason        TEXT,
    notes         TEXT
);

-- ── Admissions ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS admissions (
    admission_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id    INTEGER NOT NULL REFERENCES patients(patient_id),
    doctor_id     INTEGER NOT NULL REFERENCES doctors(doctor_id),
    dept_id       INTEGER NOT NULL REFERENCES departments(dept_id),
    admit_date    DATE    NOT NULL,
    discharge_date DATE,
    room_number   TEXT    NOT NULL,
    diagnosis     TEXT    NOT NULL,
    status        TEXT    NOT NULL DEFAULT 'Active'
                          CHECK(status IN ('Active','Discharged','Transferred'))
);

-- ── Medical Records ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS medical_records (
    record_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id    INTEGER NOT NULL REFERENCES patients(patient_id),
    doctor_id     INTEGER NOT NULL REFERENCES doctors(doctor_id),
    record_date   DATE    NOT NULL,
    diagnosis     TEXT    NOT NULL,
    prescription  TEXT,
    notes         TEXT,
    follow_up     DATE
);

-- ── Medicines ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS medicines (
    medicine_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL UNIQUE,
    category      TEXT    NOT NULL,
    unit_price    REAL    NOT NULL,
    stock_qty     INTEGER NOT NULL DEFAULT 0,
    reorder_level INTEGER NOT NULL DEFAULT 50,
    manufacturer  TEXT
);

-- ── Prescriptions ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id     INTEGER NOT NULL REFERENCES medical_records(record_id),
    medicine_id   INTEGER NOT NULL REFERENCES medicines(medicine_id),
    dosage        TEXT    NOT NULL,
    duration_days INTEGER NOT NULL,
    qty_prescribed INTEGER NOT NULL
);

-- ── Bills ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bills (
    bill_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id    INTEGER NOT NULL REFERENCES patients(patient_id),
    admission_id  INTEGER REFERENCES admissions(admission_id),
    bill_date     DATE    NOT NULL,
    consultation_fee REAL DEFAULT 0,
    medicine_cost    REAL DEFAULT 0,
    room_charge      REAL DEFAULT 0,
    lab_charge       REAL DEFAULT 0,
    total_amount     REAL NOT NULL,
    paid_amount      REAL DEFAULT 0,
    payment_status   TEXT NOT NULL DEFAULT 'Pending'
                     CHECK(payment_status IN ('Pending','Partial','Paid')),
    payment_method   TEXT CHECK(payment_method IN ('Cash','Card','Insurance','Online'))
);

-- ── Staff ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS staff (
    staff_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name    TEXT    NOT NULL,
    last_name     TEXT    NOT NULL,
    role          TEXT    NOT NULL,
    dept_id       INTEGER REFERENCES departments(dept_id),
    phone         TEXT,
    salary        REAL    NOT NULL,
    hire_date     DATE    NOT NULL
);

-- ── Indexes ──────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_appt_date     ON appointments(appt_date);
CREATE INDEX IF NOT EXISTS idx_appt_patient  ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appt_doctor   ON appointments(doctor_id);
CREATE INDEX IF NOT EXISTS idx_admit_patient ON admissions(patient_id);
CREATE INDEX IF NOT EXISTS idx_bill_patient  ON bills(patient_id);
CREATE INDEX IF NOT EXISTS idx_record_patient ON medical_records(patient_id);

-- ── Views ────────────────────────────────────────────────────
CREATE VIEW IF NOT EXISTS v_patient_summary AS
    SELECT
        p.patient_id,
        p.first_name || ' ' || p.last_name AS patient_name,
        p.gender,
        p.blood_group,
        COUNT(DISTINCT a.appt_id)       AS total_appointments,
        COUNT(DISTINCT ad.admission_id) AS total_admissions,
        COUNT(DISTINCT mr.record_id)    AS total_records,
        COALESCE(SUM(b.total_amount), 0) AS total_billed,
        COALESCE(SUM(b.paid_amount),  0) AS total_paid
    FROM patients p
    LEFT JOIN appointments   a  ON p.patient_id = a.patient_id
    LEFT JOIN admissions     ad ON p.patient_id = ad.patient_id
    LEFT JOIN medical_records mr ON p.patient_id = mr.patient_id
    LEFT JOIN bills          b  ON p.patient_id = b.patient_id
    GROUP BY p.patient_id;

CREATE VIEW IF NOT EXISTS v_doctor_workload AS
    SELECT
        d.doctor_id,
        d.first_name || ' ' || d.last_name AS doctor_name,
        d.specialization,
        dp.name AS department,
        COUNT(DISTINCT a.appt_id)          AS total_appointments,
        COUNT(DISTINCT CASE WHEN a.status='Completed' THEN a.appt_id END) AS completed,
        COUNT(DISTINCT ad.admission_id)    AS active_admissions,
        COUNT(DISTINCT mr.record_id)       AS records_created
    FROM doctors d
    JOIN departments dp ON d.dept_id = dp.dept_id
    LEFT JOIN appointments    a  ON d.doctor_id = a.doctor_id
    LEFT JOIN admissions      ad ON d.doctor_id = ad.doctor_id AND ad.status='Active'
    LEFT JOIN medical_records mr ON d.doctor_id = mr.doctor_id
    GROUP BY d.doctor_id;

CREATE VIEW IF NOT EXISTS v_revenue_summary AS
    SELECT
        strftime('%Y-%m', b.bill_date) AS month,
        COUNT(*)                        AS total_bills,
        SUM(b.total_amount)             AS gross_revenue,
        SUM(b.paid_amount)              AS collected,
        SUM(b.total_amount - b.paid_amount) AS outstanding,
        SUM(CASE WHEN b.payment_status='Paid' THEN 1 ELSE 0 END) AS paid_count
    FROM bills b
    GROUP BY strftime('%Y-%m', b.bill_date);
