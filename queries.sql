-- ============================================================
--  HOSPITAL MANAGEMENT SYSTEM — ANALYTICS QUERIES
-- ============================================================

-- ── 1. Patient Demographics ──────────────────────────────────

-- Age distribution of patients
SELECT
    CASE
        WHEN (strftime('%Y','now') - strftime('%Y', dob)) < 18  THEN 'Under 18'
        WHEN (strftime('%Y','now') - strftime('%Y', dob)) < 35  THEN '18–34'
        WHEN (strftime('%Y','now') - strftime('%Y', dob)) < 50  THEN '35–49'
        WHEN (strftime('%Y','now') - strftime('%Y', dob)) < 65  THEN '50–64'
        ELSE '65+'
    END AS age_group,
    COUNT(*) AS patient_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM patients), 1) AS pct
FROM patients
GROUP BY age_group
ORDER BY age_group;

-- Blood group distribution
SELECT blood_group, COUNT(*) AS count
FROM patients
GROUP BY blood_group
ORDER BY count DESC;

-- ── 2. Appointment Analytics ─────────────────────────────────

-- Appointment status breakdown
SELECT
    status,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM appointments), 1) AS pct
FROM appointments
GROUP BY status;

-- Busiest days of the week
SELECT
    CASE strftime('%w', appt_date)
        WHEN '0' THEN 'Sunday'    WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'   WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'  WHEN '5' THEN 'Friday'
        ELSE 'Saturday'
    END AS day_of_week,
    COUNT(*) AS appointments
FROM appointments
GROUP BY strftime('%w', appt_date)
ORDER BY appointments DESC;

-- Monthly appointment trend
SELECT
    strftime('%Y-%m', appt_date) AS month,
    COUNT(*) AS total,
    SUM(CASE WHEN status='Completed'  THEN 1 ELSE 0 END) AS completed,
    SUM(CASE WHEN status='Cancelled'  THEN 1 ELSE 0 END) AS cancelled
FROM appointments
GROUP BY month
ORDER BY month;

-- ── 3. Doctor Performance ────────────────────────────────────

-- Top doctors by completed appointments
SELECT
    d.first_name || ' ' || d.last_name AS doctor,
    d.specialization,
    COUNT(*) AS total_appts,
    SUM(CASE WHEN a.status='Completed' THEN 1 ELSE 0 END) AS completed,
    ROUND(SUM(CASE WHEN a.status='Completed' THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 1) AS completion_rate
FROM doctors d
JOIN appointments a ON d.doctor_id = a.doctor_id
GROUP BY d.doctor_id
ORDER BY completed DESC;

-- Doctor workload (using view)
SELECT * FROM v_doctor_workload ORDER BY total_appointments DESC;

-- Average admissions per doctor by department
SELECT
    dp.name AS department,
    COUNT(DISTINCT ad.doctor_id)   AS doctor_count,
    COUNT(ad.admission_id)         AS total_admissions,
    ROUND(COUNT(ad.admission_id) * 1.0 / COUNT(DISTINCT ad.doctor_id), 1) AS avg_per_doctor
FROM admissions ad
JOIN departments dp ON ad.dept_id = dp.dept_id
GROUP BY dp.dept_id
ORDER BY total_admissions DESC;

-- ── 4. Admissions & Bed Utilisation ──────────────────────────

-- Average length of stay per department
SELECT
    dp.name AS department,
    COUNT(ad.admission_id) AS admissions,
    ROUND(AVG(
        JULIANDAY(COALESCE(ad.discharge_date, DATE('now'))) - JULIANDAY(ad.admit_date)
    ), 1) AS avg_stay_days,
    MAX(JULIANDAY(COALESCE(ad.discharge_date, DATE('now'))) - JULIANDAY(ad.admit_date)) AS max_stay_days
FROM admissions ad
JOIN departments dp ON ad.dept_id = dp.dept_id
GROUP BY dp.dept_id
ORDER BY avg_stay_days DESC;

-- Currently active admissions
SELECT
    ad.admission_id,
    p.first_name || ' ' || p.last_name AS patient,
    d.first_name || ' ' || d.last_name AS doctor,
    dp.name AS department,
    ad.room_number,
    ad.admit_date,
    ad.diagnosis,
    CAST(JULIANDAY('now') - JULIANDAY(ad.admit_date) AS INTEGER) AS days_admitted
FROM admissions ad
JOIN patients    p  ON ad.patient_id = p.patient_id
JOIN doctors     d  ON ad.doctor_id  = d.doctor_id
JOIN departments dp ON ad.dept_id    = dp.dept_id
WHERE ad.status = 'Active'
ORDER BY days_admitted DESC;

-- Most common diagnoses
SELECT
    diagnosis,
    COUNT(*) AS cases,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM admissions), 1) AS pct
FROM admissions
GROUP BY diagnosis
ORDER BY cases DESC
LIMIT 10;

-- ── 5. Revenue & Billing ─────────────────────────────────────

-- Monthly revenue summary (using view)
SELECT * FROM v_revenue_summary ORDER BY month;

-- Revenue by payment method
SELECT
    COALESCE(payment_method, 'Unpaid') AS method,
    COUNT(*) AS bills,
    ROUND(SUM(paid_amount), 2) AS collected
FROM bills
GROUP BY payment_method
ORDER BY collected DESC;

-- Outstanding balances — top patients
SELECT
    p.first_name || ' ' || p.last_name AS patient,
    p.phone,
    COUNT(b.bill_id) AS bills,
    ROUND(SUM(b.total_amount), 2)  AS total_billed,
    ROUND(SUM(b.paid_amount), 2)   AS total_paid,
    ROUND(SUM(b.total_amount - b.paid_amount), 2) AS outstanding
FROM bills b
JOIN patients p ON b.patient_id = p.patient_id
WHERE b.payment_status != 'Paid'
GROUP BY b.patient_id
HAVING outstanding > 0
ORDER BY outstanding DESC
LIMIT 15;

-- Department-wise revenue contribution
SELECT
    dp.name AS department,
    COUNT(b.bill_id)                AS bills,
    ROUND(SUM(b.total_amount), 2)   AS gross,
    ROUND(SUM(b.room_charge), 2)    AS room_revenue,
    ROUND(SUM(b.lab_charge), 2)     AS lab_revenue
FROM bills b
JOIN admissions ad ON b.admission_id = ad.admission_id
JOIN departments dp ON ad.dept_id = dp.dept_id
GROUP BY dp.dept_id
ORDER BY gross DESC;

-- ── 6. Medicine & Pharmacy ───────────────────────────────────

-- Most prescribed medicines
SELECT
    m.name,
    m.category,
    COUNT(pr.prescription_id) AS times_prescribed,
    SUM(pr.qty_prescribed)    AS total_qty,
    ROUND(SUM(pr.qty_prescribed) * m.unit_price, 2) AS revenue
FROM prescriptions pr
JOIN medicines m ON pr.medicine_id = m.medicine_id
GROUP BY pr.medicine_id
ORDER BY times_prescribed DESC;

-- Low stock alert
SELECT
    medicine_id, name, category,
    stock_qty, reorder_level,
    (reorder_level - stock_qty) AS units_needed
FROM medicines
WHERE stock_qty <= reorder_level
ORDER BY units_needed DESC;

-- ── 7. Patient Journey ───────────────────────────────────────

-- Full patient summary (using view)
SELECT * FROM v_patient_summary ORDER BY total_billed DESC LIMIT 20;

-- Patients with most visits
SELECT
    p.first_name || ' ' || p.last_name AS patient,
    p.blood_group,
    COUNT(DISTINCT a.appt_id)  AS appointments,
    COUNT(DISTINCT ad.admission_id) AS admissions,
    COUNT(DISTINCT mr.record_id)    AS records
FROM patients p
LEFT JOIN appointments    a  ON p.patient_id = a.patient_id
LEFT JOIN admissions      ad ON p.patient_id = ad.patient_id
LEFT JOIN medical_records mr ON p.patient_id = mr.patient_id
GROUP BY p.patient_id
ORDER BY appointments + admissions DESC
LIMIT 10;

-- ── 8. HR & Payroll ──────────────────────────────────────────

-- Salary breakdown by department
SELECT
    dp.name AS department,
    COUNT(d.doctor_id) AS doctor_count,
    ROUND(MIN(d.salary), 0) AS min_salary,
    ROUND(AVG(d.salary), 0) AS avg_salary,
    ROUND(MAX(d.salary), 0) AS max_salary,
    ROUND(SUM(d.salary), 0) AS total_payroll
FROM doctors d
JOIN departments dp ON d.dept_id = dp.dept_id
GROUP BY dp.dept_id
ORDER BY total_payroll DESC;

-- Staff count by role
SELECT role, COUNT(*) AS headcount,
       ROUND(AVG(salary), 0) AS avg_salary
FROM staff
GROUP BY role
ORDER BY headcount DESC;
