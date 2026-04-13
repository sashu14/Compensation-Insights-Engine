from flask import Flask, render_template, request
import sqlite3
import pandas as pd
from runner import parse_sql_file

app = Flask(__name__)
DB_FILE = 'compensation.db'

# Simple mapping of report IDs to human readable info 
# In a real app this might be parsed from the SQL comments, but we can hardcode for the UI
REPORT_META = {
    'pay_equity': {
        'title': 'Pay Equity Audit',
        'description': 'Average merit award by job band and gender. Identifies potential demographic disparities.'
    },
    'budget_utilization': {
        'title': 'Budget Utilization',
        'description': 'Allocated vs awarded vs remaining funds by department.'
    },
    'policy_violation': {
        'title': 'Policy Violations',
        'description': 'Flags employees whose award exceeded their job band max caps.'
    },
    'merit_distribution': {
        'title': 'Merit Distribution Curve',
        'description': 'Count of employees per award dollar bracket to visualize the scatterplot.'
    },
    'manager_summary': {
        'title': 'Manager Impact Summary',
        'description': 'Evaluates manager award rates, volume, and total budget footprint.'
    }
}

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    return render_template('dashboard.html', reports=REPORT_META)

@app.route('/report/<report_id>')
def view_report(report_id):
    queries = parse_sql_file()
    
    if report_id not in queries:
        return "Report not found", 404
        
    query = queries[report_id]
    conn = get_db_connection()
    
    try:
        df = pd.read_sql_query(query, conn)
        
        # Render the dataframe to html
        if df.empty:
            table_html = None
        else:
            # Use formatters to nicely print numbers if needed, but standard is fine
            table_html = df.to_html(classes=['report-table'], index=False, border=0, justify='left')
    except Exception as e:
        table_html = f"<p>Error executing query: {str(e)}</p>"
    finally:
        conn.close()
        
    meta = REPORT_META.get(report_id, {'title': report_id.replace('_', ' ').title()})
        
    return render_template('report.html', title=meta['title'], table_html=table_html)

if __name__ == '__main__':
    # Run the Flask app on localhost:5000
    app.run(host='127.0.0.1', port=5000, debug=True)
