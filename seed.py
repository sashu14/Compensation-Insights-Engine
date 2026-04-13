import sqlite3
import random
import datetime

DB_FILE = 'compensation.db'
SCHEMA_FILE = 'schema.sql'

DEPARTMENTS = ['Sales', 'Engineering', 'Marketing', 'HR', 'Finance', 'Operations']
BANDS = ['B1', 'B2', 'B3', 'B4', 'B5']
GENDERS = ['Male', 'Female', 'Non-Binary']

def create_schema(conn):
    with open(SCHEMA_FILE, 'r') as f:
        schema = f.read()
    conn.executescript(schema)
    conn.commit()

def generate_names(count):
    first = ['John', 'Jane', 'Alex', 'Chris', 'Pat', 'Sam', 'Taylor', 'Jordan', 'Casey', 'Riley', 'Morgan', 'Avery', 'Drew', 'Harper', 'Cameron']
    last = ['Smith', 'Doe', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez']
    return [f"{random.choice(first)} {random.choice(last)}" for _ in range(count)]

def seed_data():
    conn = sqlite3.connect(DB_FILE)
    create_schema(conn)
    cursor = conn.cursor()

    # 1. Create 1 Cycle
    cursor.execute("""
        INSERT INTO compensation_cycles (cycle_name, start_date, end_date, status)
        VALUES ('2024 Year-End Merit', '2023-12-01', '2024-03-31', 'Closed')
    """)
    cycle_id = cursor.lastrowid

    # 2. Create Employees (100 total)
    names = generate_names(100)
    
    # We will elect one manager per department to act as a manager for everyone Else in that department
    managers = {}
    
    # Track employees to insert later
    emp_records = []
    
    for i in range(100):
        dept = random.choice(DEPARTMENTS)
        band = random.choice(BANDS)
        # Add intentional gender bias in Engineering B3
        if dept == 'Engineering' and band == 'B3':
            gender = random.choices(['Male', 'Female'], weights=[0.2, 0.8])[0] # Lots of females in B3 to show pay gap later
        else:
            gender = random.choice(GENDERS)
        
        hire_date = datetime.date(2015, 1, 1) + datetime.timedelta(days=random.randint(0, 3000))
        emp_records.append({
            'id': i+1,
            'name': names[i] + (' Jr.' if i % 10 == 0 else ''),
            'gender': gender,
            'dept': dept,
            'band': band,
            'hire_date': hire_date.isoformat()
        })
    
    # Assign managers
    for dept in DEPARTMENTS:
        dept_emps = [e for e in emp_records if e['dept'] == dept]
        if dept_emps:
            # First one is manager
            managers[dept] = dept_emps[0]['id']
            
    for e in emp_records:
        manager_id = managers[e['dept']]
        if e['id'] == manager_id:
            manager_id = None # Manager has no manager in this simulation
            e['band'] = 'B5' # Managers are higher band
            
        cursor.execute("""
            INSERT INTO employees (full_name, gender, department, job_band, manager_id, country, fte_percentage, hire_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (e['name'], e['gender'], e['dept'], e['band'], manager_id, 'US', 1.0, e['hire_date']))
        
    # 3. Create Budgets
    # Sales, Marketing, HR, Ops are within budget.
    # Finance and Engineering over budget.
    for dept in DEPARTMENTS:
        # Give $50k per department roughly
        cursor.execute("""
            INSERT INTO budgets (cycle_id, department, job_band, allocated_amount, currency)
            VALUES (?, ?, ?, ?, ?)
        """, (cycle_id, dept, 'ALL', 50000, 'USD'))
        
    # 4. Create Compensation Awards
    # Band Caps: B1:3000, B2:5000, B3:8000, B4:12000, B5:20000
    for e in emp_records:
        band = e['band']
        dept = e['dept']
        gender = e['gender']
        
        base_merit = {'B1': 1500, 'B2': 3000, 'B3': 6000, 'B4': 9000, 'B5': 15000}[band]
        award = base_merit + random.randint(-500, 500)
        
        # Injections of messiness:
        # Pay equity issue: Males in Engineering B3 get $2500 more than others avg.
        if dept == 'Engineering' and band == 'B3' and gender == 'Male':
            award += 2500
        
        # Policy violations: 5 employees randomly exceed cap by 2x.
        if e['id'] in [15, 27, 42, 68, 88]:
            award = base_merit * 2.5
            
        # Finance department overspending
        if dept == 'Finance':
            award *= 1.8 # significantly increase to blow the $50k budget
            
        cursor.execute("""
            INSERT INTO compensation_awards (employee_id, cycle_id, award_type, award_amount, currency)
            VALUES (?, ?, ?, ?, ?)
        """, (e['id'], cycle_id, 'Merit', round(award, 2), 'USD'))

    conn.commit()
    print("Database seeded successfully with 100 employees and realistic messy HR data!")
    conn.close()

if __name__ == '__main__':
    seed_data()
