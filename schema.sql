DROP TABLE IF EXISTS compensation_awards;
DROP TABLE IF EXISTS budgets;
DROP TABLE IF EXISTS compensation_cycles;
DROP TABLE IF EXISTS employees;

-- Compensation Cycles represent specific periodic events (e.g., "2024 Year-End Merit")
CREATE TABLE compensation_cycles (
    cycle_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle_name TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Planning', 'Active', 'Approved', 'Closed'))
);

-- Core demographic and organizational data for employees
CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    gender TEXT NOT NULL,
    department TEXT NOT NULL,
    job_band TEXT NOT NULL,
    manager_id INTEGER,
    country TEXT NOT NULL,
    fte_percentage REAL NOT NULL,
    hire_date DATE NOT NULL,
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);

-- Allocation of funds per department and job band for a specific cycle
CREATE TABLE budgets (
    budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle_id INTEGER NOT NULL,
    department TEXT NOT NULL,
    job_band TEXT NOT NULL,
    allocated_amount REAL NOT NULL,
    currency TEXT NOT NULL,
    FOREIGN KEY (cycle_id) REFERENCES compensation_cycles(cycle_id)
);

-- The actual merit/bonus awards given to employees
CREATE TABLE compensation_awards (
    award_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    cycle_id INTEGER NOT NULL,
    award_type TEXT NOT NULL CHECK(award_type IN ('Merit', 'Bonus', 'Promotion', 'Equity')),
    award_amount REAL NOT NULL,
    currency TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (cycle_id) REFERENCES compensation_cycles(cycle_id)
);
