import sqlite3
import pandas as pd
from tabulate import tabulate
import os
import re

DB_FILE = 'compensation.db'
SQL_FILE = 'queries.sql'
OUTPUT_DIR = 'reports'

def parse_sql_file():
    """
    Parses the queries.sql file to extract distinct queries and their names.
    Expects format:
    -- name: query_name
    SELECT ... ;
    """
    with open(SQL_FILE, 'r') as f:
        content = f.read()

    queries = {}
    current_name = None
    current_query = []
    
    for line in content.splitlines():
        name_match = re.match(r'^-- name:\s*(\w+)$', line)
        if name_match:
            if current_name and current_query:
                queries[current_name] = "\n".join(current_query).strip()
            current_name = name_match.group(1)
            current_query = []
        elif current_name:
            current_query.append(line)
            
    if current_name and current_query:
         queries[current_name] = "\n".join(current_query).strip()
         
    return queries

def run_report(report_name, query, conn):
    """Executes a parsed query, prints the tabulated result, and saves to CSV."""
    print(f"\n{'='*50}")
    print(f"REPORT: {report_name.replace('_', ' ').title()}")
    print(f"{'='*50}")
    
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("No data found for this report.")
        return
        
    print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    csv_path = os.path.join(OUTPUT_DIR, f"{report_name}.csv")
    df.to_csv(csv_path, index=False)
    print(f"-> Saved raw output to: {csv_path}\n")

def run_all():
    queries = parse_sql_file()
    
    if not os.path.exists(DB_FILE):
         print("Error: Database not found. Please run seed.py first.")
         return
         
    conn = sqlite3.connect(DB_FILE)
    
    for name, sql in queries.items():
        run_report(name, sql, conn)
        
    conn.close()
    
def run_single(report_name):
    queries = parse_sql_file()
    
    if report_name not in queries:
        print(f"Error: Report '{report_name}' not found.")
        print("Available reports:", ", ".join(queries.keys()))
        return
        
    if not os.path.exists(DB_FILE):
         print("Error: Database not found. Please run seed.py first.")
         return
         
    conn = sqlite3.connect(DB_FILE)
    run_report(report_name, queries[report_name], conn)
    conn.close()
