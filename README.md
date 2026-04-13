# HRIS Compensation Reporter

## The Real Problem
In enterprise Human Capital Management (HCM) software, notably platforms like HRsoft, out-of-the-box reporting is notoriously rigid. Core platforms provide standard forms and basic aggregates, but fail to deliver actionable insights on critical business metrics such as:
- **Pay Equity**: Ensuring demographic fairness across job bands.
- **Budget Compliance**: Actively monitoring department allocation vs. actual awards.
- **Policy Enforcement**: Quickly flagging rogue managers who award beyond band caps.

When clients need these reports, implementation teams are forced into manual, error-prone data extraction and SQL wrangling against underlying databases. 

## The Solution
`hris-compensation-reporter` is an open-source, CLI-based solution designed to query an underlying compensation PostgreSQL/SQLite database and automatically surface structured, ready-to-present analytics.

## Features
- **SQLite Relational Store**: A carefully modeled backend mimicking HCM data structures (`employees`, `budgets`, `compensation_cycles`, `compensation_awards`).
- **Seed Generator**: Generates 100 realistic rows with injected real-world complexities (pay gaps, over/under spending).
- **5 Critical Custom SQL Reports**: Addressing the business needs explicitly.

## Setup Instructions

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize and Seed Database:**
   ```bash
   python seed.py
   ```
   This will generate a `compensation.db` SQLite database file and populate it with synthetic data.

3. **Run the Reporter CLI:**
   You can run a specific report:
   ```bash
   python main.py --report pay_equity
   python main.py --report budget_utilization
   python main.py --report policy_violation
   python main.py --report merit_distribution
   python main.py --report manager_summary
   ```
   
   Or run all reports at once:
   ```bash
   python main.py --report all
   ```

The script outputs results as formatted tables in the console and saves raw CSV exports to the `reports/` directory.
