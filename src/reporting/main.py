#!/usr/bin/env python3

import logging
import sys
import os
import json
from datetime import datetime, timedelta
from ..util.logging_config import setup_logging
from ..util.output_capture import TeeOutput
from .fetch_esc_kpi import fetch_esc_kpi, analyze_filter_18891
from .fetch_weekly_report import fetch_weekly_report

def main():
    """Run ESC KPI report followed by weekly report"""
    # Create weekly_report directory if it doesn't exist
    report_dir = "weekly_report"
    os.makedirs(report_dir, exist_ok=True)
    
    # Create filenames with YYYYmmdd format in weekly_report directory
    date_str = (datetime.now() + timedelta(days=(7 - datetime.now().weekday()))).strftime('%Y%m%d')
    report_filename = os.path.join(report_dir, f"{date_str}_weekly_report.txt")
    json_filename = os.path.join(report_dir, f"{date_str}_weekly_report.json")
    
    # Setup output capture
    tee = TeeOutput(report_filename)
    original_stdout = sys.stdout
    sys.stdout = tee
    
    try:
        # Run ESC KPI report
        logging.info("Starting ESC KPI report")
        print(f"Weekly Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        kpi_data = fetch_esc_kpi()
        analysis_data = analyze_filter_18891()
        
        print("\n" + "="*80 + "\n")
        
        # Run weekly report
        logging.info("Starting weekly report")
        weekly_data = fetch_weekly_report()
        
        # Save JSON report
        json_data = {
            "generated_at": datetime.now().isoformat(),
            "report_date": date_str,
            "esc_kpi_summary": kpi_data,
            "open_esc": analysis_data,
            "high_level_objectives": weekly_data
        }
        
        with open(json_filename, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        logging.info("All reports completed successfully")
        print(f"\nReports saved to:")
        print(f"  Text: {report_filename}")
        print(f"  JSON: {json_filename}")
        
    except Exception as e:
        logging.error(f"Error running reports: {e}")
    finally:
        # Restore original stdout and close file
        sys.stdout = original_stdout
        tee.close()

if __name__ == "__main__":
    main()