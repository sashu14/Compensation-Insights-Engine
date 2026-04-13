import argparse
from runner import run_all, run_single, parse_sql_file

def main():
    parser = argparse.ArgumentParser(description="HRIS Compensation Reporter CLI")
    parser.add_argument('--report', required=True, 
                        help="Specify report name to run (e.g. 'pay_equity') or 'all' to run everything.")
    
    args = parser.parse_args()
    
    if args.report.lower() == 'all':
        run_all()
    else:
        run_single(args.report)

if __name__ == '__main__':
    main()
