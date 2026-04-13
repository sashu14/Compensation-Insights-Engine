-- name: pay_equity
-- Business Goal: Average merit award by job band and gender (pay equity check).
-- Identifies potential demographic disparities in the distribution of merit, triggering HR audits.
SELECT 
    e.job_band,
    e.gender,
    COUNT(e.employee_id) AS headcount,
    ROUND(AVG(ca.award_amount), 2) AS avg_merit_award
FROM employees e
JOIN compensation_awards ca ON e.employee_id = ca.employee_id
JOIN compensation_cycles cc ON ca.cycle_id = cc.cycle_id
WHERE ca.award_type = 'Merit' 
  AND cc.status = 'Closed'
GROUP BY 
    e.job_band, 
    e.gender
ORDER BY 
    e.job_band, 
    e.gender;


-- name: budget_utilization
-- Business Goal: Budget utilisation quantitative check by department - allocated vs awarded vs remaining.
-- Gives Finance a direct insight into which departments overspent their allocated cycle budgets.
WITH DepartmentAwards AS (
    SELECT 
        e.department,
        ca.cycle_id,
        SUM(ca.award_amount) AS total_awarded,
        ca.currency
    FROM employees e
    JOIN compensation_awards ca ON e.employee_id = ca.employee_id
    GROUP BY e.department, ca.cycle_id, ca.currency
),
DepartmentBudgets AS (
    SELECT 
        b.department,
        b.cycle_id,
        SUM(b.allocated_amount) AS total_allocated,
        b.currency
    FROM budgets b
    GROUP BY b.department, b.cycle_id, b.currency
)
SELECT 
    db.department,
    db.currency,
    ROUND(db.total_allocated, 2) AS allocated_amount,
    COALESCE(ROUND(da.total_awarded, 2), 0) AS awarded_amount,
    ROUND(db.total_allocated - COALESCE(da.total_awarded, 0), 2) AS remaining_budget,
    ROUND((COALESCE(da.total_awarded, 0) / db.total_allocated) * 100, 1) AS utilization_percent
FROM DepartmentBudgets db
LEFT JOIN DepartmentAwards da ON db.department = da.department AND db.cycle_id = da.cycle_id
ORDER BY utilization_percent DESC;


-- name: policy_violation
-- Business Goal: Identifies employees whose award exceeded their job band cap.
-- This acts as an automated policy compliance check since HRsoft doesn't block rogue submittals strictly by default.
-- Note: Assuming standard business rules here where Merit isn't expected to exceed 10% for ordinary bands, 
-- but since we don't have base pay, we'll establish a hard dollar cap per band purely for reporting simulation.
WITH BandCaps AS (
    -- Simulating a reference table for max absolute dollar caps by band
    SELECT 'B1' AS job_band, 3000 AS cap_amount UNION ALL
    SELECT 'B2' AS job_band, 5000 AS cap_amount UNION ALL
    SELECT 'B3' AS job_band, 8000 AS cap_amount UNION ALL
    SELECT 'B4' AS job_band, 12000 AS cap_amount UNION ALL
    SELECT 'B5' AS job_band, 20000 AS cap_amount
)
SELECT 
    e.employee_id,
    e.full_name,
    e.department,
    e.job_band,
    ca.award_amount,
    bc.cap_amount AS band_maximum,
    m.full_name AS approved_by_manager
FROM employees e
JOIN compensation_awards ca ON e.employee_id = ca.employee_id
JOIN BandCaps bc ON e.job_band = bc.job_band
LEFT JOIN employees m ON e.manager_id = m.employee_id
WHERE ca.award_type = 'Merit' 
  AND ca.award_amount > bc.cap_amount
ORDER BY ca.award_amount DESC;


-- name: merit_distribution
-- Business Goal: Merit distribution curve - count of employees per award dollar bracket.
-- Helps Total Rewards configure their compensation scatterplot in the downstream system.
WITH Brackets AS (
    SELECT 
        e.employee_id,
        e.job_band,
        CASE 
            WHEN ca.award_amount < 2000 THEN 'Under $2k'
            WHEN ca.award_amount >= 2000 AND ca.award_amount < 5000 THEN '$2k - $5k'
            WHEN ca.award_amount >= 5000 AND ca.award_amount < 10000 THEN '$5k - $10k'
            WHEN ca.award_amount >= 10000 THEN 'Over $10k'
            ELSE 'No Award'
        END AS award_bracket
    FROM employees e
    LEFT JOIN compensation_awards ca ON e.employee_id = ca.employee_id AND ca.award_type = 'Merit'
)
SELECT 
    award_bracket,
    COUNT(employee_id) as employee_count
FROM Brackets
GROUP BY award_bracket
ORDER BY 
    CASE award_bracket
        WHEN 'No Award' THEN 1
        WHEN 'Under $2k' THEN 2
        WHEN '$2k - $5k' THEN 3
        WHEN '$5k - $10k' THEN 4
        WHEN 'Over $10k' THEN 5
    END;


-- name: manager_summary
-- Business Goal: Manager-level summary. Evaluates manager generosity and scale of operation.
-- Total awards given, headcount, avg award per manager.
WITH ManagerDirects AS (
    SELECT 
        manager_id,
        COUNT(employee_id) AS direct_reports_count
    FROM employees
    WHERE manager_id IS NOT NULL
    GROUP BY manager_id
),
ManagerAwards AS (
    SELECT 
        e.manager_id,
        SUM(ca.award_amount) as total_awarded,
        AVG(ca.award_amount) as avg_award
    FROM employees e
    JOIN compensation_awards ca ON e.employee_id = ca.employee_id
    WHERE e.manager_id IS NOT NULL
    GROUP BY e.manager_id
)
SELECT 
    m.full_name AS manager_name,
    m.department,
    COALESCE(md.direct_reports_count, 0) AS direct_reports,
    COALESCE(ROUND(ma.total_awarded, 2), 0) AS total_dollars_awarded,
    COALESCE(ROUND(ma.avg_award, 2), 0) AS avg_award_per_employee
FROM employees m
JOIN ManagerDirects md ON m.employee_id = md.manager_id
LEFT JOIN ManagerAwards ma ON m.employee_id = ma.manager_id
ORDER BY total_dollars_awarded DESC;
